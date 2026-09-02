import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.collections import PathCollection, PolyCollection
from matplotlib.contour import QuadContourSet
from matplotlib.container import BarContainer, ErrorbarContainer
from matplotlib.legend import Legend
from matplotlib.path import Path
from matplotlib.patches import StepPatch
from matplotlib.ticker import NullLocator
from matplotlib.text import Annotation, Text

import lab74


def test_labels_and_leader_use_supplied_axes():
    _, (ax, other) = plt.subplots(1, 2)
    direct = lab74.direct_label(ax, 1, 2, "series")
    plate = lab74.plate_label(ax, "FIG. 04")
    leader = lab74.leader(ax, "peak", (1, 2), (1.5, 2.5))
    assert isinstance(direct, Annotation)
    assert isinstance(plate, Text)
    assert isinstance(leader, Annotation)
    assert direct in ax.texts and direct not in other.texts
    assert plate in ax.texts and leader in ax.texts
    assert all(
        artist.get_fontfamily() == ["IBM Plex Mono"]
        for artist in (direct, plate, leader)
    )


def test_annotations_inherit_tick_label_size():
    with plt.rc_context({"xtick.labelsize": 6.25}):
        _, ax = plt.subplots()
        direct = lab74.direct_label(ax, 1, 2, "series")
        plate = lab74.plate_label(ax, "500 MB")
        leader = lab74.leader(ax, "low", (1, 2), (1.5, 2.5))
        source = lab74.source_note(ax, "NOAA")
        overflow, _, _ = lab74.overflow_label(ax, "242 Events", (3.05, 3.075))

        assert all(
            artist.get_fontsize() == pytest.approx(6.25)
            for artist in (direct, plate, leader, source, overflow)
        )


@pytest.mark.parametrize(
    ("loc", "position", "offset"),
    [
        ("upper left", (0.04, 0.96), (4, -4)),
        ("upper right", (0.96, 0.96), (-4, -4)),
        ("lower left", (0.04, 0.04), (4, 4)),
        ("lower right", (0.96, 0.04), (-4, 4)),
    ],
)
def test_plate_labels_are_inset_four_points_from_named_corner(loc, position, offset):
    fig, ax = plt.subplots()
    label = lab74.plate_label(ax, "FIG. 05", loc=loc)
    fig.canvas.draw()

    actual = label.get_transform().transform(label.get_position())
    expected = ax.transAxes.transform(position) + np.array(offset) * fig.dpi / 72
    np.testing.assert_allclose(actual, expected)


def test_emphasized_plate_label_adds_caps_tracking_and_italics():
    _, ax = plt.subplots()

    label = lab74.plate_label(ax, "Apollo 17 Probe 1", style="emphasized")

    assert label.get_text() == "A P O L L O   1 7   P R O B E   1"
    assert label.get_fontstyle() == "italic"
    with pytest.raises(ValueError, match="plate-label style"):
        lab74.plate_label(ax, "INVALID", style="display")


def test_legend_title_and_entries_are_left_aligned():
    _, ax = plt.subplots()
    ax.plot([0, 1], [0, 1], label="SERIES")

    legend = lab74.legend(ax, title="MEASUREMENT")

    assert legend.get_alignment() == "left"


@pytest.mark.parametrize(
    ("frame_style", "loc", "axes_anchor", "legend_corner", "offset"),
    [
        ("closed", "upper right", (1, 1), ("x1", "y1"), (-6, -4)),
        ("open", "upper right", (1, 1), ("x1", "y1"), (4, 2)),
        ("open", "upper left", (0, 1), ("x0", "y1"), (6, 2)),
        ("open", "lower right", (1, 0), ("x1", "y0"), (4, 4)),
    ],
)
def test_legend_offsets_follow_visible_frame_edges(
    frame_style, loc, axes_anchor, legend_corner, offset
):
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1], label="SERIES")
    lab74.format_frame(ax, style=frame_style)

    legend = lab74.legend(ax, loc=loc)
    fig.canvas.draw()

    bounds = legend.get_window_extent(fig.canvas.get_renderer())
    actual = np.array([getattr(bounds, coordinate) for coordinate in legend_corner])
    expected = ax.transAxes.transform(axes_anchor) + np.array(offset) * fig.dpi / 72
    np.testing.assert_allclose(actual, expected)


def test_source_note_uses_a_fixed_point_offset_and_prefix():
    _, (ax, other) = plt.subplots(1, 2)

    note = lab74.source_note(ax, "WDC–SILSO")

    assert isinstance(note, Annotation)
    assert note in ax.texts and note not in other.texts
    assert note.get_text() == "SOURCE: WDC–SILSO"
    assert note.get_position() == (0, -33.0)
    assert note.get_fontfamily() == ["IBM Plex Mono"]
    with pytest.raises(ValueError, match="cannot be negative"):
        lab74.source_note(ax, "INVALID", offset=-1)


