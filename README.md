# MOF Functional-Group-Editing Database (MOF-Edit-DB)

**191,687 pore-measured MOF records built by systematic linker functional-group
(FG) editing, with unedited-parent contrasts and a 77k asset edge bank.**

Every record was assembled with [pormake](https://github.com/Sangwon91/PORMAKE),
relaxed with UFF4MOF in LAMMPS, and measured with Zeo++ under one identical
protocol, so pore metrics — including the functionalization-induced pore shift
**ΔPLD** — are internally comparable across the whole database.

---

## Why this dataset is useful

- **Paired causal contrasts, not cross-sample statistics.** 135,283 edited MOFs
  carry the measured PLD of *the same unedited parent scaffold*, so ΔPLD is a
  one-to-one before/after intervention label — a natural testbed for
  counterfactual / causal property prediction on materials.
- **Discrete, chemically executable edits.** Each edit is a functional-group
  attachment to a specific linker site (`mod_token`, e.g. `H15_S` = phosphino at
  site 15), grounded in SMILES-derived linker assets with SHA256-tracked
  3D structures — a graph-edit action space, not a black-box latent space.
- **Huge pore response range from edits alone.** ΔPLD spans −28.7 Å to
  +37.1 Å (92% of edits shrink the pore); within a fixed
  (topology × node × base linker) family, editing alone spans up to **30.4 Å**
  of pore-limiting diameter (990 families span > 10 Å).
- **Unified protocol.** All 191,687 records: pormake assembly → UFF4MOF/LAMMPS
  relaxation → Zeo++ (`-res`, `-vol`). One force field, one code, one pass —
  no cross-literature heterogeneity.

## Dataset at a glance

| | |
|---|---:|
| MOF records (all UFF4MOF-relaxed) | 191,687 |
| — edited with measured parent contrast (ΔPLD) | 135,283 |
| — edited, parent not (yet) measured | 24,780 |
| — unedited base references | 49,154 |
| Topologies × inorganic nodes × base-linker families | 600 × 458 × 600 |
| Edited-edge asset bank (with QC-clean subset) | 77,776 (77,161 clean) |
| PLD range (edited records) | 0.18 – 70.79 Å |
| ΔPLD median / range (paired records) | −3.01 Å / −28.7 … +37.1 Å |
| Force field / pore code | UFF4MOF (LAMMPS) / Zeo++ v0.3 |

## Files

| File | Rows × Cols | Size | Description |
|---|---|---|---|
| `data/mof_master_table.csv.gz` | 191,687 × 27 | 12 MB | **Main table**: one row per MOF record — identity, category, scaffold keys, FG-edit label, pore metrics, provenance |
| `data/edited_vs_base_zeo_table.csv.gz` | 142,533 × 18 | 7.3 MB | Edited-vs-base Zeo++ contrast per edited MOF: PLD/LCD/GCD/void-fraction/density on both sides + ΔPLD |
| `data/edited_edge_table.csv.gz` | 77,161 × 20 | 4.8 MB | Edited-edge asset bank: parent linker, substitution recipe (`fg_tokens`, `fg_smiles`), XYZ checksum, per-edge usage & aggregate Zeo stats |
| `data/edited_edge_table_excluded.csv.gz` | 615 × 21 | <0.1 MB | Assets excluded by geometric QC (`FAIL:anchor_dist_collapse`), with reasons |
| `data/SHA256SUMS.txt` | — | — | Checksums of all files above |

Structures (assembled CIFs, UFF4MOF-relaxed coordinates, raw Zeo++ `.res`/`.vol`
outputs) and the full row-level repair-audit CSVs are not hosted in this
lightweight repository; see **Data quality** below and contact the authors.

## Main table schema (`mof_master_table.csv`)

| Column | Meaning |
|---|---|
| `mof_id`, `mof_name` | unique record id / canonical variant name |
| `category` | `edited_delta_pld` (edit + measured parent) · `edited_no_base` (edit, parent unmeasured) · `base_reference` (unedited parent) |
| `topo`, `node_inorg`, `node_org` | topology, inorganic node(s); `node_org` empty for binary-node topologies |
| `base_edge`, `base_edge_source` | unedited parent linker family and its origin (`pormake_db` / `csv_derived`) |
| `modified_edge_id`, `mod_token` | edited linker id; substitution recipe (e.g. `H5_P` = phosphino at site 5; empty for `base_reference`) |
| `base_pld` | PLD of the unedited parent (paired records only) |
| `modified_pld`, `modified_lcd` | edited MOF pore-limiting / largest-cavity diameter (Å) |
| `delta_pld` | `modified_pld − base_pld` (Å); empty when the parent was never measured |
| `optimized_cif_path`, `zeo_res_path`, `zeo_vol_path` | provenance pointers (workspace-local; see limitations) |
| `layer`, `forcefield`, `source_round`, `source_job`, `source_table` | generation-layer provenance (`al_active_learning` 87,551 · `lammps_uff_93k` 49,548 · `lammps_uff_v2edge_round2` 37,320 · `uff_paired_gold_8k` 8,797 · `al_base_candidate` 8,471) |
| `canonical_scaffold_key`, `canonical_variant_key`, `canonical_record_name` | grouping keys: scaffold = topo+node; variant = scaffold+edge+edit |
| `structure_identity_status`, `mapping_status` | row-level audit status flags |

`edited_vs_base_zeo_table.csv` adds parent-side and edited-side
`*_zeo_pld / *_zeo_lcd / *_zeo_gcd`, `*_vf`, `*_density` (base side filled for
135,425 / 142,533 rows = 95.0%). `edited_edge_table.csv` resolves every
`augmented_edge_id` to its parent linker, substitution sites (`site_h_ids`),
FG tokens and SMILES, XYZ SHA256, and aggregate usage statistics
(`n_mof_in_master`, per-edge mean ΔPLD).

## Suggested tasks for ML / CS researchers

1. **Edit-effect regression (ΔPLD prediction).** Given (scaffold, base linker,
   FG recipe), predict the pore shift — a counterfactual regression where
   ground truth is a true before/after measurement on the same scaffold.
   Splits by scaffold family (seen/unseen) test compositional generalization.
2. **Inverse design / goal-directed editing.** Select FG edits to hit a target
   PLD window without changing topology — a discrete constrained-optimization
   benchmark with exact feasibility checking (assemble + measure).
3. **Causal / group-invariant representation learning.** Scaffold-paired
   records form natural (X, do(FG), Y) triplets; test invariance of learned
   representations under scaffold shift.
4. **Long-tail & out-of-distribution evaluation.** 18,393 edge variants are in
   measured MOFs while 77k bank assets are not — a built-in open-set split for
   evaluating models on unseen chemistry.
5. **Generative model evaluation.** Conditional diffusion / GFlowNet /
   autoregressive graph editors can be scored against the empirical
   edit→ΔPLD response surface rather than ad-hoc proxies.

## Methods

Assembly: pormake topology + node + linker XYZ. Edited linkers were generated
by SMILES/graph re-embedding and anchor-preserving 3D grafting (rigid groups:
halogens, methyl, ethynyl, cyano, hydroxy, amino, thio, phosphino, small rings;
flexible: alkyl, carboxylic acid, ester, amide, sulfonate, phosphate), then
chemically deduplicated (5,619 RDKit-level duplicates removed). Relaxation:
LAMMPS (`lmp_serial`) with UFF4MOF. Pore metrics: Zeo++ v0.3 `network -res`
(Di = LCD, Df = PLD, Dif = LFPD) and `-vol` (accessible volume fraction,
density). Every measurement uses the same protocol, so ΔPLD is internally
consistent. Reproduction scripts for the release tables and the integrity-repair
pipeline are in [`code/`](code/); audit documentation in [`docs/`](docs/).

## Data quality and known limitations

Three integrity defects were discovered in an audit and fixed **before
release**, each with row-level old→new audit CSVs and reproducible scripts
(details in [`docs/data_audit_and_repairs.md`](docs/data_audit_and_repairs.md)):

1. **Pseudo-pair base values** — 132,039 rows had inherited/mismatched parent
   PLDs; replaced by measured parent values (local rebuild + remote-archive
   recovery). 2,527 rows retain the legacy value (parent assembly/relaxation
   failed) and are flagged via `source_round`/`mapping_status`.
2. **PLD/LCD swap** — 46,509 rows had Zeo++ Di/Df interchanged; all repaired
   and verified.
3. **Missing LCD** — 19,264 rows lacked `modified_lcd`; all backfilled from
   raw source archives (0 NaN remaining).

Additional limitations to keep in mind:

- PLD/LCD are classical-force-field (UFF4MOF) values — best for *relative*
  comparisons within the dataset, not DFT-quality absolutes.
- A full MOFChecker structural scan (44,778 parseable CIFs; summary in
  [`docs/mofcheck_full_summary.md`](docs/mofcheck_full_summary.md)) confirms
  ≥ 99% metal/carbon presence and ~98% porosity on parsed records; 63,842 CIFs
  did not parse in the checker and were not assessed (documented limitation).
- 615 edge assets (0.8%) failed geometric QC and are excluded from the clean
  edge table (reasons included).
- Path columns (`optimized_cif_path`, `zeo_*_path`) resolve on the original
  workspace only.

## License & citation

Data: [CC-BY 4.0](LICENSE). Code: MIT.

```bibtex
@dataset{mof_edit_db_2026,
  title  = {MOF Functional-Group-Editing Database: 191,687 pore-measured MOFs
            with unedited-parent contrasts and a 77k edited-edge asset bank},
  author = {[Authors]},
  year   = {2026},
  url    = {https://github.com/ahian-lee/mof_edit_database}
}
```

A Zenodo DOI mirror will be added upon archiving.

## Quick start

```python
import pandas as pd

master = pd.read_csv("data/mof_master_table.csv.gz")
paired = master.dropna(subset=["delta_pld"])          # 135,283 paired edits
base   = master[master.category == "base_reference"]  # 49,154 unedited parents

edges = pd.read_csv("data/edited_edge_table.csv.gz")
paired = paired.merge(
    edges[["augmented_edge_id", "fg_tokens", "fg_smiles", "parent_base_edge_id"]],
    left_on="modified_edge_id", right_on="augmented_edge_id", how="left")

zeo = pd.read_csv("data/edited_vs_base_zeo_table.csv.gz")  # both-side metrics
```
