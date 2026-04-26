"""
final_filter_plot_uniqueLoc_polygon_only.py

Hardcoded script (no argparse) that:
1) Reads your existing OpenCellID CSV: data/opencellid_cells_<SCENARIO_NAME>.csv
2) Filters: radio=LTE, mcc=210, mnc=10
3) Optionally filters points inside your SUMO polygon (XY -> lon/lat using SUMO net projection)
4) Deduplicates: keep only ONE cell per "same location" (rounded lat/lon)
5) Saves final CSV
6) Creates an OpenStreetMap (Leaflet) HTML plot with:
   - ONLY the GREEN polygon overlay (no bbox rectangles)
   - cell point markers + range circles

If your polygon conversion fails (SUMO net not geo-referenced), the map will still plot cells,
but polygon won't be drawn.

Prereq:
  export SUMO_HOME=/usr/share/sumo   (or your SUMO install)
"""

import os
import sys
import csv
import json
import pathlib
import xml.etree.ElementTree as ET


# =========================
# HARD-CODED SETTINGS
# =========================
SCENARIO_NAME = os.getenv("SCENARIO_NAME", "demo")

SUMO_CFG_FILE = f"{pathlib.Path().resolve()}/simulation/sumo/sumo_scenario/most.sumocfg"

# Polygon in SUMO XY meters (your coordinates)
POLYGON_COORDS_XY = [
    (3499.77, 1500.07),
    (5798.43, 3799.93),
    (6452.11, 3150.56),
    (5401.44, 2099.71),
    (5751.91, 1749.63),
    (4500.10, 498.92),
]

DATA_DIR = pathlib.Path().resolve() / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Input CSV you already created earlier
IN_CSV = DATA_DIR / f"demo/opencellid_cells_{SCENARIO_NAME}.csv"
print(IN_CSV)
#IN_CSV="/home/aneet_wisec/usenix_2025/path-leakage/data/demo/opencellid_cells_demo.csv"
# Output
OUT_CSV = DATA_DIR / f"opencellid_cells_{SCENARIO_NAME}_LTE_212_10_uniqueLoc_new.csv"
OUT_HTML = DATA_DIR / f"opencellid_cells_{SCENARIO_NAME}_LTE_212_10_uniqueLoc_polygonOnly_new.html"

# Filters
FILTER_RADIO = "LTE"
FILTER_MCC = 212
FILTER_MNC = 10

# Keep only points inside polygon (only applied if polygon converts to valid lon/lat)
APPLY_POLYGON_FILTER = True

# Dedup “same location” by rounding lat/lon
ROUND_DIGITS = 3  # 4=more aggressive merge, 6=stricter

# Optional map performance cap
MAX_CELLS_ON_MAP = None  # e.g. 2000


# =========================
# Small helpers
# =========================
def safe_int(v):
    try:
        return int(float(v))
    except Exception:
        return None


def safe_float(v):
    try:
        return float(v)
    except Exception:
        return None


def read_csv_rows(path: pathlib.Path):
    with path.open("r", encoding="utf-8") as f:
        r = csv.DictReader(f)
        rows = list(r)
        fieldnames = r.fieldnames or []
    return rows, fieldnames


