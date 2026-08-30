#!/usr/bin/env python3
"""Backfill remote recovered LCD & correct PLD for 19,179 AL rows.

Evidence: outputs/remote_recovery_20260828/lcd_recovery.csv (joined from
remote archive mof_191k_properties_v2.csv, always round-mismatch-safe).
Actions per row:
  modified_pld <- remote_pld (Df)
  modified_lcd <- remote_lcd (Di)
  delta_pld    <- modified_pld - base_pld (round 5, when base_pld present)
Writes row-level audit CSV; default dry-run, --apply edits master after
one-time backup.
"""
import argparse
import csv
import pandas as pd

BASE = "/home/user/lyh/projects/mofdiffusion"
MASTER = f"{BASE}/release_prep/unified_tables/unified_mof_master.csv"
REC = f"{BASE}/outputs/remote_recovery_20260828/lcd_recovery.csv"
AUDIT = f"{BASE}/release_prep/unified_tables/remote_lcd_backfill_audit_20260828.csv"
BACKUP = MASTER.replace(".csv", ".pre_remote_lcd_fill_20260828.bak")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    rec = pd.read_csv(REC)
    rec = rec[rec.match == "edited"]
    print("recovery rows:", len(rec))

    df = pd.read_csv(MASTER, dtype=str, low_memory=False, keep_default_na=False)
    idx = {rid: i for i, rid in enumerate(df["mof_id"])}
    hits = sorted(set(rec.mof_id) & set(idx))
    print("master hits:", len(hits))

    edits = []
    for rid in hits:
        i = idx[rid]
        row = rec[rec.mof_id == rid].iloc[0]
        old_p = df.at[i, "modified_pld"]
        old_l = df.at[i, "modified_lcd"]
        old_d = df.at[i, "delta_pld"]
        rp = f"{float(row.remote_pld):.5f}"
        rl = f"{float(row.remote_lcd):.5f}"
        nd = old_d
        if df.at[i, "base_pld"] != "":
            try:
                nd = f"{float(rp) - float(df.at[i, 'base_pld']):.5f}"
            except ValueError:
                nd = old_d
        edits.append({
            "mof_id": rid,
            "source_round": row.source_round,
            "old_modified_pld": old_p,
            "new_modified_pld": rp,
            "old_modified_lcd": old_l,
            "new_modified_lcd": rl,
            "old_delta_pld": old_d,
            "new_delta_pld": nd,
        })
    edf = pd.DataFrame(edits)
    edf.to_csv(AUDIT, index=False)
    print("audit rows:", len(edf), "->", AUDIT)

    if not args.apply:
        print("DRY-RUN only")
        return
    import shutil, os
    if not os.path.exists(BACKUP):
        shutil.copy2(MASTER, BACKUP)
        print("backup:", BACKUP)
    n = 0
    for e in edits:
        i = idx[e["mof_id"]]
        df.at[i, "modified_pld"] = e["new_modified_pld"]
        df.at[i, "modified_lcd"] = e["new_modified_lcd"]
        df.at[i, "delta_pld"] = e["new_delta_pld"]
        n += 1
    df.to_csv(MASTER, index=False)
    print(f"APPLIED {n} rows")


if __name__ == "__main__":
    main()
