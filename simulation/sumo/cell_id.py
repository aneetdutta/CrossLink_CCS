import os
import csv
import json
import math
import time
import pathlib
from collections import deque, defaultdict

import requests
import traci


# -------------------------
# HARD-CODED CONFIG (your style)
# -------------------------
SUMO_BIN_PATH = "/usr/bin/"
SUMO_CFG_FILE = f"{pathlib.Path().resolve()}/{'simulation/sumo/sumo_scenario/most.sumocfg'}"

USER_TIMESTEPS = int(os.getenv("USER_TIMESTEPS", "1000"))
SCENARIO_NAME = os.getenv("SCENARIO_NAME", "demo")

# Put your OpenCellID key in env (recommended) or hardcode it here
OPENCELLID_KEY = os.getenv("OPENCELLID_KEY", "pk.178438ee4e2761a207e6244ace8d1468")

# Your polygon in SUMO XY (meters)
POLYGON_COORDS_XY = [
    (3499.77, 1500.07),
    (5798.43, 3799.93),
    (6452.11, 3150.56),
    (5401.44, 2099.71),
    (5751.91, 1749.63),
    (4500.10, 498.92),
]

# Optional OpenCellID filters (set to None if you don't want them)
FILTER_RADIO = "LTE"  # e.g., "LTE", "NR", "UMTS", "GSM"
#FILTER_MCC = 212
#FILTER_MNC = 10

# Outputs
OUT_DIR = pathlib.Path(f"{pathlib.Path().resolve()}/data")
OUT_DIR.mkdir(parents=True, exist_ok=True)

USER_FILE = OUT_DIR / f"raw_cell_data_{SCENARIO_NAME}.csv"
CELLS_CSV = OUT_DIR / f"opencellid_cells_{SCENARIO_NAME}.csv"
CELLS_MAP_HTML = OUT_DIR / f"opencellid_cells_{SCENARIO_NAME}.html"

OPENCELLID_URL = "https://opencellid.org/cell/getInArea"
LIMIT = 50  # OpenCellID docs: default+max is 50 for getInArea :contentReference[oaicite:4]{index=4}


# -------------------------
# Helpers: geometry
# -------------------------
def point_in_polygon(lon, lat, polygon_lonlat):
    """Ray casting; boundary treated as inside."""
    inside = False
    n = len(polygon_lonlat)

    for i in range(n):
        x1, y1 = polygon_lonlat[i]
        x2, y2 = polygon_lonlat[(i + 1) % n]

        # boundary check (collinear + within segment bbox)
        cross = (lon - x1) * (y2 - y1) - (lat - y1) * (x2 - x1)
        if abs(cross) < 1e-12:
            dot = (lon - x1) * (lon - x2) + (lat - y1) * (lat - y2)
            if dot <= 1e-12:
                return True

        # ray crossing
        if (y1 > lat) != (y2 > lat):
            x_at_lat = x1 + (x2 - x1) * (lat - y1) / ((y2 - y1) + 1e-30)
            if x_at_lat > lon:
                inside = not inside

    return inside


def bbox_from_polygon(polygon_lonlat):
    lons = [p[0] for p in polygon_lonlat]
    lats = [p[1] for p in polygon_lonlat]
    # OpenCellID wants: latmin, lonmin, latmax, lonmax :contentReference[oaicite:5]{index=5}
    return (min(lats), min(lons), max(lats), max(lons))


def split_bbox_4(b):
    latmin, lonmin, latmax, lonmax = b
    latmid = (latmin + latmax) / 2.0
    lonmid = (lonmin + lonmax) / 2.0
    return [
        (latmin, lonmin, latmid, lonmid),
        (latmin, lonmid, latmid, lonmax),
        (latmid, lonmin, latmax, lonmid),
        (latmid, lonmid, latmax, lonmax),
    ]


def dedupe_cells(cells):
    """Deduplicate practical identity of OpenCellID cell entries."""
    uniq = {}
    for c in cells:
        k = (c.get("mcc"), c.get("mnc"), c.get("lac"), c.get("cellid"), c.get("radio"))
        uniq[k] = c
    return list(uniq.values())


