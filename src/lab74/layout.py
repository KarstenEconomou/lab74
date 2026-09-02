"""Format ticks and compact groups of axes."""

from __future__ import annotations

from collections.abc import Iterable
from math import isfinite
from typing import Literal, TypedDict

from matplotlib.axes import Axes
from matplotlib.lines import Line2D
from matplotlib.ticker import FixedLocator, FuncFormatter
from matplotlib.typing import ColorType

from .palette import RULE

type AxesInput = Axes | Iterable[AxesInput]
type FrameStyle = Literal["open", "closed"]
type MultipanelMode = Literal["framed", "open"]
type TickAxis = Literal["both", "x", "y"]
type TickStyle = Literal["default", "cross"]


class _MultipanelValues(TypedDict):
    hspace: float
    wspace: float


class _TickValues(TypedDict):
    direction: Literal["in", "inout"]
    major_length: float
    major_width: float
    minor_length: float
    minor_width: float


_MULTIPANEL_MODES: dict[MultipanelMode, _MultipanelValues] = {
    "framed": {"hspace": 0.0, "wspace": 0.0},
    "open": {"hspace": 0.06, "wspace": 0.06},
}

_TICK_STYLES: dict[TickStyle, _TickValues] = {
    "default": {
        "direction": "in",
        "major_length": 5.0,
        "major_width": 0.55,
        "minor_length": 3.0,
        "minor_width": 0.45,
    },
    "cross": {
        "direction": "inout",
        "major_length": 8.0,
        "major_width": 0.7,
        "minor_length": 1.8,
        "minor_width": 0.5,
    },
}


def _axes_tuple(axes: AxesInput) -> tuple[Axes, ...]:
    """Return one flat tuple from a nested axes container."""
    flattened: list[Axes] = []
    active: set[int] = set()

    def visit(value: object) -> None:
        if isinstance(value, Axes):
            flattened.append(value)
            return
        if isinstance(value, (str, bytes)) or not isinstance(value, Iterable):
            raise TypeError("Axes must be an Axes object or a nested iterable of axes.")

        identity = id(value)
        if identity in active:
            raise ValueError("The axes container cannot contain itself.")
        active.add(identity)
        try:
            for item in value:
                visit(item)
        finally:
            active.remove(identity)

    visit(axes)
    return tuple(flattened)


def format_ticks(
    axes: AxesInput,
    *,
    style: Literal["default", "cross"] = "default",
    axis: Literal["both", "x", "y"] = "both",
    major_length: float | None = None,
    minor_length: float | None = None,
    major_width: float | None = None,
    minor_width: float | None = None,
) -> tuple[Axes, ...]:
    """Apply ``default`` or ``cross`` ticks to ``both``, ``x``, or ``y``."""
    if style not in _TICK_STYLES:
        choices = ", ".join(_TICK_STYLES)
        raise ValueError(
            f"The value is an unknown tick style: {style!r}. "
            f"Use one of these styles: {choices}."
        )
    if axis not in ("both", "x", "y"):
        raise ValueError("The tick axis must be 'both', 'x', or 'y'.")

    panels = _axes_tuple(axes)
    if not panels:
        raise ValueError("format_ticks requires at least one Axes object.")

    values = _TICK_STYLES[style]
    resolved_major_length = (
        values["major_length"] if major_length is None else major_length
    )
    resolved_minor_length = (
        values["minor_length"] if minor_length is None else minor_length
    )
    resolved_major_width = values["major_width"] if major_width is None else major_width
    resolved_minor_width = values["minor_width"] if minor_width is None else minor_width
    for ax in panels:
        ax.tick_params(
            axis=axis,
            which="major",
            direction=values["direction"],
            length=resolved_major_length,
            width=resolved_major_width,
        )
        ax.tick_params(
            axis=axis,
            which="minor",
            direction=values["direction"],
            length=resolved_minor_length,
            width=resolved_minor_width,
        )
    return panels


