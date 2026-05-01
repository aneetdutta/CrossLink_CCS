import os
import sys
import mmap
import struct
from dataclasses import dataclass
from typing import Optional, Tuple, Dict

import polars as pl

sys.path.append(os.getcwd())
from modules.general import str_to_bool


SCENARIO_NAME = os.getenv("SCENARIO_NAME")
ENABLE_BLUETOOTH = str_to_bool(os.getenv("ENABLE_BLUETOOTH"))
ENABLE_WIFI = str_to_bool(os.getenv("ENABLE_WIFI"))
ENABLE_LTE = str_to_bool(os.getenv("ENABLE_LTE"))



PROTO_MAP = {
    0: "Bluetooth",
    1: "WiFi",
    2: "LTE",
}


@dataclass(frozen=True)
class _BinFormat:
    has_bs_tail: bool


def _u8(mm: mmap.mmap, off: int) -> int:
    return struct.unpack_from("<B", mm, off)[0]


def _u16(mm: mmap.mmap, off: int) -> int:
    return struct.unpack_from("<H", mm, off)[0]


def _u32(mm: mmap.mmap, off: int) -> int:
    return struct.unpack_from("<I", mm, off)[0]


def _u64(mm: mmap.mmap, off: int) -> int:
    return struct.unpack_from("<Q", mm, off)[0]


def _f32(mm: mmap.mmap, off: int) -> float:
    return struct.unpack_from("<f", mm, off)[0]


def _read_lp_bytes(mm: mmap.mmap, size: int, off: int) -> Optional[Tuple[int, bytes]]:
    """Read [u8 len][bytes...]"""
    if off + 1 > size:
        return None
    n = _u8(mm, off)
    off += 1
    if off + n > size:
        return None
    return off + n, mm[off: off + n]


def _printable_ratio(b: bytes) -> float:
    if not b:
        return 0.0
    good = sum(32 <= x <= 126 for x in b)
    return good / len(b)


def _protocol_name(proto: int) -> str:
    return PROTO_MAP.get(proto, f"PROTO_{proto}")


def _parse_one_record(
    mm: mmap.mmap,
    size: int,
    off: int,
    fmt: _BinFormat,
) -> Optional[Tuple[int, Dict]]:
    """
    Parse one record.
    Returns (new_off, record_dict) or None.
    """
    # u32 timestep
    if off + 4 > size:
        return None
    timestep = _u32(mm, off)
    off += 4

    # user_id
    r = _read_lp_bytes(mm, size, off)
    if r is None:
        return None
    off, user_b = r
    if len(user_b) == 0:
        return None

    # f32 distance
    if off + 4 > size:
        return None
    distance = _f32(mm, off)
    off += 4

    # u16 sniffer_id + 4 x f32 coords
    if off + 2 + 16 > size:
        return None
    sniffer_id = _u16(mm, off)
    off += 2

    sl_x = _f32(mm, off)
    off += 4
    sl_y = _f32(mm, off)
    off += 4
    ul_x = _f32(mm, off)
    off += 4
    ul_y = _f32(mm, off)
    off += 4

    # u8 protocol
    if off + 1 > size:
        return None
    proto = _u8(mm, off)
    off += 1
    if proto not in (0, 1, 2):
        return None

    # device_id
    r = _read_lp_bytes(mm, size, off)
    if r is None:
        return None
    off, dev_b = r
    if len(dev_b) == 0:
        return None

    serving_cell_b = b""
    bs_x = float("nan")
    bs_y = float("nan")
    dist_sniffer_to_bs = float("nan")
    dist_user_to_bs = float("nan")

    if fmt.has_bs_tail:
        # serving_cell_id
        r = _read_lp_bytes(mm, size, off)
        if r is None:
            return None
        off, serving_cell_b = r

        # bs_x, bs_y, dist_sniffer_to_bs, dist_user_to_bs
        if off + 16 > size:
            return None

        bs_x = _f32(mm, off)
        off += 4
        bs_y = _f32(mm, off)
        off += 4
        dist_sniffer_to_bs = _f32(mm, off)
        off += 4
        dist_user_to_bs = _f32(mm, off)
        off += 4

    rec = {
        "timestep": int(timestep),
        "user_id_b": bytes(user_b),
        "device_id_b": bytes(dev_b),
        "protocol_byte": int(proto),
        "distance": float(distance),
        "sniffer_id": int(sniffer_id),
        "sl_x": float(sl_x),
        "sl_y": float(sl_y),
        "ul_x": float(ul_x),
        "ul_y": float(ul_y),
        "serving_cell_id_b": bytes(serving_cell_b),
        "bs_x": float(bs_x),
        "bs_y": float(bs_y),
        "dist_sniffer_to_bs": float(dist_sniffer_to_bs),
        "dist_user_to_bs": float(dist_user_to_bs),
    }
    return off, rec