def test_overflow_label_marks_region_edges_and_uses_mixed_coordinates():
    _, (ax, other) = plt.subplots(1, 2)
    ax.set(xlim=(2.5, 3.5), ylim=(0, 80))

    labelled, unlabelled, markers = lab74.overflow_label(
        ax, "242 Events", (3.05, 3.075), y=0.96
    )

    assert labelled in ax.texts and unlabelled in ax.texts
    assert labelled not in other.texts
    assert labelled.get_text() == "242 Events"
    assert len(markers) == 2
    assert all(marker in ax.lines for marker in markers)
    np.testing.assert_allclose(
        [marker.get_xdata()[0] for marker in markers], [3.05, 3.075]
    )
    with pytest.raises(ValueError, match="increasing edges"):
        lab74.overflow_label(ax, "invalid", (3.1, 3.0))


def test_emphasized_direct_label_adds_caps_tracking_and_italics():
    _, ax = plt.subplots()

    label = lab74.direct_label(ax, 1, 2, "Apollo 15 Probe 1", style="emphasized")

    assert label.get_text() == "A P O L L O   1 5   P R O B E   1"
    assert label.get_fontstyle() == "italic"
    with pytest.raises(ValueError, match="direct-label style"):
        lab74.direct_label(ax, 1, 2, "INVALID", style="display")


def test_band_uses_active_accent_and_hatch():
    lab74.use("marlin")
    _, ax = plt.subplots()
    x = np.linspace(0, 1, 12)
    band = lab74.band(ax, x, x - 0.1, x + 0.1, hatch="//")
    assert isinstance(band, PolyCollection)
    assert band in ax.collections
    assert band.get_hatch() == "//"
    assert band.get_edgecolor()[0] == pytest.approx((0.0, 133 / 255, 173 / 255, 1.0))
    np.testing.assert_allclose(band.get_hatchcolor(), band.get_edgecolor())


def test_grouped_bar_uses_graduated_defaults_and_unticked_category_axis():
    lab74.use("aerospace")
    fig, ax = plt.subplots()

    bars = lab74.grouped_bar(
        ax,
        [[1, 2], [3, 4], [5, 6]],
        labels=["EMPTY", "HATCHED", "FILLED"],
        categories=["A", "B"],
    )
    fig.canvas.draw()

    assert all(isinstance(container, BarContainer) for container in bars)
    assert [container.get_label() for container in bars] == [
        "EMPTY",
        "HATCHED",
        "FILLED",
    ]
    assert [container[0].get_hatch() for container in bars] == ["", "", "///"]
    expected_paper = mpl.colors.to_rgba(lab74.PAPER)
    expected_accent = mpl.colors.to_rgba(lab74.ACCENTS["aerospace"])
    assert bars[0][0].get_facecolor() == pytest.approx(expected_accent)
    assert bars[1][0].get_facecolor() == pytest.approx(expected_paper)
    assert bars[2][0].get_facecolor() == pytest.approx(expected_paper)
    centers = [
        bar.get_x() + bar.get_width() / 2
        for bar in (bars[0][0], bars[1][0], bars[2][0])
    ]
    assert centers == pytest.approx([-0.8 / 3, 0, 0.8 / 3])
    assert all(bar.get_width() == pytest.approx(0.8 / 3) for bar in bars[0])
    assert [tick.get_text() for tick in ax.get_xticklabels()] == ["A", "B"]
    assert all(tick.tick1line.get_markersize() == 0 for tick in ax.xaxis.majorTicks)
    assert isinstance(ax.xaxis.get_minor_locator(), NullLocator)


def test_grouped_bar_supports_a_horizontal_category_axis():
    fig, ax = plt.subplots()

    lab74.grouped_bar(
        ax,
        [[1, 2], [3, 4]],
        categories=["A", "B"],
        orientation="horizontal",
    )
    fig.canvas.draw()

    assert [tick.get_text() for tick in ax.get_yticklabels()] == ["A", "B"]
    assert all(tick.tick1line.get_markersize() == 0 for tick in ax.yaxis.majorTicks)
    assert isinstance(ax.yaxis.get_minor_locator(), NullLocator)


