"""Add text and leader lines to scientific figures."""

from collections.abc import Sequence
from itertools import pairwise
from math import isfinite, sqrt
from string import ascii_lowercase
from typing import Any, Final, Literal

import matplotlib as mpl
import matplotlib.patheffects as path_effects
from matplotlib import font_manager
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from matplotlib.legend import Legend
from matplotlib.lines import Line2D
from matplotlib.text import Annotation, Text
from matplotlib.transforms import Affine2D, blended_transform_factory, offset_copy
from matplotlib.typing import ColorType

from ._fonts import FACES, MONO_FONT, FontFace, font_for, font_size_points
from .layout import AxesInput, _axes_tuple
from .palette import INK, PAPER

type LabelLocation = Literal["upper left", "upper right", "lower left", "lower right"]
type DirectLabelStyle = Literal["emphasized"]
type AnnotationFace = FontFace
type RegionAxis = Literal["x", "y"]

_DEFAULT_ANNOTATION_FACE: Final[AnnotationFace] = "mono"
_EMPHASIS_STROKE: Final = 0.2
_LEADER_WIDTH: Final = 0.5
_RULE_WIDTH: Final = 0.65

_ANNOTATION_FACE: AnnotationFace | None = None
_ANNOTATION_SIZE_OFFSET = 0.0

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


def _emphasize(text: str) -> str:
    """Return uppercase, letter-spaced text for the ``emphasized`` style."""
    return "   ".join(" ".join(word) for word in text.upper().split())


def _validate_label_style(style: DirectLabelStyle | None, noun: str) -> None:
    """Reject a label style other than ``emphasized`` or none."""
    if style not in (None, "emphasized"):
        raise ValueError(f"The {noun} style must be 'emphasized' or None.")


def _leader_arrowprops(color: ColorType, *, shrink_a: float = 2) -> dict[str, Any]:
    """Return the properties of a thin leader line drawn to a data point."""
    return {
        "arrowstyle": "-",
        "color": color,
        "linewidth": _LEADER_WIDTH,
        "shrinkA": shrink_a,
        "shrinkB": 1,
    }


def _configure_annotation_style(
    *, size_offset: float = 0, face: AnnotationFace | None = None
) -> None:
    """Set the annotation defaults used after applying the Matplotlib style."""
    if face is not None and face not in FACES:
        choices = ", ".join(repr(name) for name in FACES)
        raise ValueError(f"The annotation face must be {choices}, or None.")
    resolved_offset = float(size_offset)
    if not isfinite(resolved_offset):
        raise ValueError("The annotation size offset must be finite.")
    legend_size = font_size_points(mpl.rcParams["legend.fontsize"])
    if legend_size + resolved_offset <= 0:
        raise ValueError("The annotation size offset produces a nonpositive size.")

    # The annotation defaults are process-wide state, like the rcParams that
    # use() sets alongside them.
    global _ANNOTATION_FACE, _ANNOTATION_SIZE_OFFSET  # noqa: PLW0603
    _ANNOTATION_FACE = face
    _ANNOTATION_SIZE_OFFSET = resolved_offset
    mpl.rcParams["legend.fontsize"] = legend_size + resolved_offset


def _resolved_annotation_face(face: AnnotationFace | None) -> AnnotationFace | None:
    return _ANNOTATION_FACE if face is None else face


def _technical_text(
    color: ColorType, face: AnnotationFace | None = None
) -> dict[str, Any]:
    """Return properties shared by technical annotations."""
    base_size = font_size_points(mpl.rcParams["xtick.labelsize"])
    resolved_face = _resolved_annotation_face(face) or _DEFAULT_ANNOTATION_FACE
    return {
        "color": color,
        "fontsize": base_size + _ANNOTATION_SIZE_OFFSET,
        "fontfamily": font_for(resolved_face),
    }


def _background_properties(background: bool) -> dict[str, Any]:
    """Return an opaque, borderless paper backing when requested."""
    if not background:
        return {}
    return {
        "bbox": {
            "boxstyle": "square,pad=0.01",
            "facecolor": PAPER,
            "edgecolor": "none",
        }
    }


