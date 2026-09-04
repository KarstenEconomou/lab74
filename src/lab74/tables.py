"""Draw sparse technical-print tables."""

from collections.abc import Sequence
from dataclasses import dataclass
from math import isfinite
from typing import Any, Final

import matplotlib as mpl
import matplotlib.patheffects as path_effects
from matplotlib.artist import Artist
from matplotlib.axes import Axes
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.text import Text
from matplotlib.transforms import offset_copy
from matplotlib.typing import ColorType

from ._fonts import GOTHIC_FONT, MONO_FONT, font_size_points
from .palette import INK, PAPER, RULE

_HORIZONTAL_INSET: Final = 0.02
_SECTION_SIZE_OFFSET: Final = 1.0
_SWATCH_LABEL_SIZE_OFFSET: Final = 1.0
_SWATCH_LABEL_OFFSET: Final = 0.70
_SWATCH_ROW_UNITS: Final = 1.75
_HEADING_STROKE: Final = 0.2
_NAME_CELL_STROKE: Final = 0.08
_RULE_WIDTH: Final = 0.55


@dataclass(frozen=True, slots=True)
class TableSwatch:
    """Describe a color bar with an optional label and outline.

    The label defaults to an uppercase hexadecimal value. A paper-colored
    swatch without an edge color receives a thin ``RULE`` outline.
    """

    color: ColorType
    label: str | None = None
    edgecolor: ColorType | None = None
    linewidth: float = 0.4


type TableCell = str | TableSwatch


def header(
    ax: Axes,
    name: str,
    title: str,
    revision: str,
    *,
    y: float = 0.993,
    inset: float = _HORIZONTAL_INSET,
    line_offset: float = 12.0,
    color: ColorType = INK,
    fontsize: float | str | None = None,
) -> tuple[Text, Text, Text]:
    """Draw a uniform 2-line technical-document header."""
    if not all(isinstance(value, str) for value in (name, title, revision)):
        raise TypeError("Header name, title, and revision must be strings.")
    if not isfinite(y) or not 0 <= y <= 1:
        raise ValueError("The header y position must be between zero and one.")
    if not isfinite(inset) or not 0 <= inset < 0.5:
        raise ValueError("The header inset must be between zero and one half.")
    if not isfinite(line_offset) or line_offset <= 0:
        raise ValueError("The header line offset must be positive and finite.")
    try:
        mpl.colors.to_rgba(color)
    except ValueError as exc:
        raise ValueError("The header color must be valid.") from exc

    resolved_size = font_size_points(
        mpl.rcParams["xtick.labelsize"] if fontsize is None else fontsize
    )
    name_size = resolved_size + _SECTION_SIZE_OFFSET
    second_line = offset_copy(
        ax.transAxes,
        fig=ax.get_figure(root=True),
        y=-line_offset,
        units="points",
    )
    defaults: dict[str, Any] = {
        "va": "top",
        "clip_on": False,
        "color": color,
        "fontsize": resolved_size,
        "fontfamily": MONO_FONT,
    }
    name_defaults: dict[str, Any] = defaults | {
        "fontsize": name_size,
        "fontweight": "medium",
        "path_effects": [
            path_effects.withStroke(linewidth=_HEADING_STROKE, foreground=color)
        ],
    }
    return (
        ax.text(inset, y, name, transform=ax.transAxes, ha="left", **name_defaults),
        ax.text(inset, y, title, transform=second_line, ha="left", **defaults),
        ax.text(1 - inset, y, revision, transform=second_line, ha="right", **defaults),
    )


def _validated_bbox(
    bbox: tuple[float, float, float, float],
) -> tuple[float, float, float, float]:
    """Return a finite, positive bounding box contained by the axes."""
    if len(bbox) != 4:
        raise ValueError("The table bounding box must contain 4 values.")
    left, bottom, width, height = (float(value) for value in bbox)
    if not all(isfinite(value) for value in (left, bottom, width, height)):
        raise ValueError("The table bounding box must contain only finite values.")
    if width <= 0 or height <= 0:
        raise ValueError("The table bounding-box width and height must be positive.")
    if left < 0 or bottom < 0 or left + width > 1 or bottom + height > 1:
        raise ValueError("The table bounding box must be contained by the axes.")
    return left, bottom, width, height


