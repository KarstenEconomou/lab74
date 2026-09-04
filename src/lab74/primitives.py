"""Draw effects that Matplotlib style parameters cannot define."""

from collections.abc import Callable, Iterable, Mapping, Sequence
from itertools import pairwise
from math import isfinite
from typing import Any, Final, Literal

import matplotlib as mpl
import numpy as np
from matplotlib.axes import Axes
from matplotlib.collections import PathCollection, PolyCollection
from matplotlib.container import BarContainer, ErrorbarContainer
from matplotlib.contour import QuadContourSet
from matplotlib.lines import Line2D
from matplotlib.patches import StepPatch
from matplotlib.path import Path
from matplotlib.ticker import NullLocator
from matplotlib.typing import ColorType
from numpy.typing import ArrayLike

from .palette import INK, MONOCHROME_LINE_COLORS, PAPER
from .sequences import CONTOUR_HATCHES, bar_styles

type ContourLabelFormat = str | Mapping[float, str] | Callable[[float], str]
type BarOrientation = Literal["vertical", "horizontal"]

_HAIRLINE_WIDTH: Final = 0.45
_OUTLINE_WIDTH: Final = 0.5
_CONTOUR_WIDTH: Final = 0.55
_ACCENT_CONTOUR_WIDTH: Final = 0.9
_STIPPLE_ATTEMPT_LIMIT: Final = 100


def _active_accent() -> ColorType | None:
    """Return the active accent, or none for a monochrome cycle."""
    colors = mpl.rcParams["axes.prop_cycle"].by_key().get("color", [])
    if not colors:
        return None
    is_monochrome = any(
        mpl.colors.same_color(colors[0], color)
        for color in (INK, MONOCHROME_LINE_COLORS[0])
    )
    return None if is_monochrome else colors[0]


def _active_color() -> ColorType:
    """Return the active accent or ink for a monochrome cycle."""
    return _active_accent() or INK


def _bar_positions(
    count: int,
    positions: ArrayLike | None,
    *,
    kind: str,
) -> np.ndarray:
    """Return validated category positions for a bar plot."""
    resolved = (
        np.arange(count, dtype=float)
        if positions is None
        else np.asarray(positions, dtype=float)
    )
    if resolved.ndim != 1 or len(resolved) != count:
        raise ValueError(f"{kind} positions must match the number of bars or groups.")
    return resolved


def _validate_bar_options(
    width: float,
    orientation: BarOrientation,
    *,
    kind: str,
) -> None:
    """Validate options shared by the two bar helpers."""
    if not isfinite(width) or width <= 0:
        raise ValueError(f"The {kind.lower()} width must be positive and finite.")
    if orientation not in ("vertical", "horizontal"):
        raise ValueError("The bar orientation must be 'vertical' or 'horizontal'.")


def _format_bar_categories(
    ax: Axes,
    positions: np.ndarray,
    categories: Sequence[str] | None,
    orientation: BarOrientation,
) -> None:
    """Label the category axis and suppress its tick marks."""
    category_axis = ax.xaxis if orientation == "vertical" else ax.yaxis
    if orientation == "vertical":
        ax.set_xticks(positions, categories)
        ax.tick_params(axis="x", which="both", length=0)
    else:
        ax.set_yticks(positions, categories)
        ax.tick_params(axis="y", which="both", length=0)
    category_axis.set_minor_locator(NullLocator())


def _bar_defaults(
    style: Mapping[str, Any], kwargs: Mapping[str, Any]
) -> dict[str, Any]:
    """Combine library bar properties with explicit Matplotlib overrides."""
    defaults: dict[str, Any] = {
        "edgecolor": INK,
        "linewidth": mpl.rcParams["patch.linewidth"],
        **style,
    }
    defaults.update(kwargs)
    return defaults


def grouped_bar(
    ax: Axes,
    values: ArrayLike,
    *,
    labels: Sequence[str] | None = None,
    categories: Sequence[str] | None = None,
    positions: ArrayLike | None = None,
    width: float = 0.8,
    orientation: BarOrientation = "vertical",
    **kwargs: Any,
) -> tuple[BarContainer, ...]:
    """Draw grouped bars with graduated fills and an unticked category axis."""
    data = np.asarray(values, dtype=float)
    if data.ndim != 2 or not all(data.shape):
        raise ValueError("Grouped-bar values must be a non-empty 2D array.")
    _validate_bar_options(width, orientation, kind="Grouped-bar")

    series_count, group_count = data.shape
    group_positions = _bar_positions(group_count, positions, kind="Grouped-bar")
    if labels is not None and len(labels) != series_count:
        raise ValueError("Grouped-bar labels must match the number of series.")
    if categories is not None and len(categories) != group_count:
        raise ValueError("Grouped-bar categories must match the number of groups.")

    styles = bar_styles(_active_accent())
    bar_width = width / series_count
    offsets = (np.arange(series_count) - (series_count - 1) / 2) * bar_width
    containers: list[BarContainer] = []
    for index, (series, offset) in enumerate(zip(data, offsets, strict=True)):
        style = styles[index % len(styles)]
        defaults = _bar_defaults(style, kwargs)
        if labels is not None:
            defaults["label"] = labels[index]
        centers = group_positions + offset
        if orientation == "vertical":
            container = ax.bar(centers, series, bar_width, **defaults)
        else:
            container = ax.barh(centers, series, bar_width, **defaults)
        containers.append(container)

    _format_bar_categories(ax, group_positions, categories, orientation)
    return tuple(containers)