def title(
    figure: Figure,
    text: str,
    subtitle: str | None = None,
    *,
    y: float = 0.975,
    line_offset: float = 12.0,
    color: ColorType = INK,
    fontsize: float | str | None = None,
) -> tuple[Text, ...]:
    """Add a centered figure title and optional subtitle."""
    if not isinstance(figure, Figure):
        raise TypeError("The title target must be a Figure.")
    if not isinstance(text, str) or not (subtitle is None or isinstance(subtitle, str)):
        raise TypeError("Title and subtitle must be strings or None.")
    if not isfinite(y) or not 0 <= y <= 1:
        raise ValueError("The title y position must be between zero and one.")
    if not isfinite(line_offset) or line_offset <= 0:
        raise ValueError("The title line offset must be positive and finite.")
    try:
        mpl.colors.to_rgba(color)
    except ValueError as exc:
        raise ValueError("The title color must be valid.") from exc
    resolved_size = font_size_points(
        mpl.rcParams["axes.titlesize"] if fontsize is None else fontsize
    )

    second_line = offset_copy(
        figure.transFigure, fig=figure, y=-line_offset, units="points"
    )
    defaults: dict[str, Any] = {
        "ha": "center",
        "va": "top",
        "clip_on": False,
        "color": color,
        "fontsize": resolved_size,
        "fontfamily": MONO_FONT,
    }
    title_defaults: dict[str, Any] = defaults | {
        "fontweight": "medium",
        "path_effects": [
            path_effects.withStroke(linewidth=_EMPHASIS_STROKE, foreground=color)
        ],
    }
    artists = [
        figure.text(0.5, y, text, transform=figure.transFigure, **title_defaults)
    ]
    if subtitle is not None:
        artists.append(figure.text(0.5, y, subtitle, transform=second_line, **defaults))
    return tuple(artists)


def plate_label(
    ax: Axes,
    text: str,
    *,
    loc: LabelLocation = "upper left",
    style: DirectLabelStyle | None = None,
    background: bool = False,
    face: AnnotationFace | None = None,
    color: ColorType = INK,
    **kwargs: Any,
) -> Text:
    """Add a technical label with an optional ``emphasized`` style."""
    if loc not in _LOCATIONS:
        choices = ", ".join(_LOCATIONS)
        raise ValueError(
            f"Unknown plate-label location: {loc!r}. "
            f"Use one of these locations: {choices}."
        )
    _validate_label_style(style, "plate-label")
    if style == "emphasized":
        text = _emphasize(text)
    xy, ha, va = _LOCATIONS[loc]
    inset_transform = offset_copy(
        ax.transAxes,
        fig=ax.get_figure(root=True),
        x=4 if ha == "left" else -4,
        y=4 if va == "bottom" else -4,
        units="points",
    )
    defaults: dict[str, Any] = (
        _technical_text(color, face)
        | _background_properties(background)
        | {
            "transform": inset_transform,
            "ha": ha,
            "va": va,
            "clip_on": False,
        }
    )
    if style == "emphasized":
        defaults["fontstyle"] = "italic"
    defaults.update(kwargs)
    return ax.text(*xy, text, **defaults)


def panel_labels(
    axes: AxesInput,
    *,
    labels: Sequence[str] | None = None,
    loc: LabelLocation = "upper left",
    style: DirectLabelStyle | None = None,
    background: bool = False,
    face: AnnotationFace | None = None,
    color: ColorType = INK,
    **kwargs: Any,
) -> tuple[Text, ...]:
    """Letter a group of panels ``(a)``, ``(b)``, ... in reading order."""
    panels = _axes_tuple(axes)
    if not panels:
        raise ValueError("panel_labels requires at least 1 Axes object.")
    if labels is None:
        if len(panels) > len(ascii_lowercase):
            raise ValueError("Default panel lettering covers at most 26 panels.")
        texts = tuple(f"({letter})" for letter in ascii_lowercase[: len(panels)])
    else:
        texts = tuple(labels)
        if len(texts) != len(panels):
            raise ValueError("Panel labels must match the number of panels.")
    return tuple(
        plate_label(
            ax,
            text,
            loc=loc,
            style=style,
            background=background,
            face=face,
            color=color,
            **kwargs,
        )
        for ax, text in zip(panels, texts, strict=True)
    )


