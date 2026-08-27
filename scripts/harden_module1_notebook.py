"""Apply the maintained live-first/offline-recovery cells to Module 1."""

from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent


ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "notebooks" / "01_module1_download_geos_fp.ipynb"


def lines(text: str) -> list[str]:
    return (dedent(text).strip() + "\n").splitlines(keepends=True)


notebook = json.loads(NOTEBOOK.read_text(encoding="utf-8"))

notebook["cells"][4]["source"] = lines('''
## 1. Acquire the GEOS-FP aerosol collection

The `.latest` endpoint follows the current operational forecast cycle. The cell
tries the live NASA service first and validates it with a small data read. If the
service is unavailable, it opens the committed Southeast Asia recovery snapshot
and prints that choice. Set `PREFER_LIVE_GEOS = False` to demonstrate the
offline path deliberately.
''')

notebook["cells"][5]["source"] = lines('''
# --- What this cell does ---
# Opens the live GEOS-FP aerosol forecast and verifies a real value can be read.
# Falls back to a timestamp-preserving regional snapshot if the service fails.
# Normalizes variable names and units and reports the active source explicitly.
# --- End annotation ---
OPENDAP_URL = (
    "https://opendap.nccs.nasa.gov/dods/GEOS-5/fp/0.25_deg/"
    "fcast/tavg3_2d_aer_Nx.latest"
)
MODULE1_DATA = TRAINING_ROOT / "data" / "module1"
REGIONAL_RECOVERY_FILE = MODULE1_DATA / "geos_fp_regional_aerosol_snapshot.nc4"
GLOBAL_RECOVERY_FILE = MODULE1_DATA / "geos_fp_global_pm25_snapshot.nc4"
PREFER_LIVE_GEOS = True

requested_aerosol_variables = [
    "PM25", "DUSMASS25", "SSSMASS25", "BCSMASS", "OCSMASS",
    "BRSMASS", "SO4SMASS", "NISMASS25", "NH4SMASS", "TOTEXTTAU",
]


def normalize_geos_dataset(dataset):
    """Normalize GrADS names, decode its historical time units, and add units."""
    time_units = dataset.time.attrs.get("units", "")
    if time_units.startswith("days since 1-1-1"):
        dataset.time.attrs["units"] = time_units.replace(
            "days since 1-1-1", "days since 0001-01-01", 1
        )
    dataset = xr.decode_cf(dataset)
    dataset = dataset.rename({name: name.upper() for name in dataset.data_vars})
    concentration_variables = {
        "PM25", "DUSMASS25", "SSSMASS25", "BCSMASS", "OCSMASS",
        "BRSMASS", "SO4SMASS", "NISMASS25", "NH4SMASS",
    }
    for name in concentration_variables.intersection(dataset.data_vars):
        dataset[name].attrs["units"] = "kg m-3"
    if "TOTEXTTAU" in dataset:
        dataset["TOTEXTTAU"].attrs["units"] = "1"
    return dataset


GEOS_LIVE_AVAILABLE = False
geos_live_error = None
try:
    if not PREFER_LIVE_GEOS:
        raise RuntimeError("Live GEOS access disabled by participant")
    candidate = xr.open_dataset(OPENDAP_URL, engine="netcdf4", decode_times=False)
    candidate = normalize_geos_dataset(candidate)
    # OPeNDAP access is lazy. Read one actual value so a failed server is caught here.
    _ = candidate["PM25"].isel(time=0, lat=0, lon=0).load().item()
    ds = candidate
    GEOS_LIVE_AVAILABLE = True
    GEOS_SOURCE_MODE = "live NASA GEOS-FP OPeNDAP"
except Exception as error:
    geos_live_error = f"{type(error).__name__}: {error}"
    ds = normalize_geos_dataset(xr.open_dataset(REGIONAL_RECOVERY_FILE, decode_times=False))
    GEOS_SOURCE_MODE = "bundled GEOS-FP regional recovery snapshot"

available_aerosol_variables = [
    variable for variable in requested_aerosol_variables if variable in ds.data_vars
]
missing_aerosol_variables = [
    variable for variable in requested_aerosol_variables if variable not in ds.data_vars
]
available_times_utc = pd.to_datetime(ds.time.values, utc=True)

print("GEOS source:", GEOS_SOURCE_MODE)
if geos_live_error:
    print("Live-service reason:", geos_live_error)
print(ds)
print("Available training variables:", available_aerosol_variables)
print("Missing from this source:", missing_aerosol_variables or "none")
print("Available valid times:", available_times_utc[0], "to", available_times_utc[-1])
''')