def _score_format(mm: mmap.mmap, size: int, header_count: int, fmt: _BinFormat) -> Tuple[int, float]:
    """
    Score parser using first few thousand rows.
    Higher is better.
    """
    off = 8
    ok = 0
    score = 0.0

    target = 5000
    if header_count > 0:
        target = min(target, header_count)

    while ok < target:
        r = _parse_one_record(mm, size, off, fmt)
        if r is None:
            break

        off, rec = r
        ur = _printable_ratio(rec["user_id_b"])
        dr = _printable_ratio(rec["device_id_b"])

        if ur < 0.70 or dr < 0.70:
            break

        bonus = 0.0
        if b"_" in rec["device_id_b"]:
            bonus += 0.10
        if fmt.has_bs_tail and rec["serving_cell_id_b"]:
            sr = _printable_ratio(rec["serving_cell_id_b"])
            if sr >= 0.70:
                bonus += 0.05

        score += ur + dr + bonus
        ok += 1

    avg = score / ok if ok else 0.0
    return ok, avg


def _detect_bin_format(mm: mmap.mmap, size: int, header_count: int) -> _BinFormat:
    candidates = [
        _BinFormat(has_bs_tail=False),
        _BinFormat(has_bs_tail=True),
    ]

    best = None
    best_key = (-1, -1.0)

    for fmt in candidates:
        ok, avg = _score_format(mm, size, header_count, fmt)
        key = (ok, avg)
        if key > best_key:
            best_key = key
            best = fmt

    if best is None or best_key[0] < 10:
        raise RuntimeError(
            "Could not reliably detect sniffed_data .bin format. "
            "Expected Rust save_observations_binary() layout."
        )

    return best


def _read_sniffed_bin_for_aggregate_id(bin_path: str) -> pl.DataFrame:
    """
    Read sniffed_data_*.bin and return a compact DataFrame with:
      id, user_id, protocol, timestep

    Only 1-2 rows per id are returned (min/max timestep),
    so your existing aggregate_id() stays efficient.
    """
    with open(bin_path, "rb") as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        try:
            size = mm.size()
            if size < 8:
                raise ValueError("BIN file too small: missing u64 count header.")

            header_count = _u64(mm, 0)
            fmt = _detect_bin_format(mm, size, header_count)

            print(
                f"[BIN] format={'extended' if fmt.has_bs_tail else 'base'} "
                f"| header_count={header_count} | size={size} bytes"
            )

            # device_id -> (user_id, proto, min_ts, max_ts)
            stats: Dict[bytes, Tuple[bytes, int, int, int]] = {}

            off = 8
            parsed = 0

            while off < size:
                r = _parse_one_record(mm, size, off, fmt)
                if r is None:
                    break

                off, rec = r
                dev_b = rec["device_id_b"]
                user_b = rec["user_id_b"]
                proto = rec["protocol_byte"]
                ts = rec["timestep"]

                prev = stats.get(dev_b)
                if prev is None:
                    stats[dev_b] = (user_b, proto, ts, ts)
                else:
                    u0, p0, mn, mx = prev
                    if ts < mn:
                        mn = ts
                    if ts > mx:
                        mx = ts
                    stats[dev_b] = (u0, p0, mn, mx)

                parsed += 1
                if header_count and parsed >= header_count:
                    break

            if header_count and parsed < header_count:
                print(
                    f"[BIN][WARN] header_count={header_count}, "
                    f"but parsed only {parsed} records before EOF/incomplete tail."
                )

        finally:
            mm.close()

    ids = []
    user_ids = []
    protocols = []
    timesteps = []

    for dev_b, (user_b, proto, mn, mx) in stats.items():
        dev_s = dev_b.decode("utf-8", errors="replace")
        user_s = user_b.decode("utf-8", errors="replace")
        proto_s = _protocol_name(proto)

        ids.append(dev_s)
        user_ids.append(user_s)
        protocols.append(proto_s)
        timesteps.append(mn)

        if mx != mn:
            ids.append(dev_s)
            user_ids.append(user_s)
            protocols.append(proto_s)
            timesteps.append(mx)

    return pl.DataFrame(
        {
            "id": ids,
            "user_id": user_ids,
            "protocol": protocols,
            "timestep": timesteps,
        }
    )


def read_observation_input(path: str) -> pl.DataFrame:
    path_s = str(path)
    if path_s.endswith(".bin"):
        return _read_sniffed_bin_for_aggregate_id(path_s)
    return pl.read_csv(path_s)