def format_frame(
    axes: AxesInput,
    *,
    style: Literal["open", "closed"] = "closed",
) -> tuple[Axes, ...]:
    """Apply an ``open`` or ``closed`` frame to one or more axes."""
    if style not in ("open", "closed"):
        raise ValueError("The frame style must be 'open' or 'closed'.")
    panels = _axes_tuple(axes)
    if not panels:
        raise ValueError("format_frame requires at least one Axes object.")
    visible = style == "closed"
    for ax in panels:
        ax.spines["top"].set_visible(visible)
        ax.spines["right"].set_visible(visible)
        ax.tick_params(which="both", top=visible, right=visible)
    return panels


def format_graticule(
    ax: Axes,
    longitudes: Iterable[float],
    latitudes: Iterable[float],
    *,
    draw_lines: bool = True,
    color: ColorType = RULE,
    linewidth: float = 0.3,
) -> tuple[tuple[Line2D, ...], tuple[Line2D, ...]]:
    """Draw a graticule with unsigned whole-degree perimeter labels."""
    longitude_values = tuple(float(value) for value in longitudes)
    latitude_values = tuple(float(value) for value in latitudes)
    if not longitude_values or not latitude_values:
        raise ValueError("A graticule requires longitude and latitude values.")
    if not all(isfinite(value) for value in longitude_values + latitude_values):
        raise ValueError("Graticule coordinates must be finite.")

    longitude_lines = tuple(
        ax.axvline(
            value,
            color=color,
            linewidth=linewidth,
            linestyle="-",
            marker="None",
            zorder=0,
        )
        for value in longitude_values
        if draw_lines
    )
    latitude_lines = tuple(
        ax.axhline(
            value,
            color=color,
            linewidth=linewidth,
            linestyle="-",
            marker="None",
            zorder=0,
        )
        for value in latitude_values
        if draw_lines
    )
    degree_label = FuncFormatter(lambda value, _: f"{abs(value):.0f}°")
    ax.xaxis.set_major_locator(FixedLocator(longitude_values))
    ax.yaxis.set_major_locator(FixedLocator(latitude_values))
    ax.xaxis.set_major_formatter(degree_label)
    ax.yaxis.set_major_formatter(degree_label)
    ax.tick_params(which="both", top=False, right=False, length=0, pad=4)
    ax.minorticks_off()
    ax.set(xlabel="", ylabel="")
    return longitude_lines, latitude_lines


def format_multipanel(
    axes: AxesInput,
    *,
    mode: Literal["framed", "open"] = "framed",
    tick_style: Literal["default", "cross"] = "default",
    hspace: float | None = None,
    wspace: float | None = None,
) -> tuple[Axes, ...]:
    """Apply a ``framed`` or ``open`` layout and a named tick style."""
    if mode not in _MULTIPANEL_MODES:
        choices = ", ".join(_MULTIPANEL_MODES)
        raise ValueError(
            f"The value is an unknown multipanel mode: {mode!r}. "
            f"Use one of these modes: {choices}."
        )
    if tick_style not in _TICK_STYLES:
        choices = ", ".join(_TICK_STYLES)
        raise ValueError(
            f"The value is an unknown tick style: {tick_style!r}. "
            f"Use one of these styles: {choices}."
        )

    panels = _axes_tuple(axes)
    if not panels:
        raise ValueError("format_multipanel requires at least one Axes object.")

    figure = panels[0].figure
    if any(ax.figure is not figure for ax in panels):
        raise ValueError("All multipanel axes must belong to the same figure.")

    defaults = _MULTIPANEL_MODES[mode]
    resolved_hspace = defaults["hspace"] if hspace is None else hspace
    resolved_wspace = defaults["wspace"] if wspace is None else wspace
    figure.subplots_adjust(hspace=resolved_hspace, wspace=resolved_wspace)

    format_frame(panels, style="closed" if mode == "framed" else "open")
    format_ticks(panels, style=tick_style)
    return panels


__all__ = [
    "AxesInput",
    "FrameStyle",
    "MultipanelMode",
    "TickAxis",
    "TickStyle",
    "format_frame",
    "format_graticule",
    "format_multipanel",
    "format_ticks",
]
