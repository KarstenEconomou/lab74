"""Provide a compact Matplotlib style for scientific figures."""

from pathlib import Path
from typing import Final

import matplotlib as mpl
import matplotlib.style as mpl_style

from . import sequences
from ._fonts import FACES, FontFace, font_for
from .annotations import (
    AnnotationFace,
    DirectLabelStyle,
    LabelLocation,
    RegionAxis,
    _configure_annotation_style,
    direct_label,
    leader,
    legend,
    marked_point,
    overflow_label,
    panel_labels,
    plate_label,
    region_labels,
    source_note,
    title,
)
from .layout import (
    AxesInput,
    FrameStyle,
    GridStyle,
    GridWhich,
    MultipanelMode,
    TickAxis,
    TickStyle,
    format_frame,
    format_graticule,
    format_grid,
    format_multipanel,
    format_ticks,
)
from .palette import (
    ACCENTS,
    INK,
    MONOCHROME_LINE_COLORS,
    PAPER,
    RULE,
    AccentName,
    get_accent,
)
from .primitives import (
    BarOrientation,
    ContourLabelFormat,
    band,
    errorbar,
    grouped_bar,
    map_linework,
    separated_bar,
    stairs,
    stipple,
    technical_contour,
)
from .sequences import LineSeriesMode, line_cycle
from .tables import TableCell, TableSwatch, header, table

STYLE_PATH: Final = Path(__file__).with_name("lab74.mplstyle")


def _validate_face(face: FontFace, noun: str) -> None:
    """Reject a font face that lab74 does not package."""
    if face not in FACES:
        choices = ", ".join(repr(name) for name in FACES)
        raise ValueError(f"The {noun} must be one of {choices}.")


def use(
    accent: AccentName | None = None,
    *,
    face: FontFace = "gothic",
    annotation_size_offset: float = 0,
    annotation_face: AnnotationFace | None = None,
    line_series: LineSeriesMode = "ink",
) -> None:
    """Apply the style to the global Matplotlib state.

    The style is monochrome unless ``accent`` names one of the lab74 accents,
    which then colors the first line of the cycle.
    ``face`` sets the text face of the whole figure, and ``annotation_face``
    overrides it for legends and for the annotation tools alone.
    ``annotation_size_offset`` shifts those same sizes in points.
    ``line_series`` chooses between varied line styles and solid graduated
    shades, and applies only when ``accent`` is ``None``: an accented cycle
    always varies its line styles.
    """
    _validate_face(face, "font face")
    if annotation_face is not None:
        _validate_face(annotation_face, "annotation face")
    if line_series not in ("ink", "grayscale"):
        raise ValueError("The line-series mode must be 'ink' or 'grayscale'.")
    color = None if accent is None else get_accent(accent)

    mpl_style.use(STYLE_PATH)
    _configure_annotation_style(
        size_offset=annotation_size_offset, face=annotation_face
    )
    mpl.rcParams["axes.prop_cycle"] = line_cycle(color, mode=line_series)
    font = font_for(face)
    mpl.rcParams["font.family"] = [font]
    mpl.rcParams["mathtext.rm"] = font
    mpl.rcParams["mathtext.it"] = f"{font}:italic"
    mpl.rcParams["mathtext.bf"] = f"{font}:bold"
    mpl.rcParams["mathtext.sf"] = font


__all__ = [
    "ACCENTS",
    "INK",
    "MONOCHROME_LINE_COLORS",
    "PAPER",
    "RULE",
    "STYLE_PATH",
    "AccentName",
    "AnnotationFace",
    "AxesInput",
    "BarOrientation",
    "ContourLabelFormat",
    "DirectLabelStyle",
    "FontFace",
    "FrameStyle",
    "GridStyle",
    "GridWhich",
    "LabelLocation",
    "LineSeriesMode",
    "MultipanelMode",
    "RegionAxis",
    "TableCell",
    "TableSwatch",
    "TickAxis",
    "TickStyle",
    "band",
    "direct_label",
    "errorbar",
    "format_frame",
    "format_graticule",
    "format_grid",
    "format_multipanel",
    "format_ticks",
    "get_accent",
    "grouped_bar",
    "header",
    "leader",
    "legend",
    "map_linework",
    "marked_point",
    "overflow_label",
    "panel_labels",
    "plate_label",
    "region_labels",
    "separated_bar",
    "sequences",
    "source_note",
    "stairs",
    "stipple",
    "table",
    "technical_contour",
    "title",
    "use",
]
