import matplotlib.pyplot as plt
import numpy as np
import pytest

import lab74


def test_format_ticks_supports_default_and_cross_styles():
    lab74.use(accent=None)
    fig, (default_ax, cross_ax) = plt.subplots(1, 2)
    default_ax.minorticks_on()
    cross_ax.minorticks_on()

    lab74.format_ticks(default_ax)
    lab74.format_ticks(cross_ax, style="cross")
    fig.canvas.draw()

    default_major = default_ax.xaxis.majorTicks[0]
    default_minor = default_ax.xaxis.minorTicks[0]
    cross_major = cross_ax.xaxis.majorTicks[0]
    cross_minor = cross_ax.xaxis.minorTicks[0]
    assert default_major.get_tickdir() == "in"
    assert default_major.tick1line.get_markersize() == pytest.approx(5.0)
    assert default_minor.tick1line.get_markersize() == pytest.approx(3.0)
    assert cross_major.get_tickdir() == "inout"
    assert cross_major.tick1line.get_markersize() == pytest.approx(8.0)
    assert cross_minor.tick1line.get_markersize() == pytest.approx(1.8)


def test_format_ticks_rejects_unknown_style():
    _, ax = plt.subplots()
    with pytest.raises(ValueError, match="unknown tick style"):
        lab74.format_ticks(ax, style="ornamental")


def test_format_ticks_supports_axis_specific_size_override():
    lab74.use(accent=None)
    fig, ax = plt.subplots()
    ax.minorticks_on()

    lab74.format_ticks(ax, style="cross")
    lab74.format_ticks(
        ax,
        style="cross",
        axis="y",
        major_length=4.0,
        minor_length=2.5,
        major_width=0.45,
        minor_width=0.35,
    )
    fig.canvas.draw()

    assert ax.xaxis.majorTicks[0].tick1line.get_markersize() == pytest.approx(8.0)
    assert ax.yaxis.majorTicks[0].get_tickdir() == "inout"
    assert ax.yaxis.majorTicks[0].tick1line.get_markersize() == pytest.approx(4.0)
    assert ax.yaxis.minorTicks[0].tick1line.get_markersize() == pytest.approx(2.5)
    assert ax.yaxis.majorTicks[0].tick1line.get_markeredgewidth() == pytest.approx(0.45)
    assert ax.yaxis.minorTicks[0].tick1line.get_markeredgewidth() == pytest.approx(0.35)


def test_format_frame_open_style_hides_spines_and_major_and_minor_ticks():
    fig, ax = plt.subplots()
    ax.minorticks_on()

    panels = lab74.format_frame(ax, style="open")
    fig.canvas.draw()

    assert panels == (ax,)
    assert not ax.spines["top"].get_visible()
    assert not ax.spines["right"].get_visible()
    assert not any(tick.tick2line.get_visible() for tick in ax.xaxis.majorTicks)
    assert not any(tick.tick2line.get_visible() for tick in ax.yaxis.majorTicks)
    assert not any(tick.tick2line.get_visible() for tick in ax.xaxis.minorTicks)
    assert not any(tick.tick2line.get_visible() for tick in ax.yaxis.minorTicks)


def test_format_frame_defaults_to_closed_and_rejects_unknown_style():
    _, ax = plt.subplots()

    lab74.format_frame(ax)

    assert ax.spines["top"].get_visible()
    assert ax.spines["right"].get_visible()
    with pytest.raises(ValueError, match="frame style"):
        lab74.format_frame(ax, style="half-open")


def test_format_graticule_draws_degree_labels_without_cartesian_axes():
    fig, ax = plt.subplots()
    ax.set(xlabel="LONGITUDE", ylabel="LATITUDE")

    longitude_lines, latitude_lines = lab74.format_graticule(
        ax, [-110, -100, -90], [30, 40, 50]
    )
    fig.canvas.draw()

    assert len(longitude_lines) == len(latitude_lines) == 3
    assert [tick.get_text() for tick in ax.get_xticklabels()] == [
        "110°",
        "100°",
        "90°",
    ]
    assert [tick.get_text() for tick in ax.get_yticklabels()] == [
        "30°",
        "40°",
        "50°",
    ]
    assert ax.get_xlabel() == ax.get_ylabel() == ""
    assert all(line.get_linewidth() == pytest.approx(0.3) for line in longitude_lines)
    assert all(line.get_zorder() == 0 for line in latitude_lines)
    with pytest.raises(ValueError, match="finite"):
        lab74.format_graticule(ax, [-100, np.nan], [40])


