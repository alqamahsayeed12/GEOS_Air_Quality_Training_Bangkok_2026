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


INLINE_GUIDANCE = {
    "00_module0_google_colab_setup.ipynb": [
        ("IN_COLAB = \"google.colab\" in sys.modules", "Detect the hosted runtime without relying on a Colab-only import."),
        ("required_paths = [", "Treat these files as the minimum complete participant package."),
        ("missing = [path for path in required_paths if not path.exists()]", "Report every missing asset together so setup problems can be fixed in one pass."),
        ("versions = {", "Record the runtime versions that control numerical and model behavior."),
    ],
    "01_module1_download_geos_fp.ipynb": [
        ("IN_COLAB = \"google.colab\" in sys.modules", "Use one setup path in Colab and another when instructors test a local clone."),
        ("PREFER_LIVE_GEOS = True", "Set this to False only when demonstrating the bundled recovery data offline."),
        ("requested_aerosol_variables = [", "Request only aerosol and PM2.5 fields needed later, which keeps the remote subset focused."),
        ("candidate = xr.open_dataset(OPENDAP_URL, engine=\"netcdf4\", decode_times=False)", "Open the OPeNDAP dataset lazily; values are transferred only when selected or loaded."),
        ("if \"kg\" in global_units and \"m-3\" in global_units:", "Convert mass concentration from kg m-3 to µg m-3 before interpreting or plotting it."),
        ("color_max = float(np.nanpercentile(finite, 99))", "Use a robust percentile so a few extreme cells do not flatten the map colors."),
        ("BBOX = [95.0, 5.0, 110.0, 25.0]", "Bounding boxes follow west, south, east, north in geographic coordinates."),
        ("start = pd.Timestamp(DATE_FROM)", "Parse participant dates explicitly, then normalize both endpoints to UTC."),
        (".sel(time=slice(start_for_xarray, end_for_xarray), lat=slice(south, north), lon=slice(west, east))", "Perform the time and bounding-box selection on the server through OPeNDAP."),
        ("regional.to_netcdf(geos_subset_file)", "Persist the exact analysis subset so later cells no longer depend on the live service."),
        ("regional_field = regional[PLOT_VARIABLE].isel(time=PLOT_TIME_INDEX)", "Select one valid time while retaining latitude and longitude dimensions."),
        ("merra2_pm25 = (", "MERRA-2 combines dry aerosol components and scales sulfate to represent associated ammonium."),
        ("geos516_pm25 = (", "This reconstruction represents the earlier GEOS-FP aerosol formulation."),
        ("gocart2g_pm25 = geos516_pm25 + regional[\"BRSMASS\"]", "The current formulation adds brown carbon to the nitrate- and ammonium-aware reconstruction."),
        ("valid = np.isfinite(reference) & np.isfinite(estimate)", "Use identical finite pairs for every metric so sample sizes remain comparable."),
        ("denominator = np.sum(", "Willmott IOA compares squared error with the potential error around the observed mean."),
        ("axis_max = max(10.0, float(np.nanpercentile(finite_values, 99.5)))", "Apply one robust axis limit to all panels for a fair visual comparison."),
        ("OPENAQ_API_KEY = getpass(", "Prompt securely so the API key is not printed or stored inside the notebook."),
        ("cache_file = OPENAQ_CACHE_DIR / f\"sensor_{sensor_id}_page_{page}.json\"", "Cache each API page to avoid repeating requests during instruction or troubleshooting."),
        ("observations = observations[", "Apply the declared concentration and bounding-box filters before station-model comparison."),
        ("station_means = (", "Average repeated hourly records to one value per mapped station and interval."),
        ("combined_max = float(np.nanpercentile(", "Share one robust color limit between the gridded field and station circles."),
        ("EXERCISE_VARIABLES = [\"SO4SMASS\", \"NISMASS25\"]", "Participants can replace these names with other downloaded aerosol components."),
    ],
    "02_module2_ground_stations_qaqc_geos25km_collocation.ipynb": [
        ("pcd_files = sorted(PCD_DIR.glob(\"th*t.csv\"))", "Discover all Thai PCD station files so the workflow scales beyond one example."),
        ("VALID_PM25_MIN = 1.0", "Values below 1 or above 1,000 µg/m³ are excluded from analysis but retained for QA/QC auditing."),
        ("frame[\"datetime_local\"] = local_naive.dt.tz_localize(LOCAL_TIMEZONE)", "Localize clock time first; localization assigns UTC+7 without shifting the recorded hour."),
        ("valid_times = frame[\"datetime_utc\"].dropna().sort_values()", "Sort valid timestamps before estimating the station's typical reporting frequency."),
        ("if len(valid) > 5000:", "Sample only for distribution graphics; all valid rows still contribute to summary counts."),
        ("STATION_CODE = \"AQMS01\"", "This is the participant control for choosing the station analyzed in the next cells."),
        ("clean_station = selected_data.loc[", "Carry forward only valid concentrations with usable local and UTC timestamps."),
        ("daily_station = (", "Collapse hourly measurements to one daily mean while retaining the number of contributing values."),
        ("~((daily_station[\"month\"] == 2) & (daily_station[\"day\"] == 29))", "Remove leap day so all years align to the same 365-day climatological axis."),
        ("day_of_year_summary = (", "Aggregate the same calendar day across years to expose recurring annual behavior."),
        ("grid = xr.open_dataset(GRID_FILE)", "Use one representative GEOS file because its grid geometry is shared by the archive."),
        ("grid_lon_2d, grid_lat_2d = np.meshgrid(geos_lons, geos_lats)", "Expand the 1-D coordinates into every two-dimensional grid-center pair."),
        ("a = (", "This is the Haversine central-angle term computed in radians."),
        ("flat_index = int(np.nanargmin(distances))", "Select the grid center with the smallest great-circle distance and retain its flattened index."),
        ("assert collocation[\"geos_distance_km\"].max() < 30", "Reject a result if any station is implausibly far from a 25 km grid center."),
        ("reference_date = pd.to_datetime(source_file.stem, format=\"%Y%m%d\", errors=\"raise\", utc=True)", "Interpret the YYYYMMDD filename as the forecast reference date in UTC."),
        ("frame[\"valid_time_utc\"] = pd.to_datetime(frame[\"valid_time_utc\"], errors=\"coerce\", utc=True)", "Use the NetCDF time coordinate as forecast valid time, not the filename date alone."),
        ("selected = dataset[extractable_variables].isel(", "Vectorized index arrays extract every station and time without looping over grid cells."),
        ("geos_collocated_wide = pd.concat(wide_frames, ignore_index=True, sort=False)", "Combine all forecast initializations into one wide table with a model column for each variable."),
        ("ground_window_start = geos_valid_start - pd.Timedelta(minutes=90)", "Extend by half a 3-hour window so edge-centered observations are not discarded."),
        ("station_3h[\"valid_time_utc\"] = station_3h[\"bin_start_utc\"] + pd.Timedelta(minutes=90)", "Place each three-hour mean at its midpoint: 01:30, 04:30, ..., 22:30 UTC."),
        ("geos_ground_comparison = geos_collocated_wide[geos_comparison_columns].merge(", "Join only on station identity and UTC valid time to prevent accidental temporal mismatches."),
        ("collocated_analysis[\"error_geos_minus_ground\"] = (", "Define signed error consistently as model minus observation; positive values indicate overprediction."),
        ("ground_plot = ground_series.reindex(timeline)", "Insert absent timestamps as NaN so the line breaks across missing data."),
        ("analysis_mask = (", "Reapply the analysis contract after reloading the saved table."),
        ("ioa_denominator = np.sum(", "Compute original Willmott IOA using potential error around the observed mean."),
        ("collocated_analysis[\"observed_pm25_bin\"] = pd.cut(", "Use fixed concentration bands to reveal whether error changes in the high-PM2.5 tail."),
        ("deduplication_key = [", "Define uniqueness by station, forecast initialization, forecast day, and valid time."),
        ("EXERCISE_STATION = \"AQMS02\"", "Participants change this value and rerun the exercise cells for another station."),
    ],
    "03_module3_bias_correction_and_downscaling.ipynb": [
        ("FEATURE_COLUMNS = [", "Keep feature order fixed because normalization arrays and trained models use this exact order."),
        ("valid_rows = (", "Apply QA/QC before splitting so every model sees the same eligible records."),
        ("static_scalars = pd.read_csv(STATIC_SCALAR_FILE, index_col=0)", "Load global training-era scalars rather than estimating new limits from this sample."),
        ("denominator = maximum - minimum", "Use one denominator per feature and stop if any declared range is zero or missing."),
        ("normalized_features = global_minmax_normalize(", "Apply the production min-max equation column by column in the locked feature order."),
        ("train_indices, test_indices = train_test_split(", "Fix the random seed so every teaching model is evaluated on the same held-out rows."),
        ("linear_model.fit(X_train_linear, y_train)", "Fit only on training targets; the test targets remain unseen until evaluation."),
        ("rf_model = RandomForestRegressor(", "The tree ensemble provides a nonlinear benchmark between linear correction and the DNN."),
        ("dnn_model = keras.Sequential([", "Build a compact multilayer perceptron for tabular station-time predictors."),
        ("optimizer=keras.optimizers.Adam(learning_rate=1e-3)", "Use a fixed learning rate so the demonstration is reproducible across runtimes."),
        ("early_stopping = keras.callbacks.EarlyStopping(", "Stop when validation loss no longer improves and restore the best epoch's weights."),
        ("finite = np.isfinite(observed) & np.isfinite(predicted)", "Evaluate every product using the same finite observed-predicted pairs."),
        ("domain_source = xr.open_dataset(DOMAIN_SAMPLE).load()", "Load the compact feature cube into memory so subsequent inference is deterministic and offline."),
        ("domain_frame = model_domain[MODEL_FEATURE_COLUMNS].to_dataframe().reset_index()", "Flatten the grid into rows while preserving coordinates and the trained feature-column order."),
        ("for fold in range(10):", "Run all ten folds; their predictions represent model-to-model uncertainty from resampling."),
        ("domain_frame[\"BC_DNN_PM25\"] = ensemble_model.predict(", "Combine baseline predictors and fold outputs using the trained ensemble model."),
        ("return tf.nn.depth_to_space(inputs, block_size=self.block_size)", "Rearrange learned channels into a grid that is five times finer in each spatial direction."),
        ("new_lat = np.arange(", "Construct explicit fine-grid coordinates so downscaled arrays retain geolocation."),
        ("native_point = native_fields.sel(lat=station.lat, lon=station.lon, method=\"nearest\")", "Sample the nearest native and downscaled cells using the same station coordinates."),
        ("station_bias_rows = []", "Calculate signed model-minus-ground bias for direct comparison across products."),
        ("aqi_breakpoints = np.array(", "Use AQI breakpoints as color anchors while retaining a continuous concentration scale."),
        ("color_norm = Normalize(vmin=0, vmax=AQI_MAX, clip=True)", "Apply one normalization to every panel so identical colors mean identical PM2.5 values."),
    ],
}


