#!/usr/bin/env python3
"""02_make_variant_edges.py — generate FG->H (and OCH3->OH) variant edges.

Reads base_edge_fg_sites.json (from 01_scan) and the FIXED base_xyz bank
(X anchors at 0.75 A). For every edge with side-chain FGs, generates:
  - per-site removal:   {stem}__f2h_{TYPE}{attach}.xyz    (FG -> H, 1.09 A)
  - per-type removal:   {stem}__f2h_{TYPE}all.xyz
  - full removal:       {stem}__f2h_all.xyz
  - O-methy cleavage:   {stem}__o2h_{attach}.xyz          (OCH3 -> OH, O-H 0.97 A)

Variant edges keep the bond table + SMILES comment, keep X anchors and the
anchor index line (re-indexed), and only touch the FG site. Backbond coords,
all other atoms and all bond orders are untouched.
"""
import os, json, math, sys
from pathlib import Path

R = Path("/home/user/lyh/projects/mofdiffusion/docs/model_desigin/stage2_multi_fg_runs/20260908_fg_to_h_50k_v1")
SITES = json.load(open(R / "manifest/base_edge_fg_sites.json"))
SRC_BANK = Path("/home/user/data/mof_data/datasets/augmented_edges_base_v2/base_xyz")
OUT = R / "assets/variant_edges"
OUT.mkdir(parents=True, exist_ok=True)

C_H_AROM = 1.09    # aromatic C-H
O_H = 0.97         # O-H (phenol)
BOND2NUM = {"S": 1, "D": 2, "T": 3, "A": 1.5}


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
    """drop_sites: list of FG dicts. If o2h: each FG must be OCH3 -> becomes OH."""
    stem = edge_file[:-4]
    ats, anchors, bonds, smiles = parse_edge(SRC_BANK / edge_file)
    n = len(ats)
    pos = [(float(a[1]), float(a[2]), float(a[3])) for a in ats]

    drop = set()
    add_h = []   # (attach_idx, [x,y,z], bond_len_display)
    for f in drop_sites:
        if o2h:
            # OCH3: f["atoms"] = [O, C_methyl, H, H, H], attach = aryl C
            O, Cm = f["atoms"][0], f["atoms"][1]
            drop.add(Cm)
            drop.update(f["atoms"][2:])          # methyl Hs
            v = [pos[Cm][k] - pos[O][k] for k in range(3)]
            d = math.sqrt(sum(x * x for x in v))
            u = [x / d for x in v]
            add_h.append((O, [pos[O][k] + u[k] * O_H for k in range(3)]))
        else:
            for a in f["atoms"]:
                drop.add(a)
            att = f["attach"]
            fg0 = f["atoms"][0]
            v = [pos[fg0][k] - pos[att][k] for k in range(3)]
            d = math.sqrt(sum(x * x for x in v))
            u = [x / d for x in v]
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
    import collections, hashlib
    manifest = []
    stats = collections.Counter()
    for edge_file, fgs in sorted(SITES.items()):
        stem = edge_file[:-4]
        # per-site removal
        for f in fgs:
            # disambiguate by FG lead-atom index (same type+attach can repeat,
            # e.g. isopropyl methyls share one attach carbon)
            vid, na = make_variant(edge_file, [f], f"f2h_{f['type']}{f['attach']}x{f['atoms'][0]}")
            manifest.append({"variant_edge_id": vid, "source_edge": stem,
                             "action": f"FG2H:{f['type']}@{f['attach']}(fg={f['atoms'][0]})", "n_atoms": na})
            stats[f"site_{f['type']}"] += 1
        # per-type removal
        by_type = {}
        for f in fgs:
            by_type.setdefault(f["type"], []).append(f)
        for t, fs in by_type.items():
            if len(fs) > 1:
                vid, na = make_variant(edge_file, fs, f"f2h_{t}all")
                manifest.append({"variant_edge_id": vid, "source_edge": stem,
                                 "action": f"FG2H:{t}@all({len(fs)})", "n_atoms": na})
                stats[f"typeall_{t}"] += 1
        # full removal
        if len(fgs) > 1:
            vid, na = make_variant(edge_file, fgs, "f2h_all")
            manifest.append({"variant_edge_id": vid, "source_edge": stem,
                             "action": f"FG2H:all({len(fgs)})", "n_atoms": na})
            stats["full_all"] += 1
        # OCH3 -> OH
        for f in fgs:
            if f["type"] == "OCH3":
                vid, na = make_variant(edge_file, [f], f"o2h_{f['atoms'][0]}", o2h=True)
                manifest.append({"variant_edge_id": vid, "source_edge": stem,
                                 "action": f"OCH3->OH@{f['atoms'][0]}", "n_atoms": na})
                stats["o2h"] += 1
    import csv
    with open(R / "manifest/variant_edges.csv", "w", newline="") as fo:
        w = csv.DictWriter(fo, fieldnames=["variant_edge_id", "source_edge", "action", "n_atoms"])
        w.writeheader()
        w.writerows(manifest)
    # sha256
    inv = {}
    for p in OUT.glob("*.xyz"):
        inv[p.name[:-4]] = hashlib.sha256(p.read_bytes()).hexdigest()
    json.dump(inv, open(R / "manifest/variant_edges_sha256.json", "w"), indent=1)
    print("variants:", len(manifest), " files:", len(inv))
    print("stats:", dict(stats))


if __name__ == "__main__":
    main()
