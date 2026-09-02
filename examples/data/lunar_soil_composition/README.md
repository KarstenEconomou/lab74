# Lunar landing-site soil composition extract

The CSV is a direct transcription of the requested cells in **Table 7.15,
“Chemical compositions (wt.%) of average soils at lunar landing sites and in
selected regions,”** in *Lunar Sourcebook: A User's Guide to the Moon*, edited
by G. H. Heiken, D. T. Vaniman, and B. M. French (Cambridge University Press,
1991). The table is on printed page 346 (PDF page 369) of the exact source file
[`LunarSourceBook.pdf`](https://www.lpi.usra.edu/publications/books/lunar_sourcebook/pdf/LunarSourceBook.pdf)
served by the Lunar and Planetary Institute.

## Selected source columns

| Terrain used in example | Site | Table 7.15 column | Published basis |
| --- | --- | --- | --- |
| Mare | Apollo 11 | `11` | Composition of soil 10002 |
| Mare | Apollo 12 | `12` | Mean of ten selected Apollo 12 soils |
| Mare | Apollo 17 | `17` | Mean composition of Apollo 17 soils |
| Highlands | Apollo 14 | `14` | Mean of four selected Apollo 14 soils |
| Highlands | Apollo 16 | `16` | Mean composition of Apollo 16 soils |
| Highlands | Luna 20 | `L20` | Mean composition of Luna 20 soils (Russian data) |

Apollo 15 is intentionally absent because the requested terrain grouping
excludes its mixed Hadley-Apennine provenance. Values and precision are
unchanged from the four `wt.%` rows `TiO₂`, `Al₂O₃`, `FeO`, and `MgO` in
Table 7.15. Unicode subscripts are presentation-only; the table itself prints
the same oxide formulae with typographic subscripts.

The transcription was checked twice: once against text extracted from PDF
page 369 and once visually against a full-resolution rendering of the table.
No values were calculated, rounded, normalized, or imputed.

## Verification matrix (wt.%)

| Site | TiO₂ | Al₂O₃ | FeO | MgO |
| --- | ---: | ---: | ---: | ---: |
| Apollo 11 | 7.8 | 13.6 | 15.3 | 7.8 |
| Apollo 12 | 3.0 | 12.9 | 15.1 | 9.3 |
| Apollo 17 | 4.2 | 17.1 | 12.2 | 10.4 |
| Apollo 14 | 1.7 | 17.4 | 10.4 | 9.4 |
| Apollo 16 | 0.54 | 27.3 | 5.1 | 5.7 |
| Luna 20 | 0.55 | 22.3 | 7.0 | 9.8 |

SHA-256:

```text
5b9b42bd678d79d5f9e1f98b03e3f0b956fe0af820826c6386d1af4e6f7beb59  lunar_sourcebook_table_7_15_subset.csv
```
