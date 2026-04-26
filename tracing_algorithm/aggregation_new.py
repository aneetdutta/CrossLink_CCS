#!/usr/bin/env python3
import os
import sys
from pathlib import Path

import polars as pl


# -------------------------
# Small helpers (self-contained)
# -------------------------
def str_to_bool(v, default=True) -> bool:
    if v is None:
        return default
    s = str(v).strip().lower()
    if s in ("1", "true", "t", "yes", "y", "on"):
        return True
    if s in ("0", "false", "f", "no", "n", "off"):
        return False
    return default


# -------------------------
# BIN parser for sniffed_data_*.bin (Rust serde/postcard Vec<ObservationSample>)
# Returns a SMALL DF with columns: id, user_id, protocol, timestep
# (1–2 rows per id: min/max timestep) so aggregation stays fast.
# -------------------------
def _read_sniffed_bin_for_aggregate_id(bin_path: str) -> pl.DataFrame:
    import mmap

    # ---------- helpers: postcard/serde unsigned varint (LEB128) ----------
    def _read_varint_u64(mm: mmap.mmap, off: int, size: int):
        val = 0
        shift = 0
        while True:
            if off >= size:
                raise EOFError("Unexpected EOF while reading varint (corrupt/truncated .bin)")
            b = mm[off]
            off += 1
            val |= (b & 0x7F) << shift
            if (b & 0x80) == 0:
                return val, off
            shift += 7
            if shift > 63:
                raise ValueError("Varint too long (corrupt file?)")

    def _read_len_and_slice(mm: mmap.mmap, off: int, size: int):
        ln, off = _read_varint_u64(mm, off, size)
        end = off + ln
        if end > size:
            raise EOFError("Unexpected EOF while reading bytes (corrupt/truncated .bin)")
        return ln, off, end

    def _infer_protocol_from_device_id(dev_b: bytes, proto_int: int) -> str:
        # Most reliable for your dataset: device_id contains "_L_" / "_W_" / "_B_"
        if b"_L_" in dev_b:
            return "LTE"
        if b"_W_" in dev_b:
            return "WiFi"
        if b"_B_" in dev_b:
            return "Bluetooth"
        # fallback (only used if the ID pattern is absent)
        return {0: "Bluetooth", 1: "WiFi", 2: "LTE"}.get(proto_int, f"PROTO_{proto_int}")

    # stats: device_id_bytes -> (user_id_bytes, proto_int, min_ts, max_ts)
    stats = {}

    bin_path = str(bin_path)
    with open(bin_path, "rb") as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        try:
            size = mm.size()
            if size == 0:
                return pl.DataFrame({"id": [], "user_id": [], "protocol": [], "timestep": []})

            # File starts with VARINT vec length (postcard), NOT 8-byte u64
            nrecs, off = _read_varint_u64(mm, 0, size)

            for _ in range(nrecs):
                # ObservationSample (postcard) assumed order:
                # timestep(u32 varint), user_id(String), device_id(String),
                # user_loc(2*f32), sniffer.id(u16 varint), sniffer.loc(2*f32),
                # distance(f32), protocol(enum varint)

                ts, off = _read_varint_u64(mm, off, size)
                ts_i = int(ts)

                # user_id string
                _, user_start, user_end = _read_len_and_slice(mm, off, size)
                off = user_end

                # device_id string (we need bytes as key)
                _, dev_start, dev_end = _read_len_and_slice(mm, off, size)
                dev_b = bytes(mm[dev_start:dev_end])  # copy (used as dict key)
                off = dev_end

                # skip user_loc: 2*f32 = 8 bytes
                off += 8
                if off > size:
                    raise EOFError("Unexpected EOF while skipping user_loc")

                # sniffer.id: varint
                _, off = _read_varint_u64(mm, off, size)

                # skip sniffer.loc: 2*f32 = 8 bytes
                off += 8
                if off > size:
                    raise EOFError("Unexpected EOF while skipping sniffer_loc")

                # skip distance: f32 = 4 bytes
                off += 4
                if off > size:
                    raise EOFError("Unexpected EOF while skipping distance")

                # protocol: varint
                proto, off = _read_varint_u64(mm, off, size)
                proto_i = int(proto)

                prev = stats.get(dev_b)
                if prev is None:
                    user_b = bytes(mm[user_start:user_end])  # copy once per device id
                    stats[dev_b] = (user_b, proto_i, ts_i, ts_i)
                else:
                    u0, p0, mn, mx = prev
                    if ts_i < mn:
                        mn = ts_i
                    if ts_i > mx:
                        mx = ts_i
                    stats[dev_b] = (u0, p0, mn, mx)

        finally:
            mm.close()

    # Build compressed DF: 1–2 rows per id (min/max)
    ids = []
    user_ids = []
    protocols = []
    timesteps = []

    for dev_b, (user_b, proto_i, mn, mx) in stats.items():
        dev_s = dev_b.decode("utf-8", errors="replace")
        user_s = user_b.decode("utf-8", errors="replace")
        proto_s = _infer_protocol_from_device_id(dev_b, proto_i)

        ids.append(dev_s)
        user_ids.append(user_s)
        protocols.append(proto_s)
        timesteps.append(mn)

        if mx != mn:
            ids.append(dev_s)
            user_ids.append(user_s)
            protocols.append(proto_s)
            timesteps.append(mx)

    return pl.DataFrame({"id": ids, "user_id": user_ids, "protocol": protocols, "timestep": timesteps})


