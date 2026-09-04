# lab74

[![PyPI](https://img.shields.io/pypi/v/lab74)](https://pypi.org/project/lab74/)
[![Python versions](https://img.shields.io/pypi/pyversions/lab74)](https://pypi.org/project/lab74/)
[![License](https://img.shields.io/pypi/l/lab74)](https://github.com/KarstenEconomou/lab74/blob/v2.0.0/LICENSE)

`lab74` is a Matplotlib style layer for scientific and institutional 
figures in the technical print style of ca. 1965–1980.

The style uses fine rules, compact type, direct labels, monochrome textures, 
and one optional accent color. It does not add old-paper,
film-grain, or other retro effects.

[![Calculated characteristics of an n+-p-p+ silicon solar cell](https://raw.githubusercontent.com/KarstenEconomou/lab74/v2.0.0/examples/output/04_silicon_solar_cell.png)](https://github.com/KarstenEconomou/lab74/blob/v2.0.0/examples/04_silicon_solar_cell.ipynb)

## Installation

Install `lab74` from PyPI:

```console
pip install lab74
```

Requirements:
* `python>=3.12`
* `matplotlib>=3.8`
* `numpy>=1.26`

## Use

[![lab74 colour reproduction standard](https://raw.githubusercontent.com/KarstenEconomou/lab74/v2.0.0/examples/output/06_palette.png)](https://github.com/KarstenEconomou/lab74/blob/v2.0.0/examples/06_palette.ipynb)

```python
import matplotlib.pyplot as plt
import lab74

lab74.use()

fig, ax = plt.subplots()
ax.plot(x, y)
ax.set(xlabel="Energy (GeV)", ylabel=r"$\sigma$ (nb)")
```

The `use()` function applies the style. The default style is monochrome and
distinguishes series by line style alone, in proportional technical text.

Use these options to add an accent or to change the line series or typeface:

```python
lab74.use("instrument")  # Draw the first series in an accent.
lab74.use("aerospace")  # Use a different accent.
lab74.use(line_series="grayscale")  # Vary solid-line shades instead.
lab74.use(face="mono")  # Use monospaced text.
```

An accent colors the first line of the cycle and carries through to bars,
bands, stairs, and contours. `line_series` applies only without one.

You can also apply the packaged Matplotlib style sheet:

```python
plt.style.use(lab74.STYLE_PATH)
```

This sheet carries the same defaults as a bare `lab74.use()` call.

## Plot tools

`lab74` includes small tools for figure titles, annotations, region labels,
error bars, grouped bars, hatched regions, contours, maps, tables, ticks, grids,
frames, and multipanel layouts.
These tools return normal Matplotlib artists.
Thus, you can change the result with the Matplotlib API.

See [src/lab74/](https://github.com/KarstenEconomou/lab74/tree/v2.0.0/src/lab74) for all available tools and their
docstrings.

## Gallery

Executable notebooks are in the [examples/](https://github.com/KarstenEconomou/lab74/tree/v2.0.0/examples). 

[![Apollo 17 orange and gray soil grain-size distributions](https://raw.githubusercontent.com/KarstenEconomou/lab74/v2.0.0/examples/output/03_apollo17_soil_grain_size.png)](https://github.com/KarstenEconomou/lab74/blob/v2.0.0/examples/03_apollo17_soil_grain_size.ipynb)

[![Apollo 17 subsurface heat-flow temperatures](https://raw.githubusercontent.com/KarstenEconomou/lab74/v2.0.0/examples/output/02_apollo17_hfe.png)](https://github.com/KarstenEconomou/lab74/blob/v2.0.0/examples/02_apollo17_hfe.ipynb)

[![Lunar landing-site soil composition by terrain type](https://raw.githubusercontent.com/KarstenEconomou/lab74/v2.0.0/examples/output/05_lunar_soil_composition.png)](https://github.com/KarstenEconomou/lab74/blob/v2.0.0/examples/05_lunar_soil_composition.ipynb)

## Fonts

`lab74` bundles IBM Plex Sans Condensed (the `gothic` face) and IBM Plex Mono
(the `mono` face), each in regular, italic, and medium weights, under the
[SIL Open Font License 1.1](https://github.com/KarstenEconomou/lab74/blob/v2.0.0/src/lab74/fonts/OFL.txt). If neither font is
installed, `lab74` falls back to DejaVu Sans and DejaVu Sans Mono.

## Development

`lab74` uses [uv](https://docs.astral.sh/uv/) for environments,
[Ruff](https://docs.astral.sh/ruff/) for formatting and linting, and
[ty](https://github.com/astral-sh/ty) for type checking. All four checks run in
CI on every push and pull request:

```console
uv sync
uv run ruff format src tests
uv run ruff check src tests
uv run ty check
uv run pytest
```

## License

`lab74` is available under the [MIT license](https://github.com/KarstenEconomou/lab74/blob/v2.0.0/LICENSE).
