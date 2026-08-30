#!/usr/bin/env python3
"""Build the three requested dataset tables (2026-08-28 v2).

Outputs under outputs/release_tables_20260828/:
  1. mof_master_table.csv           - master rows, success-only (all current
                                      rows are success), no success flags,
                                      with mof_name.
  2. edited_vs_base_zeo_table.csv   - edited vs base Zeo comparison per MOF:
                                      PLD/LCD/GCD/VF both sides.
  3. edited_edge_table.csv          - one row per edited edge with usage
                                      and aggregated Zeo stats.
"""
import csv
import json
import os
import re
import pandas as pd
import numpy as np

BASE = "/home/user/lyh/projects/mofdiffusion"
OUT = f"{BASE}/outputs/release_tables_20260828"
os.makedirs(OUT, exist_ok=True)

MASTER = f"{BASE}/release_prep/unified_tables/unified_mof_master.csv"
AUG = f"{BASE}/release_prep/release_staging/edge_bank/augmented_edges.csv"
BASE_EDGES = f"{BASE}/release_prep/release_staging/edge_bank/base_edges.csv"
PROP = f"{BASE}/outputs/remote_recovery_20260828/data/mof_191k_properties_v2.csv"
PARENT_VF = f"{OUT}/parent_vf_from_vol.csv"
RESULTS = f"{BASE}/outputs/parent_build_20260826/state/results.jsonl"

# crosswalks
fwd = {}
for fp in [f"{BASE}/edge_augmentation/base_edge_aug/edge_id_crosswalk_v2.csv",
           f"{BASE}/docs/database_paper/audit_v1/edge_id_crosswalk_v2_extension.csv"]:
    with open(fp) as f:
        for r in csv.DictReader(f):
            fwd[r["legacy_edge_id"].strip()] = (
                r.get("new_canonical_edge_id") or r.get("edge_id")).strip()
rev = {v: k for k, v in fwd.items()}


def norm_node(x):
    if pd.isna(x):
        return ""
    s = str(x)
    if s.upper().startswith("N") and s[1:].isdigit():
        return s[1:]
    return s


def canon_name(topo, n1, n2, edge_token):
    base = f"{str(topo)}_N{norm_node(n1)}"
    if n2 and str(n2) not in ("", "__none__", "None", "nan"):
        base += f"_N{norm_node(n2)}"
    return f"{base}_{edge_token}"


def edge_to_legacy(token_full):
    tok = token_full.split("_")[0]
    mods = "_".join(token_full.split("_")[1:])
    leg = rev.get(tok, tok)
    return f"{leg}_{mods}" if mods else leg


print("loading master ...")
m = pd.read_csv(MASTER, low_memory=False)

# ---- Table 1: success-only master (all rows currently success) ----
t1 = m.drop(columns=["assembly_success", "lammps_success", "zeo_success"])
t1.insert(1, "mof_name", t1["canonical_variant_key"])
t1.to_csv(f"{OUT}/mof_master_table.csv", index=False)
print("table1:", t1.shape)

# ---- props for edited-side gcd/vf/density ----
props = pd.read_csv(PROP)
pkey = {}
for _, r in props.iterrows():
    pkey[r["canonical_name"]] = (r["gcd"], r["vf"], r["density"])
print("props keys:", len(pkey))

# ---- parent-side values ----
pres = {}
for line in open(RESULTS):
    d = json.loads(line)
    if d["status"] == "ok":
        pres[d["parent_id"]] = d
vf_df = pd.read_csv(PARENT_VF, dtype=str)
vf_map = dict(zip(vf_df.parent_id,
                  zip(vf_df.base_vf, vf_df.base_density, vf_df.base_av_cm3_g)))
print("parent results:", len(pres))

# ---- Table 2: edited vs base zeo per MOF ----
ed = m[m.category.isin(["edited_delta_pld", "edited_no_base"])].copy()

def pid_of(r):
    parts = [str(r.topo), str(r.node_inorg)]
    if pd.notna(r.node_org) and str(r.node_org) not in ("", "__none__", "None"):
        parts.append(str(r.node_org))
    # master base_edge may be legacy (fixed spellings); parent ids use canonical
    be = str(r.base_edge)
    parts.append(fwd.get(be, be))
    return "+".join(parts)

rows = []
for _, r in ed.iterrows():
    p = pid_of(r)
    b = pres.get(p)
    bvf = vf_map.get(p)
    # edited side from props
    en_prop = None
    if isinstance(r.modified_edge_id, str):
        cands = [canon_name(r.topo, r.node_inorg, r.node_org,
                            edge_to_legacy(r.modified_edge_id))]
        if edge_to_legacy(r.modified_edge_id) != r.modified_edge_id:
            cands.append(canon_name(r.topo, r.node_inorg, r.node_org,
                                    r.modified_edge_id))
        for c in cands:
            if c in pkey:
                en_prop = pkey[c]
                break
    rows.append({
        "mof_name": r.canonical_variant_key,
        "mof_id": r.mof_id,
        "topo": r.topo,
        "node_inorg": r.node_inorg,
        "node_org": r.node_org,
        "base_edge": r.base_edge,
        "edited_edge_id": r.modified_edge_id,
        "base_zeo_pld": b["pld"] if b else (r.base_pld if pd.notna(r.base_pld) else ""),
        "base_zeo_lcd": b["lcd"] if b else "",
        "base_zeo_gcd": b["gcd"] if b else "",
        "base_vf": bvf[0] if bvf else "",
        "base_density": bvf[1] if bvf else "",
        "edited_zeo_pld": r.modified_pld,
        "edited_zeo_lcd": r.modified_lcd,
        "edited_zeo_gcd": en_prop[0] if en_prop else "",
        "edited_vf": en_prop[1] if en_prop else "",
        "edited_density": en_prop[2] if en_prop else "",
        "delta_zeo_pld": r.delta_pld,
    })
t2 = pd.DataFrame(rows)
t2.to_csv(f"{OUT}/edited_vs_base_zeo_table.csv", index=False)
print("table2:", t2.shape, "| base side filled:", t2.base_zeo_pld.notna().sum(),
      "| edited gcd filled:", t2.edited_zeo_gcd.notna().sum())

# ---- Table 3: edited edge table with stats ----
aug = pd.read_csv(AUG, dtype=str)
be = pd.read_csv(BASE_EDGES, dtype=str)
leg = dict(zip(be.base_edge_id, be.legacy_edge_id))
aug["parent_legacy_family"] = aug.parent_base_edge_id.map(leg)
usage = m["modified_edge_id"].value_counts()
aug["n_mof_in_master"] = aug.augmented_edge_id.map(usage).fillna(0).astype(int)
aug["in_moffusion_90k"] = aug.parent_base_edge_id.map(
    dict(zip(be.base_edge_id, be.in_moffusion_90k)))
# per-edge Zeo stats from t2
agged = t2.groupby("edited_edge_id").agg(
    mean_edited_pld=("edited_zeo_pld", "mean"),
    std_edited_pld=("edited_zeo_pld", "std"),
    mean_delta_pld=("delta_zeo_pld", "mean"),
    std_delta_pld=("delta_zeo_pld", "std"),
    mean_edited_lcd=("edited_zeo_lcd", "mean"),
).reset_index()
t3 = aug.merge(agged, left_on="augmented_edge_id", right_on="edited_edge_id",
               how="left")
t3 = t3.drop(columns=["edited_edge_id"])
t3.to_csv(f"{OUT}/edited_edge_table.csv", index=False)
print("table3:", t3.shape)

print("\nDone.")
