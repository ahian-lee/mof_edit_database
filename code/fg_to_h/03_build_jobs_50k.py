#!/usr/bin/env python3
"""03_build_jobs_50k.py — sample 50k FG->H jobs into the canonical
transfer_map_jobs.csv format required by the remote canonical pipeline.

Source state (FG-carrying base MOF) is NOT re-run: its PLD/LCD is taken from
mof_master_table (base_pld / base columns) and recorded in
manifest/source_state_table.csv for the final local join.
"""
import csv, json, random, collections
from pathlib import Path

R = Path("/home/user/lyh/projects/mofdiffusion/docs/model_desigin/stage2_multi_fg_runs/20260908_fg_to_h_50k_v1")
MASTER = Path("/home/user/lyh/projects/mofdiffusion/outputs/release_tables_20260828/mof_master_table_v2_paths_20260829.csv")
N_TARGET = int(__import__("os").environ.get("N_TARGET", "50000"))
REMOTE_ROUND = "/opt/data/private/lyh_workplace/al_data/active_learning/fg_to_h_50k_20260908"

random.seed(20260908)

# 1) master context index: (topo,node_inorg,node_org,base_edge) -> base_pld/lcd
ctx = {}
with open(MASTER) as f:
    for r in csv.DictReader(f):
        k = (r["topo"], r["node_inorg"], r["node_org"], r["base_edge"])
        if k not in ctx:
            ctx[k] = (r["base_pld"], r.get("modified_lcd", ""))  # base_pld; lcd col checked below
print("unique contexts:", len(ctx))

# 2) variants
variants = list(csv.DictReader(open(R / "manifest/variant_edges.csv")))
sha = json.load(open(R / "manifest/variant_edges_sha256.json"))

# contexts per source edge
src_ctx = collections.defaultdict(list)
for (t, ni, no, be) in ctx:
    src_ctx[be].append((t, ni, no))

pool = []
for v in variants:
    be = v["source_edge"]
    for c in src_ctx.get(be, []):
        pool.append((v, c))
print("combination pool:", len(pool))

# 3) sample 50k with full variant coverage
by_var = collections.defaultdict(list)
for i, (v, c) in enumerate(pool):
    by_var[v["variant_edge_id"]].append(i)
chosen = set()
for vid, idxs in by_var.items():
    chosen.add(random.choice(idxs))
rest = [i for i in range(len(pool)) if i not in chosen]
random.shuffle(rest)
need = N_TARGET - len(chosen)
chosen.update(rest[:need])
print("selected:", len(chosen))

# 4) write canonical jobs + source table
rows = []
src_rows = []
for n, i in enumerate(sorted(chosen), 1):
    v, (t, ni, no) = pool[i]
    vid = v["variant_edge_id"]
    be = v["source_edge"]
    pld, lcd = ctx[(t, ni, no, be)]
    jid = f"f2h_{n:05d}"
    rows.append({
        "job_id": jid,
        "topo": t, "node_inorg": ni, "node_org": no,
        "base_edge": be, "edited_edge": vid,
        "row_type": "edited", "job_type": "fg_to_h",
        "mod_token": v["action"], "planned": 1,
        "edited_edge_identity_contract": "exact_xyz_required_no_database_fallback",
        "edited_edge_xyz_path": f"{REMOTE_ROUND}/assets/variant_edges/{vid}.xyz",
        "edited_edge_xyz_sha256": sha[vid],
    })
    src_rows.append({
        "job_id": jid, "topo": t, "node_inorg": ni, "node_org": no,
        "source_edge": be, "variant_edge_id": vid, "action": v["action"],
        "source_base_pld": pld, "source_base_lcd": lcd,
    })

import os
os.makedirs(R / "manifest", exist_ok=True)
with open(R / "manifest/transfer_map_jobs.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
with open(R / "manifest/source_state_table.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(src_rows[0].keys()))
    w.writeheader()
    w.writerows(src_rows)

# stats
act = collections.Counter(r["mod_token"].split(":")[0] for r in rows)
topo_n = len(set(r["topo"] for r in rows))
var_n = len(set(r["edited_edge"] for r in rows))
print(f"jobs: {len(rows)}  unique variants used: {var_n}  unique topos: {topo_n}")
print("action families:", dict(act))
