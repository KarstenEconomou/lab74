# Apollo 17 HFE gradient-temperature extract

These four CSV files are minimally processed extracts of the NASA Planetary
Data System (PDS) **Apollo 15/17 HFE Concatenated Data** bundle, version 1.0
(St. Clair, Million, and Siegler, 2019), DOI
[10.17189/1518441](https://doi.org/10.17189/1518441):

| Local file | Exact PDS source product | Sensors | Retained rows |
| --- | --- | --- | ---: |
| `a17p1f1_19730201_19741231.csv` | [`a17p1f1_split.tab`](https://pds-geosciences.wustl.edu/lunar/urn-nasa-pds-a15_17_hfe_concatenated/data/split/a17p1f1_split.tab) | TG11A, TG11B | 17,757 |
| `a17p1f2_19730201_19741231.csv` | [`a17p1f2_split.tab`](https://pds-geosciences.wustl.edu/lunar/urn-nasa-pds-a15_17_hfe_concatenated/data/split/a17p1f2_split.tab) | TG12A, TG12B | 17,764 |
| `a17p2f1_19730201_19741231.csv` | [`a17p2f1_split.tab`](https://pds-geosciences.wustl.edu/lunar/urn-nasa-pds-a15_17_hfe_concatenated/data/split/a17p2f1_split.tab) | TG21A, TG21B | 17,702 |
| `a17p2f2_19730201_19741231.csv` | [`a17p2f2_split.tab`](https://pds-geosciences.wustl.edu/lunar/urn-nasa-pds-a15_17_hfe_concatenated/data/split/a17p2f2_split.tab) | TG22A, TG22B | 17,708 |

The PDS product labels are beside the source tables at the same URLs with
`.xml` in place of `.tab`. The bundle's full documentation is
[`bundle_documentation.md`](https://pds-geosciences.wustl.edu/lunar/urn-nasa-pds-a15_17_hfe_concatenated/document/bundle_documentation.md).

## Processing and terminology

The local files retain the source header and every source row whose
Earth-received timestamp is at or after `1973-02-01T00:00:00Z` and before
`1975-01-01T00:00:00Z`. Records remain in source order. Timestamp strings,
temperatures, numeric precision, and flags are unchanged; only rows outside
the interval were removed. The interval starts after the December 1972
deployment transient and ends where the lower-gradient PDS products end, so
all eight sensors can be plotted over one directly comparable interval.

The PDS `split` products are already quality-controlled derivatives. They
discard documented missing values and most flagged artifacts, use corrected
differential temperatures where available, and provide individual sensor
temperatures. For the older NSSDC portion, PDS derives the two sensor values
from bridge mean temperature and corrected differential temperature; for the
later reconstructed portion, it uses the archived explicit sensor values.
The example uses the requested `DTG...` notation in its code and labels; the
PDS column names omit the leading `D` (`TG...`).

All records in the retained interval have flag 0. The notebook nevertheless
applies a nonzero-flag mask so that the quality rule remains explicit and
safe if the extract is extended. No values are averaged, resampled, or
interpolated. Plot lines are broken wherever successive timestamps differ by
more than six hours.

## SHA-256

```text
dd5eb8db121a4bab903ac4cdf807a3918e49651753d0220e9cfd1be0847133c1  a17p1f1_19730201_19741231.csv
ac194e7a36115122f5c8fb200da9bf187ffcc32fd5d9d895b7133576910cb68f  a17p1f2_19730201_19741231.csv
e3636e31cc714264c4d8a866f6e209e1dd382fcae8916f0863e53363d01b58d1  a17p2f1_19730201_19741231.csv
e7e3f070df1960cc2b6470ca670aeb5be50793031e33ca0d92d2a13163780719  a17p2f2_19730201_19741231.csv
```
