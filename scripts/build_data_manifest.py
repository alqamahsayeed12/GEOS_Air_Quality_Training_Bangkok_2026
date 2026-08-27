"""Create a checksum manifest for participant data and model assets."""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GROUP_INFO = {
    "data/module1": ("NASA GEOS-FP and OpenAQ", "Module 1 offline recovery", "inherits source terms"),
    "data/module2/aqms": ("Lao PDR AQMS", "Ground-station QA/QC", "confirm before public release"),
    "data/module2/pcd": ("Thai PCD", "Ground-station QA/QC", "confirm before public release"),
    "data/module2/geos": ("NASA GEOS-FP", "Compact collocation example", "NASA source terms"),
    "data/module2/full_period": ("Derived evaluation table", "Forecast-day evaluation", "inherits ground-data terms"),
    "data/module2/geos_25km": ("NASA GEOS-FP", "Grid template", "NASA source terms"),
    "data/module3/model_assets": ("Training author", "v3.1 and downscaling inference", "educational package"),
    "data/module3": ("Derived training assets", "Module 3 demonstration", "inherits source terms"),
}


def classify(relative: str) -> tuple[str, str, str]:
    for prefix, info in GROUP_INFO.items():
        if relative.startswith(prefix):
            return info
    return "Course package", "Training support", "see documentation"


rows = []
for path in sorted((ROOT / "data").rglob("*")):
    if not path.is_file():
        continue
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    relative = path.relative_to(ROOT).as_posix()
    source, purpose, status = classify(relative)
    rows.append({
        "path": relative,
        "size_bytes": path.stat().st_size,
        "sha256": digest,
        "source": source,
        "training_purpose": purpose,
        "redistribution_status": status,
    })

output = ROOT / "data_manifest.csv"
with output.open("w", newline="", encoding="utf-8") as handle:
    writer = csv.DictWriter(handle, fieldnames=rows[0].keys(), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)

print(f"Wrote {len(rows)} records to {output}")
