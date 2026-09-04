"""Resolve the technical faces and font sizes that lab74 uses."""

from collections.abc import Mapping
from math import isfinite
from pathlib import Path
from types import MappingProxyType
from typing import Final, Literal

from matplotlib import font_manager

type FontFace = Literal["gothic", "mono"]

_FONT_DIR = Path(__file__).with_name("fonts")
for _font_path in (
    _FONT_DIR / "IBMPlexSansCondensed-Regular.ttf",
    _FONT_DIR / "IBMPlexSansCondensed-Italic.ttf",
    _FONT_DIR / "IBMPlexSansCondensed-Medium.ttf",
    _FONT_DIR / "IBMPlexMono-Regular.ttf",
    _FONT_DIR / "IBMPlexMono-Italic.ttf",
    _FONT_DIR / "IBMPlexMono-Medium.ttf",
):
    if _font_path.is_file():
        font_manager.fontManager.addfont(_font_path)

_INSTALLED = {font.name for font in font_manager.fontManager.ttflist}
GOTHIC_FONT: Final = (
    "IBM Plex Sans Condensed"
    if "IBM Plex Sans Condensed" in _INSTALLED
    else "DejaVu Sans"
)
MONO_FONT: Final = (
    "IBM Plex Mono" if "IBM Plex Mono" in _INSTALLED else "DejaVu Sans Mono"
)

FACES: Final[Mapping[FontFace, str]] = MappingProxyType(
    {"gothic": GOTHIC_FONT, "mono": MONO_FONT}
)


def font_for(face: FontFace) -> str:
    """Return the font family that a named face resolves to."""
    return FACES[face]


def font_size_points(value: float | str) -> float:
    """Return a validated Matplotlib font size in points."""
    try:
        size = font_manager.FontProperties(size=value).get_size_in_points()
    except (TypeError, ValueError) as exc:
        raise ValueError("The font size is invalid.") from exc
    if not isfinite(size) or size <= 0:
        raise ValueError("The font size must be positive and finite.")
    return size
