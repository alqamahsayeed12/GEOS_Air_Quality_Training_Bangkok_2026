"""Build compact, reproducible GEOS files for the participant repository."""

from pathlib import Path

import xarray as xr


SOURCE_ROOT = Path("/Volumes/Personal2/ADPC_UAH/GEOS_Data")
REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = REPOSITORY_ROOT / "data" / "module2" / "geos"
OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)

VARIABLES = [
    "WIND",
    "PS",
    "Q500",
    "Q850",
    "QV10M",
    "T10M",
    "T500",
    "T850",
    "U10M",
    "V10M",
    "BCSMASS",
    "DUSMASS25",
    "OCSMASS",
    "SO2SMASS",
    "SO4SMASS",
    "SSSMASS25",
    "TOTEXTTAU",
    "PM25",
    "BC_MLPM25",
    "GEOSPM25",
]

for date in ("20230505", "20230506"):
    source_path = SOURCE_ROOT / f"{date}.nc"
    output_path = OUTPUT_ROOT / f"{date}.nc"

    with xr.open_dataset(source_path) as source:
        available = [name for name in VARIABLES if name in source.data_vars]
        compact = source[available].isel(lat=slice(0, 120), lon=slice(0, 160)).load()
        compact.attrs.update(
            {
                "training_subset": "Bangkok 2026 Module 2 participant sample",
                "source_filename": source_path.name,
                "selection": "first 120 latitude and 160 longitude grid centers; all 24 forecast times",
            }
        )

    encoding = {
        name: {"zlib": True, "complevel": 4, "shuffle": True}
        for name in compact.data_vars
    }
    compact.to_netcdf(output_path, encoding=encoding)
    print(output_path, f"{output_path.stat().st_size / 1024**2:.2f} MiB")

# The collocation template must use exactly the same coordinates as the compact samples.
template = xr.Dataset(coords={"lat": compact["lat"], "lon": compact["lon"]})
template.attrs["description"] = "GEOS approximately 25 km grid used by Module 2 samples"
template_path = REPOSITORY_ROOT / "data" / "module2" / "geos_25km_grid_template.nc"
template.to_netcdf(template_path)
print(template_path, f"{template_path.stat().st_size / 1024**2:.3f} MiB")
