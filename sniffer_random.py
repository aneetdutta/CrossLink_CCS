import os
import json
import math
import random
import pathlib

import matplotlib.pyplot as plt
from matplotlib.patches import Circle


# ============================================================
# INPUT POLYGON (SUMO XY meters)
# ============================================================
polygon_coords = [
    (3499.77, 1500.07),
    (5798.43, 3799.93),
    (6452.11, 3150.56),
    (5401.44, 2099.71),
    (5751.91, 1749.63),
    (4500.10, 498.92),
]


# ============================================================
# CONFIG
# ============================================================
N_POINTS = int(os.getenv("N_POINTS", "198"))
RADIUS_M = float(os.getenv("RADIUS_M", "200"))
SEED = int(os.getenv("SEED", "1"))

# If True: the entire circle of radius RADIUS_M must lie inside the polygon
# (i.e., center must be at least RADIUS_M away from every polygon edge).
REQUIRE_FULL_CIRCLE_INSIDE = os.getenv("REQUIRE_FULL_CIRCLE_INSIDE", "false").lower() == "true"

ROUND_DECIMALS = int(os.getenv("ROUND_DECIMALS", "2"))

OUT_JSON = os.getenv("OUT_JSON", "random_points_in_polygon.json")
OUT_PNG = os.getenv("OUT_PNG", "random_points_in_polygon.png")
PLOT = os.getenv("PLOT", "true").lower() == "true"

MAX_TRIES = int(os.getenv("MAX_TRIES", "2000000"))


# ============================================================
# Geometry helpers
# ============================================================
def point_on_segment(px, py, x1, y1, x2, y2, eps=1e-9) -> bool:
    # Check colinearity via cross product
    cross = (px - x1) * (y2 - y1) - (py - y1) * (x2 - x1)
    if abs(cross) > eps:
        return False
    # Check within bounding box
    minx, maxx = (x1, x2) if x1 <= x2 else (x2, x1)
    miny, maxy = (y1, y2) if y1 <= y2 else (y2, y1)
    return (minx - eps <= px <= maxx + eps) and (miny - eps <= py <= maxy + eps)


def point_in_polygon(px, py, poly) -> bool:
    # Treat boundary as inside
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if point_on_segment(px, py, x1, y1, x2, y2):
            return True

    # Ray casting
    inside = False
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > py) != (y2 > py):
            x_int = x1 + (py - y1) * (x2 - x1) / (y2 - y1)
            if x_int >= px:
                inside = not inside
    return inside


def point_segment_distance(px, py, x1, y1, x2, y2) -> float:
    # Distance from point P to segment AB
    vx = x2 - x1
    vy = y2 - y1
    wx = px - x1
    wy = py - y1

    c1 = wx * vx + wy * vy
    if c1 <= 0:
        return math.hypot(px - x1, py - y1)

    c2 = vx * vx + vy * vy
    if c2 <= c1:
        return math.hypot(px - x2, py - y2)

    t = c1 / c2
    projx = x1 + t * vx
    projy = y1 + t * vy
    return math.hypot(px - projx, py - projy)


def min_distance_to_polygon_edges(px, py, poly) -> float:
    n = len(poly)
    dmin = float("inf")
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        d = point_segment_distance(px, py, x1, y1, x2, y2)
        if d < dmin:
            dmin = d
    return dmin


# ============================================================
# Sampling
# ============================================================
poly_xs = [p[0] for p in polygon_coords]
poly_ys = [p[1] for p in polygon_coords]
xmin, xmax = min(poly_xs), max(poly_xs)
ymin, ymax = min(poly_ys), max(poly_ys)

# Optional speed-up if requiring full circle inside:
# center must be at least RADIUS_M away from bbox edges too.
if REQUIRE_FULL_CIRCLE_INSIDE:
    xmin_s, xmax_s = xmin + RADIUS_M, xmax - RADIUS_M
    ymin_s, ymax_s = ymin + RADIUS_M, ymax - RADIUS_M
else:
    xmin_s, xmax_s = xmin, xmax
    ymin_s, ymax_s = ymin, ymax

if xmin_s >= xmax_s or ymin_s >= ymax_s:
    raise RuntimeError(
        "Sampling box collapsed. If REQUIRE_FULL_CIRCLE_INSIDE=true, "
        "your polygon/bbox may be too small for the chosen radius."
    )

rng = random.Random(SEED)

points_set = set()
points = []

tries = 0
while len(points) < N_POINTS and tries < MAX_TRIES:
    tries += 1

    x = rng.uniform(xmin_s, xmax_s)
    y = rng.uniform(ymin_s, ymax_s)

    if not point_in_polygon(x, y, polygon_coords):
        continue

    if REQUIRE_FULL_CIRCLE_INSIDE:
        # Ensure the circle of radius RADIUS_M around (x,y) stays inside polygon
        if min_distance_to_polygon_edges(x, y, polygon_coords) < RADIUS_M - 1e-9:
            continue

    xr = round(x, ROUND_DECIMALS)
    yr = round(y, ROUND_DECIMALS)
    key = (xr, yr)
    if key in points_set:
        continue

    points_set.add(key)
    points.append([xr, yr])

if len(points) < N_POINTS:
    raise RuntimeError(
        f"Could only generate {len(points)} points out of requested {N_POINTS} "
        f"after {tries} tries.\n"
        f"Tip: increase MAX_TRIES, reduce N_POINTS, or set REQUIRE_FULL_CIRCLE_INSIDE=false."
    )

print(f"Generated {len(points)} random points inside polygon (seed={SEED}).")
print(f"REQUIRE_FULL_CIRCLE_INSIDE={REQUIRE_FULL_CIRCLE_INSIDE}, radius={RADIUS_M}m, tries={tries}")


# ============================================================
# Save JSON (exact format you used before)
# ============================================================
out_json_path = pathlib.Path(OUT_JSON)
out_json_path.parent.mkdir(parents=True, exist_ok=True)

with out_json_path.open("w", encoding="utf-8") as f:
    json.dump({"sniffer_location": points}, f, indent=4)

print(f"Saved JSON: {out_json_path.resolve()}")


# ============================================================
# Plot
# ============================================================
if PLOT:
    fig, ax = plt.subplots(figsize=(10, 10))

    # Polygon outline
    poly_plot_x = [p[0] for p in polygon_coords] + [polygon_coords[0][0]]
    poly_plot_y = [p[1] for p in polygon_coords] + [polygon_coords[0][1]]
    ax.plot(poly_plot_x, poly_plot_y, linewidth=2.0, label="Polygon")

    # Points
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    ax.scatter(xs, ys, marker="x", label=f"Random points (N={len(points)})")

    # Circles (radius visualization)
    for (x, y) in points:
        ax.add_patch(Circle((x, y), RADIUS_M, fill=False, linewidth=0.5))

    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(xmin - 50, xmax + 50)
    ax.set_ylim(ymin - 50, ymax + 50)
    ax.set_xlabel("x (m)")
    ax.set_ylabel("y (m)")
    ax.set_title(f"Random points inside polygon (N={len(points)}), radius={RADIUS_M}m")
    ax.legend()

    out_png_path = pathlib.Path(OUT_PNG)
    out_png_path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(out_png_path, dpi=200)
    print(f"Saved plot: {out_png_path.resolve()}")

    plt.show()