def write_csv_rows(path: pathlib.Path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for row in rows:
            w.writerow(row)


# =========================
# Filter + dedupe
# =========================
def filter_rows_lte_210_10(rows):
    out = []
    for row in rows:
        radio = str(row.get("radio", "")).strip().upper()
        mcc = safe_int(row.get("mcc"))
        mnc = safe_int(row.get("mnc"))
        lat = safe_float(row.get("lat"))
        lon = safe_float(row.get("lon"))

        if radio != FILTER_RADIO:
            continue
        if mcc!=FILTER_MCC:
            continue
        if mnc!=FILTER_MNC:
            continue
        if lat is None or lon is None:
            continue

        out.append(row)
    return out


def pick_better_row(a, b):
    """
    If two rows have the SAME rounded location, keep the "better" one:
      1) higher samples
      2) smaller range
      3) changeable == 0 preferred
      4) keep a
    """
    a_samples = safe_int(a.get("samples")) or 0
    b_samples = safe_int(b.get("samples")) or 0
    if b_samples > a_samples:
        return b
    if b_samples < a_samples:
        return a

    a_range = safe_float(a.get("range"))
    b_range = safe_float(b.get("range"))
    a_range = a_range if a_range is not None else float("inf")
    b_range = b_range if b_range is not None else float("inf")
    if b_range < a_range:
        return b
    if b_range > a_range:
        return a

    a_ch = safe_int(a.get("changeable"))
    b_ch = safe_int(b.get("changeable"))
    if b_ch == 0 and a_ch != 0:
        return b
    if a_ch == 0 and b_ch != 0:
        return a

    return a


def dedupe_by_location(rows):
    best = {}
    for row in rows:
        lat = safe_float(row.get("lat"))
        lon = safe_float(row.get("lon"))
        if lat is None or lon is None:
            continue

        key = (round(lat, ROUND_DIGITS), round(lon, ROUND_DIGITS))
        if key not in best:
            best[key] = row
        else:
            best[key] = pick_better_row(best[key], row)

    out = list(best.values())
    out.sort(key=lambda r: (safe_float(r.get("lat")) or 0.0, safe_float(r.get("lon")) or 0.0))
    return out


# =========================
# Polygon overlay (SUMO XY -> lon/lat)
# =========================
def import_sumolib():
    sumo_home = os.environ.get("SUMO_HOME")
    if not sumo_home:
        raise RuntimeError("SUMO_HOME is not set. Example:\n  export SUMO_HOME=/usr/share/sumo")
    tools = os.path.join(sumo_home, "tools")
    if tools not in sys.path:
        sys.path.append(tools)
    import sumolib  # type: ignore
    return sumolib


def netfile_from_sumocfg(sumocfg_path: pathlib.Path) -> pathlib.Path:
    root = ET.parse(sumocfg_path).getroot()
    el = root.find(".//net-file")
    if el is None or not el.get("value"):
        raise RuntimeError("Could not find <net-file value='...'> inside the .sumocfg")
    return (sumocfg_path.parent / el.get("value")).resolve()

import math
def polygon_xy_to_lonlat(sumolib, net_file: pathlib.Path, poly_xy):
    net = sumolib.net.readNet(str(net_file))
    out = []
    for (x, y) in poly_xy:
        lon, lat = net.convertXY2LonLat(x, y)  # (lon, lat)
        out.append((float(lon), float(lat)))
    return out


def lonlat_looks_valid(poly_lonlat):
    for lon, lat in poly_lonlat:
        if not (-180 <= lon <= 180 and -90 <= lat <= 90):
            return False
    return True
def _point_on_segment(px, py, x1, y1, x2, y2, eps=1e-6):
    """
    Returns True if (px,py) is on the line segment (x1,y1)-(x2,y2) within tolerance eps.
    eps is in degrees (lon/lat units).
    """
    # Fast bbox reject (+eps padding)
    if (px < min(x1, x2) - eps or px > max(x1, x2) + eps or
        py < min(y1, y2) - eps or py > max(y1, y2) + eps):
        return False

    dx = x2 - x1
    dy = y2 - y1
    seg_len = math.hypot(dx, dy)

    # Degenerate segment (two identical points)
    if seg_len == 0:
        return math.hypot(px - x1, py - y1) <= eps

def point_in_polygon(lon, lat, poly_lonlat):
    """Ray casting; boundary treated as inside."""
    inside = False
    n = len(poly_lonlat)
    for i in range(n):
        x1, y1 = poly_lonlat[i]
        x2, y2 = poly_lonlat[(i + 1) % n]
        if _point_on_segment(lon, lat, x1, y1, x2, y2):
           return True
        # boundary check
        cross = (lon - x1) * (y2 - y1) - (lat - y1) * (x2 - x1)
        if abs(cross) < 1e-8:
            dot = (lon - x1) * (lon - x2) + (lat - y1) * (lat - y2)
            if dot <= 1e-12:
                return True

        # ray crossing
        if (y1 > lat) != (y2 > lat):
            x_at_lat = x1 + (x2 - x1) * (lat - y1) / ((y2 - y1) + 1e-30)
            if x_at_lat > lon:
                inside = not inside

    return inside


# =========================
# Map (Leaflet + OSM) — ONLY green polygon overlay (no bbox rectangles)
# =========================
def write_leaflet_map(path: pathlib.Path, rows, polygon_lonlat=None, polygon_valid=False):
    path.parent.mkdir(parents=True, exist_ok=True)

    plot_rows = rows
    if MAX_CELLS_ON_MAP is not None and len(plot_rows) > MAX_CELLS_ON_MAP:
        plot_rows = plot_rows[:MAX_CELLS_ON_MAP]

    # Prepare cells for JS
    cells_js = []
    for row in plot_rows:
        lat = safe_float(row.get("lat"))
        lon = safe_float(row.get("lon"))
        if lat is None or lon is None:
            continue

        rng = safe_float(row.get("range"))
        if rng is not None and rng <= 0:
            rng = None

        cells_js.append({
            "lat": lat,
            "lon": lon,
            "range": rng,
            "cellid": row.get("cellid"),
            "radio": row.get("radio"),
            "mcc": row.get("mcc"),
            "mnc": row.get("mnc"),
            "lac": row.get("lac"),
            "samples": row.get("samples"),
        })

    # Polygon for Leaflet: [lat, lon]
    poly_latlon = []
    polygon_warn = ""
    if polygon_lonlat is not None and not polygon_valid:
        polygon_warn = "Polygon lon/lat look invalid (SUMO net likely not geo-referenced). Polygon not drawn."
    if polygon_valid and polygon_lonlat:
        poly_latlon = [[lat, lon] for (lon, lat) in polygon_lonlat]

    html = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>LTE 210/10 cells + polygon</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>

  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

  <style>
    html, body, #map {{ height: 100%; margin: 0; }}
    #msg {{
      position: absolute;
      top: 10px; left: 10px; right: 10px;
      background: rgba(255,255,255,0.95);
      padding: 10px;
      border-radius: 6px;
      font-family: sans-serif;
      font-size: 13px;
      z-index: 9999;
      max-width: 560px;
    }}
    .dot {{
      display:inline-block;
      width:10px;height:10px;border-radius:50%;
      margin-right:6px; vertical-align:middle;
    }}
  </style>
