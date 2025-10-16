import datetime as dt
import time

import pandas as pd
import streamlit as st
from skyfield.api import EarthSatellite, load

from src.orbits.pass_predictor_optimized import fetch_tle_cached, compute_passes_optimized

st.set_page_config(
    page_title="Satellite Pass Predictor (Optimized)", 
    page_icon="🛰️", 
    layout="centered"
)

st.title("🛰️ Satellite Pass Predictor")
st.caption("Compute upcoming satellite passes for your location using live TLEs (Celestrak) - Optimized Version")

# Add performance info in sidebar
with st.sidebar:
    st.header("Parameters")
    
    # Location inputs with validation
    lat = st.number_input(
        "Latitude (deg)", 
        value=28.6139, 
        min_value=-90.0, 
        max_value=90.0, 
        format="%.6f",
        help="Latitude in degrees (-90 to 90)"
    )
    lon = st.number_input(
        "Longitude (deg)", 
        value=77.2090, 
        min_value=-180.0, 
        max_value=180.0, 
        format="%.6f",
        help="Longitude in degrees (-180 to 180)"
    )
    alt_m = st.number_input(
        "Altitude (m)", 
        value=0.0, 
        min_value=-1000.0, 
        step=10.0,
        help="Altitude above sea level in meters"
    )
    
    # Time and elevation parameters
    hours = st.slider(
        "Hours ahead", 
        min_value=1, 
        max_value=48, 
        value=24,
        help="How many hours ahead to search for passes"
    )
    min_elev = st.slider(
        "Minimum elevation (deg)", 
        min_value=0, 
        max_value=60, 
        value=5,
        help="Minimum elevation angle for visible passes"
    )
    
    # Advanced options
    with st.expander("Advanced Options"):
        time_step = st.slider(
            "Time resolution (minutes)",
            min_value=0.5,
            max_value=5.0,
            value=1.0,
            step=0.5,
            help="Smaller values = more accurate but slower computation"
        )
        
        # Popular satellites dropdown
        satellite_presets = {
            "ISS (International Space Station)": 25544,
            "Hubble Space Telescope": 20580,
            "Starlink-1007": 44713,
            "NOAA-18": 28654,
            "TERRA": 25994,
            "Custom NORAD ID": None
        }
        
        selected_satellite = st.selectbox(
            "Select Satellite",
            options=list(satellite_presets.keys()),
            index=0
        )
        
        if satellite_presets[selected_satellite] is None:
            norad = st.number_input("NORAD catalog ID", value=25544, step=1, min_value=1)
        else:
            norad = satellite_presets[selected_satellite]
            st.info(f"NORAD ID: {norad}")
    
    go = st.button(" Predict passes", type="primary")

