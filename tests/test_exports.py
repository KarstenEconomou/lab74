from pathlib import Path
from typing import Literal, TypeAliasType, get_args, get_origin, get_type_hints

import matplotlib.pyplot as plt
import pytest

import lab74


def _literal_choices(annotation: object) -> set[str]:
    while isinstance(annotation, TypeAliasType):
        annotation = annotation.__value__
    if get_origin(annotation) is Literal:
        return {value for value in get_args(annotation) if isinstance(value, str)}
    return set().union(*(_literal_choices(arg) for arg in get_args(annotation)))


@pytest.mark.parametrize(
    ("function", "parameter", "choices"),
    [
        (lab74.use, "accent", set(lab74.ACCENTS)),
        (lab74.use, "face", {"mono", "gothic"}),
        (lab74.use, "annotation_face", {"mono", "gothic"}),
        (lab74.use, "line_series", {"ink", "grayscale"}),
        (lab74.sequences.line_cycle, "mode", {"ink", "grayscale"}),
        (lab74.legend, "face", {"mono", "gothic"}),
        (lab74.get_accent, "name", set(lab74.ACCENTS)),
        (
            lab74.plate_label,
            "loc",
            {"upper left", "upper right", "lower left", "lower right"},
        ),
        (lab74.plate_label, "style", {"emphasized"}),
        (lab74.direct_label, "style", {"emphasized"}),
        (lab74.marked_point, "style", {"emphasized"}),
        (
            lab74.panel_labels,
            "loc",
            {"upper left", "upper right", "lower left", "lower right"},
        ),
        (lab74.panel_labels, "style", {"emphasized"}),
        (lab74.region_labels, "axis", {"x", "y"}),
        (lab74.region_labels, "style", {"emphasized"}),
        (lab74.format_ticks, "style", {"default", "cross"}),
        (lab74.format_ticks, "axis", {"both", "x", "y"}),
        (lab74.format_frame, "style", {"open", "closed"}),
        (lab74.format_grid, "style", {"rule", "ink"}),
        (lab74.format_grid, "axis", {"both", "x", "y"}),
        (lab74.format_grid, "which", {"major", "minor", "both"}),
        (lab74.format_multipanel, "mode", {"framed", "open"}),
        (lab74.format_multipanel, "tick_style", {"default", "cross"}),
        (lab74.format_multipanel, "grid", {"rule", "ink"}),
        (lab74.grouped_bar, "orientation", {"vertical", "horizontal"}),
        (lab74.separated_bar, "orientation", {"vertical", "horizontal"}),
    ],
)
def test_constrained_public_kwargs_expose_literal_choices(function, parameter, choices):
    annotation = get_type_hints(function)[parameter]
    assert _literal_choices(annotation) == choices


@pytest.mark.parametrize("suffix", ["png", "svg", "pdf"])
def test_figure_exports(tmp_path: Path, suffix: str):
    lab74.use()
    fig, ax = plt.subplots()
    ax.plot([0, 1, 2], [0, 1, 0])
    destination = tmp_path / f"figure.{suffix}"
    fig.savefig(destination)
    assert destination.is_file()
    assert destination.stat().st_size > 100


def test_every_exported_name_resolves():
    missing = [name for name in lab74.__all__ if not hasattr(lab74, name)]
    assert missing == []


@pytest.mark.parametrize(
    "module",
    [lab74.annotations, lab74.layout, lab74.palette, lab74.primitives, lab74.tables],
)
def test_submodule_exports_reach_the_package_namespace(module):
    """Keep the top-level namespace complete; ``sequences`` is reached as a module."""
    assert set(module.__all__) <= set(lab74.__all__)
