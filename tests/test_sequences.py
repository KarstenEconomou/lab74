import pytest

import lab74


def test_line_sequences_define_accented_ink_and_grayscale_variants():
    accented = lab74.sequences.LINE_WITH_ACCENT
    ink = lab74.sequences.LINE_INK
    grayscale = lab74.sequences.LINE_GRAYSCALE

    assert len(accented) == len(ink) == 6
    assert len(grayscale) == len(lab74.MONOCHROME_LINE_COLORS) == 4
    assert accented[0][0] == "accent"
    assert {color for color, _, _ in ink} == {"ink"}
    assert len({repr(style) for _, style, _ in ink}) == len(ink)
    assert [color for color, _, _ in grayscale] == list(lab74.MONOCHROME_LINE_COLORS)
    assert {style for _, style, _ in grayscale} == {"-"}


def test_bar_sequences_define_accented_and_monochrome_variants():
    accented = lab74.sequences.BAR_WITH_ACCENT
    monochrome = lab74.sequences.BAR_WITHOUT_ACCENT

    assert len(accented) == len(monochrome) == 6
    assert accented[0] == ("accent", "")
    assert monochrome[:2] == (("paper", ""), ("paper", "///"))
    assert monochrome[2] == ("ink", "")


def test_sequence_resolvers_apply_or_omit_the_accent():
    accent = lab74.ACCENTS["oxide"]

    accented_lines = lab74.sequences.line_cycle(accent).by_key()
    ink_lines = lab74.sequences.line_cycle(None).by_key()
    grayscale_lines = lab74.sequences.line_cycle(None, mode="grayscale").by_key()
    accented_bars = lab74.sequences.bar_styles(accent)
    monochrome_bars = lab74.sequences.bar_styles(None)

    assert accented_lines["color"][0] == accent
    assert ink_lines["color"] == [lab74.INK] * 6
    assert grayscale_lines["color"] == list(lab74.MONOCHROME_LINE_COLORS)
    assert grayscale_lines["linestyle"] == ["-"] * 4
    assert accented_bars[0]["facecolor"] == accent
    assert monochrome_bars[2]["facecolor"] == lab74.INK


def test_line_cycle_rejects_an_unknown_mode():
    with pytest.raises(ValueError, match="line-series mode"):
        lab74.sequences.line_cycle(None, mode="rainbow")  # ty: ignore[invalid-argument-type]
