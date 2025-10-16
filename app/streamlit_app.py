import datetime as dt
import time

import folium
import pandas as pd
import streamlit as st
from skyfield.api import EarthSatellite, load, wgs84
from streamlit_folium import st_folium

from src.orbits.pass_predictor import fetch_tle, compute_passes

st.set_page_config(page_title="Space Exploration AI", page_icon="🛰️", layout="wide")

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(45deg, #1e3c72, #2a5298);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    .card {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Add menu
menu = st.sidebar.selectbox("Navigation", ["🏠 Home", "🛰️ Satellite Tracker", "🗺️ Ground Track Visualizer", "📊 Satellite Database", "👨‍💻 About Developer"])

if menu == "🏠 Home":
    st.markdown('<h1 class="main-header">🛰️ Space Exploration AI</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">Advanced Satellite Pass Prediction & Orbital Analytics</p>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="metric-card"><h3>Real-time TLE</h3><p>Live satellite data from Celestrak</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card"><h3>Orbital Mechanics</h3><p>Precise pass calculations</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card"><h3>AI-Powered</h3><p>Smart prediction algorithms</p></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("🛰️ Satellite Pass Predictor")
    st.caption("Compute upcoming satellite passes for your location using live TLEs (Celestrak)")

elif menu == "🛰️ Satellite Tracker":
    st.title("🛰️ Real-Time Satellite Tracker")
    st.caption("Track satellite positions in real-time")

    norad = st.number_input("NORAD ID", value=25544, step=1)
    track_btn = st.button("Start Tracking")

    if track_btn:
        try:
            name, l1, l2 = fetch_tle(int(norad))
            ts = load.timescale()
            sat = EarthSatellite(l1, l2, name, ts)

            placeholder = st.empty()

            for _ in range(60):  # Track for 1 minute
                t = ts.now()
                geocentric = sat.at(t)
                subpoint = wgs84.subpoint(geocentric)

                with placeholder.container():
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Satellite", name)
                        st.metric("Latitude", f"{subpoint.latitude.degrees:.4f}°")
                        st.metric("Longitude", f"{subpoint.longitude.degrees:.4f}°")
                        st.metric("Altitude", f"{subpoint.elevation.m:.0f} km")

                    with col2:
                        # Create map
                        m = folium.Map(location=[subpoint.latitude.degrees, subpoint.longitude.degrees], zoom_start=3)
                        folium.Marker([subpoint.latitude.degrees, subpoint.longitude.degrees],
                                    popup=f"{name}<br>Alt: {subpoint.elevation.m:.0f} km").add_to(m)
                        st_folium(m, width=400, height=300)

                time.sleep(1)

        except Exception as e:
            st.error(f"Error: {e}")

elif menu == "🗺️ Ground Track Visualizer":
    st.title("🗺️ Ground Track Visualizer")
    st.caption("Visualize satellite ground tracks over time")

    norad = st.number_input("NORAD ID", value=25544, step=1)
    hours = st.slider("Track Duration (hours)", 1, 24, 6)
    viz_btn = st.button("Generate Track")

    if viz_btn:
        try:
            name, l1, l2 = fetch_tle(int(norad))
            ts = load.timescale()
            sat = EarthSatellite(l1, l2, name, ts)

            # Generate track points
            t0 = ts.now()
            times = ts.linspace(t0, t0 + dt.timedelta(hours=hours), 100)

            lats, lons = [], []
            for t in times:
                geocentric = sat.at(t)
                subpoint = wgs84.subpoint(geocentric)
                lats.append(subpoint.latitude.degrees)
                lons.append(subpoint.longitude.degrees)

            # Create map with track
            m = folium.Map(location=[lats[0], lons[0]], zoom_start=2)
            folium.PolyLine(list(zip(lats, lons)), color="red", weight=2.5, opacity=1).add_to(m)
            folium.Marker([lats[0], lons[0]], popup=f"Start: {name}").add_to(m)
            folium.Marker([lats[-1], lons[-1]], popup=f"End: {name}").add_to(m)

            st_folium(m, width=700, height=500)

        except Exception as e:
            st.error(f"Error: {e}")

elif menu == "📊 Satellite Database":
    st.title("📊 Satellite Database")
    st.caption("Browse and search satellites from Celestrak database")

    # This would require additional API calls to get satellite lists
    st.info("Satellite database feature coming soon! Currently supports manual NORAD ID entry.")

elif menu == "👨‍💻 About Developer":
    st.title("👨‍💻 About the Developer")
    st.subheader("Yuva")
    st.write("**Email:** astroyuvinut@gmail.com")
    st.write("Yuva is a computer science student and aspiring AI specialist with a focus on space exploration technologies. He is the creator of Space Exploration AI – Satellite Pass Predictor, a project that integrates orbital mechanics, real-time satellite data, and AI-driven analytics to provide accurate satellite visibility predictions.")
    st.subheader("Technical Skills")
    st.write("Python, NumPy, Pandas, SciPy, Skyfield, Streamlit, Typer, Rich")
    st.subheader("Vision")
    st.write("To leverage artificial intelligence to enhance astrodynamics and satellite observation, making space exploration more accessible and efficient.")
    st.stop()

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

            # Add export functionality
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download Pass Data (CSV)",
                data=csv,
                file_name=f"{name}_passes.csv",
                mime="text/csv",
                key="download-csv"
            )

            st.dataframe(df, use_container_width=True)

            st.caption("Tip: Lower the minimum elevation or increase hours to find more passes.")
    else:
        st.info("Set parameters in the sidebar and click Predict passes.")
