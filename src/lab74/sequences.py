"""Define the ordered visual sequences used by each plot type."""

from typing import Any, Final, Literal

from cycler import Cycler, cycler
from matplotlib.typing import ColorType, LineStyleType, MarkerType

from .palette import INK, MONOCHROME_LINE_COLORS, PAPER

type ColorRole = Literal["accent", "ink", "paper"]
type LineSeries = tuple[ColorRole | ColorType, LineStyleType, MarkerType]
type LineSeriesMode = Literal["ink", "grayscale"]
type BarSeries = tuple[ColorRole, str]

LINE_WITH_ACCENT: Final[tuple[LineSeries, ...]] = (
    ("accent", "-", "o"),
    ("ink", "-", "s"),
    ("ink", "--", "^"),
    ("ink", "-.", "x"),
    ("ink", (0, (5, 2, 1, 2)), "+"),
    ("ink", ":", "D"),
)

LINE_INK: Final[tuple[LineSeries, ...]] = (
    ("ink", "-", "o"),
    ("ink", "--", "s"),
    ("ink", "-.", "^"),
    ("ink", ":", "x"),
    ("ink", (0, (7, 2)), "+"),
    ("ink", (0, (5, 2, 1, 2, 1, 2)), "D"),
)

LINE_GRAYSCALE: Final[tuple[LineSeries, ...]] = (
    (MONOCHROME_LINE_COLORS[0], "-", "o"),
    (MONOCHROME_LINE_COLORS[1], "-", "s"),
    (MONOCHROME_LINE_COLORS[2], "-", "^"),
    (MONOCHROME_LINE_COLORS[3], "-", "D"),
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


def _resolve_color(role: ColorRole | ColorType, accent: ColorType | None) -> ColorType:
    """Resolve a semantic color role for an active accent state."""
    if role == "paper":
        return PAPER
    if role == "accent" and accent is not None:
        return accent
    if role in ("ink", "accent"):
        return INK
    return role


def line_cycle(accent: ColorType | None, *, mode: LineSeriesMode = "ink") -> Cycler:
    """Return an accented, all-ink, or grayscale line cycle."""
    if mode not in ("ink", "grayscale"):
        raise ValueError("The line-series mode must be 'ink' or 'grayscale'.")
    if accent is not None:
        sequence = LINE_WITH_ACCENT
    elif mode == "ink":
        sequence = LINE_INK
    else:
        sequence = LINE_GRAYSCALE
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
    "LINE_GRAYSCALE",
    "LINE_INK",
    "LINE_WITH_ACCENT",
    "BarSeries",
    "ColorRole",
    "LineSeries",
    "LineSeriesMode",
    "bar_styles",
    "line_cycle",
]