# -------------------------
# Helpers: OpenCellID
# -------------------------
def opencellid_get_page(session, bbox, offset=0):
    latmin, lonmin, latmax, lonmax = bbox

    params = {
        "key": OPENCELLID_KEY,
        "BBOX": f"{latmin},{lonmin},{latmax},{lonmax}",
        "format": "json",
        "limit": LIMIT,      # max 50 :contentReference[oaicite:6]{index=6}
        "offset": offset,    # pagination :contentReference[oaicite:7]{index=7}
    }
    if FILTER_RADIO:
        params["radio"] = FILTER_RADIO
    #if FILTER_MCC is not None:
     #   params["mcc"] = int(FILTER_MCC)
    #if FILTER_MNC is not None:
     #   params["mnc"] = int(FILTER_MNC)

    r = session.get(OPENCELLID_URL, params=params, timeout=30)

    # Often errors are returned as JSON: {"error":"...","code":...} :contentReference[oaicite:8]{index=8}
    data = r.json()
    if isinstance(data, dict) and "error" in data:
        raise RuntimeError(data["error"])

    return data.get("cells", [])


def fetch_bbox_cells_recursive(session, bbox, depth=0, max_depth=12):
    """
    Fetch cells in bbox with pagination.
    If BBOX too big (4,000,000 sq.mts error), split and recurse. :contentReference[oaicite:9]{index=9}
    """
    try:
        all_cells = []
        offset = 0
        while True:
            cells = opencellid_get_page(session, bbox, offset=offset)
            if not cells:
                break
            all_cells.extend(cells)
            if len(cells) < LIMIT:
                break
            offset += LIMIT
        return all_cells

    except RuntimeError as e:
        msg = str(e).lower()
        if "bbox too big" in msg and depth < max_depth:
            out = []
            for sb in split_bbox_4(bbox):
                out.extend(fetch_bbox_cells_recursive(session, sb, depth + 1, max_depth))
            return out
        raise


# -------------------------
# Helpers: output (CSV + Leaflet map)
# -------------------------
def save_cells_csv(path, cells):
    cols = ["cellid", "radio", "mcc", "mnc", "lac", "lat", "lon", "range", "samples", "averageSignalStrength", "changeable"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for c in cells:
            w.writerow({k: c.get(k) for k in cols})


def save_leaflet_map(path, polygon_lonlat, cells):
    # Leaflet wants [lat, lon]
    poly_latlon = [[lat, lon] for (lon, lat) in polygon_lonlat]

    # keep only needed fields
    cells_js = []
    for c in cells:
        if c.get("lat") is None or c.get("lon") is None:
            continue
        try:
            lat = float(c["lat"])
            lon = float(c["lon"])
        except Exception:
            continue

        # OpenCellID includes "range" in responses (meters) :contentReference[oaicite:10]{index=10}
        r = c.get("range")
        try:
            r = float(r) if r is not None else None
        except Exception:
            r = None

        cells_js.append({
            "lat": lat, "lon": lon, "range": r,
            "cellid": c.get("cellid"), "radio": c.get("radio"),
            "mcc": c.get("mcc"), "mnc": c.get("mnc"), "lac": c.get("lac"),
        })

    html = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>OpenCellID cells in polygon</title>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <style>html,body,#map{{height:100%;margin:0;}}</style>
</head>
<body>
<div id="map"></div>
<script>
  const polygon = {json.dumps(poly_latlon)};
  const cells = {json.dumps(cells_js)};

  const map = L.map('map');
  L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
    maxZoom: 19,
    attribution: '&copy; OpenStreetMap contributors'
  }}).addTo(map);

  const polyLayer = L.polygon(polygon, {{weight:2, fillOpacity:0.08}}).addTo(map);
  map.fitBounds(polyLayer.getBounds());

  cells.forEach(c => {{
    const popup = `
      <b>cellid:</b> ${{c.cellid}}<br/>
      <b>radio:</b> ${{c.radio}}<br/>
      <b>mcc/mnc:</b> ${{c.mcc}} / ${{c.mnc}}<br/>
      <b>lac:</b> ${{c.lac}}<br/>
      <b>range (m):</b> ${{c.range === null ? "n/a" : c.range}}
    `;
    L.circleMarker([c.lat, c.lon], {{radius:4}}).addTo(map).bindPopup(popup);
    if (c.range !== null) {{
      L.circle([c.lat, c.lon], {{radius: c.range, weight:1, fillOpacity:0.05}}).addTo(map);
    }}
  }});
