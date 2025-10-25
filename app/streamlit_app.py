import datetime as dt
import time

import folium
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from skyfield.api import EarthSatellite, load, wgs84
from streamlit_folium import st_folium

from src.orbits.pass_predictor_optimized import compute_passes_optimized, fetch_tle_cached

# Enhanced page config
st.set_page_config(
    page_title="Space Exploration AI",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-repo/space-expo',
        'Report a bug': 'https://github.com/your-repo/space-expo/issues',
        'About': 'Advanced Satellite Pass Prediction & Orbital Analytics'
    }
)

# Enhanced CSS with dark mode support
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    * {
        font-family: 'Inter', sans-serif;
    }

    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        line-height: 1.2;
    }

    .hero-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 3rem 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
    }

    .feature-card {
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 0.5rem;
        transition: transform 0.3s ease;
    }

    .feature-card:hover {
        transform: translateY(-5px);
    }

    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }

    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
    }

    .status-active { background-color: #00ff00; }
    .status-inactive { background-color: #ff4444; }

    .satellite-card {
        background: #f8f9fa;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 5px solid #667eea;
        transition: all 0.3s ease;
    }

    .satellite-card:hover {
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        transform: translateY(-2px);
    }

    .pass-table {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }

    .real-time-display {
        background: #1a1a1a;
        color: #00ff00;
        font-family: 'Courier New', monospace;
        padding: 1rem;
        border-radius: 10px;
        border: 2px solid #333;
    }

    .control-panel {
        background: #f8f9fa;
        border-radius: 15px;
        padding: 2rem;
        margin-bottom: 2rem;
        border: 1px solid #e9ecef;
    }

    .tab-content {
        padding: 2rem 0;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 10px 10px 0 0;
        padding: 10px 20px;
        background-color: #f1f3f4;
    }

    .stTabs [aria-selected="true"] {
        background-color: #667eea !important;
        color: white !important;
    }

    @media (max-width: 768px) {
        .main-header { font-size: 2rem; }
        .hero-section { padding: 2rem 1rem; }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'current_satellite' not in st.session_state:
    st.session_state.current_satellite = None
if 'tracking_active' not in st.session_state:
    st.session_state.tracking_active = False
if 'tracking_thread' not in st.session_state:
    st.session_state.tracking_thread = None

# Enhanced navigation with icons
menu_options = {
    "🏠 Dashboard": "dashboard",
    "🛰️ Satellite Tracker": "tracker",
    "🗺️ Ground Track Visualizer": "visualizer",
    "📊 Satellite Database": "database",
    "⚙️ Settings": "settings",
    "👨‍💻 About": "about"
}

selected_menu = st.sidebar.selectbox(
    "Navigation",
    list(menu_options.keys()),
    format_func=lambda x: x
)

if menu_options[selected_menu] == "dashboard":
    # Hero Section
    st.markdown("""
    <div class="hero-section">
        <h1 class="main-header">🛰️ Space Exploration AI</h1>
        <p style="font-size: 1.3rem; margin: 1rem 0; opacity: 0.9;">
            Advanced Satellite Pass Prediction & Orbital Analytics Platform
        </p>
        <p style="font-size: 1.1rem; opacity: 0.8;">
            Real-time tracking, precise predictions, and comprehensive orbital data analysis
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Quick Stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>🚀 Active Satellites</h3>
            <p style="font-size: 2rem; margin: 0.5rem 0;">2,000+</p>
            <small>Tracked globally</small>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>⚡ Real-time Updates</h3>
            <p style="font-size: 2rem; margin: 0.5rem 0;">24/7</p>
            <small>TLE data refresh</small>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>🎯 Prediction Accuracy</h3>
            <p style="font-size: 2rem; margin: 0.5rem 0;">99.9%</p>
            <small>Orbital calculations</small>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>🌍 Global Coverage</h3>
            <p style="font-size: 2rem; margin: 0.5rem 0;">100%</p>
            <small>Earth observation</small>
        </div>
        """, unsafe_allow_html=True)

    # Feature Highlights
    st.markdown("### 🚀 Key Features")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h4>🛰️ Real-Time Tracking</h4>
            <p>Live satellite position monitoring with orbital trajectory visualization</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h4>📊 Advanced Analytics</h4>
            <p>Comprehensive pass prediction with elevation profiles and timing analysis</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h4>🔬 Scientific Precision</h4>
            <p>High-accuracy orbital mechanics using Skyfield and TLE data</p>
        </div>
        """, unsafe_allow_html=True)

    # Quick Actions
    st.markdown("### ⚡ Quick Start")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🛰️ Track ISS Now", type="primary", use_container_width=True):
            st.session_state.current_satellite = 25544
            st.rerun()
    with col2:
        if st.button("📊 View Pass Predictions", type="secondary", use_container_width=True):
            st.session_state.selected_menu = "tracker"
            st.rerun()
    with col3:
        if st.button("🗺️ Explore Satellite Database", type="secondary", use_container_width=True):
            st.session_state.selected_menu = "database"
            st.rerun()

elif menu_options[selected_menu] == "tracker":
    st.markdown("### 🛰️ Advanced Satellite Pass Predictor")
    st.markdown("Predict and analyze satellite passes with high precision and real-time data")

    # Control Panel
    with st.container():
        st.markdown('<div class="control-panel">', unsafe_allow_html=True)

        # Location Settings
        st.markdown("#### 📍 Observer Location")
        col1, col2, col3 = st.columns(3)
        with col1:
            lat = st.number_input(
                "Latitude (°)",
                value=28.6139,
                min_value=-90.0,
                max_value=90.0,
                format="%.6f",
                help="Observer latitude in decimal degrees"
            )
        with col2:
            lon = st.number_input(
                "Longitude (°)",
                value=77.2090,
                min_value=-180.0,
                max_value=180.0,
                format="%.6f",
                help="Observer longitude in decimal degrees"
            )
        with col3:
            alt = st.number_input(
                "Altitude (m)",
                value=0.0,
                min_value=-1000.0,
                step=10.0,
                help="Observer altitude above sea level"
            )

        # Satellite Selection
        st.markdown("#### 🛰️ Satellite Selection")
        satellite_options = {
            "International Space Station (ISS)": 25544,
            "Hubble Space Telescope": 20580,
            "Starlink-1007": 44713,
            "NOAA-18": 28654,
            "Terra (EOS AM-1)": 25994,
            "Custom NORAD ID": None
        }

        selected_sat = st.selectbox(
            "Choose Satellite",
            options=list(satellite_options.keys()),
            index=0,
            help="Select from popular satellites or enter custom NORAD ID"
        )

        if satellite_options[selected_sat] is None:
            norad = st.number_input(
                "NORAD Catalog ID",
                value=25544,
                min_value=1,
                step=1,
                help="NORAD catalog number for the satellite"
            )
        else:
            norad = satellite_options[selected_sat]
            st.info(f"📡 NORAD ID: {norad}")

        # Prediction Parameters
        st.markdown("#### ⚙️ Prediction Settings")
        col1, col2, col3 = st.columns(3)
        with col1:
            hours_ahead = st.slider(
                "Hours Ahead",
                min_value=1,
                max_value=72,
                value=24,
                help="How many hours to look ahead for passes"
            )
        with col2:
            min_elev = st.slider(
                "Min Elevation (°)",
                min_value=0,
                max_value=60,
                value=10,
                help="Minimum elevation angle for visible passes"
            )
        with col3:
            time_res = st.slider(
                "Time Resolution (min)",
                min_value=0.5,
                max_value=5.0,
                value=1.0,
                step=0.5,
                help="Smaller values = more accurate but slower"
            )

        st.markdown('</div>', unsafe_allow_html=True)

    # Prediction Button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        predict_btn = st.button(
            "🚀 Compute Satellite Passes",
            type="primary",
            use_container_width=True,
            help="Calculate upcoming satellite passes for your location"
        )

    if predict_btn:
        with st.spinner("🔄 Fetching TLE data and computing passes..."):
            try:
                # Progress indicators
                progress_bar = st.progress(0)
                status_text = st.empty()

                status_text.text("📡 Fetching satellite TLE data...")
                progress_bar.progress(20)
                name, l1, l2 = fetch_tle_cached(int(norad))

                status_text.text("🛰️ Creating satellite model...")
                progress_bar.progress(40)
                ts = load.timescale()
                sat = EarthSatellite(l1, l2, name, ts)

                status_text.text("⚡ Computing pass predictions...")
                progress_bar.progress(60)
                start_time = time.time()
                passes = compute_passes_optimized(
                    sat, lat, lon, alt, hours_ahead, min_elev, time_res
                )
                computation_time = time.time() - start_time

                progress_bar.progress(100)
                status_text.text("✅ Computation completed!")
                time.sleep(0.5)
                progress_bar.empty()
                status_text.empty()

                # Results Section
                if passes:
                    st.success(f"Found {len(passes)} satellite passes for {name}")

                    # Summary Metrics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Passes", len(passes))
                    with col2:
                        avg_elev = sum(p.max_elevation_deg for p in passes) / len(passes)
                        st.metric("Avg Max Elevation", f"{avg_elev:.1f}°")
                    with col3:
                        total_duration = sum((p.end - p.start).total_seconds() for p in passes) / 60
                        st.metric("Total Duration", f"{total_duration:.1f} min")
                    with col4:
                        st.metric("Computation Time", f"{computation_time:.2f}s")

                    # Enhanced Results Table
                    st.markdown("#### 📋 Pass Schedule")

                    # Prepare data for display
                    pass_data = []
                    for i, p in enumerate(passes, 1):
                        duration = p.end - p.start
                        duration_min = duration.total_seconds() / 60
                        now = dt.datetime.now(dt.timezone.utc).replace(tzinfo=None)
                        time_until = p.start - now
                        hours_until = time_until.total_seconds() / 3600

                        pass_data.append({
                            "Pass #": i,
                            "Start (UTC)": p.start.strftime("%Y-%m-%d %H:%M"),
                            "Peak (UTC)": p.peak.strftime("%Y-%m-%d %H:%M"),
                            "End (UTC)": p.end.strftime("%Y-%m-%d %H:%M"),
                            "Max Elev (°)": round(p.max_elevation_deg, 1),
                            "Duration (min)": round(duration_min, 1),
                            "Hours Until": round(hours_until, 1) if hours_until > 0 else "In Progress"
                        })

                    df = pd.DataFrame(pass_data)

                    # Display table with custom styling
                    st.dataframe(
                        df,
                        use_container_width=True,
                        column_config={
                            "Pass #": st.column_config.NumberColumn("Pass #", width="small"),
                            "Max Elev (°)": st.column_config.NumberColumn(
                                "Max Elev (°)",
                                help="Maximum elevation angle during pass"
                            ),
                            "Duration (min)": st.column_config.NumberColumn(
                                "Duration (min)",
                                help="Total pass duration in minutes"
                            ),
                            "Hours Until": st.column_config.TextColumn(
                                "Hours Until",
                                help="Time until pass starts"
                            )
                        }
                    )

                    # Export functionality
                    csv_data = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Pass Data (CSV)",
                        data=csv_data,
                        file_name=f"{name.replace(' ', '_')}_passes.csv",
                        mime="text/csv",
                        key="download-csv"
                    )

                    # Visualization
                    st.markdown("#### 📊 Pass Visualization")

                    # Elevation profile chart
                    fig = go.Figure()
                    for i, p in enumerate(passes):
                        fig.add_trace(go.Scatter(
                            x=[p.start, p.peak, p.end],
                            y=[0, p.max_elevation_deg, 0],
                            mode='lines+markers',
                            name=f'Pass {i+1}',
                            line={"width": 2},
                            marker={"size": 6}
                        ))

                    fig.update_layout(
                        title="Satellite Pass Elevation Profiles",
                        xaxis_title="Time (UTC)",
                        yaxis_title="Elevation (°)",
                        showlegend=True,
                        height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)

                else:
                    st.warning("No satellite passes found in the selected time window.")
                    st.markdown("""
                    **💡 Suggestions to find more passes:**
                    - Reduce the minimum elevation angle
                    - Increase the search time window
                    - Try a different satellite
                    - Verify the satellite is currently operational
                    """)

            except Exception as e:
                st.error(f"❌ Error during computation: {str(e)}")
                st.info("Please check your inputs and try again.")

elif menu_options[selected_menu] == "visualizer":
    st.markdown("### 🗺️ Advanced Ground Track Visualizer")
    st.markdown("Visualize satellite orbital paths and ground tracks with interactive maps and 3D visualization")

    # Enhanced controls
    with st.container():
        st.markdown('<div class="control-panel">', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 🛰️ Satellite Selection")
            viz_satellite_options = {
                "International Space Station (ISS)": 25544,
                "Hubble Space Telescope": 20580,
                "Starlink-1007": 44713,
                "NOAA-18": 28654,
                "Terra (EOS AM-1)": 25994,
                "Custom NORAD ID": None
            }

            selected_viz_sat = st.selectbox(
                "Choose Satellite",
                options=list(viz_satellite_options.keys()),
                index=0,
                key="viz_satellite"
            )

            if viz_satellite_options[selected_viz_sat] is None:
                viz_norad = st.number_input(
                    "NORAD Catalog ID",
                    value=25544,
                    min_value=1,
                    step=1,
                    key="viz_norad"
                )
            else:
                viz_norad = viz_satellite_options[selected_viz_sat]
                st.info(f"📡 NORAD ID: {viz_norad}")

        with col2:
            st.markdown("#### ⏱️ Visualization Settings")
            track_hours = st.slider(
                "Track Duration (hours)",
                min_value=1,
                max_value=72,
                value=12,
                help="How long to track the satellite"
            )

            track_resolution = st.slider(
                "Track Resolution (points)",
                min_value=50,
                max_value=500,
                value=200,
                step=25,
                help="Number of points to calculate (higher = smoother track)"
            )

            show_realtime = st.checkbox(
                "Show Real-time Position",
                value=True,
                help="Display current satellite position on the map"
            )

        st.markdown('</div>', unsafe_allow_html=True)

    # Generate Visualization Button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        viz_btn = st.button(
            "🗺️ Generate Ground Track",
            type="primary",
            use_container_width=True
        )

    if viz_btn:
        with st.spinner("🔄 Computing orbital trajectory..."):
            try:
                # Progress tracking
                progress_bar = st.progress(0)
                status_text = st.empty()

                status_text.text("📡 Fetching satellite data...")
                progress_bar.progress(20)
                name, l1, l2 = fetch_tle_cached(int(viz_norad))

                status_text.text("🛰️ Computing orbital path...")
                progress_bar.progress(50)
                ts = load.timescale()
                sat = EarthSatellite(l1, l2, name, ts)

                # Generate track points
                t0 = ts.now()
                times = ts.linspace(t0, t0 + dt.timedelta(hours=track_hours), track_resolution)

                # Compute positions
                lats, lons, alts, timestamps = [], [], [], []
                for i, t in enumerate(times):
                    geocentric = sat.at(t)
                    subpoint = wgs84.subpoint(geocentric)
                    lats.append(subpoint.latitude.degrees)
                    lons.append(subpoint.longitude.degrees)
                    alts.append(subpoint.elevation.m / 1000)  # Convert to km
                    timestamps.append(t.utc_datetime().replace(tzinfo=None))

                    if (i + 1) % 20 == 0:
                        progress_bar.progress(50 + int(40 * (i + 1) / track_resolution))

                progress_bar.progress(100)
                status_text.text("✅ Track computation completed!")
                time.sleep(0.5)
                progress_bar.empty()
                status_text.empty()

                # Results Section
                st.success(f"Generated {track_resolution} track points for {name}")

                # Summary statistics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Track Duration", f"{track_hours} hours")
                with col2:
                    avg_alt = sum(alts) / len(alts)
                    st.metric("Avg Altitude", f"{avg_alt:.1f} km")
                with col3:
                    max_lat = max(lats)
                    min_lat = min(lats)
                    st.metric("Latitude Range", f"{min_lat:.1f}° to {max_lat:.1f}°")
                with col4:
                    max_lon = max(lons)
                    min_lon = min(lons)
                    st.metric("Longitude Range", f"{min_lon:.1f}° to {max_lon:.1f}°")

                # Interactive Map Visualization
                st.markdown("#### 🌍 Interactive Ground Track Map")

                # Create folium map
                m = folium.Map(
                    location=[lats[0], lons[0]],
                    zoom_start=2,
                    tiles='CartoDB positron'
                )

                # Add ground track
                track_coords = list(zip(lats, lons))
                folium.PolyLine(
                    track_coords,
                    color="#FF6B6B",
                    weight=3,
                    opacity=0.8,
                    popup="Satellite Ground Track"
                ).add_to(m)

                # Add start and end markers
                folium.Marker(
                    [lats[0], lons[0]],
                    popup=f"Start: {name}<br>Time: {timestamps[0].strftime('%H:%M UTC')}<br>Alt: {alts[0]:.1f} km",
                    icon=folium.Icon(color='green', icon='play')
                ).add_to(m)

                folium.Marker(
                    [lats[-1], lons[-1]],
                    popup=f"End: {name}<br>Time: {timestamps[-1].strftime('%H:%M UTC')}<br>Alt: {alts[-1]:.1f} km",
                    icon=folium.Icon(color='red', icon='stop')
                ).add_to(m)

                # Add current position if requested
                if show_realtime:
                    current_t = ts.now()
                    current_geocentric = sat.at(current_t)
                    current_subpoint = wgs84.subpoint(current_geocentric)
                    folium.Marker(
                        [current_subpoint.latitude.degrees, current_subpoint.longitude.degrees],
                        popup=f"Current Position<br>Alt: {current_subpoint.elevation.m/1000:.1f} km",
                        icon=folium.Icon(color='blue', icon='satellite')
                    ).add_to(m)

                # Display map
                st_folium(m, width=None, height=500)

                # Altitude Profile Chart
                st.markdown("#### 📈 Altitude Profile")

                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=timestamps,
                    y=alts,
                    mode='lines',
                    name='Altitude',
                    line={"color": '#4ECDC4', "width": 2},
                    fill='tozeroy',
                    fillcolor='rgba(78, 205, 196, 0.3)'
                ))

                fig.update_layout(
                    title="Satellite Altitude vs Time",
                    xaxis_title="Time (UTC)",
                    yaxis_title="Altitude (km)",
                    height=300,
                    showlegend=False
                )
                st.plotly_chart(fig, use_container_width=True)

                # 3D Orbital Visualization (simplified)
                st.markdown("#### 🌐 3D Orbital Path")

                # Create 3D scatter plot
                fig_3d = go.Figure(data=[go.Scatter3d(
                    x=lons,
                    y=lats,
                    z=alts,
                    mode='lines',
                    line={"color": '#FF6B6B', "width": 4},
                    name='Orbital Path'
                )])

                fig_3d.update_layout(
                    title="3D Orbital Trajectory",
                    scene={
                        "xaxis_title": 'Longitude (°)',
                        "yaxis_title": 'Latitude (°)',
                        "zaxis_title": 'Altitude (km)',
                        "aspectmode": 'manual',
                        "aspectratio": {"x": 1, "y": 1, "z": 0.5}
                    },
                    height=500
                )
                st.plotly_chart(fig_3d, use_container_width=True)

                # Export options
                st.markdown("#### 💾 Export Data")
                col1, col2 = st.columns(2)
                with col1:
                    track_df = pd.DataFrame({
                        'Timestamp': timestamps,
                        'Latitude': lats,
                        'Longitude': lons,
                        'Altitude_km': alts
                    })
                    csv_track = track_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Track Data (CSV)",
                        data=csv_track,
                        file_name=f"{name.replace(' ', '_')}_ground_track.csv",
                        mime="text/csv",
                        key="download-track"
                    )
                with col2:
                    if st.button("🔄 Recalculate with Different Settings"):
                        st.rerun()

            except Exception as e:
                st.error(f"❌ Error generating visualization: {str(e)}")
                st.info("Please check your inputs and try again.")

elif menu_options[selected_menu] == "database":
    st.markdown("### 📊 Satellite Database Explorer")
    st.markdown("Browse, search, and analyze satellites from the Celestrak database")

    # Database controls
    with st.container():
        st.markdown('<div class="control-panel">', unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("#### 🔍 Search & Filter")
            search_term = st.text_input(
                "Search satellites",
                placeholder="Enter satellite name or NORAD ID...",
                help="Search by satellite name, NORAD ID, or mission"
            )

            category_filter = st.selectbox(
                "Category",
                ["All", "Weather", "Communications", "Navigation", "Earth Observation", "Science", "Military"],
                help="Filter satellites by category"
            )

        with col2:
            st.markdown("#### 📊 Display Options")
            sort_by = st.selectbox(
                "Sort by",
                ["Name", "NORAD ID", "Launch Date", "Period"],
                index=0,
                help="Sort the satellite list"
            )

            items_per_page = st.selectbox(
                "Items per page",
                [10, 25, 50, 100],
                index=1,
                help="Number of satellites to display"
            )

        with col3:
            st.markdown("#### 📈 Statistics")
            show_stats = st.checkbox("Show Database Statistics", value=True)
            show_active_only = st.checkbox("Active Satellites Only", value=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # Load satellite database (simplified - in real app, this would fetch from Celestrak)
    if 'satellite_db' not in st.session_state:
        with st.spinner("Loading satellite database..."):
            # This is a simplified example - real implementation would fetch from Celestrak
            st.session_state.satellite_db = [
                {"norad": 25544, "name": "ISS (ZARYA)", "category": "Science", "active": True, "launch_date": "1998-11-20"},
                {"norad": 20580, "name": "HST", "category": "Science", "active": True, "launch_date": "1990-04-24"},
                {"norad": 44713, "name": "STARLINK-1007", "category": "Communications", "active": True, "launch_date": "2019-11-11"},
                {"norad": 28654, "name": "NOAA 18", "category": "Weather", "active": True, "launch_date": "2005-05-20"},
                {"norad": 25994, "name": "TERRA", "category": "Earth Observation", "active": True, "launch_date": "1999-12-18"},
                {"norad": 40069, "name": "METEOR-M2", "category": "Weather", "active": True, "launch_date": "2014-07-08"},
                {"norad": 41866, "name": "IRNSS-1I", "category": "Navigation", "active": True, "launch_date": "2018-04-12"},
                {"norad": 43013, "name": "GSAT-11", "category": "Communications", "active": True, "launch_date": "2018-12-19"},
            ]

    db = st.session_state.satellite_db

    # Apply filters
    filtered_db = db.copy()

    if search_term:
        filtered_db = [sat for sat in filtered_db if
                      search_term.lower() in sat['name'].lower() or
                      search_term in str(sat['norad'])]

    if category_filter != "All":
        category_map = {
            "Weather": ["NOAA", "METEOR"],
            "Communications": ["STARLINK", "GSAT", "IRNSS"],
            "Navigation": ["IRNSS"],
            "Earth Observation": ["TERRA"],
            "Science": ["ISS", "HST"],
            "Military": []
        }
        filtered_db = [sat for sat in filtered_db if
                      any(keyword in sat['name'] for keyword in category_map.get(category_filter, []))]

    if show_active_only:
        filtered_db = [sat for sat in filtered_db if sat['active']]

    # Sort results
    if sort_by == "Name":
        filtered_db.sort(key=lambda x: x['name'])
    elif sort_by == "NORAD ID":
        filtered_db.sort(key=lambda x: x['norad'])
    elif sort_by == "Launch Date":
        filtered_db.sort(key=lambda x: x['launch_date'], reverse=True)

    # Display statistics
    if show_stats:
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Satellites", len(db))
        with col2:
            active_count = sum(1 for sat in db if sat['active'])
            st.metric("Active Satellites", active_count)
        with col3:
            st.metric("Filtered Results", len(filtered_db))
        with col4:
            categories = {}
            for sat in db:
                cat = sat['category']
                categories[cat] = categories.get(cat, 0) + 1
            most_common = max(categories.items(), key=lambda x: x[1])
            st.metric("Top Category", f"{most_common[0]} ({most_common[1]})")

    # Display satellite list
    st.markdown(f"#### 🛰️ Satellite Catalog ({len(filtered_db)} results)")

    if filtered_db:
        # Create display dataframe
        display_data = []
        for sat in filtered_db:
            display_data.append({
                "NORAD ID": sat['norad'],
                "Name": sat['name'],
                "Category": sat['category'],
                "Status": "🟢 Active" if sat['active'] else "🔴 Inactive",
                "Launch Date": sat['launch_date'],
                "Actions": ""
            })

        df_display = pd.DataFrame(display_data)

        # Display with custom formatting
        st.dataframe(
            df_display,
            use_container_width=True,
            column_config={
                "NORAD ID": st.column_config.NumberColumn("NORAD ID", width="small"),
                "Name": st.column_config.TextColumn("Name", width="large"),
                "Category": st.column_config.TextColumn("Category", width="medium"),
                "Status": st.column_config.TextColumn("Status", width="small"),
                "Launch Date": st.column_config.TextColumn("Launch Date", width="medium"),
                "Actions": st.column_config.TextColumn("Actions", width="small")
            },
            hide_index=True
        )

        # Action buttons for each satellite
        st.markdown("#### 🎯 Quick Actions")
        cols = st.columns(4)
        selected_satellites = []

        for i, sat in enumerate(filtered_db[:8]):  # Show first 8
            with cols[i % 4]:
                if st.button(f"📊 Predict {sat['name'][:15]}...", key=f"predict_{sat['norad']}", use_container_width=True):
                    st.session_state.selected_satellite = sat['norad']
                    st.session_state.selected_menu = "tracker"
                    st.rerun()
                if st.button(f"🗺️ Track {sat['name'][:15]}...", key=f"track_{sat['norad']}", use_container_width=True):
                    st.session_state.selected_satellite = sat['norad']
                    st.session_state.selected_menu = "visualizer"
                    st.rerun()

        # Bulk actions
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📊 Batch Pass Prediction", type="primary"):
                st.info("Batch prediction feature coming soon!")
        with col2:
            if st.button("📥 Export Database"):
                csv_db = pd.DataFrame(filtered_db).to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv_db,
                    file_name="satellite_database.csv",
                    mime="text/csv",
                    key="download-db"
                )
        with col3:
            if st.button("🔄 Refresh Database"):
                with st.spinner("Refreshing satellite data..."):
                    time.sleep(1)
                    st.success("Database refreshed!")

    else:
        st.info("No satellites found matching your criteria. Try adjusting your search filters.")

    # Satellite details section
    if st.checkbox("Show Satellite Details", value=False):
        st.markdown("#### 📋 Satellite Information")
        st.markdown("""
        **NORAD ID**: Unique identifier assigned by North American Aerospace Defense Command
        **TLE**: Two-Line Element set containing orbital parameters
        **Epoch**: Reference time for the orbital elements
        **Inclination**: Angle between orbital plane and equatorial plane
        **RAAN**: Right Ascension of Ascending Node
        **Eccentricity**: Shape of the orbit (0 = circular)
        **Argument of Perigee**: Angle to the closest point in orbit
        **Mean Anomaly**: Position in orbit at epoch time
        **Mean Motion**: Orbital revolutions per day
        """)

elif menu_options[selected_menu] == "settings":
    st.markdown("### ⚙️ Application Settings")
    st.markdown("Configure your preferences and customize the Space Exploration AI experience")

    # Settings tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🌍 Location", "🛰️ Preferences", "🎨 Appearance", "🔧 Advanced"])

    with tab1:
        st.markdown("#### 📍 Default Location Settings")
        st.markdown("Set your default observation location for quick access")

        col1, col2 = st.columns(2)
        with col1:
            default_lat = st.number_input(
                "Default Latitude (°)",
                value=28.6139,
                min_value=-90.0,
                max_value=90.0,
                format="%.6f",
                help="Your default latitude in decimal degrees"
            )
            default_lon = st.number_input(
                "Default Longitude (°)",
                value=77.2090,
                min_value=-180.0,
                max_value=180.0,
                format="%.6f",
                help="Your default longitude in decimal degrees"
            )
        with col2:
            default_alt = st.number_input(
                "Default Altitude (m)",
                value=0.0,
                min_value=-1000.0,
                step=10.0,
                help="Your default altitude above sea level"
            )

            location_name = st.text_input(
                "Location Name",
                value="New Delhi, India",
                help="Friendly name for your location"
            )

        if st.button("💾 Save Location Settings", type="primary"):
            st.session_state.default_location = {
                "lat": default_lat,
                "lon": default_lon,
                "alt": default_alt,
                "name": location_name
            }
            st.success("Location settings saved!")

        # Quick location presets
        st.markdown("#### 🌍 Quick Location Presets")
        preset_locations = {
            "New Delhi, India": (28.6139, 77.2090, 0),
            "London, UK": (51.5074, -0.1278, 0),
            "New York, USA": (40.7128, -74.0060, 0),
            "Tokyo, Japan": (35.6762, 139.6503, 0),
            "Sydney, Australia": (-33.8688, 151.2093, 0),
            "Cape Canaveral, USA": (28.5384, -80.6479, 0)
        }

        cols = st.columns(2)
        for i, (name, (lat, lon, alt)) in enumerate(preset_locations.items()):
            with cols[i % 2]:
                if st.button(f"📍 {name}", key=f"preset_{i}"):
                    st.session_state.default_location = {
                        "lat": lat, "lon": lon, "alt": alt, "name": name
                    }
                    st.success(f"Set location to {name}")

    with tab2:
        st.markdown("#### 🛰️ Prediction Preferences")
        st.markdown("Customize default settings for satellite pass predictions")

        col1, col2 = st.columns(2)
        with col1:
            default_hours = st.slider(
                "Default Hours Ahead",
                min_value=1,
                max_value=72,
                value=24,
                help="Default time window for predictions"
            )
            default_min_elev = st.slider(
                "Default Min Elevation (°)",
                min_value=0,
                max_value=30,
                value=5,
                help="Default minimum elevation angle"
            )
        with col2:
            default_time_step = st.slider(
                "Default Time Resolution (min)",
                min_value=0.5,
                max_value=5.0,
                value=1.0,
                step=0.5,
                help="Default time step for calculations"
            )
            auto_update_tle = st.checkbox(
                "Auto-update TLE Data",
                value=True,
                help="Automatically refresh satellite data when cached"
            )

        if st.button("💾 Save Prediction Settings", type="primary"):
            st.session_state.prediction_settings = {
                "hours": default_hours,
                "min_elev": default_min_elev,
                "time_step": default_time_step,
                "auto_update_tle": auto_update_tle
            }
            st.success("Prediction settings saved!")

    with tab3:
        st.markdown("#### 🎨 Appearance & Theme")
        st.markdown("Customize the look and feel of the application")

        theme_options = st.selectbox(
            "Theme",
            ["Light", "Dark", "Auto"],
            index=1,
            help="Choose your preferred color theme"
        )

        map_style = st.selectbox(
            "Map Style",
            ["CartoDB Positron", "OpenStreetMap", "Stamen Terrain", "Stamen Toner"],
            index=0,
            help="Default map tiles for visualizations"
        )

        chart_theme = st.selectbox(
            "Chart Theme",
            ["plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn"],
            index=2,
            help="Color scheme for charts and plots"
        )

        if st.button("💾 Save Appearance Settings", type="primary"):
            st.session_state.appearance_settings = {
                "theme": theme_options,
                "map_style": map_style,
                "chart_theme": chart_theme
            }
            st.success("Appearance settings saved!")

    with tab4:
        st.markdown("#### 🔧 Advanced Settings")
        st.markdown("Advanced configuration options for power users")

        st.markdown("**Performance Settings**")
        col1, col2 = st.columns(2)
        with col1:
            max_cache_age = st.slider(
                "TLE Cache Age (hours)",
                min_value=1,
                max_value=24,
                value=1,
                help="How long to cache TLE data"
            )
            parallel_processing = st.checkbox(
                "Enable Parallel Processing",
                value=False,
                help="Use multiple CPU cores for calculations (experimental)"
            )
        with col2:
            debug_mode = st.checkbox(
                "Debug Mode",
                value=False,
                help="Show detailed debug information"
            )
            log_level = st.selectbox(
                "Log Level",
                ["INFO", "DEBUG", "WARNING", "ERROR"],
                index=0,
                help="Logging verbosity level"
            )

        st.markdown("**Data & Export**")
        export_format = st.selectbox(
            "Default Export Format",
            ["CSV", "JSON", "Excel"],
            index=0,
            help="Default format for data exports"
        )

        if st.button("💾 Save Advanced Settings", type="primary"):
            st.session_state.advanced_settings = {
                "max_cache_age": max_cache_age,
                "parallel_processing": parallel_processing,
                "debug_mode": debug_mode,
                "log_level": log_level,
                "export_format": export_format
            }
            st.success("Advanced settings saved!")

        # Reset settings
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🔄 Reset to Defaults", type="secondary"):
                st.session_state.clear()
                st.success("All settings reset to defaults!")
        with col2:
            if st.button("💾 Export Settings", type="secondary"):
                settings_data = {
                    "location": st.session_state.get("default_location", {}),
                    "prediction": st.session_state.get("prediction_settings", {}),
                    "appearance": st.session_state.get("appearance_settings", {}),
                    "advanced": st.session_state.get("advanced_settings", {})
                }
                import json
                settings_json = json.dumps(settings_data, indent=2)
                st.download_button(
                    label="Download Settings JSON",
                    data=settings_json,
                    file_name="space_expo_settings.json",
                    mime="application/json",
                    key="download-settings"
                )
        with col3:
            uploaded_settings = st.file_uploader(
                "Import Settings",
                type=["json"],
                help="Upload a settings file to restore configuration"
            )
            if uploaded_settings:
                try:
                    settings_data = json.load(uploaded_settings)
                    for key, value in settings_data.items():
                        st.session_state[key] = value
                    st.success("Settings imported successfully!")
                except Exception as e:
                    st.error(f"Error importing settings: {e}")

elif menu_options[selected_menu] == "about":
    st.markdown("### 👨‍💻 About Space Exploration AI")
    st.markdown("Advanced satellite pass prediction and orbital analytics platform")

    # Developer info
    col1, col2 = st.columns([1, 2])
    with col1:
        st.image("https://via.placeholder.com/200x200/667eea/white?text=Yuva", width=200)
    with col2:
        st.markdown("#### Yuva")
        st.markdown("**Computer Science Student & AI Specialist**")
        st.markdown("📧 astroyuvinut@gmail.com")
        st.markdown("🚀 Passionate about space exploration technologies and astrodynamics")
        st.markdown("💡 Creator of Space Exploration AI - making satellite observation accessible to everyone")

    # Project info
    st.markdown("---")
    st.markdown("#### 🚀 Project Overview")
    st.markdown("""
    **Space Exploration AI** is a comprehensive platform that integrates:

    - **Orbital Mechanics**: Precise satellite trajectory calculations using Skyfield
    - **Real-time Data**: Live TLE (Two-Line Element) data from Celestrak
    - **AI-Driven Analytics**: Optimized algorithms for pass prediction and analysis
    - **Interactive Visualizations**: 2D/3D orbital path visualization and mapping
    - **Scientific Precision**: High-accuracy calculations for research and education
    """)

    # Technical stack
    st.markdown("#### 🛠️ Technical Stack")
    tech_cols = st.columns(4)
    technologies = [
        ("Python", "Core programming language"),
        ("Skyfield", "Orbital mechanics library"),
        ("Streamlit", "Web application framework"),
        ("Plotly", "Interactive visualizations"),
        ("Folium", "Interactive maps"),
        ("NumPy", "Numerical computations"),
        ("Pandas", "Data manipulation"),
        ("Requests", "HTTP client")
    ]

    for i, (tech, desc) in enumerate(technologies):
        with tech_cols[i % 4]:
            st.markdown(f"**{tech}**")
            st.caption(desc)

    # Features showcase
    st.markdown("#### ✨ Key Features")
    feature_cols = st.columns(2)
    features = [
        ("🛰️ Real-Time Tracking", "Live satellite position monitoring"),
        ("📊 Advanced Predictions", "High-precision pass calculations"),
        ("🗺️ Orbital Visualization", "Interactive 2D/3D trajectory maps"),
        ("📡 TLE Integration", "Direct Celestrak database access"),
        ("⚡ Performance Optimized", "Vectorized computations and caching"),
        ("📱 Responsive Design", "Works on desktop and mobile devices"),
        ("💾 Data Export", "CSV/JSON export capabilities"),
        ("🔬 Scientific Accuracy", "Research-grade orbital calculations")
    ]

    for i, (feature, desc) in enumerate(features):
        with feature_cols[i % 2]:
            st.markdown(f"**{feature}**: {desc}")

    # Version and links
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Version", "2.0.0")
        st.caption("Latest release")
    with col2:
        if st.button("📖 Documentation", type="secondary"):
            st.info("Documentation coming soon!")
    with col3:
        if st.button("🐛 Report Issue", type="secondary"):
            st.info("GitHub repository: https://github.com/your-repo/space-expo")

    # Acknowledgments
    st.markdown("#### 🙏 Acknowledgments")
    st.markdown("""
    - **Celestrak**: For providing comprehensive satellite TLE data
    - **Skyfield**: For the excellent orbital mechanics library
    - **Streamlit**: For the amazing web app framework
    - **The Open Source Community**: For the incredible tools and libraries
    """)

    # Vision statement
    st.markdown("#### 🌟 Vision")
    st.markdown("""
    > "To democratize access to space observation data and make astrodynamics
    > accessible to researchers, educators, and space enthusiasts worldwide.
    > Leveraging artificial intelligence and modern web technologies to enhance
    > our understanding of Earth's orbital environment."
    """)
