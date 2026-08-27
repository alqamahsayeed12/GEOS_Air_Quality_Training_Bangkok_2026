#!/usr/bin/env python3
"""Build the forecast-day-1 GEOS comparison for Thai PCD and Lao PDR AQMS."""

from pathlib import Path
import os

import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = Path(
    "/Volumes/Personal2/ADPC_UAH/"
    "GEOS_RAW_TRAINING_DATASETS_MERGED_ORIGINAL_IN_NETCDF_20230505_20240930/"
    "training_eval_day1.csv"
)
SOURCE = Path(os.environ.get("DAY1_EVALUATION_CSV", DEFAULT_SOURCE))
OUTPUT = ROOT / "docs/presentation/assets/day1_geos_ground_network_scatter.png"
SUMMARY = ROOT / "docs/presentation/assets/day1_geos_ground_network_metrics.csv"

NETWORK_LABELS = {
    "PCD": "Thai PCD",
    "AQMS": "Lao PDR AQMS",
}
AXIS_MAX = 500
QA_MIN = 1
QA_MAX = 1000
GRID_BINS = 125


def metrics(observed, modeled):
    error = modeled - observed
    denominator = np.sum(
        (np.abs(modeled - observed.mean()) + np.abs(observed - observed.mean())) ** 2
    )
    return {
        "N": len(observed),
        "IOA": 1 - np.sum(error**2) / denominator if denominator else np.nan,
        "r": np.corrcoef(observed, modeled)[0, 1],
        "slope": np.polyfit(observed, modeled, 1)[0],
        "RMSE": np.sqrt(np.mean(error**2)),
        "mean_bias": np.mean(error),
    }


if not SOURCE.exists():
    raise FileNotFoundError(
        f"Day-1 evaluation table not found: {SOURCE}\n"
        "Set DAY1_EVALUATION_CSV to the merged day-1 training/evaluation CSV."
    )

columns = [
    "network",
    "station_code",
    "forecast_day",
    "datetime_utc",
    "obs_pm25",
    "obs_n_obs",
    "GEOSPM25",
]
data = pd.read_csv(SOURCE, usecols=columns)
data["datetime_utc"] = pd.to_datetime(data["datetime_utc"], errors="coerce", utc=True)
data = data[
    data["network"].isin(NETWORK_LABELS)
    & data["forecast_day"].eq(1)
    & data["obs_n_obs"].eq(3)
    & data["obs_pm25"].between(QA_MIN, QA_MAX)
    & data["GEOSPM25"].between(QA_MIN, QA_MAX)
].copy()

network_data = {}
summary_rows = []
max_density = 0.0
edges = np.linspace(0, AXIS_MAX, GRID_BINS + 1)

for network in NETWORK_LABELS:
    subset = data[data["network"].eq(network)]
    observed = subset["obs_pm25"].to_numpy(dtype=float)
    modeled = subset["GEOSPM25"].to_numpy(dtype=float)
    density, _, _ = np.histogram2d(observed, modeled, bins=(edges, edges))
    density = density / len(subset) * 100.0
    positive = density[density > 0]
    if positive.size:
        max_density = max(max_density, float(positive.max()))
    network_data[network] = (subset, observed, modeled, density)

    row = {"network": NETWORK_LABELS[network], "stations": subset["station_code"].nunique()}
    row.update(metrics(observed, modeled))
    row["start_utc"] = subset["datetime_utc"].min()
    row["end_utc"] = subset["datetime_utc"].max()
    summary_rows.append(row)

fig, axes = plt.subplots(1, 2, figsize=(14.8, 6.7), sharex=True, sharey=True)
fig.patch.set_facecolor("white")
norm = LogNorm(vmin=0.0002, vmax=max_density)

for ax, network in zip(axes, NETWORK_LABELS):
    subset, observed, modeled, density = network_data[network]
    masked_density = np.ma.masked_where(density.T <= 0, density.T)
    image = ax.pcolormesh(
        edges,
        edges,
        masked_density,
        cmap="inferno",
        norm=norm,
        shading="auto",
    )
    ax.plot([0, AXIS_MAX], [0, AXIS_MAX], color="#57606a", linewidth=1.3, linestyle=(0, (4, 3)))
    ax.set_xlim(0, AXIS_MAX)
    ax.set_ylim(0, AXIS_MAX)
    ax.set_aspect("equal", adjustable="box")
    ax.grid(False)
    ax.set_facecolor("#f7f7f8")
    ax.tick_params(labelsize=10.5, colors="#3a3a3c")
    for spine in ax.spines.values():
        spine.set_color("#c7c7cc")

    result = metrics(observed, modeled)
    ax.set_title(
        f"{NETWORK_LABELS[network]}  |  {subset['station_code'].nunique()} stations",
        loc="left",
        fontsize=16,
        fontweight="bold",
        pad=13,
        color="#1d1d1f",
    )
    metric_text = (
        f"N = {result['N']:,}\n"
        f"IOA = {result['IOA']:.3f}\n"
        f"r = {result['r']:.3f}\n"
        f"slope = {result['slope']:.3f}\n"
        f"RMSE = {result['RMSE']:.2f}\n"
        f"mean bias = {result['mean_bias']:+.2f}"
    )
    ax.text(
        0.035,
        0.965,
        metric_text,
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=10.5,
        color="#1d1d1f",
        bbox={"boxstyle": "round,pad=0.55", "facecolor": "white", "edgecolor": "none", "alpha": 0.9},
    )
    ax.set_xlabel("Observed PM$_{2.5}$ (µg m$^{-3}$)", fontsize=12, color="#1d1d1f")

axes[0].set_ylabel("GEOS-FP PM$_{2.5}$ (µg m$^{-3}$)", fontsize=12, color="#1d1d1f")

# Keep the shared legend outside both scatter panels.
cbar_ax = fig.add_axes([0.31, 0.075, 0.38, 0.026])
cbar = fig.colorbar(image, cax=cbar_ax, orientation="horizontal")
cbar.set_label("Share of network records per bin (%)", fontsize=10.5, color="#3a3a3c", labelpad=5)
cbar.ax.tick_params(labelsize=9, colors="#3a3a3c")

fig.subplots_adjust(left=0.075, right=0.975, bottom=0.18, top=0.93, wspace=0.14)
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUTPUT, dpi=220, facecolor="white")
plt.close(fig)

pd.DataFrame(summary_rows).to_csv(SUMMARY, index=False)
print(f"Saved {OUTPUT}")
print(f"Saved {SUMMARY}")
print(pd.DataFrame(summary_rows).to_string(index=False))
