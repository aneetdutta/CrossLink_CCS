import os
import csv
import json
import math
import pathlib

import matplotlib.pyplot as plt
from matplotlib.patches import Circle


# ============================================================
# CONFIG (hardcode or override with env vars)
# ============================================================
SCENARIO_NAME = os.getenv("SCENARIO_NAME", "demo")

# Base-station CSV (SUMO XY meters). Must include: cellid, x, y, range
BS_XY_CSV = os.getenv(
    "BS_XY_CSV",
    f"data/opencellid_cells_{SCENARIO_NAME}_LTE_212_10_uniqueLoc_XY.csv"
)

# Sniffer radius (meters)
SNIFFER_RADIUS_M = float(os.getenv("SNIFFER_RADIUS_M", "100"))

# Output JSON format must be exactly: {"sniffer_location": [[x,y], ...]}
OUT_JSON = os.getenv(
    "SNIFFER_JSON",
    f"data/{SCENARIO_NAME}/handover_sniffer_location_r{int(SNIFFER_RADIUS_M)}_2.json"
)

# Plot output
OUT_PNG = os.getenv(
    "SNIFFER_PLOT",
    f"data/{SCENARIO_NAME}/handover_sniffers_plot_r{int(SNIFFER_RADIUS_M)}.png"
)

# Round sniffer coordinates in output (meters)
ROUND_DECIMALS = int(os.getenv("SNIFFER_ROUND_DECIMALS", "2"))

# Drawing controls (sniffer circles can be *many*)
DRAW_SNIFFER_CIRCLES = os.getenv("DRAW_SNIFFER_CIRCLES", "true").lower() == "true"
MAX_SNIFFER_CIRCLES_TO_DRAW = int(os.getenv("MAX_SNIFFER_CIRCLES_TO_DRAW", "3000"))

# ------------------------------------------------------------
# Polygon constraint (SUMO XY meters)  ✅ sniffers must be inside this polygon
# ------------------------------------------------------------
polygon_coords = [
    (3499.77, 1500.07),
    (5798.43, 3799.93),
    (6452.11, 3150.56),
    (5401.44, 2099.71),
    (5751.91, 1749.63),
    (4500.10, 498.92),
]


# ============================================================
# Helpers
# ============================================================
def safe_float(v):
    try:
        return float(v)
    except Exception:
        return None


def pick_col(row: dict, candidates):
    """
    Fetch a column in a case-insensitive way.
    candidates: list of acceptable names, e.g. ["range", "radius"]
    """
    keys = list(row.keys())
    low = {k.lower(): k for k in keys}
    for name in candidates:
        if name in row:
            return row[name]
        if name.lower() in low:
            return row[low[name.lower()]]
    return None


def dist2(x1, y1, x2, y2):
    dx = x1 - x2
    dy = y1 - y2
    return dx * dx + dy * dy


def circles_overlap(x1, y1, r1, x2, y2, r2) -> bool:
    # overlap if distance < r1+r2
    return dist2(x1, y1, x2, y2) < (r1 + r2) * (r1 + r2)


def bbox_intersection_circle_bboxes(x1, y1, r1, x2, y2, r2):
    """
    The overlap lens (C1 ∩ C2) is contained in BOTH circle bounding boxes.
    Its bounding box lies within the intersection of those bounding boxes.
    """
    xmin = max(x1 - r1, x2 - r2)
    xmax = min(x1 + r1, x2 + r2)
    ymin = max(y1 - r1, y2 - r2)
    ymax = min(y1 + r1, y2 + r2)
    if xmin > xmax or ymin > ymax:
        return None
    return xmin, xmax, ymin, ymax


