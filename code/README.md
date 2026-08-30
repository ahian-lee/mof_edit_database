# Code

Pipelines that produced and repaired the released tables. Paths inside the
scripts are workspace constants recorded for provenance; the scripts are the
authoritative description of the pipeline.

| Script | Role |
|---|---|
| `build_release_tables.py` | builds the three release tables from the unified master + parent/property sources |
| `repair_pld_lcd_swaps.py` | fixes Zeo++ Di/Df (LCD/PLD) interchanges |
| `build_pld_lcd_recovery.py` | builds the missing-PLD/LCD recovery job index |
| `apply_remote_lcd_backfill.py` | backfills missing LCD from remote source archives |
| `merge_parent_pld.py` | merges measured unedited-parent PLDs into the master (fixes pseudo-pairs) |
| `apply_parent_remote_backfill.py` | backfills remaining parent values from a remote run archive |

Environment: Python 3.10 with `pandas`, `numpy`. pormake / LAMMPS (UFF4MOF) /
Zeo++ binaries are required only for regenerating measurements, not for the
tables.
