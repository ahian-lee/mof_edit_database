#!/usr/bin/env python3
"""02b_expand_variant_subsets.py — add random-subset FG-removal variants.

For every multi-site edge, sample extra subset-removal variants (beyond the
single-site / per-type / full variants from 02) to widen the (variant, context)
combination pool. Appends to assets/variant_edges, variant_edges.csv and the
sha256 inventory. Deterministic seed.
"""
import os, json, math, random, csv, hashlib
from pathlib import Path

R = Path("/home/user/lyh/projects/mofdiffusion/docs/model_desigin/stage2_multi_fg_runs/20260908_fg_to_h_50k_v1")
SITES = json.load(open(R / "manifest/base_edge_fg_sites.json"))
SRC_BANK = Path("/home/user/data/mof_data/datasets/augmented_edges_base_v2/base_xyz")
OUT = R / "assets/variant_edges"
random.seed(20260908)
C_H_AROM = 1.09
O_H = 0.97
MAX_EXTRA_PER_EDGE = 25


def parse_edge(path):
    ls = open(path).read().splitlines()
    n = int(ls[0])
    ats = [l.split("\t") for l in ls[2:2 + n]]
    anchors = [int(x) for x in ls[1].split()]
    bonds = []
    smiles = None
    for l in ls[2 + n:]:
        p = [x for x in l.split("\t") if x != ""]
        if len(p) == 3 and p[2].strip() in ("S", "D", "T", "A"):
            bonds.append((int(p[0]), int(p[1]), p[2].strip()))
        elif l.startswith("#") and "SMILES" in l:
            smiles = l.split("=", 1)[1].strip()
    return ats, anchors, bonds, smiles


def make_variant(edge_file, drop_sites, mode_tag, o2h=False):
    stem = edge_file[:-4]
    ats, anchors, bonds, smiles = parse_edge(SRC_BANK / edge_file)
    n = len(ats)
    pos = [(float(a[1]), float(a[2]), float(a[3])) for a in ats]
    drop = set()
    add_h = []
    for f in drop_sites:
        if o2h:
            O, Cm = f["atoms"][0], f["atoms"][1]
            drop.add(Cm); drop.update(f["atoms"][2:])
            v = [pos[Cm][k] - pos[O][k] for k in range(3)]
            d = math.sqrt(sum(x * x for x in v)); u = [x / d for x in v]
            add_h.append((O, [pos[O][k] + u[k] * O_H for k in range(3)]))
        else:
            for a in f["atoms"]:
                drop.add(a)
            att, fg0 = f["attach"], f["atoms"][0]
            v = [pos[fg0][k] - pos[att][k] for k in range(3)]
            d = math.sqrt(sum(x * x for x in v)); u = [x / d for x in v]
            add_h.append((att, [pos[att][k] + u[k] * C_H_AROM for k in range(3)]))
    keep = [i for i in range(n) if i not in drop]
    remap = {i: j for j, i in enumerate(keep)}
    new_ats = [ats[i] for i in keep]
    new_bonds = [(remap[a], remap[b], t) for a, b, t in bonds
                 if a not in drop and b not in drop]
    new_anchors = [remap[i] for i in anchors]
    for att, hp in add_h:
        new_ats.append(["H"] + [f"{c:.6f}" for c in hp])
        new_bonds.append((remap[att], len(new_ats) - 1, "S"))
    lines = [str(len(new_ats)), "\t".join(map(str, new_anchors))]
    lines += [f"{a[0]}\t{a[1]}\t{a[2]}\t{a[3]}" for a in new_ats]
    lines += [f"{a}\t{b}\t{t}" for a, b, t in new_bonds]
    if smiles:
        lines.append(f"# SMILES={smiles}")
    vid = f"{stem}__{mode_tag}"
    (OUT / f"{vid}.xyz").write_text("\n".join(lines) + "\n")
    return vid, len(new_ats)


def main():
    existing = set()
    rows = list(csv.DictReader(open(R / "manifest/variant_edges.csv")))
    for r in rows:
        existing.add(r["variant_edge_id"])
    new_rows = []
    for edge_file, fgs in sorted(SITES.items()):
        if len(fgs) < 2:
            continue
        stem = edge_file[:-4]
        # candidate subsets: mix of 2..n-1 sites, deterministic random sample
        n = len(fgs)
        tried = set()
        m = 0
        attempts = 0
        while m < MAX_EXTRA_PER_EDGE and attempts < 200:
            attempts += 1
            k = random.randint(2, n - 1) if n > 2 else 1
            sub = tuple(sorted(random.sample(fgs, k), key=lambda f: f["atoms"][0]))
            key = tuple(f["atoms"][0] for f in sub)
            if key in tried:
                continue
            tried.add(key)
            tag = "sub" + "".join(str(f["atoms"][0]) for f in sub)[:40] + f"g{k}"
            vid, na = make_variant(edge_file, list(sub), tag)
            if vid in existing:
                continue
            existing.add(vid)
            new_rows.append({"variant_edge_id": vid, "source_edge": stem,
                             "action": f"FG2H:subset({k}/{n},fg={'+'.join(str(f['atoms'][0]) for f in sub)})",
                             "n_atoms": na})
            m += 1
    # append to csv + sha
    with open(R / "manifest/variant_edges.csv", "a", newline="") as fo:
        w = csv.DictWriter(fo, fieldnames=["variant_edge_id", "source_edge", "action", "n_atoms"])
        w.writerows(new_rows)
    inv = json.load(open(R / "manifest/variant_edges_sha256.json"))
    for p in OUT.glob("*.xyz"):
        inv.setdefault(p.name[:-4], hashlib.sha256(p.read_bytes()).hexdigest())
    json.dump(inv, open(R / "manifest/variant_edges_sha256.json", "w"), indent=1)
    total = len(list(csv.DictReader(open(R / "manifest/variant_edges.csv"))))
    print("new subset variants:", len(new_rows), " total variants:", total, " files:", len(inv))


if __name__ == "__main__":
    main()
