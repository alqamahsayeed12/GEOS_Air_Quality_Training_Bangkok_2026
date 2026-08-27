# Participant Package Inventory

This register describes the files required to run the four course notebooks from
a fresh Google Colab runtime. Exact file sizes and SHA-256 checksums are stored
in `data_manifest.csv`.

## Notebooks

| Module | Notebook | Runtime inputs |
|---|---|---|
| 0 | `00_module0_google_colab_setup.ipynb` | Repository, locked environment, and package verifier |
| 1 | `01_module1_download_geos_fp.ipynb` | Live NASA/OpenAQ services with bundled recovery data |
| 2 | `02_module2_ground_stations_qaqc_geos25km_collocation.ipynb` | Module 2 station, grid, GEOS, and evaluation assets |
| 3 | `03_module3_bias_correction_and_downscaling.ipynb` | Module 3 sample data, scalars, fold models, ensemble, and downscaler |

## Module 1 Recovery Data

- One global native GEOS-FP PM2.5 field for the global map
- One Southeast Asia native GEOS-FP field with PM2.5 and nine aerosol/optical variables
- Archived OpenAQ station metadata and 1,926 hourly PM2.5 records

The notebook reports the active source. Recovery timestamps remain unchanged,
and a nonmatching GEOS/OpenAQ overlay is labeled as spatial context rather than
temporal validation.

## Module 2 Data

- 14 complete Lao PDR AQMS station CSV files
- 96 compact Thai PCD station CSV examples
- `geos_25km_grid_template.nc`
- Two compact GEOS files: `20230505.nc` and `20230506.nc`
- `full_period_aqms_geos_evaluation.csv` for forecast Days 1-3

Each compact GEOS file contains 24 timestamps and the 20 fields used in the
collocation and modeling workflow:

`WIND`, `PS`, `Q500`, `Q850`, `QV10M`, `T10M`, `T500`, `T850`, `U10M`,
`V10M`, `BCSMASS`, `DUSMASS25`, `OCSMASS`, `SO2SMASS`, `SO4SMASS`,
`SSSMASS25`, `TOTEXTTAU`, `PM25`, `BC_MLPM25`, and `GEOSPM25`.

## Module 3 Data and Models

### Demonstration data

- `aqms_geos_collocated_training_sample_day1.csv`
- `module3_geos_domain_20230509_1930.nc`
- `module3_ground_20230509_1930.csv`

### Static normalization

`max_min4.csv` contains global minima and maxima for the 17 physical and aerosol
predictors. Module 3 explicitly assigns fixed `0-1000 µg/m³` bounds to `PM25`,
`BC_MLPM25`, and `GEOSPM25`, completing the 20-feature fold-model input.

### Bias-correction models

- 30 fold models: ten each for forecast Days 1, 2, and 3
- Three ensemble models: one each for forecast Days 1, 2, and 3
- Fold-model input shape: 20 predictors; output: one PM2.5 value
- Ensemble input shape: 30 predictors, consisting of 20 predictors plus ten fold outputs

### Spatial downscaling

- `model_downscale_v1_colab.keras`
- Input: one native-grid PM2.5 channel
- Output: one PM2.5 channel at five-times finer spatial sampling
- Required custom layer `DepthToSpace` is defined in Module 3 before loading

## Presentation and Collaboration Files

- Responsive GitHub Pages course portal
- Interactive Day 1 HTML presentation
- 24-hour GEOS PM2.5 frames, hover values, and wind field
- Animation, figures, logos, Leaflet velocity library, and notebook previews
- Participant, instructor, API-key, troubleshooting, publishing, and licensing guides
- GitHub issue templates, static validation, scheduled runtime smoke testing,
  pinned dependencies, and Dependabot review

## Automated Verification

Run:

```bash
python scripts/verify_package.py
```

The check verifies required paths, notebook syntax, portable source paths,
station/model counts, all expected Day 1-3 model names, scalar feature coverage,
manifest completeness, SHA-256 checksums, presentation links, file-size limits,
and common secret patterns.

After dependency, model, or NetCDF changes, also run:

```bash
python scripts/smoke_test_runtime.py
```