notebook["cells"][7]["source"] = lines('''
# --- What this cell does ---
# Loads one global GEOS PM2.5 field from the live service when available.
# Uses the bundled real global snapshot if the live service failed.
# Converts concentration units and draws a global Cartopy map.
# --- End annotation ---
GLOBAL_VARIABLE = "PM25"
GLOBAL_TIME_INDEX = 0

if GEOS_LIVE_AVAILABLE:
    global_field = ds[GLOBAL_VARIABLE].isel(time=GLOBAL_TIME_INDEX).load()
    global_source_label = GEOS_SOURCE_MODE
else:
    with xr.open_dataset(GLOBAL_RECOVERY_FILE) as global_recovery:
        global_field = global_recovery[GLOBAL_VARIABLE].isel(time=0).load()
    global_source_label = "bundled real GEOS-FP global recovery snapshot"

global_units = global_field.attrs.get("units", "")
if "kg" in global_units and "m-3" in global_units:
    global_field = global_field * 1e9
    global_units = "µg m⁻³"

finite = np.asarray(global_field.values)[np.isfinite(global_field.values)]
color_max = float(np.nanpercentile(finite, 99))

fig = plt.figure(figsize=(15, 6.5))
ax = plt.axes(projection=ccrs.Robinson())
mesh = ax.pcolormesh(
    global_field.lon, global_field.lat, global_field,
    transform=ccrs.PlateCarree(), cmap="inferno_r",
    vmin=0, vmax=color_max, shading="auto",
)
ax.set_global()
ax.add_feature(cfeature.LAND, facecolor="#eeeeea", zorder=0)
ax.add_feature(cfeature.COASTLINE, linewidth=0.55)
ax.add_feature(cfeature.BORDERS, linewidth=0.35, alpha=0.65)
ax.set_title(
    f"GEOS-FP {GLOBAL_VARIABLE} | {pd.Timestamp(global_field.time.values)} UTC\\n"
    f"Source: {global_source_label}"
)
plt.colorbar(
    mesh, ax=ax, orientation="horizontal", pad=0.05, shrink=0.72,
    label=f"{GLOBAL_VARIABLE} ({global_units})",
)
plt.show()
''')

notebook["cells"][9]["source"] = lines('''
# --- What this cell does ---
# Collects the participant-controlled bounding box, UTC interval, and variables.
# Defaults to the first 24 hours, or all available times in a shorter snapshot.
# --- End annotation ---
BBOX = [95.0, 5.0, 110.0, 25.0]  # west, south, east, north
DATE_FROM = available_times_utc[0].isoformat()
DATE_TO = available_times_utc[min(7, ds.sizes["time"] - 1)].isoformat()

VARIABLES = [
    variable for variable in [
        "PM25", "DUSMASS25", "SSSMASS25", "BCSMASS", "OCSMASS",
        "BRSMASS", "SO4SMASS", "NISMASS25", "NH4SMASS",
    ]
    if variable in ds.data_vars
]

print("BBOX:", BBOX)
print("UTC interval:", DATE_FROM, "to", DATE_TO)
print("Requested variables:", VARIABLES)
print("GEOS source:", GEOS_SOURCE_MODE)
''')

cell10 = "".join(notebook["cells"][10]["source"])
cell10 = cell10.replace(
    'raise KeyError(f"These variables are unavailable in the live collection: {unknown}")',
    'raise KeyError(f"These variables are unavailable in the active GEOS source: {unknown}")',
)
cell10 = cell10.replace(
    '"source_opendap_url": OPENDAP_URL,',
    '"source_mode": GEOS_SOURCE_MODE,\n    "source_opendap_url": OPENDAP_URL if GEOS_LIVE_AVAILABLE else "",\n    "recovery_file": "" if GEOS_LIVE_AVAILABLE else REGIONAL_RECOVERY_FILE.name,',
)
notebook["cells"][10]["source"] = lines(cell10)

notebook["cells"][18]["source"] = lines('''
## 6. Download matching reference-monitor PM2.5 from OpenAQ

OpenAQ API v3 requires a free personal API key for the live exercise. Register
through [OpenAQ Explorer](https://explore.openaq.org/register), then copy the key
from [Account Settings](https://explore.openaq.org/account). The hidden prompt
does not save the key in the notebook.

Press **Enter without a key**, set `PREFER_LIVE_OPENAQ = False`, or continue after
a network/API failure to use the committed OpenAQ recovery tables. Their original
timestamps are retained. If those timestamps differ from the active GEOS field,
the final map is explicitly a spatial teaching overlay, not temporal validation.

Never put a key in a code cell, notebook output, screenshot, issue, or commit.
''')

