import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.lines import Line2D
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
        lab74.plate_label(ax, "INVALID", style="display")  # ty: ignore[invalid-argument-type]


def test_legend_title_and_entries_are_left_aligned():
    _, ax = plt.subplots()
    ax.plot([0, 1], [0, 1], label="SERIES")

    legend = lab74.legend(ax, title="MEASUREMENT")

    assert legend.get_alignment() == "left"


def test_legends_and_annotations_can_have_paper_backgrounds():
    _, ax = plt.subplots()
    ax.plot([0, 1], [0, 1], label="SERIES")

    legend = lab74.legend(ax, background=True)
    annotation = lab74.direct_label(ax, 0.5, 0.5, "MIDPOINT", background=True)

    assert legend.get_frame_on()
    assert legend.get_frame().get_facecolor() == mpl.colors.to_rgba(lab74.PAPER)
    patch = annotation.get_bbox_patch()
    assert patch is not None
    assert patch.get_facecolor() == mpl.colors.to_rgba(lab74.PAPER)


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

    bounds = legend.get_window_extent(fig.canvas.get_renderer())  # ty: ignore[unresolved-attribute]
    actual = np.array([getattr(bounds, coordinate) for coordinate in legend_corner])
    expected = ax.transAxes.transform(axes_anchor) + np.array(offset) * fig.dpi / 72
    np.testing.assert_allclose(actual, expected)


def test_paper_backed_legend_is_inset_two_more_points():
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1], label="SERIES")

    legend = lab74.legend(ax, loc="upper right", background=True)
    fig.canvas.draw()

    bounds = legend.get_window_extent(fig.canvas.get_renderer())  # ty: ignore[unresolved-attribute]
    actual = np.array([bounds.x1, bounds.y1])
    expected = ax.transAxes.transform((1, 1)) + np.array([-8, -6]) * fig.dpi / 72
    np.testing.assert_allclose(actual, expected)


def test_legend_offset_moves_from_automatic_position_in_points():
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1], label="SERIES")

    legend = lab74.legend(ax, loc="upper left", offset=(3, -5))
    fig.canvas.draw()

    bounds = legend.get_window_extent(fig.canvas.get_renderer())  # ty: ignore[unresolved-attribute]
    actual = np.array([bounds.x0, bounds.y1])
    expected = ax.transAxes.transform((0, 1)) + np.array([9, -9]) * fig.dpi / 72
    np.testing.assert_allclose(actual, expected)


def test_legend_offset_also_moves_the_default_location():
    fig, ax = plt.subplots()
    ax.plot([0, 1], [0, 1], label="SERIES")

    baseline = lab74.legend(ax)
    fig.canvas.draw()
    before = baseline.get_window_extent(fig.canvas.get_renderer())  # ty: ignore[unresolved-attribute]
    baseline.remove()

    shifted = lab74.legend(ax, offset=(2, -3))
    fig.canvas.draw()
    after = shifted.get_window_extent(fig.canvas.get_renderer())  # ty: ignore[unresolved-attribute]

    assert after.x0 - before.x0 == pytest.approx(2 * fig.dpi / 72)
    assert after.y0 - before.y0 == pytest.approx(-3 * fig.dpi / 72)


def test_legend_preserves_dash_patterns_in_longer_handles():
    _, ax = plt.subplots()
    ax.plot([0, 1], [0, 1], linestyle="--", label="DASHED")
    ax.plot([0, 1], [1, 0], linestyle="-.", label="DASH-DOT")

    legend = lab74.legend(ax)

    handles = [handle for handle in legend.legend_handles if isinstance(handle, Line2D)]
    assert [handle.get_linestyle() for handle in handles] == ["--", "-."]
    assert legend.handlelength == pytest.approx(2)


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
        [marker.get_xdata()[0] for marker in markers],  # ty: ignore[not-subscriptable]
        [3.05, 3.075],
    )
    with pytest.raises(ValueError, match="increasing edges"):
        lab74.overflow_label(ax, "invalid", (3.1, 3.0))


def test_emphasized_direct_label_adds_caps_tracking_and_italics():
    _, ax = plt.subplots()

    label = lab74.direct_label(ax, 1, 2, "Apollo 15 Probe 1", style="emphasized")

    assert label.get_text() == "A P O L L O   1 5   P R O B E   1"
    assert label.get_fontstyle() == "italic"
    with pytest.raises(ValueError, match="direct-label style"):
        lab74.direct_label(ax, 1, 2, "INVALID", style="display")  # ty: ignore[invalid-argument-type]


def test_panel_labels_letter_panels_in_reading_order():
    _, axes = plt.subplots(2, 2)

    texts = lab74.panel_labels(axes)

    assert [text.get_text() for text in texts] == ["(a)", "(b)", "(c)", "(d)"]
    assert [text.axes for text in texts] == list(axes.flat)
    assert texts[0].get_horizontalalignment() == "left"
    assert texts[0].get_verticalalignment() == "top"


def test_panel_labels_accept_explicit_labels_and_a_location():
    _, axes = plt.subplots(1, 2)

    texts = lab74.panel_labels(axes, labels=["I", "II"], loc="lower right")

    assert [text.get_text() for text in texts] == ["I", "II"]
    assert texts[0].get_horizontalalignment() == "right"
    assert texts[0].get_verticalalignment() == "bottom"


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

    _, label = lab74.marked_point(ax, 0.5, 0.5, "POINT", leader_line=True)

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
    np.testing.assert_allclose(np.asarray(rules[0].get_xdata()), [100, 100])
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
    assert labels[1].get_horizontalalignment() == "right"
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

    np.testing.assert_allclose(np.asarray(rules[0].get_ydata()), [40, 40])
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
