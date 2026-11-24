import json
from pathlib import Path


def test_project_notebooks_are_valid_json():
    root=Path(__file__).resolve().parents[1]
    notebooks=sorted((root/"notebooks").glob("*.ipynb"))
    assert len(notebooks)==5
    for path in notebooks:
        nb=json.loads(path.read_text(encoding="utf-8"))
        assert nb["nbformat"]>=4
        assert nb["cells"]


def test_documentation_entry_points_exist():
    root=Path(__file__).resolve().parents[1]
    for relative in [
        "README.md",
        "docs/METHODOLOGY.md",
        "docs/MODEL_AUDIT.md",
        "docs/SIMULATION_RESULTS.md",
        "docs/SOURCE_REVIEW.md",
        "CONTRIBUTIONS.md",
    ]:
        assert (root/relative).is_file()