</script>
</body>
</html>
"""
    pathlib.Path(path).write_text(html, encoding="utf-8")


# -------------------------
# MAIN (your sim loop + polygon->cells->map)
# -------------------------
def main():
    if OPENCELLID_KEY == "PUT_YOUR_KEY_HERE" or not OPENCELLID_KEY:
        raise RuntimeError("Set OPENCELLID_KEY (env var OPENCELLID_KEY or hardcode it).")

    sumo_cmd = [os.path.join(SUMO_BIN_PATH, "sumo"), "-c", SUMO_CFG_FILE]

    # user logging (your style)
    with open(USER_FILE, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["timestep", "user_id", "loc_x", "loc_y"])
        writer.writeheader()

        traci.start(sumo_cmd)

        try:
            # Convert polygon XY -> lon/lat using TraCI convenience conversion:
            # lon, lat = traci.simulation.convertGeo(x, y) :contentReference[oaicite:11]{index=11}
            polygon_lonlat = []
            for (x, y) in POLYGON_COORDS_XY:
                lon, lat = traci.simulation.convertGeo(x, y)
                polygon_lonlat.append((float(lon), float(lat)))

            bbox = bbox_from_polygon(polygon_lonlat)
            print("Polygon lon/lat sample:", polygon_lonlat[:2])
            print("BBOX latmin,lonmin,latmax,lonmax:", bbox)

            # --- Your simulation loop (kept simple)
            timestep = 0
            now = time.time()
            while timestep < USER_TIMESTEPS:
                # you usually need simulationStep() to advance time
                traci.simulationStep()
                timestep = traci.simulation.getTime()

                user_ids = traci.person.getIDList()
                if timestep % 50 == 0:
                    print("persons:", len(user_ids), "t:", timestep)

                for user_id in user_ids:
                    x, y = traci.person.getPosition(user_id)
                    writer.writerow({"timestep": timestep, "user_id": user_id, "loc_x": x, "loc_y": y})

        finally:
            traci.close()

    # Query OpenCellID AFTER simulation (doesn't need TraCI)
    session = requests.Session()
    print("Querying OpenCellID getInArea (bbox + pagination + split if too big)...")
    # getInArea supports BBOX and pagination with limit/offset; limit max 50 :contentReference[oaicite:12]{index=12}
    cells_bbox = fetch_bbox_cells_recursive(session, bbox)
    cells_bbox = dedupe_cells(cells_bbox)
    print("Cells fetched in bbox (deduped):", len(cells_bbox))

    # Filter to polygon
    cells_in_poly = []
    for c in cells_bbox:
        if c.get("lon") is None or c.get("lat") is None:
            continue
        lon = float(c["lon"])
        lat = float(c["lat"])
        if point_in_polygon(lon, lat, polygon_lonlat):
            cells_in_poly.append(c)

    cells_in_poly = dedupe_cells(cells_in_poly)
    print("Cells inside polygon (deduped):", len(cells_in_poly))

    # Save + Map (range is included in OpenCellID response) :contentReference[oaicite:13]{index=13}
    save_cells_csv(CELLS_CSV, cells_in_poly)
    save_leaflet_map(CELLS_MAP_HTML, polygon_lonlat, cells_in_poly)

    print("Wrote:", USER_FILE)
    print("Wrote:", CELLS_CSV)
    print("Wrote:", CELLS_MAP_HTML, "(open in a browser)")


if __name__ == "__main__":
    main()

