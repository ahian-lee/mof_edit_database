# FG→H reverse-editing dataset (2026-09-12)

**65,000 functional-group-removal (FG→H) edits** over the same scaffold universe as the
H→FG release — the reverse direction of the main database. Every record is the
**pore-measured H-state MOF** obtained by chemically removing side-chain functional
groups from an FG-carrying base linker, with the **relaxed FG-state parent measured
under the identical protocol**, so ΔPLD is again a one-to-one before/after label —
this time in the pore-*opening* direction.

## Construction

1. **Chemical FG identification** (`01_scan_base_edge_fg.py`) — the 476 CSV-derived
   base linkers carry their own side-chain chemistry. A bond-table-based parser
   (per-edge `a b S|D|T|A` records, no distance guessing) + conservative side-chain
   rules (halogen on non-carbonyl C; O–H with no carboxyl partner; N with exactly
   2 H and 1 heavy neighbour; terminal methyl; methoxy bridging aryl–CH3; thiol;
   terminal nitrile) identify **180 edges / 487 removable sites**:
   CH3 ×301, OH ×77, F ×40, OCH3 ×30, NH2 ×20, Br ×10, Cl ×6, SH ×2, I ×1.
2. **Variant-edge generation** (`02_make_variant_edges.py`, `02b_expand_variant_subsets.py`)
   — for every site (and per-type / full / random-subset combinations): delete the FG
   atoms, place H at 1.09 Å along the original C–FG bond (O–H 0.97 Å for OCH3→OH
   dealkylation). Backbone coordinates, bond table, anchor indices and the SMILES
   comment are untouched. **1,693 unique variant edges** with SHA256 identity contracts.
   Note: the underlying base-edge bank uses the X-anchor placement fixed to 0.75 Å
   (see the anchor-placement fix note), consistent with every edited asset.
3. **Jobs** (`03_build_jobs_50k.py`) — variant edges × contexts sampled from the
   107,268-combination pool (1,434 variants × 416 topologies, exact-XYZ identity
   contracts on both sides). 65,000 jobs executed.
4. **Pipeline** — identical to the main release: pormake assembly → UFF4MOF/LAMMPS
   relaxation → Zeo++ v0.3 `-res/-vol` with **`-ha`**, applied independently to the
   FG-state parent and the H-state product.

## Results

| stage | success | rate |
|---|---|---|
| Assembly (targets 65,000 of a 107,268 pool; sources 14,583) | 63,521 + 14,250 CIFs | 97.7% |
| LAMMPS relaxation | 63,526 + 14,134 | 99.2% |
| Zeo++ `-ha` | 63,521 + 14,132 | 99.99% / 99.98% |

- **ΔPLD (H-state − FG-state, both relaxed): 61,844 complete pairs (95.1% of 65,000).**
- Direction: **75.8% pore-increasing**, median **+0.37 Å** (p10 −0.34, p90 +1.32);
  full multi-site strips reach +1.2…+6.1 Å.
- **Monotone in FG volume and removal count** (medians, single-site): F 0.15 < OH 0.17 <
  CH3 0.35 < Cl 0.39 < Br 0.55 < I 0.76 Å; all-7-site strip 1.23 Å, all-14-site strip
  1.77 Å. Subset strips interpolate (k-of-n strips grow with k). 24.2% of pairs shrink
  slightly — LAMMPS iso-relaxation contracts the cell after de-functionalization, the
  mirror image of the 8% reverse-direction edits in the H→FG release.

## Files

| file | rows | size | description |
|---|---|---|---|
| `data/fg_to_h_table.csv.gz` | 65,000 × 18 | 3.8 MB | **Main FG→H table**: context, source edge (FG), variant edge (H), action, both-state PLD/LCD, ΔPLD/ΔLCD, provenance paths |
| `data/fg_to_h_variant_edges.csv.gz` | 1,693 | 15 KB | variant-edge bank: source edge, action, atom count |
| `data/fg_to_h_variant_edges_sha256.json.gz` | 1,693 | 73 KB | SHA256 identity contracts of the variant edges |
| `data/fg_to_h_source_jobs.csv.gz` | 14,583 | 373 KB | FG-state parent jobs (base_reference rows, exact-XYZ contracts) |
| `data/fg_to_h_source_edge_fg_sites.json.gz` | 180 | 4 KB | per-edge removable-site inventory (type, atom indices, attachment) |
| `data/fg_to_h_variant_edges_sha256.json.gz` | — | — | included in SHA256SUMS.txt |

Reproduction scripts in `code/fg_to_h/`. Structures (assembled CIFs for both states,
relaxed coordinates, raw `.res`/`.vol`) live on the measurement workspace
(`/opt/data/private/lyh_workplace/al_data/active_learning/fg_to_h_50k_20260908*/`);
paths are recorded per row in `fg_to_h_table.csv`.

## Table schema (`fg_to_h_table.csv`)

| column | meaning |
|---|---|
| `job_id` | FG→H job id (`f2h_XXXXX`) |
| `topo`, `node_inorg`, `node_org` | scaffold (as in the main table) |
| `source_edge` | FG-carrying base linker (canonical E1xxx id) |
| `variant_edge_id` | H-state linker after FG removal (`E1001__f2h_CH37x8` style) |
| `action` | removal recipe, e.g. `FG2H:CH3@7(fg=8)` / `FG2H:CH3@all(3)` / `OCH3->OH@4` |
| `source_base_pld`, `source_base_lcd` | relaxed FG-state parent PLD/LCD (Å) |
| `target_pld`, `target_lcd` | relaxed H-state product PLD/LCD (Å) |
| `delta_pld`, `delta_lcd` | target − source (Å); empty when either side failed |
| `target_cif`, `target_res` | workspace pointers (H-state CIF and raw Zeo++ .res) |

## Suggested tasks

1. **Reverse-direction ΔPLD regression** — predict pore *opening* from FG-removal
   recipes; the complement of the H→FG task, with the same scaffold-paired contrast.
2. **Edit-direction symmetry studies** — H→FG and FG→H measured under one protocol
   enable direct tests of edit-direction asymmetry (relaxation hysteresis,
   cell-contraction effects) on identical scaffold pairs.
3. **Site-set combinatorics** — 1,073 subset strips (k-of-n removals) give a
   monotone response ladder per family; ideal for additivity/interaction analyses
   of functional-group contributions to pore geometry.
4. **De-functionalization as start-state generation** — the H-state products are
   new valid MOFs absent from the 250k assembly universe (v2-generation linkers),
   expanding the measured scaffold space by 63.5k records.

## Limitations

- Same force-field caveat as the main release (UFF4MOF classical values).
- 5 target + 2 source large structures failed Zeo++ inside the host memory cgroup
  during co-tenancy with GPU-cluster jobs; they are the only rows with missing
  metrics and are identified by empty fields in the table.
- 3,659 further assembled/relaxed combinations are banked on the workspace
  (`cifs_overflow/`) and can be measured to extend this dataset without new assembly.
