import re
import tomllib
from pathlib import Path

_ROOT = Path(__file__).parents[1]
_REPO = "KarstenEconomou/lab74"


def test_readme_pins_repository_urls_to_the_packaged_version():
    """PyPI renders the README verbatim, so its links must be absolute and pinned."""
    version = tomllib.loads((_ROOT / "pyproject.toml").read_text())["project"][
        "version"
    ]
    readme = (_ROOT / "README.md").read_text()

    refs = re.findall(rf"github\.com/{_REPO}/(?:blob|tree)/([^/]+)/", readme)
    refs += re.findall(rf"raw\.githubusercontent\.com/{_REPO}/([^/]+)/", readme)

    assert refs, "the README no longer links into the repository"
    assert set(refs) == {f"v{version}"}


def test_readme_has_no_relative_links():
    readme = (_ROOT / "README.md").read_text()
    relative = [
        target
        for target in re.findall(r"\]\(([^)\s]+)\)", readme)
        if not target.startswith(("http://", "https://", "#", "mailto:"))
    ]
    assert relative == []
