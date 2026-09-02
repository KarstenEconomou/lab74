import json
import subprocess
import sys

import matplotlib as mpl
import matplotlib.font_manager as font_manager
import matplotlib.pyplot as plt
import pytest
from matplotlib.mathtext import MathTextParser

import lab74


def test_import_does_not_mutate_rcparams_in_fresh_process():
    code = """
import json
import matplotlib as mpl
before = {key: repr(value) for key, value in mpl.rcParams.items()}
import lab74
after = {key: repr(value) for key, value in mpl.rcParams.items()}
print(json.dumps(before == after))
"""
    result = subprocess.run(
        [sys.executable, "-c", code],
        check=True,
        capture_output=True,
        text=True,
    )
    assert json.loads(result.stdout) is True


def test_use_applies_required_rcparams():
    with mpl.rc_context():
        lab74.use(accent="oxide")
        assert mpl.rcParams["figure.facecolor"] == lab74.PAPER
        assert mpl.rcParams["figure.labelsize"] == pytest.approx(8.5)
        assert mpl.rcParams["axes.facecolor"] == lab74.PAPER
        assert mpl.rcParams["axes.edgecolor"] == lab74.INK
        assert mpl.rcParams["axes.linewidth"] == pytest.approx(0.6)
        assert mpl.rcParams["axes.labelsize"] == pytest.approx(8.5)
        assert mpl.rcParams["axes.labelpad"] == pytest.approx(6)
        assert mpl.rcParams["lines.linewidth"] == pytest.approx(0.55)
        assert mpl.rcParams["lines.markersize"] == pytest.approx(3)
        assert mpl.rcParams["lines.markeredgewidth"] == pytest.approx(0.55)
        assert mpl.rcParams["lines.markerfacecolor"] == lab74.PAPER
        assert mpl.rcParams["font.family"] == ["IBM Plex Sans Condensed"]
        assert mpl.rcParams["font.monospace"][:2] == [
            "IBM Plex Mono",
            "DejaVu Sans Mono",
        ]
        assert mpl.rcParams["mathtext.fontset"] == "custom"
        assert mpl.rcParams["mathtext.default"] == "it"
        assert mpl.rcParams["hatch.color"] == "edge"
        assert mpl.rcParams["xtick.direction"] == "in"
        assert mpl.rcParams["xtick.labelsize"] == pytest.approx(7.5)
        assert mpl.rcParams["ytick.labelsize"] == pytest.approx(7.5)
        assert mpl.rcParams["xtick.top"] is True
        assert mpl.rcParams["ytick.right"] is True
        assert mpl.rcParams["xtick.minor.visible"] is True
        assert mpl.rcParams["axes.grid"] is False
        assert mpl.rcParams["legend.fontsize"] == pytest.approx(7.5)
        assert mpl.rcParams["legend.handlelength"] == pytest.approx(1)
        assert mpl.rcParams["legend.handleheight"] == pytest.approx(1)
        assert mpl.rcParams["legend.handletextpad"] == pytest.approx(0.3)
        assert mpl.rcParams["savefig.pad_inches"] == pytest.approx(0.015)
        cycle = mpl.rcParams["axes.prop_cycle"].by_key()
        assert cycle["color"][0] == lab74.ACCENTS["oxide"]
        assert cycle["color"][1:] == [lab74.INK] * 5
        assert cycle["marker"] == ["o", "s", "^", "D", "x", "+"]


def test_use_rejects_unknown_accent_without_applying_style():
    with mpl.rc_context():
        before = mpl.rcParams["figure.facecolor"]
        with pytest.raises(ValueError):
            lab74.use("unknown")
        assert mpl.rcParams["figure.facecolor"] == before


def test_use_without_accent_produces_monochrome_cycle():
    with mpl.rc_context():
        lab74.use(accent=None)
        cycle = mpl.rcParams["axes.prop_cycle"].by_key()
        assert cycle["color"] == [lab74.INK] * 6


@pytest.mark.parametrize(
    ("face", "family"),
    [
        ("gothic", "IBM Plex Sans Condensed"),
        ("mono", "IBM Plex Mono"),
    ],
)
def test_bare_math_symbols_use_packaged_italic_face(face, family):
    with mpl.rc_context():
        lab74.use(face=face)
        italic = font_manager.findfont(
            font_manager.FontProperties(family=family, style="italic")
        )
        assert italic.endswith("Italic.ttf")
        font = MathTextParser("path").parse("$x$").glyphs[0][0]
        assert font.family_name == family
        assert font.style_name == "Italic"


def test_use_supports_all_mono_face():
    with mpl.rc_context():
        lab74.use(accent=None, face="mono")
        assert mpl.rcParams["font.family"] == ["IBM Plex Mono"]


def test_use_rejects_unknown_face_without_applying_style():
    with mpl.rc_context():
        before = mpl.rcParams["figure.facecolor"]
        with pytest.raises(ValueError, match="font face"):
            lab74.use(face="roman")
        assert mpl.rcParams["figure.facecolor"] == before


def test_packaged_stylesheet_is_directly_loadable():
    assert lab74.STYLE_PATH.is_file()
    with mpl.rc_context():
        plt.style.use(lab74.STYLE_PATH)
        assert mpl.rcParams["figure.facecolor"] == lab74.PAPER
        assert mpl.rcParams["axes.prop_cycle"].by_key()["color"][0] == "#CB6015"