def add_inline_guidance() -> None:
    """Insert durable teaching comments immediately before major processing lines."""
    for name, guidance_items in INLINE_GUIDANCE.items():
        notebook = load(name)
        code_cells = [cell for cell in notebook["cells"] if cell["cell_type"] == "code"]
        for needle, explanation in guidance_items:
            matches = []
            for cell in code_cells:
                source_is_list = isinstance(cell["source"], list)
                source = "".join(cell["source"]) if source_is_list else cell["source"]
                source_had_trailing_newline = source.endswith("\n")
                source_lines = source.splitlines()
                for line_index, source_line in enumerate(source_lines):
                    if source_line.strip().startswith(needle):
                        matches.append((
                            cell,
                            source_lines,
                            line_index,
                            source_is_list,
                            source_had_trailing_newline,
                        ))
            if not matches:
                raise ValueError(f"Inline-guidance target not found in {name}: {needle}")
            cell, source_lines, line_index, source_is_list, source_had_trailing_newline = matches[0]
            source_line = source_lines[line_index]
            indentation = source_line[:len(source_line) - len(source_line.lstrip())]
            comment = f"{indentation}# {explanation}"
            if comment not in source_lines:
                source_lines.insert(line_index, comment)
                updated_source = "\n".join(source_lines)
                if source_is_list or source_had_trailing_newline:
                    updated_source += "\n"
                cell["source"] = lines(updated_source) if source_is_list else updated_source
        save(name, notebook)


if __name__ == "__main__":
    rebuild_module0()
    adapt_module1()
    adapt_module2()
    adapt_module3()
    add_inline_guidance()
    print("Prepared four Colab-portable notebooks in", NOTEBOOK_DIR)
