# Cechy – Jackets & Coats: statystyki (reguły na danych, przed LLM)

Dane: `fg_produkty_kategorie.csv` · stan na 21.10.2026 · produktów w dziale: 8 324

Procent = udział produktów danej kategorii z tą wartością (w nawiasie liczba produktów). Przy cechach wielowartościowych (closure_type, colors, linning_composition) suma w kolumnie może przekraczać 100%. „(brak → LLM)” = dane nic nie mówią, wartość przydzieli LLM.

| Kategoria | Produkty |
|---|---:|
| Classic Coats | 2 198 |
| Trench Coats | 166 |
| Jackets | 4 045 |
| Bombers | 1 573 |
| Vests | 342 |

Produkty bez koloru na początku nazwy (do wykluczenia): 247 (3,0%)

## colors (kilka wartości)

| Wartość | Classic Coats | Trench Coats | Jackets | Bombers | Vests |
|---|---:|---:|---:|---:|---:|
| Black | 48,1% (1 057) | 34,9% (58) | 49,7% (2 011) | 50,6% (796) | 55,8% (191) |
| Navy | 11,3% (249) | 11,4% (19) | 7,8% (316) | 12,9% (203) | 7,6% (26) |
| Blue | 2,8% (62) | 3,0% (5) | 15,6% (633) | 4,5% (70) | 6,7% (23) |
| Grey | 10,9% (240) | 4,2% (7) | 5,4% (219) | 5,8% (92) | 7,6% (26) |
| Beige | 9,6% (211) | 29,5% (49) | 5,6% (225) | 4,5% (71) | 7,9% (27) |
| Green | 6,9% (152) | 5,4% (9) | 5,0% (202) | 10,0% (158) | 4,7% (16) |
| White | 3,3% (72) | 4,8% (8) | 4,4% (178) | 5,7% (90) | 4,7% (16) |
| Red | 2,6% (57) | 0,6% (1) | 2,5% (100) | 3,4% (54) | 3,5% (12) |
| Pink | 2,4% (53) | 3,0% (5) | 1,7% (68) | 2,0% (31) | 2,6% (9) |
| Brown | 2,3% (50) | 1,8% (3) | 1,4% (58) | 1,7% (26) | 1,8% (6) |
| Yellow | 0,8% (17) | 0 | 0,6% (26) | 1,1% (18) | 1,2% (4) |
| Multicolor | 0,8% (18) | 0,6% (1) | 0,5% (22) | 1,1% (18) | 0,3% (1) |
| Purple | 0,6% (14) | 0 | 0,6% (25) | 0,6% (10) | 0,3% (1) |
| Orange | 0,5% (12) | 0,6% (1) | 0,5% (21) | 0,6% (10) | 0,6% (2) |

## linning_composition (kilka wartości)

| Wartość | Classic Coats | Trench Coats | Jackets | Bombers | Vests |
|---|---:|---:|---:|---:|---:|
| Viscose | 27,8% (610) | 30,7% (51) | 17,8% (719) | 29,5% (464) | 19,9% (68) |
| Polyester | 11,2% (246) | 7,2% (12) | 11,3% (456) | 17,9% (282) | 7,3% (25) |
| Cotton | 9,4% (207) | 13,3% (22) | 11,1% (449) | 12,8% (201) | 9,6% (33) |
| Nylon | 7,1% (157) | 0,6% (1) | 9,8% (396) | 7,5% (118) | 10,2% (35) |
| Unlined | 14,3% (315) | 15,1% (25) | 6,9% (278) | 2,4% (38) | 5,6% (19) |
| Silk | 3,2% (70) | 4,8% (8) | 1,5% (61) | 2,4% (38) | 6,1% (21) |
| Unknown | 35,1% (771) | 38,6% (64) | 50,6% (2 048) | 38,6% (607) | 46,8% (160) |
| Other (spoza listy) | 4,0% (89) | 4,2% (7) | 3,4% (136) | 3,9% (61) | 2,9% (10) |

