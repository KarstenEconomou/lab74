import pytest

from lab74 import ACCENTS, INK, PAPER, RULE, get_accent


def test_palette_constants():
    assert PAPER == "#FFFFFF"
    assert INK == "#101112"
    assert RULE == "#D7DBDC"
    assert dict(ACCENTS) == {
        "instrument": "#CB6015",
        "aerospace": "#D92906",
        "oxide": "#8A2A2B",
        "laboratory": "#4C8C2B",
        "prairie": "#EAAA00",
        "marlin": "#0085AD",
        "technical": "#6B5AA6",
        "fermilab": "#004C97",
    }


def test_accent_lookup():
    assert get_accent("oxide") == "#8A2A2B"


def test_unknown_accent_lists_choices():
    with pytest.raises(ValueError, match="unknown lab74 accent") as error:
        get_accent("rainbow")
    assert "instrument" in str(error.value)
    assert "technical" in str(error.value)
