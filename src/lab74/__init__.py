"""Provide a compact Matplotlib style for scientific figures."""

from pathlib import Path
from typing import Final, Literal

import matplotlib as mpl
import matplotlib.style as mpl_style
from cycler import Cycler, cycler

from ._fonts import GOTHIC_FONT, TECHNICAL_FONT
from .annotations import (
    DirectLabelStyle,
    LabelLocation,
    direct_label,
    leader,
    overflow_label,
    plate_label,
    source_note,
)
from .layout import (
    AxesInput,
    MultipanelMode,
    TickAxis,
    TickStyle,
    format_frame,
    format_graticule,
    format_multipanel,
    format_ticks,
)
from .palette import ACCENTS, INK, PAPER, RULE, AccentName, get_accent
from .primitives import (
    ContourLabelFormat,
    band,
    errorbar,
    map_linework,
    stairs,
    stipple,
    technical_contour,
)

STYLE_PATH: Final = Path(__file__).with_name("lab74.mplstyle")
type FontFace = Literal["mono", "gothic"]


def _property_cycle(accent: str) -> Cycler:
    """Return the six-series cycle for the specified accent."""
    return (
        cycler(color=[accent, INK, INK, INK, INK, INK])
        + cycler(linestyle=["-", "-", "--", ":", "-.", (0, (5, 2, 1, 2))])
        + cycler(marker=["o", "s", "^", "D", "x", "+"])
    )


def use(
    accent: AccentName | None = "instrument", *, face: FontFace = "gothic"
) -> None:
    """Apply the style, selected typeface, and optional accent color."""
    if face not in ("mono", "gothic"):
        raise ValueError("The font face must be 'mono' or 'gothic'.")
    color = INK if accent is None else get_accent(accent)
    mpl_style.use(STYLE_PATH)
    mpl.rcParams["axes.prop_cycle"] = _property_cycle(color)
    font = GOTHIC_FONT if face == "gothic" else TECHNICAL_FONT
    mpl.rcParams["font.family"] = [font]
    mpl.rcParams["mathtext.rm"] = font
    mpl.rcParams["mathtext.it"] = f"{font}:italic"
    mpl.rcParams["mathtext.bf"] = f"{font}:bold"
    mpl.rcParams["mathtext.sf"] = font


__all__ = [
    "ACCENTS",
    "INK",
    "PAPER",
    "RULE",
    "STYLE_PATH",
    "AccentName",
    "AxesInput",
    "ContourLabelFormat",
    "DirectLabelStyle",
    "FontFace",
    "LabelLocation",
    "MultipanelMode",
    "TickAxis",
    "TickStyle",
    "band",
    "direct_label",
    "errorbar",
    "format_frame",
    "format_graticule",
    "format_multipanel",
    "format_ticks",
    "get_accent",
    "map_linework",
    "leader",
    "overflow_label",
    "plate_label",
    "stipple",
    "source_note",
    "stairs",
    "technical_contour",
    "use",
]
