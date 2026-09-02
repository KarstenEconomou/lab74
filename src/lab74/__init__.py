"""Provide a compact Matplotlib style for scientific figures."""

from pathlib import Path
from typing import Final, Literal

import matplotlib as mpl
import matplotlib.style as mpl_style

from . import sequences
from ._fonts import GOTHIC_FONT, TECHNICAL_FONT
from .annotations import (
    DirectLabelStyle,
    LabelLocation,
    direct_label,
    leader,
    legend,
    overflow_label,
    plate_label,
    source_note,
)
from .layout import (
    AxesInput,
    FrameStyle,
    MultipanelMode,
    TickAxis,
    TickStyle,
    format_frame,
    format_graticule,
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
from .sequences import line_cycle
from .tables import TableSwatch, header, table

STYLE_PATH: Final = Path(__file__).with_name("lab74.mplstyle")
type FontFace = Literal["mono", "gothic"]


def use(
    accent: AccentName | None = "instrument",
    *,
    face: FontFace = "gothic",
) -> None:
    """Apply a named accent (or none) and a ``mono`` or ``gothic`` face."""
    if face not in ("mono", "gothic"):
        raise ValueError("The font face must be 'mono' or 'gothic'.")
    color = None if accent is None else get_accent(accent)
    mpl_style.use(STYLE_PATH)
    mpl.rcParams["axes.prop_cycle"] = line_cycle(color)
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
    "AxesInput",
    "BarOrientation",
    "ContourLabelFormat",
    "DirectLabelStyle",
    "FontFace",
    "FrameStyle",
    "LabelLocation",
    "MultipanelMode",
    "TickAxis",
    "TickStyle",
    "TableSwatch",
    "band",
    "direct_label",
    "errorbar",
    "format_frame",
    "format_graticule",
    "format_multipanel",
    "format_ticks",
    "get_accent",
    "grouped_bar",
    "header",
    "map_linework",
    "leader",
    "legend",
    "overflow_label",
    "plate_label",
    "stipple",
    "table",
    "source_note",
    "sequences",
    "separated_bar",
    "stairs",
    "technical_contour",
    "use",
]
