import datetime as dt
from dataclasses import dataclass
from typing import List, Tuple, Optional
import functools
import time

import requests
import numpy as np
from rich.console import Console
from rich.table import Table
from skyfield.api import EarthSatellite, load, wgs84
import typer

console = Console()
app = typer.Typer(help="Predict satellite passes using live TLEs (Optimized).")

TLE_SOURCES = {
    "celestrak": "https://celestrak.org/NORAD/elements/gp.php?CATNR={norad}&FORMAT=tle",
}

# TLE Cache with TTL (Time To Live)
_tle_cache = {}
TLE_CACHE_TTL = 3600  # 1 hour in seconds


def validate_coordinates(latitude: float, longitude: float, altitude: float) -> None:
    """Validate geographic coordinates."""
    if not -90 <= latitude <= 90:
        raise ValueError(f"Latitude must be between -90 and 90 degrees, got {latitude}")
    if not -180 <= longitude <= 180:
        raise ValueError(f"Longitude must be between -180 and 180 degrees, got {longitude}")
    if altitude < -1000:  # Allow some below sea level but not extreme values
        raise ValueError(f"Altitude must be >= -1000 meters, got {altitude}")


def fetch_tle_cached(norad_id: int) -> Tuple[str, str, str]:
    """Fetch TLE with caching to avoid repeated API calls."""
    current_time = time.time()
    cache_key = norad_id
    
    # Check if we have a valid cached entry
    if cache_key in _tle_cache:
        cached_data, timestamp = _tle_cache[cache_key]
        if current_time - timestamp < TLE_CACHE_TTL:
            return cached_data
    
    # Fetch new TLE data
    url = TLE_SOURCES["celestrak"].format(norad=norad_id)
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise ValueError(f"Failed to fetch TLE data: {e}")
    
    lines = [line.strip() for line in resp.text.splitlines() if line.strip()]
    if len(lines) < 2:
        raise ValueError("Could not fetch TLE: not enough lines")
    
    name = f"NORAD {norad_id}"
    if len(lines) >= 3 and not lines[0].startswith("1 "):
        name = lines[0]
        l1, l2 = lines[-2], lines[-1]
    else:
        l1, l2 = lines[0], lines[1]
    
    # Cache the result
    result = (name, l1, l2)
    _tle_cache[cache_key] = (result, current_time)
    
    return result


@dataclass
class PassEvent:
    start: dt.datetime
    peak: dt.datetime
    end: dt.datetime
    max_elevation_deg: float


def compute_passes_optimized(
    sat: EarthSatellite,
    latitude_deg: float,
    longitude_deg: float,
    altitude_m: float,
    hours_ahead: int,
    min_elevation_deg: float,
    time_step_minutes: float = 1.0,
) -> List[PassEvent]:
    """
    Optimized pass computation using vectorized operations and adaptive time stepping.
    
    Args:
        sat: EarthSatellite object
        latitude_deg: Observer latitude in degrees
        longitude_deg: Observer longitude in degrees  
        altitude_m: Observer altitude in meters
        hours_ahead: Hours to look ahead
        min_elevation_deg: Minimum elevation angle in degrees
        time_step_minutes: Time step in minutes (smaller = more accurate but slower)
    """
    # Validate inputs
    validate_coordinates(latitude_deg, longitude_deg, altitude_m)
    if not 1 <= hours_ahead <= 168:  # Max 1 week
        raise ValueError(f"Hours ahead must be between 1 and 168, got {hours_ahead}")
    if not 0 <= min_elevation_deg <= 90:
        raise ValueError(f"Minimum elevation must be between 0 and 90 degrees, got {min_elevation_deg}")
    
    ts = load.timescale()
    observer = wgs84.latlon(latitude_deg, longitude_deg, altitude_m)
    
    # Use adaptive time stepping - coarse first pass, then refine
    passes = []
    
    # Coarse pass detection (5-minute intervals)
    coarse_step = 5.0
    coarse_passes = _find_coarse_passes(sat, observer, ts, hours_ahead, min_elevation_deg, coarse_step)
    
    # Refine each coarse pass with fine time stepping
    for coarse_start, coarse_end in coarse_passes:
        refined_pass = _refine_pass(sat, observer, ts, coarse_start, coarse_end, min_elevation_deg, time_step_minutes)
        if refined_pass:
            passes.append(refined_pass)
    
    return passes


def _find_coarse_passes(
    sat: EarthSatellite, 
    observer, 
    ts, 
    hours_ahead: int, 
    min_elevation_deg: float,
    time_step_minutes: float
) -> List[Tuple[dt.datetime, dt.datetime]]:
    """Find approximate pass windows using coarse time stepping."""
    now = dt.datetime.now(dt.timezone.utc)
    end_time = now + dt.timedelta(hours=hours_ahead)
    
    # Create time array for coarse detection
    total_minutes = int(hours_ahead * 60)
    num_points = int(total_minutes / time_step_minutes) + 1
    
    # Use numpy for efficient time array creation
    minutes_array = np.linspace(0, total_minutes, num_points)
    datetimes = [now + dt.timedelta(minutes=float(m)) for m in minutes_array]
    times = ts.from_datetimes(datetimes)
    
    # Vectorized elevation computation
    topocentric = (sat - observer).at(times)
    alt, az, distance = topocentric.altaz()
    elevations = alt.degrees
    
    # Find pass boundaries
    above_threshold = elevations >= min_elevation_deg
    pass_boundaries = []
    
    in_pass = False
    pass_start = None
    
    for i, (is_above, dt_obj) in enumerate(zip(above_threshold, datetimes)):
        if is_above and not in_pass:
            # Pass starts
            in_pass = True
            pass_start = dt_obj
        elif not is_above and in_pass:
            # Pass ends
            in_pass = False
            if pass_start:
                pass_boundaries.append((pass_start, dt_obj))
    
    # Handle ongoing pass at end of window
    if in_pass and pass_start:
        pass_boundaries.append((pass_start, end_time))
    
    return pass_boundaries


