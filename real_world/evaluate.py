

import sys
sys.path.insert(0, ".")

import csv
from collections import defaultdict

from crosslink import (
    load_lifetimes,
    load_anchors,
    compute_intra_map,
    filter_intra_map,
)


def load_ground_truth(path):
   
    rows_by_dev = defaultdict(lambda: {"BLE": [], "LTE": []})
    raw = defaultdict(list)
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            dev = row["Device"]
            rows_by_dev[dev]  # ensure key exists
            raw[(dev, row["Protocol"])].append((int(row["Position"]), row["Identifier"]))
    for (dev, proto), entries in raw.items():
        entries.sort()
        rows_by_dev[dev][proto] = [ident for _, ident in entries]
    return dict(rows_by_dev)


def load_links(intra_path="intra_links.csv", inter_path="inter_links.csv"):
   
    intra_ble = defaultdict(list)
    intra_lte = defaultdict(list)
    with open(intra_path, newline="") as f:
        for row in csv.DictReader(f):
            if row["Protocol"] == "BLE":
                intra_ble[row["From"]].append(row["To"])
            elif row["Protocol"] == "LTE":
                intra_lte[row["From"]].append(row["To"])

    inter = defaultdict(set)
    with open(inter_path, newline="") as f:
        for row in csv.DictReader(f):
            inter[row["BLE"]].add(row["LTE"])
            inter[row["LTE"]].add(row["BLE"])
    return dict(intra_ble), dict(intra_lte), dict(inter)


def reconstruct_from_anchors(intra_ble, intra_lte, anchors, ble_lt):
  
    starts_per_dev = defaultdict(list)
    for ble, lte, dev in anchors:
        starts_per_dev[dev].append((ble, lte))

    def walk(start, intra):
        chain = [start]
        cur = start
        while len(intra.get(cur, [])) == 1:
            nxt = intra[cur][0]
            if nxt in chain:
                break
            chain.append(nxt)
            cur = nxt
        return chain

    ble_recovered, lte_recovered = {}, {}
    for dev, pairs in starts_per_dev.items():
        pairs.sort(key=lambda x: ble_lt.get(x[0], (0, 0))[0])
        start_ble, start_lte = pairs[0]
        ble_recovered[dev] = walk(start_ble, intra_ble)
        lte_recovered[dev] = walk(start_lte, intra_lte)
    return ble_recovered, lte_recovered

def single_protocol_resolve(lifetimes, anchors, protocol="BLE"):

    intra = filter_intra_map(compute_intra_map(lifetimes))


    if protocol == "BLE":
        anchor_starts_ends = defaultdict(list)
        for ble, _, dev in anchors:
            if ble in lifetimes:
                anchor_starts_ends[dev].append(ble)
    else:
        anchor_starts_ends = defaultdict(list)
        for _, lte, dev in anchors:
            if lte in lifetimes:
                anchor_starts_ends[dev].append(lte)


    for dev in anchor_starts_ends:
        anchor_starts_ends[dev].sort(key=lambda x: lifetimes[x][0])

  
    anchored_ids = {x for xs in anchor_starts_ends.values() for x in xs}
    device_of = {}
    for dev, xs in anchor_starts_ends.items():
        for x in xs:
            device_of[x] = dev


    intra = {a: [b for b in cands
                 if not (a in device_of and b in device_of and device_of[a] != device_of[b])]
             for a, cands in intra.items()}
    intra = filter_intra_map(intra)

    recovered = {}
    for dev, xs in anchor_starts_ends.items():
        if not xs:
            continue
        start = xs[0]
        chain = [start]
        cur = start
        while len(intra.get(cur, [])) == 1:
            nxt = intra[cur][0]
            if nxt in chain:
                break
            chain.append(nxt)
            cur = nxt
        recovered[dev] = chain
    return recovered, intra



def transition_accuracy(recovered, ground_truth):

    correct = 0
    total = 0
    for dev, gt_chain in ground_truth.items():
        gt_pairs = list(zip(gt_chain[:-1], gt_chain[1:]))
        rec_chain = recovered.get(dev, [])
        rec_pairs = set(zip(rec_chain[:-1], rec_chain[1:]))
        total += len(gt_pairs)
        for p in gt_pairs:
            if p in rec_pairs:
                correct += 1
    return correct, total


if __name__ == "__main__":
    anchors = load_anchors("anchors.csv")
    device_ground_truth = load_ground_truth("ground_truth.csv")

    print("=" * 72)
    print(" 12-device evaluation: single-protocol vs cross-protocol")
    print("=" * 72)

    ble_lt = load_lifetimes("ble_observations.csv", "Time", "Source")
    lte_lt = load_lifetimes("lte_observations.csv", "Time", "RNTI")
    print(f"\n  {len(ble_lt)} BLE identifiers, {len(lte_lt)} LTE identifiers, "
          f"{len(anchors)} anchors, {len(device_ground_truth)} devices")

    gt_ble = {dev: d["BLE"] for dev, d in device_ground_truth.items()}
    gt_lte = {dev: d["LTE"] for dev, d in device_ground_truth.items()}

    # ---- Single-protocol baseline ----
    print("\n" + "=" * 72)
    print(" SINGLE-PROTOCOL (intra-protocol structure + anchors only)")
    print("=" * 72)
    ble_single, _ = single_protocol_resolve(ble_lt, anchors, "BLE")
    lte_single, _ = single_protocol_resolve(lte_lt, anchors, "LTE")
    ble_s_correct, ble_s_total = transition_accuracy(ble_single, gt_ble)
    lte_s_correct, lte_s_total = transition_accuracy(lte_single, gt_lte)
    print(f"  BLE: {ble_s_correct}/{ble_s_total} = {100*ble_s_correct/ble_s_total:.1f}%")
    print(f"  LTE: {lte_s_correct}/{lte_s_total} = {100*lte_s_correct/lte_s_total:.1f}%")

    # ---- Cross-protocol full pipeline (consume saved CrossLink output) ----
    print("\n" + "=" * 72)
    print(" CROSS-PROTOCOL (loaded from saved CrossLink output)")
    print("=" * 72)
    intra_ble_x, intra_lte_x, inter_x = load_links(
        "intra_links.csv", "inter_links.csv")
    print(f"  Loaded {sum(len(v) for v in intra_ble_x.values())} BLE intra-links, "
          f"{sum(len(v) for v in intra_lte_x.values())} LTE intra-links, "
          f"{sum(len(v) for v in inter_x.values())//2} inter-links")
    ble_cross, lte_cross = reconstruct_from_anchors(
        intra_ble_x, intra_lte_x, anchors, ble_lt)
    ble_c_correct, ble_c_total = transition_accuracy(ble_cross, gt_ble)
    lte_c_correct, lte_c_total = transition_accuracy(lte_cross, gt_lte)
    print(f"  BLE: {ble_c_correct}/{ble_c_total} = {100*ble_c_correct/ble_c_total:.1f}%")
    print(f"  LTE: {lte_c_correct}/{lte_c_total} = {100*lte_c_correct/lte_c_total:.1f}%")

   

    # Save results for plotting
    import json
    results = {
        "BLE_single_correct": ble_s_correct, "BLE_single_total": ble_s_total,
        "BLE_cross_correct":  ble_c_correct, "BLE_cross_total":  ble_c_total,
        "LTE_single_correct": lte_s_correct, "LTE_single_total": lte_s_total,
        "LTE_cross_correct":  lte_c_correct, "LTE_cross_total":  lte_c_total,
    }
    with open("results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("  Wrote results to results.json")
