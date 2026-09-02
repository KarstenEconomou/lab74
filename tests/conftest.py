import matplotlib as mpl
import matplotlib.pyplot as plt
import pytest


@pytest.fixture(autouse=True)
def isolate_matplotlib_state():
    """Restore global style state and close figures after each test."""
    with mpl.rc_context():
        yield
    plt.close("all")