def _column_fractions(
    count: int, column_widths: Sequence[float] | None
) -> tuple[float, ...]:
    """Return normalized, positive column widths."""
    if column_widths is None:
        return (1 / count,) * count
    if len(column_widths) != count:
        raise ValueError("Column widths must match the number of table columns.")
    widths = tuple(float(value) for value in column_widths)
    if not all(isfinite(value) and value > 0 for value in widths):
        raise ValueError("Column widths must be positive and finite.")
    total = sum(widths)
    return tuple(value / total for value in widths)


def table(
    ax: Axes,
    rows: Sequence[Sequence[TableCell]],
    *,
    columns: Sequence[str],
    title: str | None = None,
    column_widths: Sequence[float] | None = None,
    bbox: tuple[float, float, float, float] = (0, 0, 1, 1),
    inset: float = _HORIZONTAL_INSET,
    color: ColorType = INK,
    rule_color: ColorType = INK,
    fontsize: float | str | None = None,
) -> tuple[Artist, ...]:
    """Draw a sparse table in axes coordinates and return its artists.

    The first column of every row carries medium weight as its name column.
    A :class:`TableSwatch` uses a double-height row to place a solid color bar
    above its label. This function keeps cell text exactly as given.
    """
    if title is not None and not isinstance(title, str):
        raise TypeError("The table title must be a string or None.")
    if isinstance(columns, (str, bytes)):
        raise TypeError("Table columns must be a sequence of headings.")
    headings = tuple(columns)
    if not headings:
        raise ValueError("A table requires at least 1 column.")
    if not all(isinstance(heading, str) for heading in headings):
        raise TypeError("Table column headings must be strings.")

    if isinstance(rows, (str, bytes)):
        raise TypeError("Table rows must be a sequence of row sequences.")
    row_values = tuple(rows)
    if any(isinstance(row, (str, bytes)) for row in row_values):
        raise TypeError("Each table row must be a sequence of cells.")
    body = tuple(tuple(row) for row in row_values)
    if not body:
        raise ValueError("A table requires at least 1 row.")
    if any(len(row) != len(headings) for row in body):
        raise ValueError("Every table row must match the number of columns.")
    for row in body:
        for cell in row:
            if not isinstance(cell, (str, TableSwatch)):
                raise TypeError("Table cells must be strings or TableSwatch values.")
            if isinstance(cell, TableSwatch):
                if cell.label is not None and not isinstance(cell.label, str):
                    raise TypeError("Table swatch labels must be strings or None.")
                try:
                    mpl.colors.to_rgba(cell.color)
                except ValueError as exc:
                    raise ValueError("The table swatch color is invalid.") from exc
                if cell.edgecolor is not None:
                    try:
                        mpl.colors.to_rgba(cell.edgecolor)
                    except ValueError as exc:
                        raise ValueError(
                            "The table swatch edge color is invalid."
                        ) from exc
                if not isfinite(cell.linewidth) or cell.linewidth < 0:
                    raise ValueError(
                        "The table swatch line width must be finite and non-negative."
                    )

    left, bottom, width, height = _validated_bbox(bbox)
    fractions = _column_fractions(len(headings), column_widths)
    if not isfinite(inset) or not 0 <= inset < 0.5:
        raise ValueError("The table inset must be between zero and one half.")
    try:
        mpl.colors.to_rgba(color)
        mpl.colors.to_rgba(rule_color)
    except ValueError as exc:
        raise ValueError("The table text and rule colors must be valid.") from exc
    text_size = font_size_points(
        mpl.rcParams["xtick.labelsize"] if fontsize is None else fontsize
    )
    swatch_label_size = max(text_size - _SWATCH_LABEL_SIZE_OFFSET, 1.0)

    row_units = tuple(
        _SWATCH_ROW_UNITS if any(isinstance(cell, TableSwatch) for cell in row) else 1.0
        for row in body
    )
    title_units = 1.1 if title is not None else 0.0
    last_content_units = (
        _SWATCH_LABEL_OFFSET
        if any(isinstance(cell, TableSwatch) for cell in body[-1])
        else 0.0
    )
    layout_units = title_units + 1.0 + sum(row_units[:-1]) + last_content_units
    unit = height / layout_units
    top = bottom + height
    x_edges = [left]
    for fraction in fractions:
        x_edges.append(x_edges[-1] + width * fraction)
    padding = width * inset
    text_defaults: dict[str, Any] = {
        "transform": ax.transAxes,
        "ha": "left",
        "va": "top",
        "clip_on": False,
        "color": color,
        "fontsize": text_size,
        "fontfamily": MONO_FONT,
    }
    heading_defaults: dict[str, Any] = text_defaults | {
        "fontfamily": GOTHIC_FONT,
        "fontweight": "medium",
        "path_effects": [
            path_effects.withStroke(linewidth=_HEADING_STROKE, foreground=color)
        ],
    }
    section_defaults: dict[str, Any] = heading_defaults | {
        "fontsize": text_size + _SECTION_SIZE_OFFSET,
    }
    name_cell_defaults: dict[str, Any] = text_defaults | {
        "fontweight": "medium",
        "path_effects": [
            path_effects.withStroke(linewidth=_NAME_CELL_STROKE, foreground=color)
        ],
    }

    artists: list[Artist] = []
    cursor = top
    if title is not None:
        artists.append(ax.text(left + padding, cursor, title, **section_defaults))
        cursor -= unit * 0.76
        rule = Line2D(
            [left + padding, left + width - padding],
            [cursor, cursor],
            transform=ax.transAxes,
            color=rule_color,
            linewidth=_RULE_WIDTH,
            solid_capstyle="butt",
            clip_on=False,
        )
        ax.add_line(rule)
        artists.append(rule)
        cursor -= unit * 0.34

    for index, heading in enumerate(headings):
        artists.append(
            ax.text(x_edges[index] + padding, cursor, heading, **heading_defaults)
        )
    cursor -= unit

    for row, units in zip(body, row_units, strict=True):
        for index, cell in enumerate(row):
            x = x_edges[index] + padding
            cell_width = x_edges[index + 1] - x_edges[index] - 2 * padding
            if isinstance(cell, TableSwatch):
                label = (
                    mpl.colors.to_hex(cell.color).upper()
                    if cell.label is None
                    else cell.label
                )
                edgecolor = cell.edgecolor
                if edgecolor is None and mpl.colors.same_color(cell.color, PAPER):
                    edgecolor = RULE
                swatch_height = unit * 0.58
                swatch = Rectangle(
                    (x, cursor - swatch_height),
                    cell_width,
                    swatch_height,
                    transform=offset_copy(
                        ax.transAxes,
                        fig=ax.get_figure(root=True),
                        y=1,
                        units="points",
                    ),
                    facecolor=cell.color,
                    edgecolor="none" if edgecolor is None else edgecolor,
                    linewidth=0 if edgecolor is None else cell.linewidth,
                    clip_on=False,
                )
                ax.add_patch(swatch)
                artists.append(swatch)
                swatch_label_defaults: dict[str, Any] = text_defaults | {
                    "fontsize": swatch_label_size
                }
                artists.append(
                    ax.text(
                        x,
                        cursor - unit * _SWATCH_LABEL_OFFSET,
                        label,
                        **swatch_label_defaults,
                    )
                )
            else:
                defaults = name_cell_defaults if index == 0 else text_defaults
                artists.append(ax.text(x, cursor, cell, **defaults))
        cursor -= unit * units

    return tuple(artists)


__all__ = ["TableCell", "TableSwatch", "header", "table"]