def separated_bar(
    ax: Axes,
    values: ArrayLike,
    *,
    categories: Sequence[str] | None = None,
    positions: ArrayLike | None = None,
    width: float = 0.8,
    orientation: BarOrientation = "vertical",
    **kwargs: Any,
) -> BarContainer:
    """Draw separate bars, advancing the active bar style for every bar."""
    data = np.asarray(values, dtype=float)
    if data.ndim != 1 or not len(data):
        raise ValueError("Separated-bar values must be a non-empty 1D array.")
    _validate_bar_options(width, orientation, kind="Separated-bar")
    bar_positions = _bar_positions(len(data), positions, kind="Separated-bar")
    if categories is not None and len(categories) != len(data):
        raise ValueError("Separated-bar categories must match the number of bars.")

    sequence = bar_styles(_active_accent())
    styles = [sequence[index % len(sequence)] for index in range(len(data))]
    defaults = _bar_defaults(
        {
            "facecolor": [style["facecolor"] for style in styles],
            "hatch": [style["hatch"] for style in styles],
        },
        kwargs,
    )
    if orientation == "vertical":
        container = ax.bar(bar_positions, data, width, **defaults)
    else:
        container = ax.barh(bar_positions, data, width, **defaults)
    _format_bar_categories(ax, bar_positions, categories, orientation)
    return container


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
        "elinewidth": _HAIRLINE_WIDTH,
        "capsize": mpl.rcParams["errorbar.capsize"],
        "capthick": _HAIRLINE_WIDTH,
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
    """Draw a paper-filled interval outlined in the active accent or ink."""
    edge = _active_color() if color is None else color
    defaults: dict[str, Any] = {
        "facecolor": PAPER,
        "edgecolor": edge,
        "linewidth": _OUTLINE_WIDTH,
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
    edge = _active_color() if color is None else color
    stroke = float(mpl.rcParams["patch.linewidth"]) if linewidth is None else linewidth
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

    The dot count follows the polygon area on the page, so set the final axes
    limits and figure size before this call.
    """
    data_vertices = np.asarray(vertices, dtype=float)
    if data_vertices.ndim != 2 or data_vertices.shape[1] != 2 or len(data_vertices) < 3:
        raise ValueError("The vertices must have shape (n, 2) and at least 3 points.")
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
        while remaining and attempts < _STIPPLE_ATTEMPT_LIMIT:
            candidates = rng.uniform(low, high, size=(max(remaining * 3, 64), 2))
            inside = candidates[path.contains_points(candidates)]
            if len(inside):
                take = inside[:remaining]
                accepted.append(take)
                remaining -= len(take)
            attempts += 1
        if remaining:
            raise RuntimeError("Sampling the stipple polygon did not converge.")
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
    accent_level: float | None = None,
    labels: bool = False,
    label_format: ContourLabelFormat = "%g",
    label_kwargs: Mapping[str, Any] | None = None,
    hatches: Sequence[str] | None = None,
    **kwargs: Any,
) -> tuple[QuadContourSet, QuadContourSet | None]:
    """Draw explicit contour levels and optional hatched regions.

    One level may be drawn in the active accent at a heavier weight, in
    keeping with the single-accent style.
    """
    values = list(levels)
    if len(values) < 2:
        raise ValueError("Technical contours require at least 2 explicit levels.")
    if not all(isfinite(value) for value in values):
        raise ValueError("Technical contour levels must be finite.")
    if any(first >= second for first, second in pairwise(values)):
        raise ValueError("Technical contour levels must be in increasing order.")
    if accent_level is not None and accent_level not in values:
        raise ValueError("The accented contour level must be present in levels.")
    accent = _active_color()
    is_accented = [level == accent_level for level in values]
    colors = [accent if accented else INK for accented in is_accented]
    linewidths = [
        _ACCENT_CONTOUR_WIDTH if accented else _CONTOUR_WIDTH
        for accented in is_accented
    ]

    regions: QuadContourSet | None = None
    if filled:
        region_hatches = list(CONTOUR_HATCHES if hatches is None else hatches)
        if not region_hatches:
            raise ValueError("Hatches must contain at least 1 pattern.")
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
    linewidth: float = _HAIRLINE_WIDTH,
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
    "BarOrientation",
    "ContourLabelFormat",
    "band",
    "errorbar",
    "grouped_bar",
    "map_linework",
    "separated_bar",
    "stairs",
    "stipple",
    "technical_contour",
]
