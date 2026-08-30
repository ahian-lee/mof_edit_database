# Full MOFChecker audit summary (n=191687)

- master rows: 191687
- records with usable CIF: 108620
- CIF parsed OK: 44778
- CIF parse failed: 63842
- timeout records: 210

## overall: ALL (parsed n=44778)

| check | 检出(fail) | 检出率 | 未判定(NA) | 通过率 |
|---|---:|---:|---:|---:|
| has_metal | 44546 | 99.48% | 42 | 190 |
| has_carbon | 44736 | 99.91% | 42 | 0 |
| is_porous | 44071 | 98.42% | 386 | 321 |
| has_atomic_overlaps | 17339 | 38.72% | 49 | 27390 |
| has_overcoordinated_c | 7136 | 15.94% | 43 | 37599 |
| has_overcoordinated_n | 2717 | 6.07% | 42 | 42019 |
| has_overcoordinated_h | 10051 | 22.45% | 46 | 34681 |
| has_undercoordinated_c | 16490 | 36.83% | 43 | 28245 |
| has_undercoordinated_n | 12122 | 27.07% | 43 | 32613 |
| has_suspicious_terminal_oxo | 1678 | 3.75% | 42 | 43058 |
| has_3d_connected_graph | 41856 | 93.47% | 52 | 2870 |
| has_lone_molecule | 8239 | 18.40% | 116 | 36423 |
| has_hydrogen | 43770 | 97.75% | 42 | 966 |
| has_high_charges | 828 | 1.85% | 37357 | 6593 |

## by_category: base_reference (parsed n=22138)

| check | 检出(fail) | 检出率 | 未判定(NA) | 通过率 |
|---|---:|---:|---:|---:|
| has_metal | 21957 | 99.18% | 6 | 175 |
| has_carbon | 22132 | 99.97% | 6 | 0 |
| is_porous | 21851 | 98.70% | 108 | 179 |
| has_atomic_overlaps | 10618 | 47.96% | 6 | 11514 |
| has_overcoordinated_c | 2025 | 9.15% | 6 | 20107 |
| has_overcoordinated_n | 127 | 0.57% | 6 | 22005 |
| has_overcoordinated_h | 3757 | 16.97% | 6 | 18375 |
| has_undercoordinated_c | 6812 | 30.77% | 6 | 15320 |
| has_undercoordinated_n | 5505 | 24.87% | 6 | 16627 |
| has_suspicious_terminal_oxo | 816 | 3.69% | 6 | 21316 |
| has_3d_connected_graph | 19543 | 88.28% | 7 | 2588 |
| has_lone_molecule | 5496 | 24.83% | 19 | 16623 |
| has_hydrogen | 21741 | 98.21% | 6 | 391 |
| has_high_charges | 78 | 0.35% | 18510 | 3550 |

## by_category: edited_delta_pld (parsed n=16722)

| check | 检出(fail) | 检出率 | 未判定(NA) | 通过率 |
|---|---:|---:|---:|---:|
| has_metal | 16685 | 99.78% | 34 | 3 |
| has_carbon | 16688 | 99.80% | 34 | 0 |
| is_porous | 16391 | 98.02% | 257 | 74 |
| has_atomic_overlaps | 3401 | 20.34% | 41 | 13280 |
| has_overcoordinated_c | 1613 | 9.65% | 34 | 15075 |
| has_overcoordinated_n | 773 | 4.62% | 34 | 15915 |
| has_overcoordinated_h | 2761 | 16.51% | 38 | 13923 |
| has_undercoordinated_c | 6496 | 38.85% | 35 | 10191 |
| has_undercoordinated_n | 4792 | 28.66% | 35 | 11895 |
| has_suspicious_terminal_oxo | 579 | 3.46% | 34 | 16109 |
| has_3d_connected_graph | 16565 | 99.06% | 43 | 114 |
| has_lone_molecule | 1907 | 11.40% | 90 | 14725 |
| has_hydrogen | 16225 | 97.03% | 34 | 463 |
| has_high_charges | 238 | 1.42% | 14744 | 1740 |

## by_category: edited_no_base (parsed n=5918)