def test_separated_bar_advances_the_bar_sequence_for_each_bar():
    lab74.use(accent=None)
    fig, ax = plt.subplots()

    bars = lab74.separated_bar(
        ax,
        [6, 4, 8, 5, 7, 3, 9],
        categories=list("ABCDEFG"),
    )
    fig.canvas.draw()

    assert isinstance(bars, BarContainer)
    assert [bar.get_hatch() for bar in bars] == [
        "",
        "///",
        "",
        "\\\\\\",
        "xxx",
        "...",
        "",
    ]
    expected_paper = mpl.colors.to_rgba(lab74.PAPER)
    expected_ink = mpl.colors.to_rgba(lab74.INK)
    assert bars[0].get_facecolor() == pytest.approx(expected_paper)
    assert bars[2].get_facecolor() == pytest.approx(expected_ink)
    assert bars[6].get_facecolor() == pytest.approx(expected_paper)
    assert all(bar.get_width() == pytest.approx(0.8) for bar in bars)
    assert [tick.get_text() for tick in ax.get_xticklabels()] == list("ABCDEFG")
    assert all(tick.tick1line.get_markersize() == 0 for tick in ax.xaxis.majorTicks)
    assert isinstance(ax.xaxis.get_minor_locator(), NullLocator)


def test_separated_bar_supports_accented_horizontal_bars():
    lab74.use("oxide")
    fig, ax = plt.subplots()

    bars = lab74.separated_bar(
        ax,
        [1, 2, 3, 4],
        categories=["A", "B", "C", "D"],
        orientation="horizontal",
    )
    fig.canvas.draw()

    assert bars[0].get_facecolor() == pytest.approx(
        mpl.colors.to_rgba(lab74.ACCENTS["oxide"])
    )
    assert bars[3].get_facecolor() == pytest.approx(mpl.colors.to_rgba(lab74.INK))
    assert all(tick.tick1line.get_markersize() == 0 for tick in ax.yaxis.majorTicks)
    assert isinstance(ax.yaxis.get_minor_locator(), NullLocator)


def test_stairs_uses_active_accent_and_one_stroke_width():
    lab74.use("fermilab")
    original_hatch_width = plt.rcParams["hatch.linewidth"]
    _, ax = plt.subplots()

    stairs = lab74.stairs(ax, [2, 4, 3], [0, 1, 2, 3], hatch="///", linewidth=0.8)

    assert isinstance(stairs, StepPatch)
    assert stairs in ax.patches
    assert stairs.get_facecolor() == pytest.approx(
        tuple(int(lab74.PAPER[index : index + 2], 16) / 255 for index in (1, 3, 5))
        + (1.0,)
    )
    assert stairs.get_edgecolor() == pytest.approx((0.0, 76 / 255, 151 / 255, 1.0))
    assert stairs.get_linewidth() == pytest.approx(0.8)
    assert stairs.get_hatch_linewidth() == pytest.approx(0.8)
    assert plt.rcParams["hatch.linewidth"] == original_hatch_width


def test_band_and_stairs_accept_matplotlib_property_overrides():
    _, ax = plt.subplots()
    x = np.linspace(0, 1, 4)

    interval = lab74.band(
        ax, x, x - 0.1, x + 0.1, hatch="x", facecolor="none", linewidth=1.2
    )
    steps = lab74.stairs(
        ax, [2, 4, 3], [0, 1, 2, 3], hatch="", fill=False, linewidth=1.1
    )

    assert interval.get_hatch() == "x"
    assert interval.get_linewidths() == pytest.approx([1.2])
    assert steps.get_hatch() == ""
    assert not steps.get_fill()
    assert steps.get_linewidth() == pytest.approx(1.1)


def test_stairs_uses_matplotlib_legend_handler_without_global_mutation():
    original_handler = Legend.get_default_handler_map()[StepPatch]
    lab74.use()
    _, ax = plt.subplots()
    stairs = lab74.stairs(ax, [2, 4, 3], [0, 1, 2, 3], label="distribution")

    legend = ax.legend()

    assert stairs.get_hatch() == "//"
    assert legend.legend_handles[0].get_hatch() == "//"
    assert Legend.get_default_handler_map()[StepPatch] is original_handler


def test_default_hollow_marker_masks_its_line_with_paper():
    lab74.use("instrument")
    _, ax = plt.subplots()
    (line,) = ax.plot([0, 1], [0, 1])
    assert line.get_markerfacecolor() == lab74.PAPER
    assert line.get_markerfacecolor() != "none"


def test_errorbar_uses_open_circle_defaults():
    lab74.use(accent=None)
    _, ax = plt.subplots()

    container = lab74.errorbar(ax, [0, 1], [2, 3], yerr=[0.2, 0.3])

    assert isinstance(container, ErrorbarContainer)
    line = container.lines[0]
    assert line.get_linestyle() == "-"
    assert line.get_linewidth() == pytest.approx(0.55)
    assert line.get_marker() == "o"
    assert line.get_markersize() == pytest.approx(3)
    assert line.get_markerfacecolor() == lab74.PAPER
    assert line.get_markeredgewidth() == pytest.approx(0.55)
    assert container.lines[1][0].get_markersize() == pytest.approx(4)