def test_format_graticule_can_format_perimeter_without_lines():
    fig, ax = plt.subplots()

    longitude_lines, latitude_lines = lab74.format_graticule(
        ax, [-100, -90], [30, 40], draw_lines=False
    )
    fig.canvas.draw()

    assert longitude_lines == latitude_lines == ()
    assert [tick.get_text() for tick in ax.get_xticklabels()] == ["100°", "90°"]
    assert [tick.get_text() for tick in ax.get_yticklabels()] == ["30°", "40°"]


def test_format_multipanel_defaults_to_joined_framed_panels():
    fig, axes = plt.subplots(2, 2)

    panels = lab74.format_multipanel(axes)

    assert len(panels) == 4
    assert fig.subplotpars.hspace == pytest.approx(0)
    assert fig.subplotpars.wspace == pytest.approx(0)
    for ax in panels:
        assert ax.spines["top"].get_visible()
        assert ax.spines["right"].get_visible()
        assert all(tick.tick2line.get_visible() for tick in ax.xaxis.majorTicks)
        assert all(tick.tick2line.get_visible() for tick in ax.yaxis.majorTicks)


def test_format_multipanel_open_mode_applies_spacing_and_open_frame():
    fig, axes = plt.subplots(2, 2)

    panels = lab74.format_multipanel(axes, mode="open")

    assert len(panels) == 4
    assert fig.subplotpars.hspace == pytest.approx(0.06)
    assert fig.subplotpars.wspace == pytest.approx(0.06)
    for ax in panels:
        assert not ax.spines["top"].get_visible()
        assert not ax.spines["right"].get_visible()
        assert not any(tick.tick2line.get_visible() for tick in ax.xaxis.majorTicks)
        assert not any(tick.tick2line.get_visible() for tick in ax.yaxis.majorTicks)
        assert not any(tick.tick2line.get_visible() for tick in ax.xaxis.minorTicks)
        assert not any(tick.tick2line.get_visible() for tick in ax.yaxis.minorTicks)


def test_format_multipanel_accepts_cross_tick_style():
    lab74.use(accent=None)
    fig, axes = plt.subplots(2, 1)
    for ax in axes:
        ax.minorticks_on()

    lab74.format_multipanel(axes, mode="open", tick_style="cross")
    fig.canvas.draw()

    for ax in axes:
        assert ax.xaxis.majorTicks[0].get_tickdir() == "inout"
        assert ax.xaxis.majorTicks[0].tick1line.get_markersize() == pytest.approx(8.0)
        assert ax.xaxis.minorTicks[0].tick1line.get_markersize() == pytest.approx(1.8)


def test_format_multipanel_spacing_can_be_overridden():
    fig, ax = plt.subplots()

    panels = lab74.format_multipanel(ax, mode="open", hspace=0.08, wspace=0.12)

    assert panels == (ax,)
    assert fig.subplotpars.hspace == pytest.approx(0.08)
    assert fig.subplotpars.wspace == pytest.approx(0.12)
    assert not ax.spines["top"].get_visible()
    assert not ax.spines["right"].get_visible()


def test_format_multipanel_rejects_axes_from_different_figures():
    _, ax1 = plt.subplots()
    _, ax2 = plt.subplots()

    with pytest.raises(ValueError, match="same figure"):
        lab74.format_multipanel([ax1, ax2])


def test_format_multipanel_rejects_unknown_mode():
    _, ax = plt.subplots()

    with pytest.raises(ValueError, match="unknown multipanel mode"):
        lab74.format_multipanel(ax, mode="cards")


@pytest.mark.parametrize("formatter", [lab74.format_ticks, lab74.format_frame])
def test_axes_formatters_reject_invalid_containers(formatter):
    with pytest.raises(TypeError, match="Axes object"):
        formatter("not axes")


def test_axes_formatters_reject_empty_and_recursive_containers():
    with pytest.raises(ValueError, match="at least one"):
        lab74.format_ticks([])

    recursive = []
    recursive.append(recursive)
    with pytest.raises(ValueError, match="contain itself"):
        lab74.format_frame(recursive)