| check | 检出(fail) | 检出率 | 未判定(NA) | 通过率 |
|---|---:|---:|---:|---:|
| has_metal | 5904 | 99.76% | 2 | 12 |
| has_carbon | 5916 | 99.97% | 2 | 0 |
| is_porous | 5829 | 98.50% | 21 | 68 |
| has_atomic_overlaps | 3320 | 56.10% | 2 | 2596 |
| has_overcoordinated_c | 3498 | 59.11% | 3 | 2417 |
| has_overcoordinated_n | 1817 | 30.70% | 2 | 4099 |
| has_overcoordinated_h | 3533 | 59.70% | 2 | 2383 |
| has_undercoordinated_c | 3182 | 53.77% | 2 | 2734 |
| has_undercoordinated_n | 1825 | 30.84% | 2 | 4091 |
| has_suspicious_terminal_oxo | 283 | 4.78% | 2 | 5633 |
| has_3d_connected_graph | 5748 | 97.13% | 2 | 168 |
| has_lone_molecule | 836 | 14.13% | 7 | 5075 |
| has_hydrogen | 5804 | 98.07% | 2 | 112 |
| has_high_charges | 512 | 8.65% | 4103 | 1303 |

## by_layer: al_active_learning (parsed n=10914)

| check | 检出(fail) | 检出率 | 未判定(NA) | 通过率 |
|---|---:|---:|---:|---:|
| has_metal | 10897 | 99.84% | 5 | 12 |
| has_carbon | 10909 | 99.95% | 5 | 0 |
| is_porous | 10760 | 98.59% | 33 | 121 |
| has_atomic_overlaps | 5823 | 53.35% | 5 | 5086 |
| has_overcoordinated_c | 6822 | 62.51% | 6 | 4086 |
| has_overcoordinated_n | 2708 | 24.81% | 5 | 8201 |
| has_overcoordinated_h | 6682 | 61.22% | 5 | 4227 |
| has_undercoordinated_c | 6239 | 57.17% | 5 | 4670 |
| has_undercoordinated_n | 3005 | 27.53% | 5 | 7904 |
| has_suspicious_terminal_oxo | 535 | 4.90% | 5 | 10374 |
| has_3d_connected_graph | 9251 | 84.76% | 5 | 1658 |
| has_lone_molecule | 2788 | 25.55% | 13 | 8113 |
| has_hydrogen | 10774 | 98.72% | 5 | 135 |
| has_high_charges | 764 | 7.00% | 7099 | 3051 |

## by_layer: lammps_uff_93k (parsed n=14412)

| check | 检出(fail) | 检出率 | 未判定(NA) | 通过率 |
|---|---:|---:|---:|---:|
| has_metal | 14376 | 99.75% | 33 | 3 |
| has_carbon | 14379 | 99.77% | 33 | 0 |
| is_porous | 14140 | 98.11% | 250 | 22 |
| has_atomic_overlaps | 2022 | 14.03% | 40 | 12350 |
| has_overcoordinated_c | 24 | 0.17% | 33 | 14355 |
| has_overcoordinated_n | 0 | 0.00% | 33 | 14379 |
| has_overcoordinated_h | 1207 | 8.37% | 37 | 13168 |
| has_undercoordinated_c | 5285 | 36.67% | 34 | 9093 |
| has_undercoordinated_n | 3924 | 27.23% | 34 | 10454 |
| has_suspicious_terminal_oxo | 452 | 3.14% | 33 | 13927 |
| has_3d_connected_graph | 14347 | 99.55% | 42 | 23 |
| has_lone_molecule | 1609 | 11.16% | 89 | 12714 |
| has_hydrogen | 13929 | 96.65% | 33 | 450 |
| has_high_charges | 6 | 0.04% | 13596 | 810 |

## by_layer: lammps_uff_v2edge_round2 (parsed n=19452)

| check | 检出(fail) | 检出率 | 未判定(NA) | 通过率 |
|---|---:|---:|---:|---:|
| has_metal | 19273 | 99.08% | 4 | 175 |
| has_carbon | 19448 | 99.98% | 4 | 0 |
| is_porous | 19171 | 98.56% | 103 | 178 |
| has_atomic_overlaps | 9494 | 48.81% | 4 | 9954 |
| has_overcoordinated_c | 290 | 1.49% | 4 | 19158 |
| has_overcoordinated_n | 9 | 0.05% | 4 | 19439 |
| has_overcoordinated_h | 2162 | 11.11% | 4 | 17286 |
| has_undercoordinated_c | 4966 | 25.53% | 4 | 14482 |
| has_undercoordinated_n | 5193 | 26.70% | 4 | 14255 |
| has_suspicious_terminal_oxo | 691 | 3.55% | 4 | 18757 |
| has_3d_connected_graph | 18258 | 93.86% | 5 | 1189 |
| has_lone_molecule | 3842 | 19.75% | 14 | 15596 |
| has_hydrogen | 19067 | 98.02% | 4 | 381 |
| has_high_charges | 58 | 0.30% | 16662 | 2732 |

