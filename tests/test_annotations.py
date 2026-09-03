import matplotlib.pyplot as plt
import numpy as np
import pytest

import lab74


def test_panel_labels_letter_panels_in_reading_order():
    _, axes = plt.subplots(2, 2)

    texts = lab74.panel_labels(axes)

    assert [text.get_text() for text in texts] == ["(a)", "(b)", "(c)", "(d)"]
    assert [text.axes for text in texts] == list(axes.flat)
    assert texts[0].get_ha() == "left"
    assert texts[0].get_va() == "top"


def test_panel_labels_accept_explicit_labels_and_a_location():
    _, axes = plt.subplots(1, 2)

    texts = lab74.panel_labels(axes, labels=["I", "II"], loc="lower right")

    assert [text.get_text() for text in texts] == ["I", "II"]
    assert texts[0].get_ha() == "right"
    assert texts[0].get_va() == "bottom"


def test_panel_labels_reject_a_label_count_mismatch():
    _, axes = plt.subplots(1, 3)

    with pytest.raises(ValueError, match="match the number of panels"):
        lab74.panel_labels(axes, labels=["(a)", "(b)"])


def test_marked_point_stays_out_of_the_legend():
    _, ax = plt.subplots()
    ax.plot([0, 1], [0, 1], label="AM0")

    point, label = lab74.marked_point(ax, 0.5, 0.5, "MAXIMUM POWER")
    legend = lab74.legend(ax)

    assert point.get_label() == "_nolegend_"
    assert point.get_markerfacecolor() == lab74.PAPER
    assert point.get_linestyle() == "None"
    assert label.get_text() == "MAXIMUM POWER"
    assert [text.get_text() for text in legend.get_texts()] == ["AM0"]


def test_marked_point_can_draw_a_leader_to_its_label():
    _, ax = plt.subplots()

    _, label = lab74.marked_point(ax, 0.5, 0.5, "POINT", leader=True)

    assert label.arrowprops is not None
    assert label.arrowprops["arrowstyle"] == "-"


def test_marked_point_rejects_non_finite_coordinates():
    _, ax = plt.subplots()

    with pytest.raises(ValueError, match="finite"):
        lab74.marked_point(ax, np.nan, 0.0, "J_SC")


def test_region_labels_rule_interior_edges_and_center_labels():
    fig, ax = plt.subplots()
    ax.set_xlim(0, 250)

    rules, labels = lab74.region_labels(
        ax, [0, 100, 250], ["FRONT", "REAR"], position=0.9
    )
    fig.canvas.draw()

    assert len(rules) == 1
    assert list(rules[0].get_xdata()) == [100, 100]
    assert rules[0].get_linestyle() == "--"
    assert rules[0].get_linewidth() == pytest.approx(0.65)
    assert [label.get_text() for label in labels] == ["FRONT", "REAR"]
    assert labels[0].xy == pytest.approx((50.0, 0.9))
    assert labels[1].xy == pytest.approx((175.0, 0.9))


def test_region_labels_center_geometrically_on_a_logarithmic_axis():
    fig, ax = plt.subplots()
    ax.set_xscale("log")
    ax.set_xlim(1e-2, 1e2)

    _, labels = lab74.region_labels(ax, [1e-2, 1e0, 1e2], ["LEFT", "RIGHT"])
    fig.canvas.draw()

    assert labels[0].xy[0] == pytest.approx(0.1)
    assert labels[1].xy[0] == pytest.approx(10.0)


def test_region_labels_use_a_leader_for_a_region_narrower_than_its_label():
    fig, ax = plt.subplots()
    ax.set_xlim(0, 250)

    _, labels = lab74.region_labels(
        ax,
        [0, 249.5, 250],
        ["p BASE", "p+ BACK-SURFACE FIELD"],
        leader_offset=(8, 6),
    )
    fig.canvas.draw()

    assert labels[0].arrowprops is None
    assert labels[1].arrowprops is not None
    assert labels[1].get_ha() == "right"
    assert labels[1].get_position() == pytest.approx((-8, -6))


def test_region_labels_can_omit_the_rules():
    _, ax = plt.subplots()
    ax.set_xlim(0, 10)

    rules, labels = lab74.region_labels(ax, [0, 5, 10], ["A", "B"], rules=False)

    assert rules == ()
    assert len(labels) == 2


def test_region_labels_validate_boundaries_and_placement():
    _, ax = plt.subplots()
    ax.set_xlim(0, 10)

    with pytest.raises(ValueError, match="1 more value than labels"):
        lab74.region_labels(ax, [0, 10], ["A", "B"])
    with pytest.raises(ValueError, match="must increase"):
        lab74.region_labels(ax, [0, 5, 5], ["A", "B"])
    with pytest.raises(ValueError, match="finite"):
        lab74.region_labels(ax, [0, np.nan, 10], ["A", "B"])
    with pytest.raises(ValueError, match="between 0 and 1"):
        lab74.region_labels(ax, [0, 10], ["A"], position=1.4)
    with pytest.raises(ValueError, match="region axis"):
        lab74.region_labels(ax, [0, 10], ["A"], axis="z")  # ty: ignore[invalid-argument-type]
    with pytest.raises(ValueError, match="leader offset"):
        lab74.region_labels(ax, [0, 10], ["A"], leader_offset=(-1, 2))


def test_region_labels_reject_non_positive_edges_on_a_logarithmic_axis():
    _, ax = plt.subplots()
    ax.set_xscale("log")

    with pytest.raises(ValueError, match="must be positive"):
        lab74.region_labels(ax, [0, 1, 10], ["A", "B"])


def test_region_labels_can_name_bands_along_the_y_axis():
    fig, ax = plt.subplots()
    ax.set_ylim(0, 100)

    rules, labels = lab74.region_labels(
        ax, [0, 40, 100], ["LOWER", "UPPER"], axis="y", position=0.5
    )
    fig.canvas.draw()

    assert list(rules[0].get_ydata()) == [40, 40]
    assert labels[0].xy == pytest.approx((0.5, 20.0))


def test_title_centers_an_optional_subtitle_at_the_lower_default_position():
    fig, axes = plt.subplots(2, 2)

    title, subtitle = lab74.title(fig, "PLATE TITLE", "SUBTITLE")
    fig.canvas.draw()

    assert [text.get_text() for text in (title, subtitle)] == [
        "PLATE TITLE",
        "SUBTITLE",
    ]
    assert all(text.axes is None for text in (title, subtitle))
    assert all(text in fig.texts for text in (title, subtitle))
    assert all(text.get_horizontalalignment() == "center" for text in (title, subtitle))
    assert all(
        text.get_fontsize() == pytest.approx(axes.flat[0].title.get_fontsize())
        for text in (title, subtitle)
    )
    assert title.get_position() == pytest.approx((0.5, 0.975))


def test_title_rejects_a_target_that_is_not_a_figure():
    with pytest.raises(TypeError, match="must be a Figure"):
        lab74.title("plate", "PLATE")  # ty: ignore[invalid-argument-type]