# Main content area
if go:
    # Input validation
    try:
        if not (-90 <= lat <= 90):
            st.error("Latitude must be between -90 and 90 degrees")
            st.stop()
        if not (-180 <= lon <= 180):
            st.error("Longitude must be between -180 and 180 degrees")
            st.stop()
        if alt_m < -1000:
            st.error("Altitude must be >= -1000 meters")
            st.stop()
            
        with st.spinner("Fetching TLE and computing passes..."):
            start_time = time.time()
            
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Step 1: Fetch TLE
            status_text.text("Fetching satellite TLE data...")
            progress_bar.progress(20)
            name, l1, l2 = fetch_tle_cached(int(norad))
            
            # Step 2: Create satellite object
            status_text.text("Creating satellite model...")
            progress_bar.progress(40)
            ts = load.timescale()
            sat = EarthSatellite(l1, l2, name, ts)
            
            # Step 3: Compute passes
            status_text.text("Computing satellite passes...")
            progress_bar.progress(60)
            passes = compute_passes_optimized(
                sat, 
                float(lat), 
                float(lon), 
                float(alt_m), 
                int(hours), 
                float(min_elev),
                float(time_step)
            )
            
            progress_bar.progress(100)
            computation_time = time.time() - start_time
            status_text.text(f"Computation completed in {computation_time:.2f} seconds")
            
            # Clear progress indicators after a moment
            time.sleep(1)
            progress_bar.empty()
            status_text.empty()
            
    except Exception as e:
        st.error(f"Error: {e}")
        st.stop()

    # Display results
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader(f"Upcoming passes for {name}")
    
    with col2:
        st.metric("Computation Time", f"{computation_time:.2f}s")
    
    if not passes:
        st.info("No passes found in the selected window.")
        st.markdown("""
        **Suggestions to find more passes:**
        - Lower the minimum elevation angle
        - Increase the search window (hours ahead)
        - Try a different satellite
        - Check if the satellite is currently active
        """)
    else:
        def fmt(d: dt.datetime) -> str:
            return d.strftime("%Y-%m-%d %H:%M")

        # Create enhanced data with additional metrics
        data = []
        for i, p in enumerate(passes, 1):
            duration = p.end - p.start
            duration_minutes = duration.total_seconds() / 60
            
            # Time until pass starts
            now = dt.datetime.now(dt.timezone.utc).replace(tzinfo=None)
            time_until = p.start - now
            hours_until = time_until.total_seconds() / 3600
            
            data.append({
                "#": i,
                "Start (UTC)": fmt(p.start),
                "Peak (UTC)": fmt(p.peak),
                "End (UTC)": fmt(p.end),
                "Max Elev (°)": round(p.max_elevation_deg, 1),
                "Duration (min)": round(duration_minutes, 1),
                "Hours Until": round(hours_until, 1) if hours_until > 0 else "In Progress"
            })
        
        df = pd.DataFrame(data)
        
        # Display the table with better formatting
        st.dataframe(
            df, 
            use_container_width=True,
            column_config={
                "#": st.column_config.NumberColumn("Pass #", width="small"),
                "Max Elev (°)": st.column_config.NumberColumn(
                    "Max Elev (°)",
                    help="Maximum elevation angle during the pass"
                ),
                "Duration (min)": st.column_config.NumberColumn(
                    "Duration (min)",
                    help="Total duration of the pass"
                ),
                "Hours Until": st.column_config.TextColumn(
                    "Hours Until",
                    help="Time until pass starts"
                )
            }
        )
        
        # Summary statistics
        st.subheader("Pass Summary")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Passes", len(passes))
        
        with col2:
            avg_elevation = sum(p.max_elevation_deg for p in passes) / len(passes)
            st.metric("Avg Max Elevation", f"{avg_elevation:.1f}°")
        
        with col3:
            avg_duration = sum((p.end - p.start).total_seconds() for p in passes) / len(passes) / 60
            st.metric("Avg Duration", f"{avg_duration:.1f} min")
        
        with col4:
            best_pass = max(passes, key=lambda p: p.max_elevation_deg)
            st.metric("Best Pass Elevation", f"{best_pass.max_elevation_deg:.1f}°")
        
        # Tips and information
        st.markdown("---")
        st.markdown("""
        **Tips:**
        - Lower minimum elevation or increase hours to find more passes
        - Passes with higher elevation angles are generally more visible
        - Times are shown in UTC - convert to your local timezone
        - Weather conditions affect actual visibility
        """)
        
        # Performance info
        with st.expander("Performance Details"):
            st.write(f"**Computation time:** {computation_time:.3f} seconds")
            st.write(f"**Time resolution:** {time_step} minutes")
            st.write(f"**Search window:** {hours} hours")
            st.write(f"**Data points processed:** ~{int(hours * 60 / time_step)}")
            
else:
    st.info("👈 Set parameters in the sidebar and click **Predict passes** to begin.")
    
    # Show example/demo information
    st.markdown("---")
    st.subheader("About This Tool")
    st.markdown("""
    This optimized satellite pass predictor uses:
    
    **🚀 Performance Improvements:**
    - Adaptive time stepping (coarse detection + fine refinement)
    - Vectorized computations using NumPy
    - TLE data caching to avoid repeated API calls
    - Memory-efficient algorithms
    
    **✅ Enhanced Features:**
    - Input validation and error handling
    - Popular satellite presets
    - Adjustable time resolution
    - Detailed performance metrics
    - Enhanced pass statistics
    
    **📡 Default Location:** New Delhi, India (28.6139°N, 77.2090°E)
    """)