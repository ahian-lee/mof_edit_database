#!/usr/bin/env python3
"""Backfill failed-parent base_pld from remote AL archive (124 parents / 660 rows).

Evidence: outputs/remote_recovery_20260828/parent_fail_recovery.csv
matched clean unedited canonical names. Actions per master row:
  base_pld  <- remote_pld
  delta_pld <- modified_pld - base_pld (round 5) when modified_pld present
Audit CSV per row; --apply after one-time backup.
"""
import argparse
import pandas as pd

BASE = "/home/user/lyh/projects/mofdiffusion"
MASTER = f"{BASE}/release_prep/unified_tables/unified_mof_master.csv"
AUDIT = f"{BASE}/release_prep/unified_tables/parent_remote_backfill_audit_20260828.csv"
PAUDIT = f"{BASE}/release_prep/unified_tables/parent_pld_merge_audit_20260828.csv"
REC = f"{BASE}/outputs/remote_recovery_20260828/parent_fail_recovery.csv"
BACKUP = MASTER.replace(".csv", ".pre_parent_remote_fill_20260828.bak")


def clean(name):
    return bool(name) and len(str(name).split("_")) == 3


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    rec = pd.read_csv(REC)
    found = rec[(rec.match == "found") & rec.remote_name.apply(clean)]
    pa = pd.read_csv(PAUDIT)
    sub = pa[pa.parent_id.isin(set(found.parent_id))]
    mapping = found.set_index("parent_id")["remote_pld"].to_dict()
    pmap = found.set_index("parent_id")["remote_name"].to_dict()
    print("target rows:", len(sub))

    df = pd.read_csv(MASTER, dtype=str, low_memory=False, keep_default_na=False)
    idx = {rid: i for i, rid in enumerate(df["mof_id"])}
    edits = []
    for _, r in sub.iterrows():
        rid = r["mof_id"]
        if rid not in idx:
            continue
        i = idx[rid]
        old_b = df.at[i, "base_pld"]
        new_b = f"{float(mapping[r['parent_id']]):.5f}"
        nd = df.at[i, "delta_pld"]
        if df.at[i, "modified_pld"] != "":
            try:
                nd = f"{float(df.at[i, 'modified_pld']) - float(new_b):.5f}"
            except ValueError:
                pass
        edits.append({
            "mof_id": rid,
            "parent_id": r["parent_id"],
            "remote_name": pmap[r["parent_id"]],
            "old_base_pld": old_b,
            "new_base_pld": new_b,
            "old_delta_pld": df.at[i, "delta_pld"],
            "new_delta_pld": nd,
        })
    edf = pd.DataFrame(edits)
    edf.to_csv(AUDIT, index=False)
    print("audit rows:", len(edf), "->", AUDIT)

    if not args.apply:
        print("DRY-RUN only")
        return
    import os, shutil
    if not os.path.exists(BACKUP):
        shutil.copy2(MASTER, BACKUP)
        print("backup:", BACKUP)
    n = 0
    for e in edits:
        i = idx[e["mof_id"]]
        df.at[i, "base_pld"] = e["new_base_pld"]
        df.at[i, "delta_pld"] = e["new_delta_pld"]
        n += 1
    df.to_csv(MASTER, index=False)
    print(f"APPLIED {n} rows")


if __name__ == "__main__":
    main()
