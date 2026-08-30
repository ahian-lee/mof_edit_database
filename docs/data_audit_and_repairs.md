# Data Audit & Repair Record

All repairs below were applied **before** the released tables were frozen
(2026-08-28/29). Every value-level change is logged in row-level
old→new audit CSVs with pre-repair backups; the pipeline scripts are in
[`code/`](../code/).

## Integrity defects found and fixed

### 1. Pseudo-pair base PLD values (132,039 rows)

The base PLD of edited rows was initially inherited from scaffold-level
annotations that did not correspond to a measured unedited parent of the same
scaffold ("pseudo-pairs"). Fix:

- 128,852 rows: parent rebuilt and measured under the release protocol
  (pormake → UFF4MOF/LAMMPS → Zeo++), `outputs/parent_build_20260826`,
  merged by `merge_parent_pld.py` with cell-level audit.
- 660 rows: recovered from a remote run archive
  (`apply_parent_remote_backfill.py`).
- **2,527 rows: parent assembly/relaxation failed (350 distinct parents) —
  these retain the legacy base value and are a known limitation.** They remain
  flagged and can be filtered via `mapping_status` / `source_round`.

### 2. PLD/LCD Di/Df swap (46,509 rows)

Zeo++ `.res` fields Df (free sphere / PLD) and Di (included sphere / LCD) were
interchanged for 46,509 rows. All repaired by `repair_pld_lcd_swaps.py` and
100% re-verified (0 remaining swaps; 0 PLD > LCD violations in the release).

### 3. Missing modified LCD (19,264 rows)

Backfilled in three recovery rounds from raw source archives
(`build_pld_lcd_recovery.py` → `apply_remote_lcd_backfill.py`), including a
final 85-row manual-review pass. Coverage is now 191,687/191,687 (0 NaN).

## Edge-bank geometric QC (615 exclusions)

The edited-edge asset table ships QC-cleaned (77,161 of 77,776). The 615
excluded assets carry `exclude_reason = FAIL:anchor_dist_collapse:<d>` —
their grafted 3D structures collapsed the attachment-anchor distance and are
unusable for assembly. The excluded rows are released verbatim in
`edited_edge_table_excluded.csv.gz`.

## Post-freeze verification checks (all PASS on the shipped tables)

| Check | Result |
|---|---|
| `mof_id` uniqueness | 191,687/191,687 |
| Required identity fields non-null (topo/node/base/edited edge/layer) | 0 NaN |
| `modified_lcd` coverage | 191,687/191,687 |
| Physical legality (PLD > 0, LCD ≥ PLD) | 0 violations |
| Row-level provenance (`layer`/`source_round`/`source_table`) | 100% |
| Force field uniformity | UFF4MOF × 191,687 |

## MOFChecker structural scan (2026-08-30)

A full MOFChecker run over all 191,687 records is summarized in
[`mofcheck_full_summary.md`](mofcheck_full_summary.md). Interpretation note:
in that raw output the columns for positive checks (`has_metal`,
`has_carbon`, `is_porous`, `has_3d_connected_graph`, `has_hydrogen`) report
**pass rates** (e.g. 99.48% of parsed records contain a metal), while the
remaining checks (`has_atomic_overlaps`, `has_overcoordinated_*`,
`has_undercoordinated_*`, `has_lone_molecule`, `has_suspicious_terminal_oxo`,
`has_high_charges`) report true warning rates. Coverage: 108,620 records had a
usable CIF path; 44,778 parsed in the checker, 63,842 failed to parse and 210
timed out and are therefore unassessed by this tool (physical-consistency
covariation PLD–density–void-fraction, r = −0.78/+0.81, is used as the
global structural proxy).

## Reproduction

`code/build_release_tables.py` rebuilds the three release tables from the
unified master; the repair scripts rebuild each fix from the archived
pre-repair backups. Scripts contain their workspace paths as constants and
serve as the authoritative record of the pipeline.