def triangular_lattice_points(xmin, xmax, ymin, ymax, r):
    """
    Triangular lattice that guarantees plane coverage by circles of radius r.

    Spacing:
      a  = sqrt(3)*r   (horizontal spacing)
      dy = 1.5*r       (vertical spacing)
    Odd rows are shifted by a/2.
    """
    a = math.sqrt(3.0) * r
    dy = 1.5 * r

    # align start so output is stable run-to-run
    y0 = math.floor(ymin / dy) * dy
    y1 = math.ceil(ymax / dy) * dy

    row = 0
    y = y0
    while y <= y1 + 1e-9:
        x_offset = 0.0 if (row % 2 == 0) else (a / 2.0)

        x0 = math.floor((xmin - x_offset) / a) * a + x_offset
        x1 = math.ceil((xmax - x_offset) / a) * a + x_offset

        x = x0
        while x <= x1 + 1e-9:
            if xmin - 1e-9 <= x <= xmax + 1e-9 and ymin - 1e-9 <= y <= ymax + 1e-9:
                yield x, y
            x += a

        y += dy
        row += 1


# ------------------------------------------------------------
# Point-in-polygon (boundary treated as inside)
# ------------------------------------------------------------
def point_on_segment(px, py, x1, y1, x2, y2, eps=1e-9):
    cross = (px - x1) * (y2 - y1) - (py - y1) * (x2 - x1)
    if abs(cross) > eps:
        return False
    minx, maxx = (x1, x2) if x1 <= x2 else (x2, x1)
    miny, maxy = (y1, y2) if y1 <= y2 else (y2, y1)
    return (minx - eps <= px <= maxx + eps) and (miny - eps <= py <= maxy + eps)


def point_in_polygon(px, py, poly):
    # boundary check first
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if point_on_segment(px, py, x1, y1, x2, y2):
            return True

    # ray casting
    inside = False
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > py) != (y2 > py):
            x_int = x1 + (py - y1) * (x2 - x1) / (y2 - y1)
            if x_int >= px:
                inside = not inside
    return inside


# Precompute polygon bbox for faster rejection
poly_xs = [p[0] for p in polygon_coords]
poly_ys = [p[1] for p in polygon_coords]
POLY_XMIN, POLY_XMAX = min(poly_xs), max(poly_xs)
POLY_YMIN, POLY_YMAX = min(poly_ys), max(poly_ys)