# -------------------------
# Your aggregations (writes required parquet files)
# -------------------------
def aggregate_id(input_bin: str, output_file: str, enable_bluetooth: bool, enable_wifi: bool, enable_lte: bool) -> pl.DataFrame:
    df = _read_sniffed_bin_for_aggregate_id(input_bin)

    if not enable_bluetooth:
        df = df.filter(pl.col("protocol") != "Bluetooth")
    if not enable_wifi:
        df = df.filter(pl.col("protocol") != "WiFi")
    if not enable_lte:
        df = df.filter(pl.col("protocol") != "LTE")

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

    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    aggregated_df.write_parquet(output_file)
    print(aggregated_df)
    print(f"[OK] wrote: {output_file}  (rows={aggregated_df.height})")
    return aggregated_df


def aggregate_users(aggregated_id_df: pl.DataFrame, output_file: str) -> pl.DataFrame:
    # Group per user_id, collect ids by protocol, and protocol time ranges
    user_aggregation = (
        aggregated_id_df.lazy()
        .group_by("user_id")
        .agg([
            # Unique IDs for each protocol (may include null -> drop later)
            pl.when(pl.col("protocol") == "LTE").then(pl.col("id")).otherwise(None).unique().alias("lte_ids"),
            pl.when(pl.col("protocol") == "WiFi").then(pl.col("id")).otherwise(None).unique().alias("wifi_ids"),
            pl.when(pl.col("protocol") == "Bluetooth").then(pl.col("id")).otherwise(None).unique().alias("bluetooth_ids"),
            pl.col("id").unique().alias("ids"),

            # Start/end per protocol
            pl.when(pl.col("protocol") == "LTE").then(pl.col("start_timestep")).otherwise(None).min().alias("lte_start_timestep"),
            pl.when(pl.col("protocol") == "LTE").then(pl.col("last_timestep")).otherwise(None).max().alias("lte_end_timestep"),

            pl.when(pl.col("protocol") == "Bluetooth").then(pl.col("start_timestep")).otherwise(None).min().alias("ble_start_timestep"),
            pl.when(pl.col("protocol") == "Bluetooth").then(pl.col("last_timestep")).otherwise(None).max().alias("ble_end_timestep"),

            pl.when(pl.col("protocol") == "WiFi").then(pl.col("start_timestep")).otherwise(None).min().alias("wifi_start_timestep"),
            pl.when(pl.col("protocol") == "WiFi").then(pl.col("last_timestep")).otherwise(None).max().alias("wifi_end_timestep"),
        ])
        .collect()
        .with_columns([
            # Drop nulls from lists
            pl.col("lte_ids").list.drop_nulls(),
            pl.col("wifi_ids").list.drop_nulls(),
            pl.col("bluetooth_ids").list.drop_nulls(),
            pl.col("ids").list.drop_nulls(),
        ])
    )

    # Durations per protocol
    user_aggregation = user_aggregation.with_columns([
        (pl.col("lte_end_timestep") - pl.col("lte_start_timestep") + 1).alias("lte_duration"),
        (pl.col("ble_end_timestep") - pl.col("ble_start_timestep") + 1).alias("ble_duration"),
        (pl.col("wifi_end_timestep") - pl.col("wifi_start_timestep") + 1).alias("wifi_duration"),
    ])

    # Overall start/last across protocols (skip nulls using sentinels)
    BIG = 2**63 - 1
    user_aggregation = user_aggregation.with_columns([
        pl.max_horizontal([
            pl.coalesce([pl.col("lte_end_timestep"), pl.lit(-1)]),
            pl.coalesce([pl.col("wifi_end_timestep"), pl.lit(-1)]),
            pl.coalesce([pl.col("ble_end_timestep"), pl.lit(-1)]),
        ]).alias("_last_tmp"),
        pl.min_horizontal([
            pl.coalesce([pl.col("lte_start_timestep"), pl.lit(BIG)]),
            pl.coalesce([pl.col("wifi_start_timestep"), pl.lit(BIG)]),
            pl.coalesce([pl.col("ble_start_timestep"), pl.lit(BIG)]),
        ]).alias("_start_tmp"),
    ]).with_columns([
        pl.when(pl.col("_last_tmp") == -1)
          .then(pl.lit(None).cast(pl.Int64))
          .otherwise(pl.col("_last_tmp"))
          .alias("last_timestep"),
        pl.when(pl.col("_start_tmp") == BIG)
          .then(pl.lit(None).cast(pl.Int64))
          .otherwise(pl.col("_start_tmp"))
          .alias("start_timestep"),
    ]).with_columns([
        pl.when(pl.col("last_timestep").is_null() | pl.col("start_timestep").is_null())
          .then(pl.lit(None).cast(pl.Int64))
          .otherwise(pl.col("last_timestep") - pl.col("start_timestep") + 1)
          .alias("ideal_duration")
    ]).drop(["_last_tmp", "_start_tmp"])
    print(user_aggregation)
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    user_aggregation.write_parquet(output_file)
    print(f"[OK] wrote: {output_file}  (rows={user_aggregation.height})")
    return user_aggregation