## hood

| Wartość | Classic Coats | Trench Coats | Jackets | Bombers | Vests |
|---|---:|---:|---:|---:|---:|
| Without Hood | 71,2% (1 565) | 97,6% (162) | 76,7% (3 102) | 96,0% (1 510) | 88,0% (301) |
| With Hood | 28,8% (633) | 2,4% (4) | 23,3% (943) | 4,0% (63) | 12,0% (41) |

## coat_style

| Wartość | Classic Coats |
|---|---:|
| Parka | 7,5% (165) |
| Other | 6,4% (140) |
| Standard | 86,1% (1 893) |

## jacket_style

| Wartość | Jackets |
|---|---:|
| Denim | 21,1% (852) |
| Biker | 12,2% (492) |
| Windbreaker | 3,3% (132) |
| Other | 63,5% (2 569) |

## closure_type (kilka wartości)

| Wartość | Classic Coats | Trench Coats | Jackets | Bombers | Vests |
|---|---:|---:|---:|---:|---:|
| Zip | 34,0% (748) | 3,0% (5) | 60,3% (2 438) | 77,7% (1 223) | 38,3% (131) |
| Button | 52,0% (1 143) | 84,3% (140) | 31,7% (1 284) | 5,3% (84) | 30,4% (104) |
| Press-Stud | 27,6% (607) | 7,2% (12) | 26,7% (1 082) | 25,6% (403) | 24,9% (85) |
| Double-Breasted | 15,4% (339) | 65,7% (109) | 2,0% (81) | 0,1% (1) | 7,0% (24) |
| Belted | 7,2% (159) | 59,6% (99) | 3,9% (157) | 0,2% (3) | 4,4% (15) |
| Open Front | 2,1% (46) | 0 | 0,5% (21) | 0 | 2,9% (10) |
| Other | 2,9% (63) | 0 | 1,2% (50) | 0,4% (6) | 8,2% (28) |
| (brak → LLM) | 2,6% (58) | 0,6% (1) | 2,4% (97) | 2,8% (44) | 5,0% (17) |

## collar_type

| Wartość | Classic Coats | Trench Coats | Jackets |
|---|---:|---:|---:|
| Point Collar | 14,4% (316) | 60,8% (101) | 36,1% (1 460) |
| Stand Collar | 17,8% (391) | 3,0% (5) | 28,5% (1 151) |
| Lapel Collar | 37,8% (830) | 30,1% (50) | 12,3% (496) |
| Other | 4,7% (103) | 3,0% (5) | 3,5% (143) |
| (brak → LLM) | 25,4% (558) | 3,0% (5) | 19,7% (795) |

## insulation

| Wartość | Classic Coats | Trench Coats | Jackets | Bombers | Vests |
|---|---:|---:|---:|---:|---:|
| Down | 11,4% (250) | 0 | 16,2% (656) | 4,5% (71) | 29,8% (102) |
| Synthetic Padding | 7,0% (154) | 1,2% (2) | 7,5% (305) | 22,3% (351) | 9,9% (34) |
| Shearling Lined | 1,9% (42) | 0 | 2,2% (89) | 0,6% (10) | 0,9% (3) |
| Fleece Lined | 1,0% (21) | 0 | 1,8% (71) | 0,5% (8) | 0,3% (1) |
| Other | 0,6% (14) | 1,2% (2) | 0,2% (8) | 0,5% (8) | 0 |
| Uninsulated | 78,1% (1 717) | 97,6% (162) | 72,1% (2 916) | 71,5% (1 125) | 59,1% (202) |

## fit

| Wartość | Classic Coats | Trench Coats | Jackets | Bombers | Vests |
|---|---:|---:|---:|---:|---:|
| Regular | 91,6% (2 014) | 88,6% (147) | 95,4% (3 860) | 95,5% (1 503) | 89,8% (307) |
| Oversized | 8,4% (184) | 11,4% (19) | 4,6% (185) | 4,5% (70) | 10,2% (35) |
