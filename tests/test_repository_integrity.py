import ast
import json
from pathlib import Path


def test_main_notebook_is_valid_json_and_has_code():
    path = Path(__file__).resolve().parents[1] / "notebooks" / "01_margining_simulation_submission.ipynb"
    notebook = json.loads(path.read_text(encoding="utf-8"))
    assert notebook["nbformat"] >= 4
    code_cells = [cell for cell in notebook["cells"] if cell.get("cell_type") == "code"]
    assert code_cells
    for cell in code_cells:
        source = "".join(cell.get("source", []))
        if source.strip():
            ast.parse(source)


def test_core_documentation_exists():
    root = Path(__file__).resolve().parents[1]
    for relative in [
        "README.md",
        "docs/METHODOLOGY.md",
        "docs/MODEL_AUDIT.md",
        "docs/SIMULATION_RESULTS.md",
        "docs/SOURCE_REVIEW.md",
    ]:
        assert (root / relative).is_file()