# -------------------------
# Main
# -------------------------
def main():
    # You can set SCENARIO_NAME in env, or pass as argv[1]
    scenario = os.getenv("SCENARIO_NAME") or (sys.argv[1] if len(sys.argv) > 1 else None)
    if not scenario:
        raise SystemExit("ERROR: Set SCENARIO_NAME or run: python script.py <SCENARIO_NAME>")

    enable_bluetooth = str_to_bool(os.getenv("ENABLE_BLUETOOTH"), default=True)
    enable_wifi = str_to_bool(os.getenv("ENABLE_WIFI"), default=True)
    enable_lte = str_to_bool(os.getenv("ENABLE_LTE"), default=True)

    input_file = f"data/{scenario}/sniffed_data_{scenario}.bin"
    out_agg_id = f"data/{scenario}/aggregated_id_{scenario}.parquet"
    out_agg_users = f"data/{scenario}/aggregated_users_{scenario}.parquet"

    if not os.path.exists(input_file):
        raise SystemExit(f"ERROR: input .bin not found: {input_file}")

    print(f"[INFO] scenario={scenario}")
    print(f"[INFO] input={input_file}")
    print(f"[INFO] ENABLE_BLUETOOTH={enable_bluetooth} ENABLE_WIFI={enable_wifi} ENABLE_LTE={enable_lte}")

    aggregated_id_df = aggregate_id(
        input_bin=input_file,
        output_file=out_agg_id,
        enable_bluetooth=enable_bluetooth,
        enable_wifi=enable_wifi,
        enable_lte=enable_lte,
    )
    print(aggregated_id_df)
    aggregate_users(aggregated_id_df, out_agg_users)
    print("[DONE] Aggregate ID + Aggregate Users completed")



if __name__ == "__main__":
    main()

