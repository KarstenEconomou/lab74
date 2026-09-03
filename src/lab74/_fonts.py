"""Select the technical fonts that lab74 uses."""

from pathlib import Path
from typing import Final

from matplotlib import font_manager

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
TECHNICAL_FONT: Final = (
    "IBM Plex Mono" if "IBM Plex Mono" in _INSTALLED else "DejaVu Sans Mono"
)
GOTHIC_FONT: Final = (
    "IBM Plex Sans Condensed"
    if "IBM Plex Sans Condensed" in _INSTALLED
    else "DejaVu Sans"
)
