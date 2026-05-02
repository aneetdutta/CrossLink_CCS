

import csv
from collections import defaultdict
from copy import deepcopy

INTRA_SLACK = 180.0   # max gap (seconds) for a successor candidate
INTER_SLACK = 120.0   # lifetime-overlap tolerance for inter-map


def load_lifetimes(path, time_col, id_col):

    events = defaultdict(list)
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            events[row[id_col]].append(float(row[time_col]))
    return {i: (min(ts), max(ts)) for i, ts in events.items()}


def load_anchors(path):

    with open(path, newline="") as f:
        return [(r["BLE"], r["LTE"], r["Device"]) for r in csv.DictReader(f)]


def save_links(intra_ble, intra_lte, inter, ble_lt, lte_lt,
               intra_path="intra_links.csv", inter_path="inter_links.csv"):

    n_intra = 0
    with open(intra_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Protocol", "From", "To"])
        for a in sorted(intra_ble, key=lambda x: ble_lt[x][0]):
            for b in intra_ble[a]:
                w.writerow(["BLE", a, b]); n_intra += 1
        for a in sorted(intra_lte, key=lambda x: lte_lt[x][0]):
            for b in intra_lte[a]:
                w.writerow(["LTE", a, b]); n_intra += 1

    n_inter, seen = 0, set()
    with open(inter_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["BLE", "LTE"])
        for k in sorted(inter):
            for v in sorted(inter[k]):
                if k in ble_lt and v in lte_lt:
                    pair = (k, v)
                elif v in ble_lt and k in lte_lt:
                    pair = (v, k)
                else:
                    continue
                if pair not in seen:
                    seen.add(pair); w.writerow(pair); n_inter += 1

    print(f"  Wrote {n_intra:>5} intra-protocol links to {intra_path}")
    print(f"  Wrote {n_inter:>5} inter-protocol links to {inter_path}")



def compute_intra_map(lifetimes, slack=INTRA_SLACK):

    intra = {i: [] for i in lifetimes}
    for a, (_, a_last) in lifetimes.items():
        for b, (b_first, _) in lifetimes.items():
            if a == b:
                continue
            gap = b_first - a_last
            if 0 < gap <= slack:
                intra[a].append(b)
    return intra


def compute_inter_map(ble_lt, lte_lt, slack=INTER_SLACK):

    inter = defaultdict(set)
    for b, (b_f, b_l) in ble_lt.items():
        for l, (l_f, l_l) in lte_lt.items():
            if not (b_l + slack < l_f or l_l + slack < b_f):
                inter[b].add(l)
                inter[l].add(b)
    return dict(inter)


def filter_intra_map(intra):
    
    intra = {a: list(v) for a, v in intra.items()}
    changed = True
    while changed:
        changed = False
        singletons = {a: v[0] for a, v in intra.items() if len(v) == 1}
        for a, target in singletons.items():
            for b, cands in intra.items():
                if b != a and len(cands) > 1 and target in cands:
                    cands.remove(target); changed = True
    return intra


def apply_anchors(inter, anchors):
    
    inter = {k: set(v) for k, v in inter.items()}
    anchored_bles = {a[0] for a in anchors}
    anchored_ltes = {a[1] for a in anchors}
    for ble, lte, _ in anchors:
        for other_lte in anchored_ltes:
            if other_lte != lte:
                inter.setdefault(other_lte, set()).discard(ble)
                inter.setdefault(ble, set()).discard(other_lte)
        for other_ble in anchored_bles:
            if other_ble != ble:
                inter.setdefault(other_ble, set()).discard(lte)
                inter.setdefault(lte, set()).discard(other_ble)
    return inter


def propagate_chain_exclusivity(inter, intra_ble, intra_lte, anchors):
 
    inter = {k: set(v) for k, v in inter.items()}

    def reverse(intra):
        rev = defaultdict(list)
        for a, cs in intra.items():
            for b in cs:
                rev[b].append(a)
        return rev

    rev_ble, rev_lte = reverse(intra_ble), reverse(intra_lte)
    device_of_ble = {a[0]: a[2] for a in anchors}
    device_of_lte = {a[1]: a[2] for a in anchors}

    def walk_forward(start, intra):
        chain, cur = [start], start
        while len(intra.get(cur, [])) == 1:
            nxt = intra[cur][0]
            if nxt in chain:
                break
            chain.append(nxt); cur = nxt
        return chain

    def walk_backward(end, rev):
        chain, cur = [end], end
        while len(rev.get(cur, [])) == 1:
            pred = rev[cur][0]
            if pred in chain:
                break
            chain.append(pred); cur = pred
        return chain

    for ble, _, dev in anchors:
        if not rev_ble.get(ble):                  # anchored start
            for x in walk_forward(ble, intra_ble):
                device_of_ble.setdefault(x, dev)
        if not intra_ble.get(ble, []):            # anchored end
            for x in walk_backward(ble, rev_ble):
                device_of_ble.setdefault(x, dev)

    for _, lte, dev in anchors:
        if not rev_lte.get(lte):
            for x in walk_forward(lte, intra_lte):
                device_of_lte.setdefault(x, dev)
        if not intra_lte.get(lte, []):
            for x in walk_backward(lte, rev_lte):
                device_of_lte.setdefault(x, dev)

    # Prune inter-map by inferred device disagreement
    for ble, ble_dev in list(device_of_ble.items()):
        for lte in list(inter.get(ble, set())):
            lte_dev = device_of_lte.get(lte)
            if lte_dev is not None and lte_dev != ble_dev:
                inter[ble].discard(lte)
                inter.setdefault(lte, set()).discard(ble)

    return inter


def refine_intra_map(intra, inter):
    
    return {a: [b for b in cands if inter.get(a, set()) & inter.get(b, set())]
            for a, cands in intra.items()}


def refine_inter_map(inter, intra_ble, intra_lte):
    
    inter = {k: set(v) for k, v in inter.items()}

    def intra_of(x):
        return intra_ble.get(x, []) if x in intra_ble else intra_lte.get(x, [])

    for a in list(inter):
        cands = set(inter[a])
        succ_union = set()
        for s in intra_of(a):
            succ_union |= inter.get(s, set())
        if not succ_union:
            continue
        retain = cands & succ_union
        if not retain:
            continue
        changed = True
        while changed:
            changed = False
            for c in list(cands - retain):
                if any(s in retain for s in intra_of(c)):
                    retain.add(c); changed = True
        inter[a] = retain

    for a in list(inter):
        for b in list(inter[a]):
            if a not in inter.get(b, set()):
                inter[a].discard(b)
    return inter


def crosslink(ble_lt, lte_lt, anchors, max_iter=10):
   
    intra_ble = filter_intra_map(compute_intra_map(ble_lt))
    intra_lte = filter_intra_map(compute_intra_map(lte_lt))
    inter = compute_inter_map(ble_lt, lte_lt)


    inter = apply_anchors(inter, anchors)
    inter = propagate_chain_exclusivity(inter, intra_ble, intra_lte, anchors)


    for _ in range(max_iter):
        prev = (deepcopy(intra_ble), deepcopy(intra_lte), deepcopy(inter))

        intra_ble = filter_intra_map(refine_intra_map(intra_ble, inter))
        intra_lte = filter_intra_map(refine_intra_map(intra_lte, inter))
        inter = refine_inter_map(inter, intra_ble, intra_lte)

        inter = propagate_chain_exclusivity(inter, intra_ble, intra_lte, anchors)

        if (intra_ble, intra_lte, inter) == prev:
            break

    return intra_ble, intra_lte, inter


if __name__ == "__main__":
    ble_lt = load_lifetimes("ble_observations.csv", "Time", "Source")
    lte_lt = load_lifetimes("lte_observations.csv", "Time", "RNTI")
    anchors = load_anchors("anchors.csv")
    print(f"Loaded {len(ble_lt)} BLE identifiers, "
          f"{len(lte_lt)} LTE identifiers, {len(anchors)} anchors.")

    intra_ble, intra_lte, inter = crosslink(ble_lt, lte_lt, anchors)

    save_links(intra_ble, intra_lte, inter, ble_lt, lte_lt)