def legend(
    ax: Axes,
    *args: Any,
    background: bool = False,
    face: AnnotationFace | None = None,
    offset: tuple[float, float] = (0, 0),
    **kwargs: Any,
) -> Legend:
    """Add a left-aligned legend with frame-aware and freeform point offsets."""
    if len(offset) != 2 or not all(isfinite(value) for value in offset):
        raise ValueError("The legend offset must contain 2 finite values.")
    user_x_offset, user_y_offset = offset
    defaults: dict[str, Any] = {"alignment": "left"}
    resolved_face = _resolved_annotation_face(face)
    if resolved_face is not None:
        font = font_for(resolved_face)
        size = font_size_points(mpl.rcParams["legend.fontsize"])
        defaults.update(
            {
                "prop": font_manager.FontProperties(family=font, size=size),
                "title_fontproperties": font_manager.FontProperties(
                    family=font, size=size
                ),
            }
        )
    if background:
        defaults.update(
            {
                "frameon": True,
                "facecolor": PAPER,
                "edgecolor": "none",
                "framealpha": 1.0,
                "borderpad": 0.01,
            }
        )
    loc = kwargs.get("loc")
    has_explicit_anchor = "bbox_to_anchor" in kwargs or "bbox_transform" in kwargs
    offset_applied = False
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
        if background:
            if horizontal == "left":
                x_offset += 2
            elif horizontal == "right":
                x_offset -= 2
            if vertical == "bottom":
                y_offset += 2
            elif vertical == "top":
                y_offset -= 2
        x_offset += user_x_offset
        y_offset += user_y_offset
        offset_applied = True
        defaults.update(
            {
                "bbox_to_anchor": anchor,
                "bbox_transform": offset_copy(
                    ax.transAxes,
                    fig=ax.get_figure(root=True),
                    x=x_offset,
                    y=y_offset,
                    units="points",
                ),
                "borderaxespad": 0,
            }
        )
    elif has_explicit_anchor and offset != (0, 0):
        base_transform = kwargs.get("bbox_transform", ax.transAxes)
        kwargs["bbox_transform"] = offset_copy(
            base_transform,
            fig=ax.get_figure(root=True),
            x=user_x_offset,
            y=user_y_offset,
            units="points",
        )
        offset_applied = True
    defaults.update(kwargs)
    result = ax.legend(*args, **defaults)
    if offset != (0, 0) and not offset_applied:
        figure = ax.get_figure(root=True)
        assert figure is not None
        translation = Affine2D().translate(
            user_x_offset * figure.dpi / 72,
            user_y_offset * figure.dpi / 72,
        )
        result.set_bbox_to_anchor(result.get_bbox_to_anchor(), transform=translation)
    return result


def source_note(
    ax: Axes,
    text: str,
    *,
    offset: float = 33.0,
    color: ColorType = INK,
    background: bool = False,
    face: AnnotationFace | None = None,
    **kwargs: Any,
) -> Annotation:
    """Add a prefixed source credit below the lower-left axes corner."""
    if offset < 0:
        raise ValueError("The source-note offset cannot be negative.")

    defaults: dict[str, Any] = (
        _technical_text(color, face)
        | _background_properties(background)
        | {
            "ha": "left",
            "va": "top",
            "clip_on": False,
            "annotation_clip": False,
        }
    )
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
    background: bool = False,
    face: AnnotationFace | None = None,
    **kwargs: Any,
) -> Annotation:
    """Add technical text and a thin leader line to a data point."""
    defaults: dict[str, Any] = (
        _technical_text(color, face)
        | _background_properties(background)
        | {
            "ha": "left",
            "va": "center",
            "arrowprops": _leader_arrowprops(color) | {"arrowstyle": arrowstyle},
        }
    )
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
    background: bool = False,
    face: AnnotationFace | None = None,
    color: ColorType = INK,
    **kwargs: Any,
) -> Annotation:
    """Add a technical label with an optional ``emphasized`` style."""
    _validate_label_style(style, "direct-label")
    if style == "emphasized":
        text = _emphasize(text)

    defaults: dict[str, Any] = (
        _technical_text(color, face)
        | _background_properties(background)
        | {
            "xytext": offset,
            "textcoords": "offset points",
            "ha": "left",
            "va": "center",
            "annotation_clip": False,
        }
    )
    if style == "emphasized":
        defaults["fontstyle"] = "italic"
    defaults.update(kwargs)
    return ax.annotate(text, xy=(x, y), **defaults)