</head>
<body>
<div id="map"></div>

<div id="msg">
  <b>Legend</b><br/>
  <span class="dot" style="background:green;"></span>Polygon (only overlay)<br/>
  <span class="dot" style="background:#3388ff;"></span>Cell point + range circle<br/><br/>

  <b>Filter:</b> radio={FILTER_RADIO}, mcc={FILTER_MCC}, mnc={FILTER_MNC}<br/>
  <b>Dedup:</b> one cell per rounded lat/lon (digits={ROUND_DIGITS})<br/>
  <b>Cells plotted:</b> {len(cells_js)}<br/>
  <span style="color:#b00;">{polygon_warn}</span>
</div>

<script>
window.addEventListener("load", () => {{
  // If Leaflet didn't load (offline / CDN blocked)
  if (typeof L === "undefined") {{
    document.getElementById("msg").innerHTML =
      "<b>Leaflet failed to load.</b><br/>" +
      "Likely no internet access or unpkg.com blocked.<br/>" +
      "Open DevTools Console (F12) to see network errors.";
    return;
  }}

  const polygon = {json.dumps(poly_latlon)};
  const cells = {json.dumps(cells_js)};

  const map = L.map("map");
  L.tileLayer("https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png", {{
    maxZoom: 19,
    attribution: "&copy; OpenStreetMap contributors"
  }}).addTo(map);

  const layers = [];

  // ONLY polygon overlay (green)
  let polyLayer = null;
  if (polygon.length > 0) {{
    polyLayer = L.polygon(polygon, {{
      color: "green",
      weight: 2,
      fillOpacity: 0.06
    }}).addTo(map);
    layers.push(polyLayer);
  }}

  // Cells + range circles
  cells.forEach(c => {{
    const popup = `
      <b>cellid:</b> ${{c.cellid}}<br/>
      <b>radio:</b> ${{c.radio}}<br/>
      <b>mcc/mnc:</b> ${{c.mcc}} / ${{c.mnc}}<br/>
      <b>lac:</b> ${{c.lac}}<br/>
      <b>samples:</b> ${{c.samples}}<br/>
      <b>range (m):</b> ${{c.range === null ? "n/a" : c.range}}
    `;

    const pt = L.circleMarker([c.lat, c.lon], {{ radius: 4 }}).addTo(map).bindPopup(popup);
    layers.push(pt);

    if (c.range !== null) {{
      const circle = L.circle([c.lat, c.lon], {{
        radius: c.range,
        weight: 1,
        fillOpacity: 0.05
      }}).addTo(map);
      layers.push(circle);
    }}
  }});

  // Fit: polygon first, else cells, else world
  if (polyLayer !== null) {{
    map.fitBounds(polyLayer.getBounds().pad(0.1));
  }} else if (layers.length > 0) {{
    const group = L.featureGroup(layers);
    map.fitBounds(group.getBounds().pad(0.1));
  }} else {{
    map.setView([0,0], 2);
  }}
}});
</script>
</body>
</html>
"""
    path.write_text(html, encoding="utf-8")


# =========================
# MAIN
# =========================
def main():
    if not IN_CSV.exists():
        raise FileNotFoundError(f"Input CSV not found: {IN_CSV}")

    # Read existing CSV
    rows, fieldnames = read_csv_rows(IN_CSV)
    print("Read:", IN_CSV, "rows:", len(rows))

    #Filter LTE/210/10
    filtered = filter_rows_lte_210_10(rows)
    print("After LTE/210/10 filter:", len(filtered))

    # Try polygon conversion for overlay/filtering
    polygon_lonlat = None
    polygon_valid = False
    try:
        sumolib = import_sumolib()
        net_file = netfile_from_sumocfg(pathlib.Path(SUMO_CFG_FILE).resolve())
        polygon_lonlat = polygon_xy_to_lonlat(sumolib, net_file, POLYGON_COORDS_XY)
        polygon_valid = lonlat_looks_valid(polygon_lonlat)
        print("Net file:", net_file)
        print("Polygon lon/lat valid?:", polygon_valid)
        if polygon_lonlat:
            print("Polygon lon/lat sample:", polygon_lonlat[:2])
    except Exception as e:
        print("Polygon conversion failed (polygon will not be drawn):", str(e))

    # Optional: polygon filter (only if polygon is valid)
    if APPLY_POLYGON_FILTER and polygon_valid and polygon_lonlat:
        before = len(filtered)
        tmp = []
        for r in filtered:
            lon = safe_float(r.get("lon"))
            lat = safe_float(r.get("lat"))
            if lon is None or lat is None:
                continue
            if point_in_polygon(lon, lat, polygon_lonlat):
                tmp.append(r)
        filtered = tmp
        print("After polygon filter:", len(filtered), f"(from {before})")
    elif APPLY_POLYGON_FILTER:
        print("Polygon filter requested but polygon is invalid/unavailable -> skipping polygon filter.")

    # Dedupe by location (ONE cell per rounded lat/lon)
    final_rows = dedupe_by_location(filtered)
    print("After location dedupe:", len(final_rows))

    # Save final CSV (keep original header if possible)
    if not fieldnames:
        fieldnames = sorted({k for r in final_rows for k in r.keys()})
    write_csv_rows(OUT_CSV, final_rows, fieldnames)
    print("Wrote CSV:", OUT_CSV)

    # Save map HTML (ONLY green polygon overlay + cells)
    write_leaflet_map(OUT_HTML, final_rows, polygon_lonlat=polygon_lonlat, polygon_valid=polygon_valid)
    print("Wrote map HTML:", OUT_HTML, "(open in browser)")

    print("\nIf the HTML looks blank/white:")
    print(" - Open browser DevTools (F12) Console -> check Leaflet/OSM tile loading errors (CDN/internet).")


if __name__ == "__main__":
    main()

