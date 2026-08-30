# Dataset Characterization

Numbers computed directly from the shipped tables (`data/*.csv.gz`, frozen
2026-08-28/29).

## Scale

| Quantity | Value |
|---|---:|
| MOF records | 191,687 |
| Paired edits (ΔPLD available) | 135,283 |
| Edited without measured parent | 24,780 |
| Unedited base references | 49,154 |
| Topologies | 600 |
| Inorganic nodes | 458 |
| Base-linker families in measured MOFs | 600 |
| Edge assets in bank (clean) | 77,161 (+615 excluded) |
| Edge variants appearing in measured MOFs | 18,393 |

Generation layers: `al_active_learning` 87,551 · `lammps_uff_93k` 49,548 ·
`lammps_uff_v2edge_round2` 37,320 · `uff_paired_gold_8k` 8,797 ·
`al_base_candidate` 8,471.

## Pore geometry

Edited records: PLD 0.18 – 70.79 Å (ultramicroporous → mesoporous).
Paired ΔPLD: median −3.01 Å, range −28.7 … +37.1 Å; 92.4% of edits shrink the
pore, 7.6% open it. Per-category (paired subset of `edited_no_base`):
median −3.34 Å, 91.4% negative.

Edited-vs-base Zeo contrast table: base side measured for 135,425/142,533
rows (95.0%).

## Edit response by linker family

Within fixed (topology × inorganic node × base linker) families:

- maximum PLD span achievable by FG editing alone: **30.4 Å**
- families spanning > 5 Å: 4,764; > 10 Å: 990

## Chemical diversity

- Top-5 topologies: bct 2,588 · est 1,913 · hcp 1,707 · cdl 1,597 · rob 1,561
- Substitution sites per edit: median 4, up to 20 (multi-site functionalization)
- FG repertoire: halogens, methyl, ethynyl, cyano, hydroxy, amino, thio,
  phosphino, small rings (rigid); alkyl, carboxylic acid, ester, amide,
  sulfonate, phosphate (flexible)
- Edge-bank long tail: variants per family range 1 – 4,124 (median 124)

## Reproducibility of these numbers

```python
import pandas as pd
m = pd.read_csv("data/mof_master_table.csv.gz")
m.category.value_counts()
m.dropna(subset=["delta_pld"]).delta_pld.describe()
```
