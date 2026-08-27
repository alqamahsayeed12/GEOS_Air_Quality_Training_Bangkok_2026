# Troubleshooting

## Colab Cannot Find the Repository

Restart the runtime, reopen the notebook from the README's Colab link, and rerun
the first setup cell. Confirm that GitHub is reachable from the browser.

## A Package Import Fails

Rerun the setup cell, then choose **Runtime > Restart session** if Colab requests
it. Include the printed package versions in a support issue.

## NASA OPeNDAP Is Slow or Unavailable

Wait briefly and retry the request. Reduce the time interval, bounding box, or
variable list. Module 2 uses bundled compact files and does not require the live
endpoint.

## OpenAQ Returns 401 or 403

Re-enter a current API key in the hidden prompt. Do not add the key to source.

## Outputs Disappeared

Colab runtime storage is temporary. Re-run the notebook or restore files that you
downloaded before the session ended.

