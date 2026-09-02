"""Add text and leader lines to scientific figures."""

from __future__ import annotations

from typing import Any, Literal

import matplotlib as mpl
from matplotlib.axes import Axes
from matplotlib.legend import Legend
from matplotlib.lines import Line2D
from matplotlib.text import Annotation, Text
from matplotlib.transforms import blended_transform_factory, offset_copy
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

_LEGEND_LOCATIONS: dict[str, tuple[tuple[float, float], str, str]] = {
    "upper left": ((0, 1), "left", "top"),
    "upper center": ((0.5, 1), "center", "top"),
    "upper right": ((1, 1), "right", "top"),
    "center left": ((0, 0.5), "left", "center"),
    "center": ((0.5, 0.5), "center", "center"),
    "center right": ((1, 0.5), "right", "center"),
    "right": ((1, 0.5), "right", "center"),
    "lower left": ((0, 0), "left", "bottom"),
    "lower center": ((0.5, 0), "center", "bottom"),
    "lower right": ((1, 0), "right", "bottom"),
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
    loc: Literal["upper left", "upper right", "lower left", "lower right"] = (
        "upper left"
    ),
    style: Literal["emphasized"] | None = None,
    color: ColorType = INK,
    **kwargs: Any,
) -> Text:
    """Add a technical label with an optional ``emphasized`` style."""
    if loc not in _LOCATIONS:
        choices = ", ".join(_LOCATIONS)
        raise ValueError(
            f"The value is an unknown plate-label location: {loc!r}. "
            f"Use one of these locations: {choices}."
        )
    if style not in (None, "emphasized"):
        raise ValueError("The plate-label style must be 'emphasized' or None.")
    if style == "emphasized":
        text = "   ".join(" ".join(word) for word in text.upper().split())
    xy, ha, va = _LOCATIONS[loc]
    inset_transform = offset_copy(
        ax.transAxes,
        fig=ax.figure,
        x=4 if ha == "left" else -4,
        y=4 if va == "bottom" else -4,
        units="points",
    )
    defaults: dict[str, Any] = _technical_text(color) | {
        "transform": inset_transform,
        "ha": ha,
        "va": va,
        "clip_on": False,
    }
    if style == "emphasized":
        defaults["fontstyle"] = "italic"
    defaults.update(kwargs)
    return ax.text(*xy, text, **defaults)


def legend(ax: Axes, *args: Any, **kwargs: Any) -> Legend:
    """Add a left-aligned legend with frame-aware edge offsets."""
    defaults: dict[str, Any] = {"alignment": "left"}
    loc = kwargs.get("loc")
    has_explicit_anchor = "bbox_to_anchor" in kwargs or "bbox_transform" in kwargs
    if isinstance(loc, str) and loc in _LEGEND_LOCATIONS and not has_explicit_anchor:
        anchor, horizontal, vertical = _LEGEND_LOCATIONS[loc]
        right_open = not ax.spines["right"].get_visible()
        top_open = not ax.spines["top"].get_visible()
        x_offset = 0
        y_offset = 0
        if horizontal == "left":
            x_offset = 6
        elif horizontal == "right":
            x_offset = 4 if right_open else -6
        if vertical == "bottom":
            y_offset = 4
        elif vertical == "top":
            y_offset = 2 if top_open else -4
        defaults.update(
            {
                "bbox_to_anchor": anchor,
                "bbox_transform": offset_copy(
                    ax.transAxes,
                    fig=ax.figure,
                    x=x_offset,
                    y=y_offset,
                    units="points",
                ),
                "borderaxespad": 0,
            }
        )
    defaults.update(kwargs)
    return ax.legend(*args, **defaults)


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
    style: Literal["emphasized"] | None = None,
    color: ColorType = INK,
    **kwargs: Any,
) -> Annotation:
    """Add a technical label with an optional ``emphasized`` style."""
    if style not in (None, "emphasized"):
        raise ValueError("The direct-label style must be 'emphasized' or None.")
    if style == "emphasized":
        text = "   ".join(" ".join(word) for word in text.upper().split())

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
    "legend",
    "overflow_label",
    "plate_label",
    "source_note",
]