def _refine_pass(
    sat: EarthSatellite,
    observer,
    ts,
    start_time: dt.datetime,
    end_time: dt.datetime,
    min_elevation_deg: float,
    time_step_minutes: float
) -> Optional[PassEvent]:
    """Refine a coarse pass to get accurate timing and peak elevation."""
    # Extend the window slightly to catch exact boundaries
    buffer_minutes = 10
    refined_start = start_time - dt.timedelta(minutes=buffer_minutes)
    refined_end = end_time + dt.timedelta(minutes=buffer_minutes)
    
    # Create fine-grained time array
    duration_minutes = (refined_end - refined_start).total_seconds() / 60
    num_points = int(duration_minutes / time_step_minutes) + 1
    
    minutes_array = np.linspace(0, duration_minutes, num_points)
    datetimes = [refined_start + dt.timedelta(minutes=float(m)) for m in minutes_array]
    times = ts.from_datetimes(datetimes)
    
    # Compute elevations
    topocentric = (sat - observer).at(times)
    alt, az, distance = topocentric.altaz()
    elevations = alt.degrees
    
    # Find exact pass boundaries and peak
    above_threshold = elevations >= min_elevation_deg
    
    if not np.any(above_threshold):
        return None
    
    # Find first and last points above threshold
    above_indices = np.where(above_threshold)[0]
    start_idx = above_indices[0]
    end_idx = above_indices[-1]
    
    # Find peak elevation within the pass
    pass_elevations = elevations[start_idx:end_idx+1]
    peak_idx_relative = np.argmax(pass_elevations)
    peak_idx = start_idx + peak_idx_relative
    
    return PassEvent(
        start=datetimes[start_idx],
        peak=datetimes[peak_idx],
        end=datetimes[end_idx],
        max_elevation_deg=float(elevations[peak_idx])
    )


# Legacy function for backward compatibility
def compute_passes(
    sat: EarthSatellite,
    latitude_deg: float,
    longitude_deg: float,
    altitude_m: float,
    hours_ahead: int,
    min_elevation_deg: float,
) -> List[PassEvent]:
    """Legacy function - redirects to optimized version."""
    return compute_passes_optimized(
        sat, latitude_deg, longitude_deg, altitude_m, hours_ahead, min_elevation_deg
    )


def fetch_tle(norad_id: int) -> Tuple[str, str, str]:
    """Legacy function - redirects to cached version."""
    return fetch_tle_cached(norad_id)


@app.command()
def predict(
    lat: float = typer.Option(..., "--lat", help="Observer latitude in degrees"),
    lon: float = typer.Option(..., "--lon", help="Observer longitude in degrees"),
    hours: int = typer.Option(6, "--hours", min=1, max=72, help="Hours ahead to search"),
    min_elev: float = typer.Option(10.0, "--min-elev", help="Minimum elevation angle in degrees"),
    alt_m: float = typer.Option(0.0, "--alt", help="Observer altitude in meters"),
    norad: int = typer.Option(25544, "--norad", help="NORAD catalog ID (default: ISS)"),
    time_step: float = typer.Option(1.0, "--time-step", help="Time step in minutes (default: 1.0)"),
):
    """Predict visible passes for a satellite above a ground location.
    
    Times are in UTC. Uses optimized algorithms for better performance.
    """
    console.rule("Satellite Pass Predictor (Optimized)")
    
    try:
        start_time = time.time()
        console.print(f"Fetching TLE for NORAD {norad}...")
        name, l1, l2 = fetch_tle_cached(norad)
        console.print(f"Using TLE: {name}")

        ts = load.timescale()
        satellite = EarthSatellite(l1, l2, name, ts)

        console.print(f"Computing passes with {time_step}-minute resolution...")
        passes = compute_passes_optimized(satellite, lat, lon, alt_m, hours, min_elev, time_step)
        
        computation_time = time.time() - start_time
        console.print(f"Computation completed in {computation_time:.2f} seconds")

        if not passes:
            console.print("No passes found in the time window.")
            return

        table = Table(title=f"Upcoming passes for {name} (UTC)")
        table.add_column("Start")
        table.add_column("Peak")
        table.add_column("End")
        table.add_column("Max Elev (deg)", justify="right")
        table.add_column("Duration", justify="right")

        for p in passes:
            duration = p.end - p.start
            duration_str = f"{duration.total_seconds()/60:.1f}m"
            
            table.add_row(
                p.start.strftime("%Y-%m-%d %H:%M"),
                p.peak.strftime("%Y-%m-%d %H:%M"),
                p.end.strftime("%Y-%m-%d %H:%M"),
                f"{p.max_elevation_deg:.1f}",
                duration_str,
            )

        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


def main():
    app()


if __name__ == "__main__":
    main()