## by_source_round: 93k (parsed n=14412)

| check | 检出(fail) | 检出率 | 未判定(NA) | 通过率 |
|---|---:|---:|---:|---:|
| has_metal | 14376 | 99.75% | 33 | 3 |
| has_carbon | 14379 | 99.77% | 33 | 0 |
| is_porous | 14140 | 98.11% | 250 | 22 |
| has_atomic_overlaps | 2022 | 14.03% | 40 | 12350 |
| has_overcoordinated_c | 24 | 0.17% | 33 | 14355 |
| has_overcoordinated_n | 0 | 0.00% | 33 | 14379 |
| has_overcoordinated_h | 1207 | 8.37% | 37 | 13168 |
| has_undercoordinated_c | 5285 | 36.67% | 34 | 9093 |
| has_undercoordinated_n | 3924 | 27.23% | 34 | 10454 |
| has_suspicious_terminal_oxo | 452 | 3.14% | 33 | 13927 |
| has_3d_connected_graph | 14347 | 99.55% | 42 | 23 |
| has_lone_molecule | 1609 | 11.16% | 89 | 12714 |
| has_hydrogen | 13929 | 96.65% | 33 | 450 |
| has_high_charges | 6 | 0.04% | 13596 | 810 |

## by_source_round: fg (parsed n=1686)

| check | 检出(fail) | 检出率 | 未判定(NA) | 通过率 |
|---|---:|---:|---:|---:|
| has_metal | 1686 | 100.00% | 0 | 0 |
| has_carbon | 1686 | 100.00% | 0 | 0 |
| is_porous | 1632 | 96.80% | 3 | 51 |
| has_atomic_overlaps | 1306 | 77.46% | 0 | 380 |
| has_overcoordinated_c | 1578 | 93.59% | 0 | 108 |
| has_overcoordinated_n | 763 | 45.26% | 0 | 923 |
| has_overcoordinated_h | 1503 | 89.15% | 0 | 183 |
| has_undercoordinated_c | 942 | 55.87% | 0 | 744 |
| has_undercoordinated_n | 505 | 29.95% | 0 | 1181 |
| has_suspicious_terminal_oxo | 84 | 4.98% | 0 | 1602 |
| has_3d_connected_graph | 1597 | 94.72% | 0 | 89 |
| has_lone_molecule | 260 | 15.42% | 0 | 1426 |
| has_hydrogen | 1673 | 99.23% | 0 | 13 |
| has_high_charges | 229 | 13.58% | 625 | 832 |

## by_source_round: gfn (parsed n=376)

| check | 检出(fail) | 检出率 | 未判定(NA) | 通过率 |
|---|---:|---:|---:|---:|
| has_metal | 374 | 99.47% | 1 | 1 |
| has_carbon | 375 | 99.73% | 1 | 0 |
| is_porous | 368 | 97.87% | 2 | 6 |
| has_atomic_overlaps | 283 | 75.27% | 1 | 92 |
| has_overcoordinated_c | 339 | 90.16% | 2 | 35 |
| has_overcoordinated_n | 165 | 43.88% | 1 | 210 |
| has_overcoordinated_h | 319 | 84.84% | 1 | 56 |
| has_undercoordinated_c | 185 | 49.20% | 1 | 190 |
| has_undercoordinated_n | 122 | 32.45% | 1 | 253 |
| has_suspicious_terminal_oxo | 11 | 2.93% | 1 | 364 |
| has_3d_connected_graph | 355 | 94.41% | 1 | 20 |
| has_lone_molecule | 67 | 17.82% | 2 | 307 |
| has_hydrogen | 363 | 96.54% | 1 | 12 |
| has_high_charges | 34 | 9.04% | 227 | 115 |

## by_source_round: ref (parsed n=2652)

| check | 检出(fail) | 检出率 | 未判定(NA) | 通过率 |
|---|---:|---:|---:|---:|
| has_metal | 2650 | 99.92% | 2 | 0 |
| has_carbon | 2650 | 99.92% | 2 | 0 |
| is_porous | 2646 | 99.77% | 5 | 1 |
| has_atomic_overlaps | 1120 | 42.23% | 2 | 1530 |
| has_overcoordinated_c | 1729 | 65.20% | 2 | 921 |
| has_overcoordinated_n | 112 | 4.22% | 2 | 2538 |
| has_overcoordinated_h | 1589 | 59.92% | 2 | 1061 |
| has_undercoordinated_c | 1841 | 69.42% | 2 | 809 |
| has_undercoordinated_n | 310 | 11.69% | 2 | 2340 |
| has_suspicious_terminal_oxo | 125 | 4.71% | 2 | 2525 |
| has_3d_connected_graph | 1251 | 47.17% | 2 | 1399 |
| has_lone_molecule | 1650 | 62.22% | 5 | 997 |
| has_hydrogen | 2646 | 99.77% | 2 | 4 |
| has_high_charges | 20 | 0.75% | 1824 | 808 |

