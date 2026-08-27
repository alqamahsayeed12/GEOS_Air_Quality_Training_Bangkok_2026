# Troubleshooting

## Colab Cannot Find the Repository

Restart the runtime, reopen the notebook from the README's Colab link, and rerun
the first setup cell. Confirm that GitHub is reachable from the browser.

## A Package Import Fails

Rerun the setup cell, then choose **Runtime > Restart session** if Colab requests
it. Include the printed package versions in a support issue.

## NASA OPeNDAP Is Slow or Unavailable

Module 1 automatically opens its bundled GEOS recovery snapshots and prints the
live-service error. Continue the mapping exercise in recovery mode. Retry the
live request later by rerunning the acquisition cell. Modules 2 and 3 do not
require the live endpoint.

## OpenAQ Returns 401 or 403

Re-enter a current API key in the hidden prompt. If live access is not required,
press Enter without a key and continue with the bundled OpenAQ recovery tables.
Do not add the key to source.

## A Dependency Update Breaks a Notebook

Disconnect and delete the Colab runtime, then rerun the notebook so it installs
`requirements-lock.txt`. If the current `main` branch is under repair, use the
most recent tagged GitHub Release.

## Outputs Disappeared

Colab runtime storage is temporary. Re-run the notebook or restore files that you
downloaded before the session ended.
