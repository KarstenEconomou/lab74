"""Provide a compact Matplotlib style for scientific figures."""

from pathlib import Path
from typing import Final, Literal

import matplotlib as mpl
import matplotlib.style as mpl_style

from . import sequences
from ._fonts import GOTHIC_FONT, TECHNICAL_FONT
from .annotations import (
    AnnotationFace,
    DirectLabelStyle,
    LabelLocation,
    RegionAxis,
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
    _configure_annotation_style,
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
from .tables import TableSwatch, header, table

STYLE_PATH: Final = Path(__file__).with_name("lab74.mplstyle")
type FontFace = Literal["mono", "gothic"]


def use(
    accent: AccentName | None = "instrument",
    *,
    face: FontFace = "gothic",
    annotation_size_offset: float = 0,
    annotation_face: AnnotationFace | None = None,
    line_series: LineSeriesMode = "ink",
) -> None:
    """Apply the style, including optional annotation size and face overrides."""
    if face not in ("mono", "gothic"):
        raise ValueError("The font face must be 'mono' or 'gothic'.")
    if annotation_face not in (None, "mono", "gothic"):
        raise ValueError("The annotation face must be 'mono', 'gothic', or None.")
    if line_series not in ("ink", "grayscale"):
        raise ValueError("The line-series mode must be 'ink' or 'grayscale'.")
    color = None if accent is None else get_accent(accent)
    mpl_style.use(STYLE_PATH)
    _configure_annotation_style(
        size_offset=annotation_size_offset, face=annotation_face
    )
    mpl.rcParams["axes.prop_cycle"] = line_cycle(color, mode=line_series)
    font = GOTHIC_FONT if face == "gothic" else TECHNICAL_FONT
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
    "TickAxis",
    "TickStyle",
    "TableSwatch",
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
    "map_linework",
    "leader",
    "legend",
    "marked_point",
    "overflow_label",
    "panel_labels",
    "plate_label",
    "region_labels",
    "stipple",
    "table",
    "source_note",
    "sequences",
    "separated_bar",
    "stairs",
    "technical_contour",
    "title",
    "use",
]
