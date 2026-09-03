import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.text import Text

import lab74


def test_header_uses_one_font_size_and_the_shared_horizontal_inset():
    fig, ax = plt.subplots()

    labels = lab74.header(
        ax,
        "LAB74",
        "COLOUR REPRODUCTION STANDARD",
        "REV. 1.0.0",
        fontsize=8.5,
    )
    fig.canvas.draw()

    assert [label.get_text() for label in labels] == [
        "LAB74",
        "COLOUR REPRODUCTION STANDARD",
        "REV. 1.0.0",
    ]
    assert labels[0].get_fontsize() == pytest.approx(9.5)
    assert all(label.get_fontsize() == pytest.approx(8.5) for label in labels[1:])
    assert all(label.get_fontfamily() == ["IBM Plex Mono"] for label in labels)
    assert labels[0].get_fontweight() == "medium"
    assert all(label.get_fontweight() == "normal" for label in labels[1:])
    actual = np.asarray(
        [label.get_transform().transform(label.get_position()) for label in labels]
    )
    expected = np.asarray(
        [
            ax.transAxes.transform((0.02, 0.993)),
            ax.transAxes.transform((0.02, 0.993)) + (0, -12 * fig.dpi / 72),
            ax.transAxes.transform((0.98, 0.993)) + (0, -12 * fig.dpi / 72),
        ]
    )
    np.testing.assert_allclose(actual, expected)


def test_table_draws_sparse_technical_text_and_rule_on_supplied_axes():
    _, (ax, other) = plt.subplots(1, 2)

    artists = lab74.table(
        ax,
        [["PAPER", "FIGURE GROUND"]],
        columns=["NAME", "USE"],
        title="BASIC MATERIALS",
        column_widths=[1, 2],
    )

    texts = [artist for artist in artists if isinstance(artist, Text)]
    rules = [artist for artist in artists if isinstance(artist, Line2D)]
    assert [text.get_text() for text in texts] == [
        "BASIC MATERIALS",
        "NAME",
        "USE",
        "PAPER",
        "FIGURE GROUND",
    ]
    assert all(text in ax.texts and text not in other.texts for text in texts)
    assert all(
        text.get_fontfamily() == ["IBM Plex Sans Condensed"] for text in texts[:3]
    )
    assert all(text.get_fontfamily() == ["IBM Plex Mono"] for text in texts[3:])
    assert all(text.get_fontweight() == "medium" for text in texts[:3])
    assert texts[0].get_fontsize() == pytest.approx(
        texts[1].get_fontsize() + 1  # ty: ignore[unsupported-operator]
    )
    assert texts[3].get_fontweight() == "medium"
    assert texts[4].get_fontweight() == "normal"
    assert len(rules) == 1 and rules[0] in ax.lines
    assert rules[0].get_color() == lab74.INK
    np.testing.assert_allclose(  # ty: ignore[no-matching-overload]
        rules[0].get_xdata(), [0.02, 0.98]
    )
    assert texts[0].get_position()[0] == pytest.approx(0.02)
    assert texts[2].get_position()[0] == pytest.approx(1 / 3 + 0.02)


def test_table_swatch_has_an_independent_fill_and_label():
    fig, ax = plt.subplots()

    artists = lab74.table(
        ax,
        [["INSTRUMENT", lab74.TableSwatch("#CB6015", "#CB6015")]],
        columns=["NAME", "DISPLAY"],
    )

    swatches = [artist for artist in artists if isinstance(artist, Rectangle)]
    labels = [
        artist
        for artist in artists
        if isinstance(artist, Text) and artist.get_text() == "#CB6015"
    ]
    assert len(swatches) == 1 and swatches[0] in ax.patches
    assert swatches[0].get_facecolor() == pytest.approx(mpl.colors.to_rgba("#CB6015"))
    assert swatches[0].get_linewidth() == 0
    assert len(labels) == 1
    assert labels[0].get_color() == lab74.INK
    body_label = next(
        artist
        for artist in artists
        if isinstance(artist, Text) and artist.get_text() == "INSTRUMENT"
    )
    assert labels[0].get_fontsize() == pytest.approx(
        body_label.get_fontsize() - 1  # ty: ignore[unsupported-operator]
    )
    assert labels[0].get_position()[1] < swatches[0].get_y()
    actual_bottom = (
        swatches[0]
        .get_data_transform()
        .transform((swatches[0].get_x(), swatches[0].get_y()))
    )
    axes_bottom = ax.transAxes.transform((swatches[0].get_x(), swatches[0].get_y()))
    np.testing.assert_allclose(actual_bottom, axes_bottom + (0, fig.dpi / 72))


