# GEOS Air Quality Training: Bangkok 2026

Collaborative, Colab-first materials for the **Technical Training on GEOS Data
for Air Quality Monitoring in Lao PDR**, Bangkok, 7-9 September 2026.

The course progresses from GEOS-FP data acquisition to ground-station QA/QC,
spatial and temporal collocation, model evaluation, bias correction, and domain
downscaling. The notebooks include compact, versioned training data so every
participant can reproduce the worked examples in Google Colab.

[Open the course portal](https://alqamahsayeed12.github.io/GEOS_Air_Quality_Training_Bangkok_2026/)

## Start Here

1. Sign in to a Google account.
2. Open **Module 0** using the button below.
3. In Colab, choose **File > Save a copy in Drive**.
4. Choose **Runtime > Run all** and confirm that the asset check passes.
5. Return here and open Modules 1-3 in order.
6. Save a personal Drive copy before editing each notebook.

| Module | Topic | Launch |
|---|---|---|
| 0 | Google Colab setup and environment verification | [Open in Colab](https://colab.research.google.com/github/alqamahsayeed12/GEOS_Air_Quality_Training_Bangkok_2026/blob/main/notebooks/00_module0_google_colab_setup.ipynb) |
| 1 | Acquire, subset, and map GEOS-FP aerosol data | [Open in Colab](https://colab.research.google.com/github/alqamahsayeed12/GEOS_Air_Quality_Training_Bangkok_2026/blob/main/notebooks/01_module1_download_geos_fp.ipynb) |
| 2 | Thai PCD and Lao PDR AQMS QA/QC and GEOS 25 km collocation | [Open in Colab](https://colab.research.google.com/github/alqamahsayeed12/GEOS_Air_Quality_Training_Bangkok_2026/blob/main/notebooks/02_module2_ground_stations_qaqc_geos25km_collocation.ipynb) |
| 3 | Bias correction and spatial downscaling | [Open in Colab](https://colab.research.google.com/github/alqamahsayeed12/GEOS_Air_Quality_Training_Bangkok_2026/blob/main/notebooks/03_module3_bias_correction_and_downscaling.ipynb) |

## Course Sequence

**Module 0 - Colab setup**  
Clone the training repository, install the declared environment, and verify all
participant assets.

**Module 1 - Download GEOS-FP**  
Inspect aerosol variables, retrieve data through NASA OPeNDAP, map global and
participant-defined domains, compare embedded and reconstructed PM2.5, and
retrieve matching OpenAQ reference-monitor data.

**Module 2 - Ground stations and collocation**  
Apply explicit `1-1000 µg/m³` QA/QC, convert local time to UTC, calculate complete
three-hour averages (`n_obs = 3`) at GEOS midpoint timestamps, match Thai PCD and
Lao PDR AQMS stations to GEOS grid centers with the Haversine distance, and assess
forecast Days 1-3.

**Module 3 - Correction and downscaling**  
Compare raw GEOS, linear correction, Random Forest, and DNN models; apply static
global min-max normalization; run the v3.1 ensemble; and compare native and
downscaled PM2.5 fields with ground observations.

## Participant Files

```text
notebooks/          four ordered Colab notebooks
data/module2/       station samples, compact GEOS files, evaluation table
data/module3/       training sample, model assets, domain example
docs/               course portal, presentation, participant guides
scripts/            package verification and provenance utilities
outputs/            generated at run time and ignored by Git
```

The repository contains compact teaching products, not the complete research
archive. See [Data Sources and Licenses](docs/DATA_SOURCES_AND_LICENSES.md) and
the machine-readable [data manifest](data_manifest.csv).

## OpenAQ API Key

Only the live OpenAQ exercise in Module 1 requires a personal key. Register at
[OpenAQ Explorer](https://explore.openaq.org/register), then enter the key in the
hidden Colab prompt. Never paste keys into notebook source, outputs, issues, or
commits. See [API Key Setup](docs/API_KEY_SETUP.md).

## Local Use

Google Colab is the supported participant environment. For local Jupyter:

```bash
git clone https://github.com/alqamahsayeed12/GEOS_Air_Quality_Training_Bangkok_2026.git
cd GEOS_Air_Quality_Training_Bangkok_2026
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-local.txt
jupyter lab
```

## Collaboration

- Use **Issues** for setup problems, questions, and reproducible bug reports.
- Create a branch for code or documentation changes and submit a pull request.
- Do not commit API keys, participant personal information, or unapproved data.
- Run `python scripts/verify_package.py` before submitting changes.

## Authoritative Services

- [NASA GEOS-FP aerosol OPeNDAP collection](https://opendap.nccs.nasa.gov/dods/GEOS-5/fp/0.25_deg/fcast/tavg3_2d_aer_Nx)
- [NASA GMAO products](https://gmao.gsfc.nasa.gov/gmao-products/)
- [OpenAQ API documentation](https://docs.openaq.org/)
- [Google Colab FAQ](https://research.google.com/colaboratory/faq.html)

## License

Original code is released under the MIT License. Original training text and
figures are released under CC BY 4.0. Third-party data, imagery, logos, basemaps,
and model assets retain their original terms; see the data source register.

