"""Define the ordered visual sequences used by each plot type."""

from __future__ import annotations

from typing import Any, Final, Literal

from cycler import Cycler, cycler
from matplotlib.typing import ColorType

from .palette import INK, MONOCHROME_LINE_COLORS, PAPER

type ColorRole = Literal["accent", "ink", "paper"]
type LineSeries = tuple[str, Any, str]
type BarSeries = tuple[ColorRole, str]

LINE_WITH_ACCENT: Final[tuple[LineSeries, ...]] = (
    ("accent", "-", "o"),
    ("ink", "-", "s"),
    ("ink", "--", "^"),
    ("ink", "-.", "x"),
    ("ink", (0, (5, 2, 1, 2)), "+"),
    ("ink", ":", "D"),
)

LINE_WITHOUT_ACCENT: Final[tuple[LineSeries, ...]] = (
    (MONOCHROME_LINE_COLORS[0], "-", "o"),
    (MONOCHROME_LINE_COLORS[1], "-", "s"),
    (MONOCHROME_LINE_COLORS[2], "--", "^"),
    (MONOCHROME_LINE_COLORS[3], "-.", "x"),
    (MONOCHROME_LINE_COLORS[0], (0, (5, 2, 1, 2)), "+"),
    (MONOCHROME_LINE_COLORS[1], ":", "D"),
)

BAR_WITH_ACCENT: Final[tuple[BarSeries, ...]] = (
    ("accent", ""),
    ("paper", ""),
    ("paper", "///"),
    ("ink", ""),
    ("paper", "xxx"),
    ("paper", "..."),
)

BAR_WITHOUT_ACCENT: Final[tuple[BarSeries, ...]] = (
    ("paper", ""),
    ("paper", "///"),
    ("ink", ""),
    ("paper", "\\\\\\"),
    ("paper", "xxx"),
    ("paper", "..."),
)

CONTOUR_HATCHES: Final[tuple[str, ...]] = ("", "/", "\\", "x", ".", "..")


def _resolve_color(role: str, accent: ColorType | None) -> ColorType:
    """Resolve a semantic color role for an active accent state."""
    if role == "paper":
        return PAPER
    if role == "accent" and accent is not None:
        return accent
    if role == "ink" or role == "accent":
        return INK
    return role


def line_cycle(accent: ColorType | None) -> Cycler:
    """Return the line cycle for an accented or monochrome figure."""
    sequence = LINE_WITH_ACCENT if accent is not None else LINE_WITHOUT_ACCENT
    return (
        cycler(color=[_resolve_color(color, accent) for color, _, _ in sequence])
        + cycler(linestyle=[linestyle for _, linestyle, _ in sequence])
        + cycler(marker=[marker for _, _, marker in sequence])
    )


def bar_styles(accent: ColorType | None) -> tuple[dict[str, Any], ...]:
    """Return bar artist properties for the active accent state."""
    sequence = BAR_WITH_ACCENT if accent is not None else BAR_WITHOUT_ACCENT
    return tuple(
        {"facecolor": _resolve_color(color, accent), "hatch": hatch}
        for color, hatch in sequence
    )


__all__ = [
    "BAR_WITHOUT_ACCENT",
    "BAR_WITH_ACCENT",
    "CONTOUR_HATCHES",
    "LINE_WITHOUT_ACCENT",
    "LINE_WITH_ACCENT",
    "BarSeries",
    "ColorRole",
    "LineSeries",
    "bar_styles",
    "line_cycle",
]
