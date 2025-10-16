import datetime as dt

import pandas as pd
import streamlit as st
from skyfield.api import EarthSatellite, load

from src.orbits.pass_predictor import fetch_tle, compute_passes

st.set_page_config(page_title="Satellite Pass Predictor", page_icon="🛰️", layout="centered")
st.title("🛰️ Satellite Pass Predictor")
st.caption("Compute upcoming satellite passes for your location using live TLEs (Celestrak)")

with st.sidebar:
	st.header("Parameters")
	lat = st.number_input("Latitude (deg)", value=28.6139, format="%.6f")
	lon = st.number_input("Longitude (deg)", value=77.2090, format="%.6f")
	alt_m = st.number_input("Altitude (m)", value=0.0, step=10.0)
	hours = st.slider("Hours ahead", min_value=1, max_value=48, value=24)
	min_elev = st.slider("Minimum elevation (deg)", min_value=0, max_value=60, value=5)
	norad = st.number_input("NORAD catalog ID", value=25544, step=1)
	go = st.button("Predict passes")

if go:
	with st.spinner("Fetching TLE and computing passes..."):
		try:
			name, l1, l2 = fetch_tle(int(norad))
			ts = load.timescale()
			sat = EarthSatellite(l1, l2, name, ts)
			passes = compute_passes(sat, float(lat), float(lon), float(alt_m), int(hours), float(min_elev))
		except Exception as e:
			st.error(f"Error: {e}")
			st.stop()

	st.subheader(f"Upcoming passes for {name}")
	if not passes:
		st.info("No passes found in the selected window.")
	else:
		def fmt(d: dt.datetime) -> str:
			return d.strftime("%Y-%m-%d %H:%M")

		data = [
			{
				"Start (UTC)": fmt(p.start),
				"Peak (UTC)": fmt(p.peak),
				"End (UTC)": fmt(p.end),
				"Max Elev (deg)": round(p.max_elevation_deg, 1),
			}
			for p in passes
		]
		df = pd.DataFrame(data)
		st.dataframe(df, use_container_width=True)

		st.caption("Tip: Lower the minimum elevation or increase hours to find more passes.")
else:
	st.info("Set parameters in the sidebar and click Predict passes.")
