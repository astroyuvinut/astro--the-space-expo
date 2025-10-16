import datetime as dt
from dataclasses import dataclass
from typing import List, Tuple

import requests
from rich.console import Console
from rich.table import Table
from skyfield.api import EarthSatellite, load, wgs84
import typer

console = Console()
app = typer.Typer(help="Predict satellite passes using live TLEs.")

TLE_SOURCES = {
	"celestrak": "https://celestrak.org/NORAD/elements/gp.php?CATNR={norad}&FORMAT=tle",
}


def fetch_tle(norad_id: int) -> Tuple[str, str, str]:
	url = TLE_SOURCES["celestrak"].format(norad=norad_id)
	resp = requests.get(url, timeout=15)
	resp.raise_for_status()
	lines = [line.strip() for line in resp.text.splitlines() if line.strip()]
	if len(lines) < 2:
		raise ValueError("Could not fetch TLE: not enough lines")
	name = f"NORAD {norad_id}"
	if len(lines) >= 3 and not lines[0].startswith("1 "):
		name = lines[0]
		l1, l2 = lines[-2], lines[-1]
	else:
		l1, l2 = lines[0], lines[1]
	return name, l1, l2


@dataclass
class PassEvent:
	start: dt.datetime
	peak: dt.datetime
	end: dt.datetime
	max_elevation_deg: float


def compute_passes(
	sat: EarthSatellite,
	latitude_deg: float,
	longitude_deg: float,
	altitude_m: float,
	hours_ahead: int,
	min_elevation_deg: float,
) -> List[PassEvent]:
	ts = load.timescale()

	now = dt.datetime.now(dt.timezone.utc)
	datetimes = [now + dt.timedelta(minutes=i) for i in range(hours_ahead * 60 + 1)]
	times = ts.from_datetimes(datetimes)

	observer = wgs84.latlon(latitude_deg, longitude_deg, altitude_m)

	passes: List[PassEvent] = []
	in_pass = False
	current_start = None
	current_peak = None
	current_max_elev = -90.0

	for t in times:
		topocentric = (sat - observer).at(t)
		alt, az, distance = topocentric.altaz()
		elev_deg = alt.degrees

		if elev_deg >= min_elevation_deg and not in_pass:
			in_pass = True
			current_start = t.utc_datetime().replace(tzinfo=None)
			current_peak = current_start
			current_max_elev = elev_deg
		elif elev_deg >= min_elevation_deg and in_pass:
			if elev_deg > current_max_elev:
				current_max_elev = elev_deg
				current_peak = t.utc_datetime().replace(tzinfo=None)
		elif elev_deg < min_elevation_deg and in_pass:
			end_dt = t.utc_datetime().replace(tzinfo=None)
			passes.append(
				PassEvent(
					start=current_start,
					peak=current_peak,
					end=end_dt,
					max_elevation_deg=current_max_elev,
				)
			)
			in_pass = False

	return passes


@app.command()
def predict(
	lat: float = typer.Option(..., "--lat", help="Observer latitude in degrees"),
	lon: float = typer.Option(..., "--lon", help="Observer longitude in degrees"),
	hours: int = typer.Option(6, "--hours", min=1, max=72, help="Hours ahead to search"),
	min_elev: float = typer.Option(10.0, "--min-elev", help="Minimum elevation angle in degrees"),
	alt_m: float = typer.Option(0.0, "--alt", help="Observer altitude in meters"),
	norad: int = typer.Option(25544, "--norad", help="NORAD catalog ID (default: ISS)"),
):
	"""Predict visible passes for a satellite above a ground location.

	Times are in UTC.
	"""
	console.rule("Satellite Pass Predictor")
	console.print(f"Fetching TLE for NORAD {norad}...")
	name, l1, l2 = fetch_tle(norad)
	console.print(f"Using TLE: {name}")

	ts = load.timescale()
	satellite = EarthSatellite(l1, l2, name, ts)

	passes = compute_passes(satellite, lat, lon, alt_m, hours, min_elev)

	if not passes:
		console.print("No passes found in the time window.")
		return

	table = Table(title=f"Upcoming passes for {name} (UTC)")
	table.add_column("Start")
	table.add_column("Peak")
	table.add_column("End")
	table.add_column("Max Elev (deg)", justify="right")

	for p in passes:
		table.add_row(
			p.start.strftime("%Y-%m-%d %H:%M"),
			p.peak.strftime("%Y-%m-%d %H:%M"),
			p.end.strftime("%Y-%m-%d %H:%M"),
			f"{p.max_elevation_deg:.1f}",
		)

	console.print(table)


def main():
	app()


if __name__ == "__main__":
	main()