notebook["cells"][19]["source"] = lines('''
# --- What this cell does ---
# Requests an OpenAQ API key through a hidden prompt and queries live locations.
# Selects the bundled recovery path if the key is blank or the request fails.
# --- End annotation ---
PREFER_LIVE_OPENAQ = True
OPENAQ_BASE = "https://api.openaq.org/v3"
OPENAQ_API_KEY = getpass(
    "Paste your OpenAQ API key, or press Enter for the bundled recovery data: "
).strip()
headers = {"X-API-Key": OPENAQ_API_KEY} if OPENAQ_API_KEY else {}
bbox_text = ",".join(map(str, BBOX))

locations = []
openaq_live_error = None
OPENAQ_LIVE_AVAILABLE = False
if PREFER_LIVE_OPENAQ and OPENAQ_API_KEY:
    try:
        location_response = requests.get(
            f"{OPENAQ_BASE}/locations",
            headers=headers,
            params={
                "bbox": bbox_text,
                "parameters_id": 2,
                "monitor": "true",
                "mobile": "false",
                "limit": 1000,
                "page": 1,
            },
            timeout=60,
        )
        location_response.raise_for_status()
        locations = location_response.json().get("results", [])
        if not locations:
            raise RuntimeError("The live query returned no matching locations")
        OPENAQ_LIVE_AVAILABLE = True
    except Exception as error:
        openaq_live_error = f"{type(error).__name__}: {error}"
elif not OPENAQ_API_KEY:
    openaq_live_error = "No API key entered"
else:
    openaq_live_error = "Live OpenAQ access disabled by participant"

OPENAQ_SOURCE_MODE = (
    "live OpenAQ API v3" if OPENAQ_LIVE_AVAILABLE
    else "bundled OpenAQ recovery snapshot"
)
print("OpenAQ source:", OPENAQ_SOURCE_MODE)
if openaq_live_error:
    print("Live-service reason:", openaq_live_error)
print("Reference-monitor locations returned:", len(locations))
''')

