"""Draw effects that Matplotlib style parameters cannot define."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, Sequence
from itertools import pairwise
from math import isfinite
from typing import Any

import matplotlib as mpl
import numpy as np
from matplotlib.axes import Axes
from matplotlib.collections import PathCollection, PolyCollection
from matplotlib.contour import QuadContourSet
from matplotlib.container import ErrorbarContainer
from matplotlib.lines import Line2D
from matplotlib.path import Path
from matplotlib.patches import StepPatch
from matplotlib.typing import ColorType
from numpy.typing import ArrayLike

from .palette import ACCENTS, INK, PAPER

_HATCHES = ("", "/", "\\", "x", ".", "..")

type ContourLabelFormat = str | Mapping[float, str] | Callable[[float], str]


def _active_accent() -> ColorType:
    """Return the first active color or the default accent."""
    colors = mpl.rcParams["axes.prop_cycle"].by_key().get("color", [])
    return colors[0] if colors else ACCENTS["instrument"]


def errorbar(
    ax: Axes,
    x: ArrayLike,
    y: ArrayLike,
    yerr: ArrayLike | None = None,
    *,
    xerr: ArrayLike | None = None,
    **kwargs: Any,
) -> ErrorbarContainer:
    """Draw error bars with the lab74 line and open-circle defaults."""
    defaults: dict[str, Any] = {
        "color": INK,
        "ecolor": INK,
        "linestyle": "-",
        "linewidth": mpl.rcParams["lines.linewidth"],
        "marker": "o",
        "markersize": mpl.rcParams["lines.markersize"],
        "markerfacecolor": PAPER,
        "markeredgewidth": mpl.rcParams["lines.markeredgewidth"],
        "elinewidth": 0.45,
        "capsize": mpl.rcParams["errorbar.capsize"],
        "capthick": 0.45,
    }
    defaults.update(kwargs)
    return ax.errorbar(x, y, yerr=yerr, xerr=xerr, **defaults)


def band(
    ax: Axes,
    x: ArrayLike,
    lower: ArrayLike,
    upper: ArrayLike,
    *,
    hatch: str = "//",
    color: ColorType | None = None,
    **kwargs: Any,
) -> PolyCollection:
    """Draw a paper-filled interval in the active accent."""
    edge = _active_accent() if color is None else color
    defaults: dict[str, Any] = {
        "facecolor": PAPER,
        "edgecolor": edge,
        "linewidth": 0.5,
        "hatch": hatch,
    }
    defaults.update(kwargs)
    return ax.fill_between(x, lower, upper, **defaults)


def stairs(
    ax: Axes,
    values: ArrayLike,
    edges: ArrayLike | None = None,
    *,
    hatch: str = "//",
    color: ColorType | None = None,
    linewidth: float | None = None,
    **kwargs: Any,
) -> StepPatch:
    """Draw paper-filled stairs with equal hatch and outline widths."""
    edge = _active_accent() if color is None else color
    stroke = (
        float(mpl.rcParams["patch.linewidth"]) if linewidth is None else linewidth
    )
    defaults: dict[str, Any] = {
        "fill": True,
        "facecolor": PAPER,
        "edgecolor": edge,
        "linewidth": stroke,
        "hatch": hatch,
    }
    defaults.update(kwargs)
    with mpl.rc_context({"hatch.linewidth": stroke}):
        return ax.stairs(values, edges, **defaults)


def _polygon_area(vertices: np.ndarray) -> float:
    """Return the area of a polygon in square coordinate units."""
    x = vertices[:, 0]
    y = vertices[:, 1]
    return 0.5 * abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))


def stipple(
    ax: Axes,
    vertices: ArrayLike,
    *,
    density: float = 55,
    seed: int | None = 0,
    size: float = 2.0,
    color: ColorType = INK,
    **kwargs: Any,
) -> PathCollection:
    """Fill a polygon with dots at an approximate density per square inch.

    Set the final axes limits before this call because density uses the current
    data transform.
    """
    data_vertices = np.asarray(vertices, dtype=float)
    if data_vertices.ndim != 2 or data_vertices.shape[1] != 2 or len(data_vertices) < 3:
        raise ValueError(
            "The vertices must have shape (n, 2) and at least three points."
        )
    if not np.isfinite(data_vertices).all():
        raise ValueError("The vertices must contain only finite values.")
    if not isfinite(density) or density < 0:
        raise ValueError("The density must be finite and non-negative.")

    display_vertices = ax.transData.transform(data_vertices)
    area_inches = _polygon_area(display_vertices) / (ax.figure.dpi**2)
    count = round(density * area_inches)
    if count == 0:
        points = np.empty((0, 2))
    else:
        rng = np.random.default_rng(seed)
        closed_vertices = np.vstack([display_vertices, display_vertices[0]])
        path = Path(closed_vertices, closed=True)
        low = display_vertices.min(axis=0)
        high = display_vertices.max(axis=0)
        accepted: list[np.ndarray] = []
        remaining = count
        attempts = 0
        while remaining and attempts < 100:
            candidates = rng.uniform(low, high, size=(max(remaining * 3, 64), 2))
            inside = candidates[path.contains_points(candidates)]
            if len(inside):
                take = inside[:remaining]
                accepted.append(take)
                remaining -= len(take)
            attempts += 1
        if remaining:
            raise RuntimeError("The function could not sample the stipple polygon.")
        points = ax.transData.inverted().transform(np.vstack(accepted))

    defaults: dict[str, Any] = {
        "s": size,
        "c": color,
        "marker": ".",
        "linewidths": 0,
        "clip_on": True,
        "zorder": 1,
    }
    defaults.update(kwargs)
    return ax.scatter(points[:, 0], points[:, 1], **defaults)


def technical_contour(
    ax: Axes,
    x: ArrayLike,
    y: ArrayLike,
    z: ArrayLike,
    *,
    levels: Iterable[float],
    filled: bool = False,
    accent_levels: Iterable[float] = (),
    labels: bool = False,
    label_format: ContourLabelFormat = "%g",
    label_kwargs: Mapping[str, Any] | None = None,
    hatches: Sequence[str] | None = None,
    **kwargs: Any,
) -> tuple[QuadContourSet, QuadContourSet | None]:
    """Draw explicit contour levels and optional hatched regions."""
    values = list(levels)
    if len(values) < 2:
        raise ValueError("Technical contours require at least two explicit levels.")
    if not all(isfinite(value) for value in values):
        raise ValueError("Technical contour levels must be finite.")
    if any(first >= second for first, second in pairwise(values)):
        raise ValueError("Technical contour levels must be in increasing order.")
    accented = set(accent_levels)
    if len(accented) > 1:
        raise ValueError("Technical contours may accent at most one level.")
    if not accented.issubset(values):
        raise ValueError("The accented contour level must be present in levels.")
    accent = _active_accent()
    colors = [accent if level in accented else INK for level in values]
    linewidths = [0.9 if level in accented else 0.55 for level in values]

    regions: QuadContourSet | None = None
    if filled:
        region_hatches = list(_HATCHES if hatches is None else hatches)
        if not region_hatches:
            raise ValueError("Hatches must contain at least one pattern.")
        repeats = (len(values) - 1 + len(region_hatches) - 1) // len(region_hatches)
        region_hatches = (region_hatches * repeats)[: len(values) - 1]
        regions = ax.contourf(
            x,
            y,
            z,
            levels=values,
            colors=[PAPER] * (len(values) - 1),
            hatches=region_hatches,
            antialiased=True,
        )

    line_defaults: dict[str, Any] = {
        "colors": colors,
        "linewidths": linewidths,
    }
    line_defaults.update(kwargs)
    lines = ax.contour(x, y, z, levels=values, **line_defaults)
    if labels:
        label_defaults: dict[str, Any] = {
            "inline": True,
            "fontsize": mpl.rcParams["xtick.labelsize"],
            "fmt": label_format,
        }
        if label_kwargs is not None:
            label_defaults.update(label_kwargs)
        ax.clabel(lines, **label_defaults)
    return lines, regions


def map_linework(
    ax: Axes,
    paths: Iterable[ArrayLike],
    *,
    color: ColorType = INK,
    linewidth: float = 0.45,
    **kwargs: Any,
) -> tuple[Line2D, ...]:
    """Draw solid, marker-free map paths from coordinate arrays."""
    defaults: dict[str, Any] = {
        "color": color,
        "linewidth": linewidth,
        "linestyle": "-",
        "marker": "None",
        "zorder": 1,
    }
    defaults.update(kwargs)
    coordinates_list = tuple(np.asarray(path) for path in paths)
    for coordinates in coordinates_list:
        if coordinates.ndim != 2 or coordinates.shape[1] < 2:
            raise ValueError("Map linework paths require longitude/latitude columns.")
    artists: list[Line2D] = []
    for coordinates in coordinates_list:
        artists.extend(ax.plot(coordinates[:, 0], coordinates[:, 1], **defaults))
    return tuple(artists)


__all__ = [
    "ContourLabelFormat",
    "band",
    "errorbar",
    "map_linework",
    "stairs",
    "stipple",
    "technical_contour",
]
