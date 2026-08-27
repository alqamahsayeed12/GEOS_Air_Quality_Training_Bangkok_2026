# Publishing the Participant Repository

## 1. Final Release Checks

1. Confirm permission to redistribute the Thai PCD and Lao PDR AQMS station
   files listed in `data_manifest.csv`.
2. Confirm that partner logos may be used in the public course site.
3. Run `python scripts/verify_package.py`.
4. Run `python scripts/smoke_test_runtime.py` in the locked environment.
5. Review `git status` and confirm no outputs, API keys, or unrelated files are
   staged.

## 2. Create the Public GitHub Repository

With GitHub CLI authenticated as `alqamahsayeed12`:

```bash
cd /path/to/GEOS_Air_Quality_Training_Bangkok_2026
gh repo create alqamahsayeed12/GEOS_Air_Quality_Training_Bangkok_2026 \
  --public --source=. --remote=origin --push
```

If the repository already exists:

```bash
git remote add origin https://github.com/alqamahsayeed12/GEOS_Air_Quality_Training_Bangkok_2026.git
git push -u origin main
```

## 3. Enable the Course Portal

In GitHub, open **Settings > Pages**. Under **Build and deployment**, choose
**Deploy from a branch**, select `main`, choose `/docs`, and save. The portal
will be published at:

`https://alqamahsayeed12.github.io/GEOS_Air_Quality_Training_Bangkok_2026/`

## 4. Test as a Participant

1. Open the published portal in a signed-out browser window.
2. Open Module 0 in Colab and save a Drive copy.
3. Run Module 0 from a fresh hosted runtime.
4. Run Module 2 through the collocation and full-period evaluation sections.
5. Run Module 3 and confirm the final four-panel figure appears.
6. Test the issue templates without submitting a real issue.

## 5. Protect the Main Branch

In **Settings > Branches**, require a pull request and both Actions checks before
merging into `main`. Disable force pushes. Enable Dependabot alerts and review
its monthly pull requests only after both checks pass.

## 6. Freeze the Training Version

Create a GitHub release such as `v2026.09-training`. Ask participants to use the
release tag or the unchanged `main` branch during the event. Publish corrections
through reviewed commits and state the exact commit participants should reopen.
