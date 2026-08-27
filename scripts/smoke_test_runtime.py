"""Exercise the bundled runtime assets without contacting external services."""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
os.environ.setdefault("MPLCONFIGDIR", "/tmp/geos-training-matplotlib")

import keras
import numpy as np
import pandas as pd
import tensorflow as tf
import xarray as xr


ROOT = Path(__file__).resolve().parents[1]


@keras.saving.register_keras_serializable(package="ADPC")
class DepthToSpace(keras.layers.Layer):
    def __init__(self, block_size=5, **kwargs):
        super().__init__(**kwargs)
        self.block_size = int(block_size)

    def call(self, inputs):
        return tf.nn.depth_to_space(inputs, block_size=self.block_size)

    def get_config(self):
        return {**super().get_config(), "block_size": self.block_size}


def assert_finite_prediction(model, feature_count: int) -> None:
    prediction = model.predict(
        np.zeros((1, feature_count), dtype=np.float32), verbose=0
    )
    if not np.isfinite(prediction).all():
        raise RuntimeError(f"Nonfinite prediction from {model.name}")


def main() -> None:
    module1 = ROOT / "data" / "module1"
    with xr.open_dataset(module1 / "geos_fp_global_pm25_snapshot.nc4") as dataset:
        assert "PM25" in dataset and dataset["PM25"].size > 0
        assert np.isfinite(dataset["PM25"].isel(time=0).values).any()

    required_species = {
        "PM25", "DUSMASS25", "SSSMASS25", "BCSMASS", "OCSMASS",
        "BRSMASS", "SO4SMASS", "NISMASS25", "NH4SMASS", "TOTEXTTAU",
    }
    with xr.open_dataset(module1 / "geos_fp_regional_aerosol_snapshot.nc4") as dataset:
        missing = required_species - set(dataset.data_vars)
        if missing:
            raise RuntimeError(f"Module 1 recovery NetCDF is missing {sorted(missing)}")

    observations = pd.read_csv(module1 / "openaq_reference_pm25_hourly.csv")
    required_observation_columns = {
        "location_id", "location_name", "datetime_utc", "pm25_ug_m3",
        "latitude", "longitude",
    }
    if not required_observation_columns.issubset(observations.columns):
        raise RuntimeError("Module 1 recovery observations have an invalid schema")
    if not pd.to_numeric(observations["pm25_ug_m3"], errors="coerce").notna().any():
        raise RuntimeError("Module 1 recovery observations contain no numeric PM2.5")

    model_root = ROOT / "data" / "module3" / "model_assets"
    for day in (1, 2, 3):
        fold = keras.models.load_model(
            model_root / f"v3_1_dnn_bias_Correction_day{day}_fold00.h5",
            compile=False,
        )
        assert_finite_prediction(fold, 20)
        ensemble = keras.models.load_model(
            model_root / f"v3_1_dnn_bias_Correction_day{day}_ensemble.h5",
            compile=False,
        )
        assert_finite_prediction(ensemble, 30)

    downscale = keras.models.load_model(
        model_root / "model_downscale_v1_colab.keras",
        custom_objects={"DepthToSpace": DepthToSpace},
        compile=False,
    )
    with xr.open_dataset(ROOT / "data" / "module3" / "module3_geos_domain_20230509_1930.nc") as domain:
        sample = np.zeros(
            (1, domain.sizes["lat"], domain.sizes["lon"], 1), dtype=np.float32
        )
    prediction = downscale.predict(sample, verbose=0)
    if not np.isfinite(prediction).all() or prediction.ndim != 4:
        raise RuntimeError("Downscaling model smoke prediction failed")

    print("Runtime smoke test passed")
    print("OpenAQ recovery rows:", f"{len(observations):,}")
    print("Bias-correction models exercised: 6")
    print("Downscaling output shape:", prediction.shape)


if __name__ == "__main__":
    main()
