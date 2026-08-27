# Maintenance and recovery

## Supported execution paths

- Google Colab with Python 3.10-3.12 and `requirements-lock.txt`.
- Local Python 3.11 using `environment.yml` or `requirements-local.txt`.
- Offline teaching mode using only files committed under `data/`.

Module 1 tries NASA GEOS-FP and OpenAQ first. A failed connection, missing
OpenAQ key, rate limit, or server error switches to the committed snapshots and
prints the active source. Modules 2 and 3 are fully bundled.

## Before every release

1. Create a branch and make the proposed change.
2. Run `python scripts/verify_package.py`.
3. In the locked environment, run `python scripts/smoke_test_runtime.py`.
4. Open every notebook in a fresh Colab runtime and run it from top to bottom.
5. Confirm the two GitHub Actions workflows pass.
6. Update `VERSION` and `CHANGELOG.md`.
7. Create an annotated tag such as `v2026.09.1` and a GitHub Release.

Never merge an automated dependency update solely because it is newer. Merge it
only after the model-loading and notebook smoke tests pass.

## Recovery during a class

If the live acquisition cell fails, continue with the bundled recovery mode. If
a participant environment is inconsistent, choose **Runtime > Disconnect and
delete runtime**, reopen the notebook, and rerun from the first cell. If `main`
is broken, open the most recent tagged release in Colab instead.

## Updating recovery snapshots

Use real service outputs, preserve native timestamps and metadata, and never
alter observations to make them match a model timestamp. After replacing any
file under `data/`, run `python scripts/build_data_manifest.py` so its SHA-256
checksum is recorded.

## Repository settings

Protect `main`, require both Actions checks before merging, require pull
requests, and disallow force pushes. Enable Dependabot security alerts and keep
GitHub Pages deployed from `docs/` on `main`.
