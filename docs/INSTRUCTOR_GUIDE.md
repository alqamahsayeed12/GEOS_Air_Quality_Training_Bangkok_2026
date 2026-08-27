# Instructor Guide

## Release Checklist

1. Confirm permission to redistribute all station samples and model assets.
2. Run all notebooks in a clean Colab runtime using the public GitHub URLs.
3. Verify that NASA OPeNDAP and OpenAQ endpoints still match Module 1.
4. Run `python scripts/verify_package.py` and review `data_manifest.csv`.
5. Create a versioned GitHub release before the course begins.
6. Freeze the participant branch during the live training.

## Classroom Workflow

- Demonstrate Module 0 before participants begin.
- Ask participants to save a Drive copy of every notebook.
- Keep a downloaded copy of the compact data as an offline contingency.
- Use GitHub Issues for questions that require follow-up after the session.
- Publish corrected notebooks through reviewed pull requests and announce the
  commit or release tag participants should use.

## Scientific Invariants

- Ground PM2.5 valid range: `1-1000 µg/m³` inclusive.
- Complete three-hour means require `n_obs = 3`.
- UTC bins are `[00:00,03:00) -> 01:30`, then every three hours.
- Spatial matching uses nearest GEOS grid center by Haversine distance.
- Forecast day is retained with initialization and valid timestamps.
- Static global min-max values are reused during model training and inference.

