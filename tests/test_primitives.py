import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.collections import PathCollection, PolyCollection
from matplotlib.container import BarContainer, ErrorbarContainer
from matplotlib.contour import QuadContourSet
from matplotlib.legend import Legend
from matplotlib.patches import StepPatch
from matplotlib.path import Path
from matplotlib.ticker import NullLocator

import lab74


def test_band_uses_active_accent_and_hatch():
    lab74.use("telemetry")
    _, ax = plt.subplots()
    x = np.linspace(0, 1, 12)
    band = lab74.band(ax, x, x - 0.1, x + 0.1, hatch="//")
    assert isinstance(band, PolyCollection)
    assert band in ax.collections
    assert band.get_hatch() == "//"
    assert band.get_edgecolor()[0] == pytest.approx((0.0, 133 / 255, 173 / 255, 1.0))
    np.testing.assert_allclose(  # ty: ignore[no-matching-overload]
        band.get_hatchcolor(), band.get_edgecolor()
    )


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
    lab74.use("laboratory")
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
    assert interval.get_linewidths() == pytest.approx([1.2])  # ty: ignore[unresolved-attribute]
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
    assert legend.legend_handles[0].get_hatch() == "//"  # ty: ignore[unresolved-attribute]
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
    assert line.get_linewidth() == pytest.approx(mpl.rcParams["xtick.major.width"])
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
    np.testing.assert_allclose(  # ty: ignore[no-matching-overload]
        first.get_offsets(), second.get_offsets()
    )
    assert len(first.get_offsets()) > 0  # ty: ignore[invalid-argument-type]
    assert Path(vertices).contains_points(first.get_offsets()).all()


def test_technical_contour_line_and_filled_modes():
    x = np.linspace(-2, 2, 31)
    y = np.linspace(-2, 2, 31)
    xx, yy = np.meshgrid(x, y)
    z = xx**2 - yy**2
    lab74.use("laboratory")
    _, (ax1, ax2) = plt.subplots(1, 2)
    lines, regions = lab74.technical_contour(
        ax1, x, y, z, levels=[-2, -1, 0, 1, 2], accent_level=0
    )
    assert isinstance(lines, QuadContourSet)
    assert regions is None
    expected_ink = tuple(
        int(lab74.INK[index : index + 2], 16) / 255 for index in (1, 3, 5)
    )
    expected_accent = tuple(
        int(lab74.ACCENTS["laboratory"][index : index + 2], 16) / 255
        for index in (1, 3, 5)
    )
    np.testing.assert_allclose(
        lines.get_edgecolors(),  # ty: ignore[unresolved-attribute]
        [
            (*expected_ink, 1),
            (*expected_ink, 1),
            (*expected_accent, 1),
            (*expected_ink, 1),
            (*expected_ink, 1),
        ],
    )
    np.testing.assert_allclose(
        lines.get_linewidths(),  # ty: ignore[unresolved-attribute]
        [0.55, 0.55, 0.9, 0.55, 0.55],
    )
    lines2, regions2 = lab74.technical_contour(
        ax2, x, y, z, levels=[-2, -1, 0, 1, 2], filled=True
    )
    assert isinstance(lines2, QuadContourSet)
    assert isinstance(regions2, QuadContourSet)
    assert regions2.hatches == ["", "/", "\\", "x"]
    np.testing.assert_allclose(
        regions2.get_facecolors(),  # ty: ignore[unresolved-attribute]
        np.ones((4, 4)),
    )
    with pytest.raises(ValueError, match="present in levels"):
        lab74.technical_contour(
            ax1,
            x,
            y,
            z,
            levels=[-2, -1, 0, 1, 2],
            accent_level=3,
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
    lab74.use("laboratory")
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
