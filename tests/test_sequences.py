import lab74


def test_line_sequences_define_accented_and_monochrome_variants():
    accented = lab74.sequences.LINE_WITH_ACCENT
    monochrome = lab74.sequences.LINE_WITHOUT_ACCENT

    assert len(accented) == len(monochrome) == 6
    assert accented[0][0] == "accent"
    assert [color for color, _, _ in monochrome] == [
        *lab74.MONOCHROME_LINE_COLORS,
        *lab74.MONOCHROME_LINE_COLORS[:2],
    ]
    assert [style for _, style, _ in accented] == [style for _, style, _ in monochrome]
    assert [marker for _, _, marker in accented] == [
        marker for _, _, marker in monochrome
    ]


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
    monochrome_lines = lab74.sequences.line_cycle(None).by_key()
    accented_bars = lab74.sequences.bar_styles(accent)
    monochrome_bars = lab74.sequences.bar_styles(None)

    assert accented_lines["color"][0] == accent
    assert monochrome_lines["color"] == [
        *lab74.MONOCHROME_LINE_COLORS,
        *lab74.MONOCHROME_LINE_COLORS[:2],
    ]
    assert accented_bars[0]["facecolor"] == accent
    assert monochrome_bars[2]["facecolor"] == lab74.INK
