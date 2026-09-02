"""Add text and leader lines to scientific figures."""

from __future__ import annotations

from typing import Any, Literal

import matplotlib as mpl
from matplotlib.axes import Axes
from matplotlib.lines import Line2D
from matplotlib.text import Annotation, Text
from matplotlib.transforms import blended_transform_factory
from matplotlib.typing import ColorType

from ._fonts import TECHNICAL_FONT
from .palette import INK

type LabelLocation = Literal["upper left", "upper right", "lower left", "lower right"]
type DirectLabelStyle = Literal["emphasized"]

_LOCATIONS: dict[LabelLocation, tuple[tuple[float, float], str, str]] = {
    "upper left": ((0.04, 0.96), "left", "top"),
    "upper right": ((0.96, 0.96), "right", "top"),
    "lower left": ((0.04, 0.04), "left", "bottom"),
    "lower right": ((0.96, 0.04), "right", "bottom"),
}


def _technical_text(color: ColorType) -> dict[str, Any]:
    """Return properties shared by technical annotations."""
    return {
        "color": color,
        "fontsize": mpl.rcParams["xtick.labelsize"],
        "fontfamily": TECHNICAL_FONT,
    }


def plate_label(
    ax: Axes,
    text: str,
    *,
    loc: LabelLocation = "upper left",
    color: ColorType = INK,
    **kwargs: Any,
) -> Text:
    """Add a technical label at a fixed position in the axes."""
    if loc not in _LOCATIONS:
        choices = ", ".join(_LOCATIONS)
        raise ValueError(
            f"The value is an unknown plate-label location: {loc!r}. "
            f"Use one of these locations: {choices}."
        )
    xy, ha, va = _LOCATIONS[loc]
    defaults: dict[str, Any] = _technical_text(color) | {
        "transform": ax.transAxes,
        "ha": ha,
        "va": va,
        "clip_on": False,
    }
    defaults.update(kwargs)
    return ax.text(*xy, text, **defaults)


def source_note(
    ax: Axes,
    text: str,
    *,
    offset: float = 33.0,
    color: ColorType = INK,
    **kwargs: Any,
) -> Annotation:
    """Add a prefixed source credit below the lower-left axes corner."""
    if offset < 0:
        raise ValueError("The source-note offset cannot be negative.")

    defaults: dict[str, Any] = _technical_text(color) | {
        "ha": "left",
        "va": "top",
        "clip_on": False,
        "annotation_clip": False,
    }
    defaults.update(kwargs)
    return ax.annotate(
        f"SOURCE: {text}",
        xy=(0, 0),
        xycoords="axes fraction",
        xytext=(0, -offset),
        textcoords="offset points",
        **defaults,
    )


def leader(
    ax: Axes,
    text: str,
    xy: tuple[float, float],
    xytext: tuple[float, float],
    *,
    arrowstyle: str = "-",
    color: ColorType = INK,
    **kwargs: Any,
) -> Annotation:
    """Add technical text and a thin leader line to a data point."""
    defaults: dict[str, Any] = _technical_text(color) | {
        "ha": "left",
        "va": "center",
        "arrowprops": {
            "arrowstyle": arrowstyle,
            "color": color,
            "linewidth": 0.5,
            "shrinkA": 2,
            "shrinkB": 1,
        },
    }
    defaults.update(kwargs)
    return ax.annotate(text, xy=xy, xytext=xytext, **defaults)


def direct_label(
    ax: Axes,
    x: float,
    y: float,
    text: str,
    *,
    offset: tuple[float, float] = (4, 0),
    style: DirectLabelStyle | None = None,
    color: ColorType = INK,
    **kwargs: Any,
) -> Annotation:
    """Add a technical label at a point, with an optional point offset."""
    if style not in (None, "emphasized"):
        raise ValueError("The direct-label style must be 'emphasized' or None.")
    if style == "emphasized":
        text = "   ".join(" ".join(word) for word in text.split())

    defaults: dict[str, Any] = _technical_text(color) | {
        "xytext": offset,
        "textcoords": "offset points",
        "ha": "left",
        "va": "center",
        "annotation_clip": False,
    }
    if style == "emphasized":
        defaults["fontstyle"] = "italic"
    defaults.update(kwargs)
    return ax.annotate(text, xy=(x, y), **defaults)


def overflow_label(
    ax: Axes,
    text: str,
    xspan: tuple[float, float],
    *,
    y: float = 0.965,
    text_x: float | None = None,
    right_x: float | None = None,
    marker_height: float = 0.065,
    color: ColorType = INK,
    **kwargs: Any,
) -> tuple[Annotation, Annotation, tuple[Line2D, Line2D]]:
    """Mark a clipped histogram span with arrows and its true value.

    Horizontal positions use data coordinates. Vertical positions use axes
    coordinates.
    """
    left, right = xspan
    if not left < right:
        raise ValueError("The overflow span must contain increasing edges.")
    if not 0 <= y <= 1:
        raise ValueError("The overflow-label y position must be between 0 and 1.")
    if not 0 < marker_height <= 1:
        raise ValueError("The overflow marker height must be between 0 and 1.")

    xmin, xmax = ax.get_xlim()
    width = xmax - xmin
    label_x = left - 0.37 * width if text_x is None else text_x
    arrow_x = right + 0.09 * width if right_x is None else right_x
    transform = blended_transform_factory(ax.transData, ax.transAxes)
    arrow = {
        "arrowstyle": "->",
        "color": color,
        "linewidth": 0.65,
        "mutation_scale": 7,
        "shrinkA": 2,
        "shrinkB": 1,
    }
    defaults: dict[str, Any] = _technical_text(color) | {
        "xycoords": transform,
        "textcoords": transform,
        "ha": "left",
        "va": "center",
        "arrowprops": arrow,
        "annotation_clip": False,
    }
    defaults.update(kwargs)
    labelled = ax.annotate(text, xy=(left, y), xytext=(label_x, y), **defaults)
    unlabelled = ax.annotate(
        "",
        xy=(right, y),
        xytext=(arrow_x, y),
        xycoords=transform,
        textcoords=transform,
        arrowprops=defaults["arrowprops"],
        annotation_clip=defaults["annotation_clip"],
    )

    half_height = marker_height / 2
    markers = tuple(
        ax.plot(
            [x, x],
            [y - half_height, y + half_height],
            transform=transform,
            color=color,
            linewidth=0.65,
            linestyle=(0, (3, 2)),
            marker="",
            clip_on=False,
        )[0]
        for x in xspan
    )
    return labelled, unlabelled, markers


__all__ = [
    "DirectLabelStyle",
    "LabelLocation",
    "direct_label",
    "leader",
    "overflow_label",
    "plate_label",
    "source_note",
]
