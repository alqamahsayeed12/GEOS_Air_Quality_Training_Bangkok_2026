"""Fast, dependency-free checks for the participant training package."""

from __future__ import annotations

import json
import csv
import hashlib
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "README.md",
    "VERSION",
    "CHANGELOG.md",
    "requirements-colab.txt",
    "requirements-lock.txt",
    "environment.yml",
    ".github/dependabot.yml",
    ".github/workflows/runtime-smoke.yml",
    ".github/workflows/notebook-smoke.yml",
    "docs/MAINTENANCE.md",
    "scripts/execute_notebooks_offline.py",
    "notebooks/00_module0_google_colab_setup.ipynb",
    "notebooks/01_module1_download_geos_fp.ipynb",
    "notebooks/02_module2_ground_stations_qaqc_geos25km_collocation.ipynb",
    "notebooks/03_module3_bias_correction_and_downscaling.ipynb",
    "data/module1/geos_fp_global_pm25_snapshot.nc4",
    "data/module1/geos_fp_regional_aerosol_snapshot.nc4",
    "data/module1/openaq_reference_pm25_stations.csv",
    "data/module1/openaq_reference_pm25_hourly.csv",
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
REQUIRED_MODULE1_SOURCE = [
    "GEOS_SOURCE_MODE",
    "OPENAQ_SOURCE_MODE",
    "geos_fp_regional_aerosol_snapshot.nc4",
    "openaq_reference_pm25_hourly.csv",
]
SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|token|secret)\s*=\s*['\"][A-Za-z0-9_-]{16,}"),
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
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

    if path.suffix.lower() in {
        ".ipynb", ".json", ".md", ".py", ".txt", ".yml", ".yaml", ".html"
    }:
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in SECRET_PATTERNS:
            if pattern.search(text):
                errors.append(f"Possible committed secret: {path.relative_to(ROOT)}")

# Course asset counts are part of the notebook contract, not incidental inventory.
asset_expectations = {
    "Lao PDR AQMS station files": (
        sorted((ROOT / "data/module2/aqms").glob("AQMS[0-9][0-9].csv")), 14
    ),
    "Thai PCD station files": (
        sorted((ROOT / "data/module2/pcd").glob("th*t.csv")), 96
    ),
    "compact GEOS NetCDF files": (
        sorted((ROOT / "data/module2/geos").glob("*.nc")), 2
    ),
    "v3.1 fold models": (
        sorted((ROOT / "data/module3/model_assets").glob("*fold*.h5")), 30
    ),
    "v3.1 ensemble models": (
        sorted((ROOT / "data/module3/model_assets").glob("*ensemble.h5")), 3
    ),
}
for label, (paths, expected_count) in asset_expectations.items():
    if len(paths) != expected_count:
        errors.append(f"Expected {expected_count} {label}; found {len(paths)}")

for day in (1, 2, 3):
    model_root = ROOT / "data/module3/model_assets"
    expected_day_models = [
        model_root / f"v3_1_dnn_bias_Correction_day{day}_fold{fold:02d}.h5"
        for fold in range(10)
    ] + [model_root / f"v3_1_dnn_bias_Correction_day{day}_ensemble.h5"]
    for model_path in expected_day_models:
        if not model_path.exists() or model_path.stat().st_size == 0:
            errors.append(f"Missing or empty model asset: {model_path.relative_to(ROOT)}")

# The scalar table stores 17 physical predictors. Module 3 explicitly appends
# 0-1000 bounds for the three PM2.5 baseline predictors.
scalar_path = ROOT / "data/module3/model_assets/max_min4.csv"
physical_features = {
    "WIND", "PS", "Q500", "Q850", "QV10M", "T10M", "T500", "T850",
    "U10M", "V10M", "BCSMASS", "DUSMASS25", "OCSMASS", "SO2SMASS",
    "SO4SMASS", "SSSMASS25", "TOTEXTTAU",
}
if scalar_path.exists():
    with scalar_path.open(newline="", encoding="utf-8-sig") as handle:
        scalar_rows = list(csv.reader(handle))
    scalar_cells = {cell.strip() for row in scalar_rows for cell in row}
    missing_scalar_features = sorted(physical_features - scalar_cells)
    if missing_scalar_features:
        errors.append(f"Scalar table is missing features: {missing_scalar_features}")

# Confirm every packaged data/model file still matches the committed manifest.
manifest_path = ROOT / "data_manifest.csv"
if manifest_path.exists():
    with manifest_path.open(newline="", encoding="utf-8") as handle:
        manifest_rows = list(csv.DictReader(handle))
    manifest_files = {row["path"] for row in manifest_rows}
    packaged_files = {
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "data").rglob("*")
        if path.is_file() and path.name != ".DS_Store"
    }
    if manifest_files != packaged_files:
        errors.append("data_manifest.csv does not match the packaged data file inventory")
    for row in manifest_rows:
        data_path = ROOT / row["path"]
        if not data_path.exists():
            continue
        digest = hashlib.sha256(data_path.read_bytes()).hexdigest()
        if digest != row["sha256"]:
            errors.append(f"Checksum mismatch: {row['path']}")

for notebook_path in sorted((ROOT / "notebooks").glob("*.ipynb")):
    try:
        notebook = json.loads(notebook_path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"Invalid notebook JSON {notebook_path.name}: {exc}")
        continue
    source = "\n".join(
        "".join(cell.get("source", [])) for cell in notebook.get("cells", [])
    )
    saved_outputs = json.dumps(
        [cell.get("outputs", []) for cell in notebook.get("cells", [])],
        ensure_ascii=False,
    )
    for forbidden in FORBIDDEN_SOURCE:
        if forbidden in source:
            errors.append(f"Nonportable source in {notebook_path.name}: {forbidden}")
        if forbidden in saved_outputs:
            errors.append(f"Nonportable saved output in {notebook_path.name}: {forbidden}")
    if notebook_path.name == "01_module1_download_geos_fp.ipynb":
        for required_text in REQUIRED_MODULE1_SOURCE:
            if required_text not in source:
                errors.append(f"Module 1 recovery logic is missing: {required_text}")
    for index, cell in enumerate(notebook.get("cells", [])):
        if not cell.get("id"):
            errors.append(f"Missing cell ID in {notebook_path.name} cell {index}")
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

# The Colab environment must be reproducible and free of open-ended ranges.
lock_path = ROOT / "requirements-lock.txt"
if lock_path.exists():
    lock_lines = [
        line.strip() for line in lock_path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    for line in lock_lines:
        if "==" not in line:
            errors.append(f"Unpinned dependency in requirements-lock.txt: {line}")

if errors:
    print("PACKAGE VALIDATION FAILED")
    for error in errors:
        print("-", error)
    sys.exit(1)

print("Package validation passed")
print("Required files:", len(REQUIRED))
print("Notebooks:", len(list((ROOT / "notebooks").glob("*.ipynb"))))