notebook["cells"][20]["source"] = lines('''
# --- What this cell does ---
# Downloads live hourly OpenAQ PM2.5 with caching, pagination, and retries.
# Loads schema-compatible recovery tables if the live path yields no observations.
# Applies concentration QA/QC and records the source and original time coverage.
# --- End annotation ---
import json
import time

OPENAQ_CACHE_DIR = OUTPUT_DIR / "openaq_hour_cache"
OPENAQ_CACHE_DIR.mkdir(parents=True, exist_ok=True)


def get_openaq_sensor_page(sensor_id, page):
    """Download one sensor page with caching and bounded retries."""
    cache_file = OPENAQ_CACHE_DIR / f"sensor_{sensor_id}_page_{page}.json"
    if cache_file.exists():
        return json.loads(cache_file.read_text(encoding="utf-8")), None
    for attempt in range(1, 4):
        try:
            response = requests.get(
                f"{OPENAQ_BASE}/sensors/{sensor_id}/hours",
                headers=headers,
                params={
                    "datetime_from": start.isoformat(),
                    "datetime_to": end.isoformat(),
                    "limit": 1000,
                    "page": page,
                },
                timeout=60,
            )
            if response.status_code == 429:
                time.sleep(max(int(float(response.headers.get("X-Ratelimit-Reset", 5))), 1) + 1)
                continue
            if response.status_code >= 500:
                time.sleep(5 * attempt)
                continue
            response.raise_for_status()
            payload = response.json()
            cache_file.write_text(json.dumps(payload), encoding="utf-8")
            return payload, None
        except requests.RequestException as error:
            if attempt == 3:
                return None, f"{type(error).__name__}: {error}"
            time.sleep(5 * attempt)
    return None, "request attempts exhausted"


station_rows = []
measurement_rows = []
failed_requests = []
if OPENAQ_LIVE_AVAILABLE:
    for location in locations:
        coordinates = location.get("coordinates") or {}
        pm25_sensors = [
            sensor for sensor in location.get("sensors", [])
            if (sensor.get("parameter") or {}).get("name") == "pm25"
        ]
        for sensor in pm25_sensors:
            station_rows.append({
                "location_id": location.get("id"),
                "location_name": location.get("name"),
                "sensor_id": sensor.get("id"),
                "sensor_name": sensor.get("name"),
                "latitude": coordinates.get("latitude"),
                "longitude": coordinates.get("longitude"),
                "country": (location.get("country") or {}).get("code"),
                "provider": (location.get("provider") or {}).get("name"),
                "owner": (location.get("owner") or {}).get("name"),
                "instruments": "; ".join(
                    item.get("name", "") for item in location.get("instruments", [])
                ),
                "monitor": location.get("isMonitor", location.get("monitor", True)),
            })
            page = 1
            while True:
                payload, error_message = get_openaq_sensor_page(sensor["id"], page)
                if payload is None:
                    failed_requests.append({
                        "location_id": location.get("id"), "sensor_id": sensor.get("id"),
                        "page": page, "error": error_message,
                    })
                    break
                rows = payload.get("results", [])
                for item in rows:
                    period = item.get("period") or {}
                    datetime_to = period.get("datetimeTo") or item.get("datetime") or {}
                    measurement_rows.append({
                        "location_id": location.get("id"),
                        "location_name": location.get("name"),
                        "sensor_id": sensor.get("id"),
                        "datetime_utc": datetime_to.get("utc"),
                        "pm25_ug_m3": item.get("value"),
                        "latitude": coordinates.get("latitude"),
                        "longitude": coordinates.get("longitude"),
                        "provider": (location.get("provider") or {}).get("name"),
                        "owner": (location.get("owner") or {}).get("name"),
                    })
                found = int((payload.get("meta") or {}).get("found", len(rows)))
                if page * 1000 >= found or not rows:
                    break
                page += 1

stations = pd.DataFrame(station_rows)
observations = pd.DataFrame(measurement_rows)
failed = pd.DataFrame(failed_requests)

if observations.empty:
    stations = pd.read_csv(MODULE1_DATA / "openaq_reference_pm25_stations.csv")
    observations = pd.read_csv(MODULE1_DATA / "openaq_reference_pm25_hourly.csv")
    failed = pd.DataFrame(columns=["location_id", "sensor_id", "page", "error"])
    OPENAQ_SOURCE_MODE = "bundled OpenAQ recovery snapshot"

stations = stations.drop_duplicates(subset=["sensor_id"]).copy()
observations["datetime_utc"] = pd.to_datetime(observations["datetime_utc"], utc=True)
observations["pm25_ug_m3"] = pd.to_numeric(observations["pm25_ug_m3"], errors="coerce")
observations = observations[
    observations["pm25_ug_m3"].between(0, 1000, inclusive="both")
    & observations["longitude"].between(west, east)
    & observations["latitude"].between(south, north)
].copy()

observation_start = observations["datetime_utc"].min()
observation_end = observations["datetime_utc"].max()
observation_period_text = f"{observation_start} to {observation_end}"

stations_file = OUTPUT_DIR / "openaq_reference_pm25_stations.csv"
observations_file = OUTPUT_DIR / "openaq_reference_pm25_hourly.csv"
failed_file = OUTPUT_DIR / "openaq_failed_sensor_requests.csv"
stations.to_csv(stations_file, index=False)
observations.to_csv(observations_file, index=False)
failed.to_csv(failed_file, index=False)

print("OpenAQ source:", OPENAQ_SOURCE_MODE)
print("Observation time coverage:", observation_period_text)
print("Station-sensor records:", len(stations))
print("Valid hourly observations in BBOX:", len(observations))
print("Skipped live sensor-page requests:", len(failed))
if OPENAQ_SOURCE_MODE.startswith("bundled"):
    print("Offline overlay is spatial context only unless its timestamps match GEOS.")
''')

cell22 = "".join(notebook["cells"][22]["source"])
old_title = '''ax.set_title(
    f"GEOS-FP PM2.5 and OpenAQ reference monitors\\n"
    f"{start.isoformat()} to {end.isoformat()} UTC"
)'''
new_title = '''ax.set_title(
    "GEOS-FP PM2.5 and OpenAQ reference monitors\\n"
    f"GEOS: {pd.Timestamp(geos_pm25.time.values)} UTC | "
    f"stations: {observation_period_text}\\n"
    f"Sources: {GEOS_SOURCE_MODE}; {OPENAQ_SOURCE_MODE}"
)'''
if old_title in cell22:
    cell22 = cell22.replace(old_title, new_title)
elif "Sources: {GEOS_SOURCE_MODE}; {OPENAQ_SOURCE_MODE}" not in cell22:
    raise RuntimeError("Module 1 map title pattern changed; update the hardening script")
notebook["cells"][22]["source"] = lines(cell22)

NOTEBOOK.write_text(
    json.dumps(notebook, indent=1, ensure_ascii=False) + "\n",
    encoding="utf-8",
)
print("Updated", NOTEBOOK)
