"""Replace workstation paths in retained notebook outputs with portable labels."""

from __future__ import annotations

import json
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPLACEMENTS = {
    "/Volumes/Personal2/ADPC_UAH/GEOS_Training_Bangkok_2026": "{TRAINING_ROOT}",
    "/Volumes/Personal2/ADPC_UAH/GEOS_Data": "{TRAINING_ROOT}/data/module2/geos",
    "/private/tmp/module1_execution/GEOS_Module1": "{TRAINING_ROOT}/outputs/module1",
    "/Users/asayeed/": "{HOME}/",
    "/Volumes/Personal2/": "{EXTERNAL_VOLUME}/",
}


def clean(value):
    if isinstance(value, str):
        for old, new in REPLACEMENTS.items():
            value = value.replace(old, new)
        return value
    if isinstance(value, list):
        return [clean(item) for item in value]
    if isinstance(value, dict):
        return {key: clean(item) for key, item in value.items()}
    return value


for notebook_path in sorted((ROOT / "notebooks").glob("*.ipynb")):
    notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
    for index, cell in enumerate(notebook.get("cells", [])):
        if "id" not in cell:
            identity = f"{notebook_path.name}:{index}:{''.join(cell.get('source', []))}"
            cell["id"] = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:12]
        if cell.get("cell_type") == "code":
            cell["outputs"] = clean(cell.get("outputs", []))
    notebook_path.write_text(
        json.dumps(notebook, indent=1, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print("Sanitized", notebook_path.name)
