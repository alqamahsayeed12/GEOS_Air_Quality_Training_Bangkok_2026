"""Make the Bangkok training notebooks portable across Colab and local clones."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from textwrap import dedent


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK_DIR = ROOT / "notebooks"
REPO_NAME = "GEOS_Air_Quality_Training_Bangkok_2026"
REPO_URL = f"https://github.com/alqamahsayeed12/{REPO_NAME}.git"


def lines(text: str) -> list[str]:
    text = dedent(text).strip() + "\n"
    return text.splitlines(keepends=True)


def markdown(text: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": lines(text)}


def code(text: str) -> dict:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": lines(text),
    }


def load(name: str) -> dict:
    return json.loads((NOTEBOOK_DIR / name).read_text(encoding="utf-8"))


def save(name: str, notebook: dict) -> None:
    for index, cell in enumerate(notebook["cells"]):
        if "id" not in cell:
            identity = f'{name}:{index}:{cell["cell_type"]}:{"".join(cell["source"])}'
            cell["id"] = hashlib.sha1(identity.encode("utf-8")).hexdigest()[:12]
    (NOTEBOOK_DIR / name).write_text(
        json.dumps(notebook, indent=1, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


BOOTSTRAP = f'''
# --- What this cell does ---
# Clones the participant repository in a fresh Colab runtime.
# Locates the same project root when the notebook runs from a local clone.
# Installs the shared scientific Python environment used by this module.
# --- End annotation ---
from pathlib import Path
import subprocess
import sys

REPO_NAME = "{REPO_NAME}"
REPO_URL = "{REPO_URL}"
IN_COLAB = "google.colab" in sys.modules

if IN_COLAB:
    TRAINING_ROOT = Path("/content") / REPO_NAME
    if not (TRAINING_ROOT / ".git").exists():
        subprocess.run(
            ["git", "clone", "--depth", "1", REPO_URL, str(TRAINING_ROOT)],
            check=True,
        )
    else:
        subprocess.run(
            ["git", "-C", str(TRAINING_ROOT), "pull", "--ff-only"],
            check=True,
        )
else:
    candidates = [Path.cwd(), Path.cwd().parent]
    TRAINING_ROOT = next(
        (path.resolve() for path in candidates if (path / "requirements-colab.txt").exists()),
        None,
    )
    if TRAINING_ROOT is None:
        raise FileNotFoundError("Run this notebook from the cloned repository.")

requirements_path = TRAINING_ROOT / "requirements-colab.txt"
print("Python:", sys.version.split()[0])
subprocess.run(
    [sys.executable, "-m", "pip", "install", "-q", "-r", str(requirements_path)],
    check=True,
)
print("Training root:", TRAINING_ROOT)
'''


def rebuild_module0() -> None:
    original = load("00_module0_google_colab_setup.ipynb")
    original["cells"] = [
        markdown('''
        # Module 0: Set Up Google Colab

        **Technical Training on GEOS Data for Air Quality Monitoring in Lao PDR**  
        Bangkok, 7 September 2026

        Google Colab is the participant environment for all modules. This setup
        notebook connects the runtime, retrieves the course repository, installs
        its declared dependencies, and verifies the training assets.

        **Participant workflow**

        1. Open this notebook with the **Open in Colab** link in the course README.
        2. Choose **File > Save a copy in Drive** so your edits are retained.
        3. Connect to a hosted runtime and run the cells from top to bottom.
        '''),
        markdown('''
        ## 1. Confirm the Colab runtime

        Choose **Runtime > Connect to hosted runtime**, then run this cell.
        '''),
        code('''
        import platform
        import sys

        IN_COLAB = "google.colab" in sys.modules
        print("Running in Google Colab:", IN_COLAB)
        print("Python:", platform.python_version())

        if not IN_COLAB:
            print("Local mode detected. The remaining cells also support a local clone.")
        '''),
        markdown('''
        ## 2. Retrieve the course repository

        In Colab, the next cell makes a shallow clone under `/content`. In a local
        Jupyter session it discovers the existing clone instead. Re-running the
        cell is safe.
        '''),
        code(BOOTSTRAP),
        markdown('''
        ## 3. Verify the participant assets

        This check catches an incomplete clone before a later module begins.
        '''),
        code('''
        required_paths = [
            TRAINING_ROOT / "notebooks" / "01_module1_download_geos_fp.ipynb",
            TRAINING_ROOT / "notebooks" / "02_module2_ground_stations_qaqc_geos25km_collocation.ipynb",
            TRAINING_ROOT / "notebooks" / "03_module3_bias_correction_and_downscaling.ipynb",
            TRAINING_ROOT / "requirements-lock.txt",
            TRAINING_ROOT / "data" / "module1" / "geos_fp_global_pm25_snapshot.nc4",
            TRAINING_ROOT / "data" / "module1" / "geos_fp_regional_aerosol_snapshot.nc4",
            TRAINING_ROOT / "data" / "module1" / "openaq_reference_pm25_hourly.csv",
            TRAINING_ROOT / "data" / "module2" / "geos_25km_grid_template.nc",
            TRAINING_ROOT / "data" / "module2" / "full_period_aqms_geos_evaluation.csv",
            TRAINING_ROOT / "data" / "module3" / "model_assets" / "max_min4.csv",
        ]

        missing = [path for path in required_paths if not path.exists()]
        if missing:
            raise FileNotFoundError("Missing training assets:\\n" + "\\n".join(map(str, missing)))

        print(f"Verified {len(required_paths)} required assets.")
        print("Repository:", TRAINING_ROOT)
        '''),
        markdown('''
        ## 4. Check the scientific environment

        The versions printed here can be included in a troubleshooting report.
        '''),
        code('''
        import cartopy
        import matplotlib
        import netCDF4
        import numpy
        import pandas
        import requests
        import sklearn
        import xarray

        versions = {
            "NumPy": numpy.__version__,
            "pandas": pandas.__version__,
            "xarray": xarray.__version__,
            "netCDF4": netCDF4.__version__,
            "Matplotlib": matplotlib.__version__,
            "Cartopy": cartopy.__version__,
            "scikit-learn": sklearn.__version__,
            "requests": requests.__version__,
        }
        for package, version in versions.items():
            print(f"{package:14s} {version}")
        '''),
        markdown('''
        ## Module 0 checkpoint

        - [ ] Saved a personal copy of the notebook in Google Drive
        - [ ] Connected to a Colab runtime
        - [ ] Cloned the course repository
        - [ ] Verified all required assets
        - [ ] Printed the package versions

        Files under `/content` are temporary. Your notebook copy remains in Drive,
        but generated outputs should be downloaded before the runtime is recycled.
        '''),
    ]
    save("00_module0_google_colab_setup.ipynb", original)


def adapt_module1() -> None:
    name = "01_module1_download_geos_fp.ipynb"
    notebook = load(name)
    notebook["cells"][1]["source"] = lines('''
    ## 0. Colab setup

    Run this cell once in a new Google Colab runtime. It retrieves the course
    repository and installs the shared environment. The cell is idempotent.
    ''')
    notebook["cells"][2] = code(BOOTSTRAP)
    source = "".join(notebook["cells"][3]["source"])
    source = source.replace(
        'IN_COLAB = "google.colab" in sys.modules\nOUTPUT_DIR = Path("/content/GEOS_Module1") if IN_COLAB else Path.cwd() / "GEOS_Module1"',
        'OUTPUT_DIR = TRAINING_ROOT / "outputs" / "module1"',
    )
    notebook["cells"][3]["source"] = lines(source)
    save(name, notebook)


def adapt_module2() -> None:
    name = "02_module2_ground_stations_qaqc_geos25km_collocation.ipynb"
    notebook = load(name)
    notebook["cells"][2]["source"] = lines('''
    ## 0. Environment and paths

    The setup cell retrieves the course repository in Colab, installs the shared
    environment, and points every input to a versioned participant asset.
    ''')
    module2_setup = BOOTSTRAP + dedent('''

    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    import xarray as xr

    plt.rcParams.update({
        "figure.dpi": 130,
        "axes.titleweight": "semibold",
        "axes.grid": False,
    })

    PROJECT_ROOT = TRAINING_ROOT
    PCD_DIR = PROJECT_ROOT / "data" / "module2" / "pcd"
    AQMS_DIR = PROJECT_ROOT / "data" / "module2" / "aqms"
    GRID_FILE = PROJECT_ROOT / "data" / "module2" / "geos_25km_grid_template.nc"
    GEOS_DATA_DIR = PROJECT_ROOT / "data" / "module2" / "geos"
    OUTPUT_DIR = PROJECT_ROOT / "outputs" / "module2"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Project:", PROJECT_ROOT)
    print("Thai PCD folder:", PCD_DIR)
    print("Lao PDR AQMS folder:", AQMS_DIR)
    print("GEOS grid:", GRID_FILE)
    print("Output folder:", OUTPUT_DIR)
    ''')
    notebook["cells"][3] = code(module2_setup)

    cell24 = "".join(notebook["cells"][24]["source"])
    if 'GEOS_DATA_DIR = Path("/Volumes' in cell24:
        start = cell24.index('GEOS_DATA_DIR = Path("/Volumes')
        end = cell24.index("missing_geos_files =")
        cell24 = cell24[:start] + '''GEOS_FILES = [
        GEOS_DATA_DIR / "20230505.nc",
        GEOS_DATA_DIR / "20230506.nc",
    ]

    ''' + cell24[end:]
    notebook["cells"][24]["source"] = lines(cell24)

    notebook["cells"][44]["source"] = lines('''
    ## Section 6: Full-period AQMS scatter matrix

    The two-file example is useful for tracing the workflow, but it is too short
    for station-level evaluation. This section loads a compact, analysis-ready
    table prepared from the full archive with the same UTC alignment and QA/QC
    rules used above.
    ''')
    notebook["cells"][45]["source"] = lines('''
    ### 6.1 Load and verify the compact AQMS evaluation table

    The bundled table retains station identity, initialization time, valid time,
    forecast day, complete three-hour observations (`n_obs = 3`), and GEOS PM2.5.
    Loading the compact product makes the participant workflow reproducible without
    distributing the multi-gigabyte intermediate archive.
    ''')
    notebook["cells"][46] = code('''
    # --- What this cell does ---
    # Loads the compact full-period Lao PDR AQMS evaluation table.
    # Reapplies n_obs and concentration checks, removes duplicate forecast records,
    # and saves a working copy under the participant output directory.
    # --- End annotation ---

    FULL_EVALUATION_FILE = (
        PROJECT_ROOT / "data" / "module2" / "full_period_aqms_geos_evaluation.csv"
    )
    full_aqms_evaluation = pd.read_csv(
        FULL_EVALUATION_FILE,
        parse_dates=["initialization_time_utc", "datetime_utc"],
    )

    valid = (
        full_aqms_evaluation["network"].eq("Lao PDR AQMS")
        & full_aqms_evaluation["station_code"].astype(str).str.match(r"^AQMS\\d{2}$")
        & pd.to_numeric(full_aqms_evaluation["obs_n_obs"], errors="coerce").eq(3)
        & pd.to_numeric(full_aqms_evaluation["observed_pm25"], errors="coerce").between(1, 1000)
        & pd.to_numeric(full_aqms_evaluation["GEOSPM25"], errors="coerce").between(1, 1000)
    )
    full_aqms_evaluation = full_aqms_evaluation.loc[valid].copy()

    deduplication_key = [
        "station_code", "forecast_day", "initialization_time_utc", "datetime_utc"
    ]
    rows_before = len(full_aqms_evaluation)
    full_aqms_evaluation = full_aqms_evaluation.drop_duplicates(
        deduplication_key, keep="last"
    ).reset_index(drop=True)
    duplicate_rows_removed = rows_before - len(full_aqms_evaluation)

    compact_aqms_output = OUTPUT_DIR / "module2_full_period_aqms_geos_evaluation.csv"
    full_aqms_evaluation.to_csv(compact_aqms_output, index=False)

    aqms_station_metadata = (
        full_aqms_evaluation[["station_code", "station_name"]]
        .drop_duplicates("station_code")
        .sort_values("station_code")
        .reset_index(drop=True)
    )
    aqms_codes = [f"AQMS{number:02d}" for number in range(1, 15)]
    availability = (
        full_aqms_evaluation.groupby(["station_code", "forecast_day"])
        .size()
        .unstack(fill_value=0)
        .reindex(index=aqms_codes, columns=[1, 2, 3], fill_value=0)
    )
    availability.columns = [f"Day {day}" for day in availability.columns]

    print("Source:", FULL_EVALUATION_FILE)
    print("Compact AQMS records:", f"{len(full_aqms_evaluation):,}")
    print("Duplicate records removed:", f"{duplicate_rows_removed:,}")
    print("Stations represented:", full_aqms_evaluation["station_code"].nunique(), "of 14")
    print("Working copy:", compact_aqms_output)
    display(availability)
    ''')
    trace_source = "".join(notebook["cells"][28]["source"])
    trace_source = trace_source.replace(
        'geos_collocated_long_trace["station_code"]',
        'geos_value_lineage_examples["station_code"]',
    ).replace(
        'geos_collocated_long_trace["variable"]',
        'geos_value_lineage_examples["variable"]',
    )
    notebook["cells"][28]["source"] = lines(trace_source)
    save(name, notebook)


def adapt_module3() -> None:
    name = "03_module3_bias_correction_and_downscaling.ipynb"
    notebook = load(name)
    notebook["cells"][1]["source"] = lines('''
    ## 0. Colab setup and reproducibility

    The setup cell retrieves the participant repository and installs the declared
    dependencies. A GPU speeds up DNN training but is not required for the compact
    demonstration.
    ''')
    original = "".join(notebook["cells"][2]["source"])
    analysis_start = original.index("\nfrom pathlib import Path\nimport os\n")
    tail = original[analysis_start + 1:]
    tail = tail.replace(
        'TRAINING_ROOT\n    / "data"\n    / "collocated_pairs"\n    / "aqms_geos_collocated_training_sample_day1.csv"',
        'MODULE3_DATA / "aqms_geos_collocated_training_sample_day1.csv"',
    )
    notebook["cells"][2] = code(BOOTSTRAP + "\n" + tail)
    save(name, notebook)


if __name__ == "__main__":
    rebuild_module0()
    adapt_module1()
    adapt_module2()
    adapt_module3()
    print("Prepared four Colab-portable notebooks in", NOTEBOOK_DIR)