def marked_point(
    ax: Axes,
    x: float,
    y: float,
    text: str,
    *,
    offset: tuple[float, float] = (4, 0),
    marker: str = "o",
    style: DirectLabelStyle | None = None,
    background: bool = False,
    face: AnnotationFace | None = None,
    leader_line: bool = False,
    color: ColorType = INK,
    **kwargs: Any,
) -> tuple[Line2D, Annotation]:
    """Mark one labelled point without adding a plotted series.

    The marker is excluded from the legend, so operating points can be
    identified on a curve that already carries its own label. Set
    ``leader_line`` to join the label to the marker with a thin rule.
    """
    if not isfinite(x) or not isfinite(y):
        raise ValueError("A marked point must have finite coordinates.")

    (point,) = ax.plot(
        [x],
        [y],
        linestyle="none",
        marker=marker,
        color=color,
        markerfacecolor=PAPER,
        label="_nolegend_",
        clip_on=False,
    )
    label_defaults: dict[str, Any] = {}
    if leader_line:
        label_defaults["arrowprops"] = _leader_arrowprops(color, shrink_a=1)
    label_defaults.update(kwargs)
    label = direct_label(
        ax,
        x,
        y,
        text,
        offset=offset,
        style=style,
        background=background,
        face=face,
        color=color,
        **label_defaults,
    )
    return point, label


def _span_center(left: float, right: float, logarithmic: bool) -> float:
    """Return the middle of a span on a linear or logarithmic scale."""
    if logarithmic:
        return sqrt(left * right)
    return (left + right) / 2


def region_labels(
    ax: Axes,
    boundaries: Sequence[float],
    labels: Sequence[str],
    *,
    axis: RegionAxis = "x",
    position: float = 0.94,
    rules: bool = True,
    style: DirectLabelStyle | None = None,
    background: bool = False,
    face: AnnotationFace | None = None,
    leader_offset: tuple[float, float] = (16, 14),
    color: ColorType = INK,
    **kwargs: Any,
) -> tuple[tuple[Line2D, ...], tuple[Annotation, ...]]:
    """Name the regions between ``boundaries`` and rule their interior edges.

    Positions along ``axis`` use data coordinates; ``position`` places the
    labels across the other axis in axes coordinates. A label that is wider
    than its region is drawn outside it on a leader line instead.
    """
    if axis not in ("x", "y"):
        raise ValueError("The region axis must be 'x' or 'y'.")
    _validate_label_style(style, "region-label")
    if not isfinite(position) or not 0 <= position <= 1:
        raise ValueError("The region-label position must be between 0 and 1.")
    if len(leader_offset) != 2 or not all(
        isfinite(value) and value >= 0 for value in leader_offset
    ):
        raise ValueError(
            "The region-label leader offset must contain 2 finite, nonnegative values."
        )
    horizontal_offset, vertical_offset = leader_offset

    edges = tuple(float(value) for value in boundaries)
    names = tuple(labels)
    if len(edges) != len(names) + 1:
        raise ValueError("Region boundaries must contain 1 more value than labels.")
    if not names:
        raise ValueError("region_labels requires at least 1 region.")
    if not all(isfinite(value) for value in edges):
        raise ValueError("Region boundaries must be finite.")
    if any(later <= earlier for earlier, later in pairwise(edges)):
        raise ValueError("Region boundaries must increase.")

    logarithmic = (ax.get_xscale() if axis == "x" else ax.get_yscale()) == "log"
    if logarithmic and edges[0] <= 0:
        raise ValueError("Region boundaries on a logarithmic axis must be positive.")

    transform = (
        blended_transform_factory(ax.transData, ax.transAxes)
        if axis == "x"
        else blended_transform_factory(ax.transAxes, ax.transData)
    )

    def at(value: float) -> tuple[float, float]:
        return (value, position) if axis == "x" else (position, value)

    def rule(edge: float) -> Line2D:
        across = [edge, edge], [0, 1]
        return ax.plot(
            *(across if axis == "x" else across[::-1]),
            transform=transform,
            color=color,
            linewidth=_RULE_WIDTH,
            linestyle=(0, (3, 2)),
            marker="",
            clip_on=False,
            zorder=0.8,
        )[0]

    marks = tuple(rule(edge) for edge in edges[1:-1]) if rules else ()

    defaults: dict[str, Any] = (
        _technical_text(color, face)
        | _background_properties(background)
        | {
            "xycoords": transform,
            "ha": "center",
            "va": "center",
            "annotation_clip": False,
        }
    )
    if style == "emphasized":
        defaults["fontstyle"] = "italic"
    defaults.update(kwargs)

    placed: list[Annotation] = []
    for left, right, label in zip(edges[:-1], edges[1:], names, strict=True):
        name = _emphasize(label) if style == "emphasized" else label
        center = _span_center(left, right, logarithmic)
        annotation = ax.annotate(name, xy=at(center), **defaults)
        span = abs(
            transform.transform(at(right))[0 if axis == "x" else 1]
            - transform.transform(at(left))[0 if axis == "x" else 1]
        )
        extent = annotation.get_window_extent()
        needed = extent.width if axis == "x" else extent.height
        if needed <= span:
            placed.append(annotation)
            continue

        annotation.remove()
        inboard = transform.transform(at(center))
        axes_fraction = ax.transAxes.inverted().transform(inboard)
        toward_start = axes_fraction[0 if axis == "x" else 1] > 0.5
        callout: dict[str, Any] = defaults | {
            "textcoords": "offset points",
            "ha": "right" if toward_start else "left",
            "va": "center",
            "arrowprops": _leader_arrowprops(color),
        }
        away = -vertical_offset if position > 0.5 else vertical_offset
        placed.append(
            ax.annotate(
                name,
                xy=at(center),
                xytext=(
                    -horizontal_offset if toward_start else horizontal_offset,
                    away,
                ),
                **callout,
            )
        )
    return marks, tuple(placed)


