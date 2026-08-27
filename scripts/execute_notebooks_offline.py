"""Execute every participant notebook using bundled recovery data."""

from __future__ import annotations

import argparse
import re
import time
from pathlib import Path

import nbformat
from nbclient import NotebookClient


def prepare_notebook(path: Path):
    """Disable prompts/live services while preserving the participant workflow."""
    notebook = nbformat.read(path, as_version=4)
    for cell in notebook.cells:
        if cell.cell_type != "code":
            continue
        source = "\n".join(
            "print('Locked environment already installed by the notebook audit.')"
            if line.lstrip().startswith("%pip install")
            else line
            for line in cell.source.splitlines()
        )
        if path.name.startswith("01_"):
            source = source.replace("PREFER_LIVE_GEOS = True", "PREFER_LIVE_GEOS = False")
            source = source.replace("PREFER_LIVE_OPENAQ = True", "PREFER_LIVE_OPENAQ = False")
            source = re.sub(
                r"OPENAQ_API_KEY\s*=\s*getpass\([\s\S]*?\)\.strip\(\)",
                'OPENAQ_API_KEY = ""',
                source,
            )
        cell.source = source
    return notebook


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    parser.add_argument("--output", type=Path, default=Path("/tmp/geos-notebook-audit"))
    args = parser.parse_args()

    root = args.root.resolve()
    output_root = args.output.resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    notebook_paths = sorted((root / "notebooks").glob("*.ipynb"))
    if not notebook_paths:
        raise FileNotFoundError(f"No notebooks found under {root}")

    for notebook_path in notebook_paths:
        started = time.time()
        print(f"EXECUTING {notebook_path.name}", flush=True)
        client = NotebookClient(
            prepare_notebook(notebook_path),
            timeout=1200,
            kernel_name="python3",
            allow_errors=False,
            resources={"metadata": {"path": str(root)}},
        )
        executed = client.execute(cwd=str(root))
        output_path = output_root / notebook_path.name
        nbformat.write(executed, output_path)
        print(
            f"PASSED {notebook_path.name} in {time.time() - started:.1f}s",
            flush=True,
        )


if __name__ == "__main__":
    main()
