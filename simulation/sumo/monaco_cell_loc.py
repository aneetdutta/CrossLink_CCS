import os
import sys
import csv
import pathlib
import xml.etree.ElementTree as ET

# -------------------------
# HARDCODED PATHS (adjust if needed)
# -------------------------
SCENARIO_NAME = os.getenv("SCENARIO_NAME", "demo")
SUMO_CFG_FILE = f"{pathlib.Path().resolve()}/simulation/sumo/sumo_scenario/most.sumocfg"

DATA_DIR = pathlib.Path().resolve() / "data"

# This should be the CSV you used for plotting (must contain lat/lon)
# Example if you plotted the filtered+deduped list:
IN_CSV = DATA_DIR / f"opencellid_cells_{SCENARIO_NAME}_LTE_212_10_uniqueLoc.csv"

# Output XY-only CSV (range stays meters)
OUT_CSV = DATA_DIR / f"opencellid_cells_{SCENARIO_NAME}_LTE_212_10_uniqueLoc_XY_new.csv"


# -------------------------
# Helpers
# -------------------------
def safe_float(v):
    try:
        return float(v)
    except Exception:
        return None


def import_sumolib():
    sumo_home = os.environ.get("SUMO_HOME")
    if not sumo_home:
        raise RuntimeError("SUMO_HOME is not set. Example: export SUMO_HOME=/usr/share/sumo")
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


def main():
    if not IN_CSV.exists():
        raise FileNotFoundError(f"Input CSV not found: {IN_CSV}")

    sumolib = import_sumolib()
    net_file = netfile_from_sumocfg(pathlib.Path(SUMO_CFG_FILE).resolve())
    net = sumolib.net.readNet(str(net_file))

    # Read input (geo) CSV
    with IN_CSV.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        raise RuntimeError("Input CSV has no rows.")

    # Convert each row lon/lat -> x/y and write output
    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)

    out_fields = [
        "cellid", "radio", "mcc", "mnc", "lac",
        "x", "y",
        "range",
        "samples", "averageSignalStrength", "changeable",
    ]

    written = 0
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=out_fields)
        w.writeheader()

        for r in rows:
            lon = safe_float(r.get("lon"))
            lat = safe_float(r.get("lat"))
            if lon is None or lat is None:
                continue

            # Convert lon/lat -> SUMO network x/y (meters)
            x, y = net.convertLonLat2XY(lon, lat)

            out = {
                "cellid": r.get("cellid"),
                "radio": r.get("radio"),
                "mcc": r.get("mcc"),
                "mnc": r.get("mnc"),
                "lac": r.get("lac"),
                "x": float(x),
                "y": float(y),
                "range": r.get("range"),
                "samples": r.get("samples"),
                "averageSignalStrength": r.get("averageSignalStrength"),
                "changeable": r.get("changeable"),
            }
            w.writerow(out)
            written += 1

    print("Net file:", net_file)
    print("Read:", IN_CSV, "rows:", len(rows))
    print("Wrote:", OUT_CSV, "rows:", written)
    print("Done.")


if __name__ == "__main__":
    main()