def overflow_label(
    ax: Axes,
    text: str,
    xspan: tuple[float, float],
    *,
    y: float = 0.965,
    label_x: float | None = None,
    arrow_x: float | None = None,
    marker_height: float = 0.065,
    color: ColorType = INK,
    background: bool = False,
    face: AnnotationFace | None = None,
    **kwargs: Any,
) -> tuple[Annotation, Annotation, tuple[Line2D, Line2D]]:
    """Mark a clipped histogram span with arrows and its true value.

    ``label_x`` places the text and its inbound arrow to the left of the span,
    and ``arrow_x`` places the tail of the outbound arrow to its right. Both
    default to a position derived from the current x limits. Horizontal
    positions use data coordinates; vertical positions use axes coordinates.
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
    label_position = left - 0.37 * width if label_x is None else label_x
    arrow_position = right + 0.09 * width if arrow_x is None else arrow_x
    transform = blended_transform_factory(ax.transData, ax.transAxes)
    arrow = {
        "arrowstyle": "->",
        "color": color,
        "linewidth": _RULE_WIDTH,
        "mutation_scale": 7,
        "shrinkA": 2,
        "shrinkB": 1,
    }
    defaults: dict[str, Any] = (
        _technical_text(color, face)
        | _background_properties(background)
        | {
            "xycoords": transform,
            "textcoords": transform,
            "ha": "left",
            "va": "center",
            "arrowprops": arrow,
            "annotation_clip": False,
        }
    )
    defaults.update(kwargs)
    labelled = ax.annotate(text, xy=(left, y), xytext=(label_position, y), **defaults)
    unlabelled = ax.annotate(
        "",
        xy=(right, y),
        xytext=(arrow_position, y),
        xycoords=transform,
        textcoords=transform,
        arrowprops=defaults["arrowprops"],
        annotation_clip=defaults["annotation_clip"],
    )

    half_height = marker_height / 2

    def edge_marker(x: float) -> Line2D:
        return ax.plot(
            [x, x],
            [y - half_height, y + half_height],
            transform=transform,
            color=color,
            linewidth=_RULE_WIDTH,
            linestyle=(0, (3, 2)),
            marker="",
            clip_on=False,
        )[0]

    markers = (edge_marker(left), edge_marker(right))
    return labelled, unlabelled, markers


__all__ = [
    "AnnotationFace",
    "DirectLabelStyle",
    "LabelLocation",
    "RegionAxis",
    "direct_label",
    "leader",
    "legend",
    "marked_point",
    "overflow_label",
    "panel_labels",
    "plate_label",
    "region_labels",
    "source_note",
    "title",
]