def test_stipple_is_deterministic_and_uses_supplied_axes():
    _, ax = plt.subplots(figsize=(4, 4), dpi=100)
    ax.set(xlim=(0, 1), ylim=(0, 1))
    vertices = [(0.1, 0.1), (0.9, 0.1), (0.8, 0.8), (0.2, 0.9)]
    first = lab74.stipple(ax, vertices, density=20, seed=7)
    second = lab74.stipple(ax, vertices, density=20, seed=7)
    assert isinstance(first, PathCollection)
    np.testing.assert_allclose(first.get_offsets(), second.get_offsets())
    assert len(first.get_offsets()) > 0
    assert Path(vertices).contains_points(first.get_offsets()).all()


def test_technical_contour_line_and_filled_modes():
    x = np.linspace(-2, 2, 31)
    y = np.linspace(-2, 2, 31)
    xx, yy = np.meshgrid(x, y)
    z = xx**2 - yy**2
    lab74.use("fermilab")
    _, (ax1, ax2) = plt.subplots(1, 2)
    lines, regions = lab74.technical_contour(
        ax1, x, y, z, levels=[-2, -1, 0, 1, 2], accent_levels=[0]
    )
    assert isinstance(lines, QuadContourSet)
    assert regions is None
    expected_ink = tuple(
        int(lab74.INK[index : index + 2], 16) / 255 for index in (1, 3, 5)
    )
    expected_accent = tuple(
        int(lab74.ACCENTS["fermilab"][index : index + 2], 16) / 255
        for index in (1, 3, 5)
    )
    np.testing.assert_allclose(
        lines.get_edgecolors(),
        [
            (*expected_ink, 1),
            (*expected_ink, 1),
            (*expected_accent, 1),
            (*expected_ink, 1),
            (*expected_ink, 1),
        ],
    )
    np.testing.assert_allclose(lines.get_linewidths(), [0.55, 0.55, 0.9, 0.55, 0.55])
    lines2, regions2 = lab74.technical_contour(
        ax2, x, y, z, levels=[-2, -1, 0, 1, 2], filled=True
    )
    assert isinstance(lines2, QuadContourSet)
    assert isinstance(regions2, QuadContourSet)
    assert regions2.hatches == ["", "/", "\\", "x"]
    np.testing.assert_allclose(regions2.get_facecolors(), np.ones((4, 4)))
    with pytest.raises(ValueError, match="at most one"):
        lab74.technical_contour(
            ax1,
            x,
            y,
            z,
            levels=[-2, -1, 0, 1, 2],
            accent_levels=[-1, 1],
        )
    with pytest.raises(ValueError, match="present in levels"):
        lab74.technical_contour(
            ax1,
            x,
            y,
            z,
            levels=[-2, -1, 0, 1, 2],
            accent_levels=[3],
        )


def test_technical_contour_labels_inherit_tick_label_size():
    x = np.linspace(-2, 2, 31)
    y = np.linspace(-2, 2, 31)
    xx, yy = np.meshgrid(x, y)
    z = xx**2 + yy**2
    with plt.rc_context({"xtick.labelsize": 6.25}):
        _, ax = plt.subplots()
        lab74.technical_contour(ax, x, y, z, levels=[1, 2, 3], labels=True)

        assert ax.texts
        assert all(text.get_fontsize() == pytest.approx(6.25) for text in ax.texts)


def test_technical_contour_supports_custom_label_formatting():
    x = np.linspace(-2, 2, 31)
    y = np.linspace(-2, 2, 31)
    xx, yy = np.meshgrid(x, y)
    z = 5400 + 60 * (xx**2 + yy**2)
    _, ax = plt.subplots()

    lab74.technical_contour(
        ax,
        x,
        y,
        z,
        levels=[5400, 5460, 5520],
        labels=True,
        label_format=lambda value: f"{value / 10:.0f}",
        label_kwargs={"fontsize": 7},
    )

    assert {text.get_text() for text in ax.texts} <= {"540", "546", "552"}
    assert ax.texts
    assert all(text.get_fontsize() == pytest.approx(7) for text in ax.texts)


def test_map_linework_suppresses_series_markers_and_linestyles():
    lab74.use("fermilab")
    _, ax = plt.subplots()

    lines = lab74.map_linework(
        ax,
        [np.array([[-110, 30], [-100, 40]]), np.array([[-90, 35], [-80, 45]])],
    )

    assert len(lines) == 2
    assert all(line.get_color() == lab74.INK for line in lines)
    assert all(line.get_linestyle() == "-" for line in lines)
    assert all(line.get_marker() == "None" for line in lines)
    with pytest.raises(ValueError, match="longitude/latitude"):
        lab74.map_linework(ax, [[1, 2, 3]])


def test_map_linework_validates_all_paths_before_drawing():
    _, ax = plt.subplots()

    with pytest.raises(ValueError, match="longitude/latitude"):
        lab74.map_linework(ax, [[[0, 0], [1, 1]], [1, 2, 3]])

    assert not ax.lines
