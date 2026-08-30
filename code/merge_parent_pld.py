#!/usr/bin/env python3
"""Merge measured parent PLD into unified_mof_master pseudo-pair rows.

Plan A repair step:
- master rows classified PSEUDO_PAIR_pormake_base_vs_external_edit get their
  base_pld replaced with the measured PLD of the true (unedited) parent MOF
  built from the self-built base edge XYZ.
- delta_pld is recomputed as modified_pld - new_base_pld.
- A row-level audit CSV (old -> new) is written.
- Default run is dry-run; --apply performs the cell edits after backing up
  the master table exactly once.

Usage:
  python merge_parent_pld.py                 # dry-run diagnostic
  python merge_parent_pld.py --apply         # backup + apply cell edits
"""
import argparse
import csv
import json
import os
import shutil
import sys
from collections import Counter, defaultdict

BASE = "/home/user/lyh/projects/mofdiffusion"
MASTER = f"{BASE}/release_prep/unified_tables/unified_mof_master.csv"
PROV_ROWS = f"{BASE}/docs/database_paper/audit_v1/mof_edge_provenance_rows.csv"
RESULTS = f"{BASE}/outputs/parent_build_20260826/state/results.jsonl"
CW_LIST = [
    f"{BASE}/edge_augmentation/base_edge_aug/edge_id_crosswalk_v2.csv",
    f"{BASE}/docs/database_paper/audit_v1/edge_id_crosswalk_v2_extension.csv",
]
BACKUP = MASTER.replace(".csv", ".pre_merge_parent_pld_20260828.bak")
AUDIT = f"{BASE}/release_prep/unified_tables/parent_pld_merge_audit_20260828.csv"


def load_crosswalk():
    fwd = {}
    for p in CW_LIST:
        with open(p) as f:
            for r in csv.DictReader(f):
                leg = r["legacy_edge_id"].strip()
                canon = (r.get("new_canonical_edge_id") or r.get("edge_id")).strip()
                fwd[leg] = canon
    return fwd


def load_results():
    res = {}
    for line in open(RESULTS):
        d = json.loads(line)
        res[d["parent_id"]] = d
    return res


def parent_key(base_family, topo, node_inorg, node_org):
    canon = FW.get(base_family)
    if canon is None:
        return None
    if not node_org or node_org in ("__none__", "None", "nan"):
        return f"{topo}+{node_inorg}+{canon}"
    return f"{topo}+{node_inorg}+{node_org}+{canon}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    global FW
    FW = load_crosswalk()
    res = load_results()
    print(f"crosswalk: {len(FW)}; results parents: {len(res)}", file=sys.stderr)

    # collect pseudo-pair row mappings
    prow = {}  # row_id -> dict with parent key + evidence
    for r in csv.DictReader(open(PROV_ROWS)):
        if (r["dataset"] == "unified_mof_master"
                and r["edge_provenance_class"]
                == "PSEUDO_PAIR_pormake_base_vs_external_edit"):
            pk = parent_key(r["restored_legacy_base_family"], r["topo"],
                            r["node_inorg"], r["node_org"])
            prow[r["row_id"]] = {
                "restored_base": r["restored_legacy_base_family"],
                "parent_key": pk,
            }
    print(f"pseudo-pair master rows: {len(prow)}", file=sys.stderr)

    # match status per row
    status = Counter()
    row_parent = {}  # row_id -> parent result dict or None
    for rid, info in prow.items():
        pk = info["parent_key"]
        if pk is None:
            status["no_crosswalk"] += 1
            row_parent[rid] = None
        elif pk not in res:
            status["no_parent_result"] += 1
            row_parent[rid] = None
        else:
            d = res[pk]
            row_parent[rid] = d
            status["parent_" + d["status"]] += 1
    print(dict(status), file=sys.stderr)

    # load master
    import pandas as pd
    df = pd.read_csv(MASTER, dtype=str, low_memory=False)

    # compute edits (cell-level)
    edits = []
    for idx, m in df.iterrows():
        rid = m["mof_id"]
        if rid not in prow:
            continue
        d = row_parent[rid]
        if d is None or d["status"] != "ok":
            edits.append({
                "mof_id": rid, "parent_id": prow[rid]["parent_key"],
                "parent_status": (d or {}).get("status", "unmatched"),
                "old_base_pld": m["base_pld"],
                "new_base_pld": "",
                "old_delta_pld": m["delta_pld"],
                "new_delta_pld": "",
                "action": "skipped_parent_not_ok",
            })
            continue
        new_base = d["pld"]
        old_base = m["base_pld"]
        if old_base == new_base or (old_base is not None and old_base != ""):
            # numeric compare to avoid no-op rewrites
            try:
                if abs(float(old_base) - float(new_base)) < 1e-9:
                    edits.append({
                        "mof_id": rid, "parent_id": d["parent_id"],
                        "parent_status": "ok",
                        "old_base_pld": old_base,
                        "new_base_pld": new_base,
                        "old_delta_pld": m["delta_pld"],
                        "new_delta_pld": m["delta_pld"],
                        "action": "unchanged_base",
                    })
                    continue
            except (TypeError, ValueError):
                pass
        new_delta = ""
        if m["modified_pld"] not in ("", None) and str(m["modified_pld"]) != "nan":
            try:
                nd = round(float(m["modified_pld"]) - float(new_base), 5)
                new_delta = f"{nd:.5f}"
            except (TypeError, ValueError):
                new_delta = m["delta_pld"]
        else:
            new_delta = m["delta_pld"]
        edits.append({
            "mof_id": rid, "parent_id": d["parent_id"], "parent_status": "ok",
            "old_base_pld": old_base, "new_base_pld": new_base,
            "old_delta_pld": m["delta_pld"], "new_delta_pld": new_delta,
            "action": "updated",
        })

    print(f"row edits planned: {len(edits)}", file=sys.stderr)
    upd = [e for e in edits if e["action"] == "updated"]
    skip = [e for e in edits if e["action"] == "skipped_parent_not_ok"]
    unch = [e for e in edits if e["action"] == "unchanged_base"]
    print(f"  updated={len(upd)} skipped_parent_not_ok={len(skip)} "
          f"unchanged_base={len(unch)}", file=sys.stderr)

    # write audit CSV always
    with open(AUDIT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(edits[0].keys()))
        w.writeheader()
        w.writerows(edits)
    print(f"audit CSV written: {AUDIT}", file=sys.stderr)

    if not args.apply:
        print("DRY-RUN: no changes applied. Use --apply to write the master.")
        return

    if not os.path.exists(BACKUP):
        shutil.copy2(MASTER, BACKUP)
        print(f"backup created: {BACKUP}", file=sys.stderr)
    else:
        print(f"backup exists, keeping: {BACKUP}", file=sys.stderr)

    # apply cell edits
    base_map = {e["mof_id"]: e for e in edits}
    n_applied = 0
    for idx, rid in enumerate(df["mof_id"]):
        e = base_map.get(rid)
        if e is None or e["action"] != "updated":
            continue
        df.at[idx, "base_pld"] = e["new_base_pld"]
        df.at[idx, "delta_pld"] = e["new_delta_pld"]
        n_applied += 1
    df.to_csv(MASTER, index=False)
    print(f"APPLIED {n_applied} cell edits to {MASTER}")


if __name__ == "__main__":
    main()
