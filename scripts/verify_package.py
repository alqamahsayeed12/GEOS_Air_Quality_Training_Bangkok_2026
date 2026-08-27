"""Fast, dependency-free checks for the participant training package."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "README.md",
    "requirements-colab.txt",
    "notebooks/00_module0_google_colab_setup.ipynb",
    "notebooks/01_module1_download_geos_fp.ipynb",
    "notebooks/02_module2_ground_stations_qaqc_geos25km_collocation.ipynb",
    "notebooks/03_module3_bias_correction_and_downscaling.ipynb",
    "data/module2/geos/20230505.nc",
    "data/module2/geos/20230506.nc",
    "data/module2/full_period_aqms_geos_evaluation.csv",
    "data/module3/model_assets/max_min4.csv",
    "docs/index.html",
    "docs/presentation/day1_geos_training.html",
    "docs/presentation/assets/animation.gif",
]
FORBIDDEN_SOURCE = [
    "/Volumes/Personal2/",
    "/Users/asayeed/",
    "day1_colab_support_files.zip",
]
SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|token|secret)\s*=\s*['\"][A-Za-z0-9_-]{16,}"),
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
]


errors: list[str] = []

for relative in REQUIRED:
    if not (ROOT / relative).exists():
        errors.append(f"Missing required file: {relative}")

for path in ROOT.rglob("*"):
    if not path.is_file() or ".git" in path.parts:
        continue
    size = path.stat().st_size
    if size >= 100 * 1024 * 1024:
        errors.append(f"File exceeds GitHub 100 MiB limit: {path.relative_to(ROOT)}")

    if path.suffix.lower() in {".md", ".py", ".txt", ".yml", ".yaml", ".html"}:
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                errors.append(f"Possible committed secret: {path.relative_to(ROOT)}")

for notebook_path in sorted((ROOT / "notebooks").glob("*.ipynb")):
    try:
        notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"Invalid notebook JSON {notebook_path.name}: {exc}")
        continue
    source = "\n".join(
        "".join(cell.get("source", [])) for cell in notebook.get("cells", [])
    )
    for forbidden in FORBIDDEN_SOURCE:
        if forbidden in source:
            errors.append(f"Nonportable source in {notebook_path.name}: {forbidden}")
    for index, cell in enumerate(notebook.get("cells", [])):
        if cell.get("cell_type") != "code":
            continue
        code = "".join(cell.get("source", []))
        plain_python = "\n".join(
            line for line in code.splitlines()
            if not line.lstrip().startswith(("%", "!"))
        )
        try:
            compile(plain_python, f"{notebook_path.name}:cell{index}", "exec")
        except SyntaxError as exc:
            errors.append(f"Syntax error in {notebook_path.name} cell {index}: {exc}")

presentation = ROOT / "docs" / "presentation" / "day1_geos_training.html"
if presentation.exists():
    html = presentation.read_text(encoding="utf-8", errors="ignore")
    linked_assets = re.findall(r'(?:src|href)=["\']([^"\']+)', html)
    linked_assets += re.findall(r'url\(["\']?([^"\')]+)', html)
    for reference in linked_assets:
        if reference.startswith(("http://", "https://", "#", "data:")):
            continue
        target = (presentation.parent / reference).resolve()
        if not target.exists():
            errors.append(f"Broken presentation link: {reference}")

if errors:
    print("PACKAGE VALIDATION FAILED")
    for error in errors:
        print("-", error)
    sys.exit(1)

print("Package validation passed")
print("Required files:", len(REQUIRED))
print("Notebooks:", len(list((ROOT / "notebooks").glob("*.ipynb"))))
