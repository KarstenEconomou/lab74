"""Define the small lab74 print palette."""

from collections.abc import Mapping
from types import MappingProxyType
from typing import Final, Literal

type AccentName = Literal[
    "instrument",
    "aerospace",
    "oxide",
    "laboratory",
    "prairie",
    "marlin",
    "technical",
    "fermilab",
]

PAPER: Final = "#FFFFFF"
INK: Final = "#101112"
RULE: Final = "#D7DBDC"

# Ordered light-to-dark for distinguishing multiple series without an accent.
MONOCHROME_LINE_COLORS: Final[tuple[str, ...]] = (
    "#858788",
    "#606263",
    "#393A3B",
    INK,
)

ACCENTS: Final[Mapping[AccentName, str]] = MappingProxyType(
    {
        "instrument": "#CB6015",
        "aerospace": "#D92906",
        "oxide": "#8A2A2B",
        "laboratory": "#4C8C2B",
        "prairie": "#EAAA00",
        "marlin": "#0085AD",
        "technical": "#6B5AA6",
        "fermilab": "#004C97",
    }
)


def get_accent(
    name: Literal[
        "instrument",
        "aerospace",
        "oxide",
        "laboratory",
        "prairie",
        "marlin",
        "technical",
        "fermilab",
    ],
) -> str:
    """Return the hexadecimal value of a named accent."""
    try:
        return ACCENTS[name]
    except KeyError as exc:
        choices = ", ".join(ACCENTS)
        raise ValueError(
            f"The value is an unknown lab74 accent: {name!r}. "
            f"Use one of these names: {choices}."
        ) from exc


__all__ = [
    "ACCENTS",
    "INK",
    "MONOCHROME_LINE_COLORS",
    "PAPER",
    "RULE",
    "AccentName",
    "get_accent",
]