## by_source_round: round (parsed n=768)

| check | 检出(fail) | 检出率 | 未判定(NA) | 通过率 |
|---|---:|---:|---:|---:|
| has_metal | 767 | 99.87% | 0 | 1 |
| has_carbon | 768 | 100.00% | 0 | 0 |
| is_porous | 764 | 99.48% | 2 | 2 |
| has_atomic_overlaps | 573 | 74.61% | 0 | 195 |
| has_overcoordinated_c | 699 | 91.02% | 0 | 69 |
| has_overcoordinated_n | 239 | 31.12% | 0 | 529 |
| has_overcoordinated_h | 623 | 81.12% | 0 | 145 |
| has_undercoordinated_c | 413 | 53.78% | 0 | 355 |
| has_undercoordinated_n | 221 | 28.78% | 0 | 547 |
| has_suspicious_terminal_oxo | 21 | 2.73% | 0 | 747 |
| has_3d_connected_graph | 721 | 93.88% | 0 | 47 |
| has_lone_molecule | 169 | 22.01% | 0 | 599 |
| has_hydrogen | 743 | 96.74% | 0 | 25 |
| has_high_charges | 94 | 12.24% | 454 | 220 |

## by_source_round: round004c (parsed n=2117)

| check | 检出(fail) | 检出率 | 未判定(NA) | 通过率 |
|---|---:|---:|---:|---:|
| has_metal | 2107 | 99.53% | 1 | 9 |
| has_carbon | 2116 | 99.95% | 1 | 0 |
| is_porous | 2080 | 98.25% | 7 | 30 |
| has_atomic_overlaps | 1780 | 84.08% | 1 | 336 |
| has_overcoordinated_c | 1997 | 94.33% | 1 | 119 |
| has_overcoordinated_n | 1090 | 51.49% | 1 | 1026 |
| has_overcoordinated_h | 1922 | 90.79% | 1 | 194 |
| has_undercoordinated_c | 1240 | 58.57% | 1 | 876 |
| has_undercoordinated_n | 646 | 30.51% | 1 | 1470 |
| has_suspicious_terminal_oxo | 95 | 4.49% | 1 | 2021 |
| has_3d_connected_graph | 2020 | 95.42% | 1 | 96 |
| has_lone_molecule | 350 | 16.53% | 3 | 1764 |
| has_hydrogen | 2079 | 98.21% | 1 | 37 |
| has_high_charges | 319 | 15.07% | 1104 | 694 |

## by_source_round: round2 (parsed n=19452)

| check | 检出(fail) | 检出率 | 未判定(NA) | 通过率 |
|---|---:|---:|---:|---:|
| has_metal | 19273 | 99.08% | 4 | 175 |
| has_carbon | 19448 | 99.98% | 4 | 0 |
| is_porous | 19171 | 98.56% | 103 | 178 |
| has_atomic_overlaps | 9494 | 48.81% | 4 | 9954 |
| has_overcoordinated_c | 290 | 1.49% | 4 | 19158 |
| has_overcoordinated_n | 9 | 0.05% | 4 | 19439 |
| has_overcoordinated_h | 2162 | 11.11% | 4 | 17286 |
| has_undercoordinated_c | 4966 | 25.53% | 4 | 14482 |
| has_undercoordinated_n | 5193 | 26.70% | 4 | 14255 |
| has_suspicious_terminal_oxo | 691 | 3.55% | 4 | 18757 |
| has_3d_connected_graph | 18258 | 93.86% | 5 | 1189 |
| has_lone_molecule | 3842 | 19.75% | 14 | 15596 |
| has_hydrogen | 19067 | 98.02% | 4 | 381 |
| has_high_charges | 58 | 0.30% | 16662 | 2732 |

## by_source_round: taskS (parsed n=380)