def aggregate_id(input_file: str, output_file: str) -> pl.DataFrame:
    df = read_observation_input(input_file)

    if not ENABLE_BLUETOOTH:
        df = df.filter(pl.col("protocol") != "Bluetooth")
    if not ENABLE_WIFI:
        df = df.filter(pl.col("protocol") != "WiFi")
    if not ENABLE_LTE:
        df = df.filter(pl.col("protocol") != "LTE")

    print(df)

    aggregated_df = (
        df.lazy()
        .group_by("id")
        .agg([
            pl.col("user_id").first().alias("user_id"),
            pl.col("protocol").first().alias("protocol"),
            pl.col("timestep").min().alias("start_timestep"),
            pl.col("timestep").max().alias("last_timestep"),
            (pl.col("timestep").max() - pl.col("timestep").min() + 1).alias("total_time"),
        ])
        .sort("start_timestep")
        .collect()
    )

    aggregated_df.write_parquet(output_file)
    return aggregated_df


def aggregate_users(df: pl.DataFrame, output_file: str):
    user_aggregation = (
        df.lazy()
        .group_by("user_id")
        .agg([
            pl.when(pl.col("protocol") == "LTE").then(pl.col("id")).unique().alias("lte_ids"),
            pl.when(pl.col("protocol") == "WiFi").then(pl.col("id")).unique().alias("wifi_ids"),
            pl.when(pl.col("protocol") == "Bluetooth").then(pl.col("id")).unique().alias("bluetooth_ids"),
            pl.col("id").unique().alias("ids"),

            pl.when(pl.col("protocol") == "LTE").then(pl.col("start_timestep")).min().alias("lte_start_timestep"),
            pl.when(pl.col("protocol") == "LTE").then(pl.col("last_timestep")).max().alias("lte_end_timestep"),

            pl.when(pl.col("protocol") == "Bluetooth").then(pl.col("start_timestep")).min().alias("ble_start_timestep"),
            pl.when(pl.col("protocol") == "Bluetooth").then(pl.col("last_timestep")).max().alias("ble_end_timestep"),

            pl.when(pl.col("protocol") == "WiFi").then(pl.col("start_timestep")).min().alias("wifi_start_timestep"),
            pl.when(pl.col("protocol") == "WiFi").then(pl.col("last_timestep")).max().alias("wifi_end_timestep"),
        ])
        .with_columns([
            pl.col("lte_ids").map_elements(
                lambda lst: [x for x in lst if x is not None] if lst is not None else [],
                return_dtype=pl.List(pl.Utf8),
            ).alias("lte_ids"),
            pl.col("wifi_ids").map_elements(
                lambda lst: [x for x in lst if x is not None] if lst is not None else [],
                return_dtype=pl.List(pl.Utf8),
            ).alias("wifi_ids"),
            pl.col("bluetooth_ids").map_elements(
                lambda lst: [x for x in lst if x is not None] if lst is not None else [],
                return_dtype=pl.List(pl.Utf8),
            ).alias("bluetooth_ids"),
            pl.col("ids").map_elements(
                lambda lst: [x for x in lst if x is not None] if lst is not None else [],
                return_dtype=pl.List(pl.Utf8),
            ).alias("ids"),
        ])
        .collect()
    )

    print(user_aggregation)

    user_aggregation = user_aggregation.with_columns([
        (pl.col("lte_end_timestep") - pl.col("lte_start_timestep") + 1).alias("lte_duration"),
        (pl.col("ble_end_timestep") - pl.col("ble_start_timestep") + 1).alias("ble_duration"),
        (pl.col("wifi_end_timestep") - pl.col("wifi_start_timestep") + 1).alias("wifi_duration"),
    ])

    user_aggregation = user_aggregation.to_pandas()

    user_aggregation["last_timestep"] = user_aggregation[
        ["lte_end_timestep", "wifi_end_timestep", "ble_end_timestep"]
    ].max(axis=1, skipna=True)

    user_aggregation["start_timestep"] = user_aggregation[
        ["lte_start_timestep", "wifi_start_timestep", "ble_start_timestep"]
    ].min(axis=1, skipna=True)

    user_aggregation["ideal_duration"] = (
        user_aggregation["last_timestep"] - user_aggregation["start_timestep"] + 1
    )

    print(user_aggregation)
    user_aggregation.to_parquet(output_file)


# =========================
# Run
# =========================
input_file = f"data/{SCENARIO_NAME}/sniffed_data_{SCENARIO_NAME}.bin"
aggregated_id_output = f"data/{SCENARIO_NAME}/aggregated_id_{SCENARIO_NAME}.parquet"
aggregated_users_output = f"data/{SCENARIO_NAME}/aggregated_users_{SCENARIO_NAME}.parquet"

aggregated_id_df = aggregate_id(input_file, aggregated_id_output)
print("Aggregate ID completed")

aggregate_users(aggregated_id_df, aggregated_users_output)
print("Aggregate users completed")
