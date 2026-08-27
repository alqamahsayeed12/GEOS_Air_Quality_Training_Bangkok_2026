# Module 1 recovery data

These files keep the acquisition and mapping lesson runnable when NASA OPeNDAP
or OpenAQ is temporarily unavailable. The notebook always reports whether it is
using a live service or a bundled snapshot.

| File | Purpose |
|---|---|
| `geos_fp_global_pm25_snapshot.nc4` | One real global native GEOS-FP PM2.5 field for the global map exercise |
| `geos_fp_regional_aerosol_snapshot.nc4` | One real Southeast Asia field containing native PM2.5 and aerosol species |
| `openaq_reference_pm25_stations.csv` | Archived station metadata produced by the Module 1 OpenAQ workflow |
| `openaq_reference_pm25_hourly.csv` | Archived hourly PM2.5 produced by the Module 1 OpenAQ workflow |

The GEOS and OpenAQ recovery snapshots retain their original timestamps. When
their times do not coincide, the notebook labels the overlay as a spatial
teaching example and does not present it as validation or temporal collocation.