| check | 检出(fail) | 检出率 | 未判定(NA) | 通过率 |
|---|---:|---:|---:|---:|
| has_metal | 379 | 99.74% | 0 | 1 |
| has_carbon | 380 | 100.00% | 0 | 0 |
| is_porous | 380 | 100.00% | 0 | 0 |
| has_atomic_overlaps | 49 | 12.89% | 0 | 331 |
| has_overcoordinated_c | 1 | 0.26% | 0 | 379 |
| has_overcoordinated_n | 0 | 0.00% | 0 | 380 |
| has_overcoordinated_h | 44 | 11.58% | 0 | 336 |
| has_undercoordinated_c | 180 | 47.37% | 0 | 200 |
| has_undercoordinated_n | 113 | 29.74% | 0 | 267 |
| has_suspicious_terminal_oxo | 18 | 4.74% | 0 | 362 |
| has_3d_connected_graph | 380 | 100.00% | 0 | 0 |
| has_lone_molecule | 34 | 8.95% | 0 | 346 |
| has_hydrogen | 371 | 97.63% | 0 | 9 |
| has_high_charges | 0 | 0.00% | 369 | 11 |

## by_source_round: taskY (parsed n=544)

| check | 检出(fail) | 检出率 | 未判定(NA) | 通过率 |
|---|---:|---:|---:|---:|
| has_metal | 544 | 100.00% | 0 | 0 |
| has_carbon | 544 | 100.00% | 0 | 0 |
| is_porous | 517 | 95.04% | 0 | 27 |
| has_atomic_overlaps | 432 | 79.41% | 0 | 112 |
| has_overcoordinated_c | 459 | 84.38% | 0 | 85 |
| has_overcoordinated_n | 325 | 59.74% | 0 | 219 |
| has_overcoordinated_h | 447 | 82.17% | 0 | 97 |
| has_undercoordinated_c | 264 | 48.53% | 0 | 280 |
| has_undercoordinated_n | 184 | 33.82% | 0 | 360 |
| has_suspicious_terminal_oxo | 58 | 10.66% | 0 | 486 |
| has_3d_connected_graph | 541 | 99.45% | 0 | 3 |
| has_lone_molecule | 45 | 8.27% | 1 | 498 |
| has_hydrogen | 540 | 99.26% | 0 | 4 |
| has_high_charges | 65 | 11.95% | 342 | 137 |

## by_source_round: taskZ (parsed n=1675)

| check | 检出(fail) | 检出率 | 未判定(NA) | 通过率 |
|---|---:|---:|---:|---:|
| has_metal | 1675 | 100.00% | 0 | 0 |
| has_carbon | 1675 | 100.00% | 0 | 0 |
| is_porous | 1661 | 99.16% | 12 | 2 |
| has_atomic_overlaps | 192 | 11.46% | 0 | 1483 |
| has_overcoordinated_c | 5 | 0.30% | 0 | 1670 |
| has_overcoordinated_n | 1 | 0.06% | 0 | 1674 |
| has_overcoordinated_h | 166 | 9.91% | 0 | 1509 |
| has_undercoordinated_c | 864 | 51.58% | 0 | 811 |
| has_undercoordinated_n | 531 | 31.70% | 0 | 1144 |
| has_suspicious_terminal_oxo | 75 | 4.48% | 0 | 1600 |
| has_3d_connected_graph | 1674 | 99.94% | 0 | 1 |
| has_lone_molecule | 161 | 9.61% | 1 | 1513 |
| has_hydrogen | 1644 | 98.15% | 0 | 31 |
| has_high_charges | 0 | 0.00% | 1555 | 120 |

## by_source_round: taskp (parsed n=716)

| check | 检出(fail) | 检出率 | 未判定(NA) | 通过率 |
|---|---:|---:|---:|---:|
| has_metal | 715 | 99.86% | 1 | 0 |
| has_carbon | 715 | 99.86% | 1 | 0 |
| is_porous | 712 | 99.44% | 2 | 2 |
| has_atomic_overlaps | 88 | 12.29% | 1 | 627 |
| has_overcoordinated_c | 15 | 2.09% | 1 | 700 |
| has_overcoordinated_n | 13 | 1.82% | 1 | 702 |
| has_overcoordinated_h | 69 | 9.64% | 1 | 646 |
| has_undercoordinated_c | 310 | 43.30% | 1 | 405 |
| has_undercoordinated_n | 373 | 52.09% | 1 | 342 |
| has_suspicious_terminal_oxo | 48 | 6.70% | 1 | 667 |
| has_3d_connected_graph | 712 | 99.44% | 1 | 3 |
| has_lone_molecule | 52 | 7.26% | 1 | 663 |
| has_hydrogen | 715 | 99.86% | 1 | 0 |
| has_high_charges | 3 | 0.42% | 599 | 114 |

## Coverage vs master

- master rows: 191687
- checked (CIF available + processed): 108620
- remaining to process: 0