def test_table_swatch_supports_an_explicit_thin_outline():
    _, ax = plt.subplots()

    artists = lab74.table(
        ax,
        [[lab74.TableSwatch(lab74.PAPER, lab74.PAPER, edgecolor=lab74.INK)]],
        columns=["DISPLAY"],
    )

    swatch = next(artist for artist in artists if isinstance(artist, Rectangle))
    assert swatch.get_facecolor() == pytest.approx(mpl.colors.to_rgba(lab74.PAPER))
    assert swatch.get_edgecolor() == pytest.approx(mpl.colors.to_rgba(lab74.INK))
    assert swatch.get_linewidth() == pytest.approx(0.4)


def test_paper_swatch_gets_a_rule_outline_and_generated_hex_label():
    _, ax = plt.subplots()

    artists = lab74.table(
        ax,
        [[lab74.TableSwatch(lab74.PAPER)]],
        columns=["SPECIMEN"],
    )

    swatch = next(artist for artist in artists if isinstance(artist, Rectangle))
    labels = [artist.get_text() for artist in artists if isinstance(artist, Text)]
    assert swatch.get_edgecolor() == pytest.approx(mpl.colors.to_rgba(lab74.RULE))
    assert swatch.get_linewidth() == pytest.approx(0.4)
    assert "#FFFFFF" in labels


@pytest.mark.parametrize(
    ("rows", "kwargs", "message"),
    [
        ([], {"columns": ["A"]}, "at least 1 row"),
        ([[]], {"columns": []}, "at least 1 column"),
        ([["A"]], {"columns": ["A", "B"]}, "match the number"),
        ([["A"]], {"columns": ["A"], "column_widths": [1, 2]}, "Column widths"),
        ([["A"]], {"columns": ["A"], "column_widths": [0]}, "positive"),
        ([["A"]], {"columns": ["A"], "bbox": (0, 0, 0, 1)}, "positive"),
        ([["A"]], {"columns": ["A"], "bbox": (0.5, 0, 0.6, 1)}, "contained"),
    ],
)
def test_table_rejects_invalid_layout(rows, kwargs, message):
    _, ax = plt.subplots()
    with pytest.raises(ValueError, match=message):
        lab74.table(ax, rows, **kwargs)


def test_table_rejects_unsupported_cells_and_invalid_swatch_colors():
    _, ax = plt.subplots()
    with pytest.raises(TypeError, match="strings or TableSwatch"):
        lab74.table(ax, [[42]], columns=["VALUE"])  # ty: ignore[invalid-argument-type]
    with pytest.raises(ValueError, match="swatch color is invalid"):
        lab74.table(
            ax,
            [[lab74.TableSwatch("not-a-color", "INVALID")]],
            columns=["DISPLAY"],
        )
    with pytest.raises(ValueError, match="text and rule colors"):
        lab74.table(ax, [["A"]], columns=["VALUE"], rule_color="not-a-color")


def test_table_rejects_strings_in_place_of_column_or_row_sequences():
    _, ax = plt.subplots()
    with pytest.raises(TypeError, match="sequence of headings"):
        lab74.table(ax, [["A"]], columns="VALUE")
    with pytest.raises(TypeError, match="sequence of cells"):
        lab74.table(ax, ["A"], columns=["VALUE"])