# ============================================================
# Load base stations
# ============================================================
stations = []
with open(BS_XY_CSV, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        cellid = str(pick_col(row, ["cellid", "cell_id", "cid"]) or "").strip()
        x = safe_float(pick_col(row, ["x", "loc_x", "pos_x"]))
        y = safe_float(pick_col(row, ["y", "loc_y", "pos_y"]))
        r = safe_float(pick_col(row, ["range", "radius", "range_m"]))

        if not cellid or x is None or y is None or r is None:
            continue
        if r <= 0:
            continue

        stations.append({"cellid": cellid, "x": x, "y": y, "r": r})

if len(stations) < 2:
    raise RuntimeError(f"Need at least 2 base stations. Found {len(stations)} in {BS_XY_CSV}")

print(f"Loaded {len(stations)} base stations from: {BS_XY_CSV}")


# ============================================================
# Generate sniffers (ONLY if inside polygon)
# ============================================================
sniffer_points = set()  # set of (rounded_x, rounded_y)

pairs_checked = 0
overlap_pairs = 0
Rsn = SNIFFER_RADIUS_M

candidates_total = 0
candidates_in_poly = 0

for i in range(len(stations)):
    s1 = stations[i]
    for j in range(i + 1, len(stations)):
        s2 = stations[j]
        pairs_checked += 1

        if not circles_overlap(s1["x"], s1["y"], s1["r"], s2["x"], s2["y"], s2["r"]):
            continue

        overlap_pairs += 1

        bb = bbox_intersection_circle_bboxes(s1["x"], s1["y"], s1["r"], s2["x"], s2["y"], s2["r"])
        if bb is None:
            continue

        xmin, xmax, ymin, ymax = bb

        # Expand bbox by sniffer radius so lattice points that cover boundary are included.
        xmin -= Rsn
        xmax += Rsn
        ymin -= Rsn
        ymax += Rsn

        lim1 = (s1["r"] + Rsn) ** 2
        lim2 = (s2["r"] + Rsn) ** 2

        for x, y in triangular_lattice_points(xmin, xmax, ymin, ymax, Rsn):
            candidates_total += 1

            # prune far away points (keep your original pruning)
            if dist2(x, y, s1["x"], s1["y"]) > lim1:
                continue
            if dist2(x, y, s2["x"], s2["y"]) > lim2:
                continue

            # ✅ NEW: force sniffer center inside polygon
            # fast bbox reject
            if x < POLY_XMIN or x > POLY_XMAX or y < POLY_YMIN or y > POLY_YMAX:
                continue
            if not point_in_polygon(x, y, polygon_coords):
                continue

            candidates_in_poly += 1

            sniffer_points.add((round(x, ROUND_DECIMALS), round(y, ROUND_DECIMALS)))

sniffer_location = [[x, y] for (x, y) in sorted(sniffer_points, key=lambda t: (t[0], t[1]))]

print(f"Pairs checked: {pairs_checked}")
print(f"Overlapping (handover) pairs: {overlap_pairs}")
print(f"Candidate lattice points checked: {candidates_total}")
print(f"Candidate points inside polygon (after pruning): {candidates_in_poly}")
print(f"Generated sniffers (deduped): {len(sniffer_location)}")

# Safety assert: every saved sniffer is inside polygon
bad = [p for p in sniffer_location if not point_in_polygon(p[0], p[1], polygon_coords)]
if bad:
    raise RuntimeError(f"BUG: {len(bad)} sniffers are outside polygon (first 5: {bad[:5]})")


# ============================================================
# Save JSON in exact format: {"sniffer_location": [[x,y], ...]}
# ============================================================
out_json_path = pathlib.Path(OUT_JSON)
out_json_path.parent.mkdir(parents=True, exist_ok=True)

with out_json_path.open("w", encoding="utf-8") as f:
    json.dump({"sniffer_location": sniffer_location}, f, indent=4)

print(f"Saved sniffer JSON: {out_json_path}")


# ============================================================
# Plot base stations + radii AND sniffers + radii + polygon outline
# ============================================================
fig, ax = plt.subplots(figsize=(10, 10))

# Polygon outline
poly_plot_x = [p[0] for p in polygon_coords] + [polygon_coords[0][0]]
poly_plot_y = [p[1] for p in polygon_coords] + [polygon_coords[0][1]]
ax.plot(poly_plot_x, poly_plot_y, linewidth=2.0, label="Polygon")

# Base station centers
bs_x = [s["x"] for s in stations]
bs_y = [s["y"] for s in stations]
ax.scatter(bs_x, bs_y, marker="o", label="Base stations")

# Base station circles (range)
for s in stations:
    ax.add_patch(Circle((s["x"], s["y"]), s["r"], fill=False, linestyle="--", linewidth=1.0))

# Sniffer centers
sn_x = [p[0] for p in sniffer_location]
sn_y = [p[1] for p in sniffer_location]
ax.scatter(sn_x, sn_y, marker="x", label="Sniffers")

# Sniffer circles
if DRAW_SNIFFER_CIRCLES:
    if len(sniffer_location) > MAX_SNIFFER_CIRCLES_TO_DRAW:
        print(
            f"NOTE: {len(sniffer_location)} sniffers is a lot to draw circles for.\n"
            f"      Drawing only centers. To force circles, increase MAX_SNIFFER_CIRCLES_TO_DRAW."
        )
    else:
        for (x, y) in sniffer_location:
            ax.add_patch(Circle((x, y), Rsn, fill=False, linestyle="-", linewidth=0.5))

# Set axis limits based on polygon (prevents blank plot and focuses on your area)
margin = max([max([s["r"] for s in stations]), Rsn]) + 20.0
ax.set_xlim(POLY_XMIN - margin, POLY_XMAX + margin)
ax.set_ylim(POLY_YMIN - margin, POLY_YMAX + margin)

ax.set_aspect("equal", adjustable="box")
ax.set_xlabel("x (m)")
ax.set_ylabel("y (m)")
ax.set_title(f"Base stations (range) + sniffers (radius={Rsn}m) inside polygon")
ax.legend()

out_png_path = pathlib.Path(OUT_PNG)
out_png_path.parent.mkdir(parents=True, exist_ok=True)
plt.tight_layout()
plt.savefig(out_png_path, dpi=200)
print(f"Saved plot PNG: {out_png_path}")

plt.show()

