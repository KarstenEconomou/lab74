from pathlib import Path

import matplotlib.pyplot as plt
import pytest

import lab74


@pytest.mark.parametrize("suffix", ["png", "svg", "pdf"])
def test_figure_exports(tmp_path: Path, suffix: str):
    lab74.use()
    fig, ax = plt.subplots()
    ax.plot([0, 1, 2], [0, 1, 0])
    destination = tmp_path / f"figure.{suffix}"
    fig.savefig(destination)
    assert destination.is_file()
    assert destination.stat().st_size > 100
