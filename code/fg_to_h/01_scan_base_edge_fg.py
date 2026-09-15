#!/usr/bin/env python3
"""Scan base_edge XYZ bank for side-chain functional groups (FG).

base_xyz files carry a bond table after the coordinate block:
  line0 natom / line1 anchor idxs / natom atom lines / bond lines 'a b S|D|T|A' / '# SMILES=...'
Build RDKit mol from that table (no distance guessing), then apply conservative
side-chain FG rules. X anchors are kept as dummies and never counted.
"""
import os, json, collections, sys
from rdkit import Chem
from rdkit import RDLogger
RDLogger.DisableLog('rdApp.*')

D = sys.argv[1] if len(sys.argv) > 1 else "/home/user/data/mof_data/datasets/augmented_edges_base_v2/base_xyz"
BOND = {"S": Chem.BondType.SINGLE, "D": Chem.BondType.DOUBLE,
        "T": Chem.BondType.TRIPLE, "A": Chem.BondType.AROMATIC}


def parse_edge(path):
    ls = open(path).read().splitlines()
    n = int(ls[0])
    ats = [l.split("\t") for l in ls[2:2 + n]]
    bonds = []
    smiles = None
    for l in ls[2 + n:]:
        p = [x for x in l.split("\t") if x != ""]
        if len(p) == 3 and p[2].strip() in BOND:
            bonds.append((int(p[0]), int(p[1]), BOND[p[2].strip()]))
        elif l.startswith("#") and "SMILES" in l:
            smiles = l.split("=", 1)[1].strip()
    return ats, bonds, smiles


def build_mol(ats, bonds):
    rw = Chem.RWMol()
    xyz2rk = {}
    for i, a in enumerate(ats):
        if a[0] == "X":
            at = Chem.Atom(0)  # dummy anchor
        else:
            at = Chem.Atom(a[0])
        at.SetNoImplicit(True)
        xyz2rk[i] = rw.AddAtom(at)
    for a, b, t in bonds:
        if a in xyz2rk and b in xyz2rk:
            rw.AddBond(xyz2rk[a], xyz2rk[b], t)
    return rw.GetMol(), xyz2rk


def find_fgs(m, ats, xyz2rk):
    rk2xyz = {v: k for k, v in xyz2rk.items()}

    def el(x):
        return ats[x][0]

    def heavy_x(x):
        return [rk2xyz[nb.GetIdx()] for nb in m.GetAtomWithIdx(xyz2rk[x]).GetNeighbors()
                if ats[rk2xyz[nb.GetIdx()]][0] not in ("X", "H")]

    def hx(x):
        return [rk2xyz[nb.GetIdx()] for nb in m.GetAtomWithIdx(xyz2rk[x]).GetNeighbors()
                if ats[rk2xyz[nb.GetIdx()]][0] == "H"]

    fgs = []
    for x in range(len(ats)):
        s = el(x)
        if s in ("Cl", "Br", "I", "F"):
            hv = heavy_x(x)
            if len(hv) == 1 and el(hv[0]) == "C":
                fgs.append({"type": s, "atoms": [x], "attach": hv[0]})
        elif s == "O":
            hs, hv = hx(x), heavy_x(x)
            if len(hs) == 1 and len(hv) == 1 and el(hv[0]) == "C":
                c = hv[0]
                other_o = [nb for nb in heavy_x(c) if el(nb) == "O" and nb != x]
                if not other_o:  # exclude COOH (C has a =O neighbor)
                    fgs.append({"type": "OH", "atoms": [x, hs[0]], "attach": c})
        elif s == "N":
            hs, hv = hx(x), heavy_x(x)
            if len(hs) == 2 and len(hv) == 1:
                fgs.append({"type": "NH2", "atoms": [x] + hs, "attach": hv[0]})
        elif s == "S":
            hs, hv = hx(x), heavy_x(x)
            if len(hs) == 1 and len(hv) == 1:
                fgs.append({"type": "SH", "atoms": [x, hs[0]], "attach": hv[0]})
        elif s == "C":
            hs, hv = hx(x), heavy_x(x)
            if len(hs) == 3 and len(hv) == 1 and el(hv[0]) != "O":
                fgs.append({"type": "CH3", "atoms": [x] + hs, "attach": hv[0]})
    for x in range(len(ats)):
        if el(x) != "O":
            continue
        hv = heavy_x(x)
        if len(hv) != 2:
            continue
        for c in hv:
            if len(hx(c)) == 3 and len(heavy_x(c)) == 1:
                other = [o for o in hv if o != c][0]
                fgs.append({"type": "OCH3", "atoms": [x, c] + hx(c), "attach": other})
    for x in range(len(ats)):
        if el(x) != "C":
            continue
        hs, hv = hx(x), heavy_x(x)
        if len(hs) == 0 and len(hv) == 1:
            nq = hv[0]
            if el(nq) == "N" and not hx(nq) and len(heavy_x(nq)) == 1:
                fgs.append({"type": "CN", "atoms": [x, nq], "attach": None})
    return fgs


def main():
    detail = collections.Counter()
    all_sites = {}
    fails = []
    smi_mismatch = 0
    for fn in sorted(os.listdir(D)):
        if not fn.endswith(".xyz"):
            continue
        try:
            ats, bonds, smiles = parse_edge(os.path.join(D, fn))
            m, xyz2rk = build_mol(ats, bonds)
            fgs = find_fgs(m, ats, xyz2rk)
        except Exception as e:
            fails.append((fn, str(e)))
            continue
        if fgs:
            all_sites[fn] = fgs
            for f in fgs:
                detail[f["type"]] += 1
    print("fails:", len(fails))
    for f in fails[:5]:
        print("  ", f)
    print("edges with FG:", len(all_sites), "/ 476")
    print("total FG sites:", sum(len(v) for v in all_sites.values()))
    print("by type:", dict(detail))
    json.dump(all_sites, open("/tmp/base_edge_fg_sites.json", "w"), indent=1)
    print("saved /tmp/base_edge_fg_sites.json")


if __name__ == "__main__":
    main()
