#!/usr/bin/env python3
"""
Simple test to demonstrate the optimization improvements.
"""

import time

from skyfield.api import EarthSatellite, load

from src.orbits.pass_predictor import compute_passes as compute_passes_original

# Import both versions
from src.orbits.pass_predictor_optimized import compute_passes_optimized, fetch_tle_cached


def test_performance():
    """Test performance comparison between original and optimized versions."""
    print("=" * 60)
    print("SATELLITE PASS PREDICTOR OPTIMIZATION TEST")
    print("=" * 60)

    # Test parameters
    lat = 28.6139  # New Delhi
    lon = 77.2090
    alt_m = 0.0
    hours = 24
    min_elev = 5.0
    norad = 25544  # ISS

    print(f"Location: {lat:.4f}°N, {lon:.4f}°E")
    print(f"Search window: {hours} hours")
    print(f"Minimum elevation: {min_elev}°")
    print(f"Satellite: NORAD {norad} (ISS)")
    print()

    # Fetch TLE data
    print("Fetching TLE data...")
    name, l1, l2 = fetch_tle_cached(norad)
    print(f"Satellite: {name}")

    # Create satellite object
    ts = load.timescale()
    sat = EarthSatellite(l1, l2, name, ts)

    # Test original implementation
    print("\n" + "-" * 40)
    print("TESTING ORIGINAL IMPLEMENTATION")
    print("-" * 40)
    start_time = time.time()
    original_passes = compute_passes_original(sat, lat, lon, alt_m, hours, min_elev)
    original_time = time.time() - start_time

    print(f"Execution time: {original_time:.3f} seconds")
    print(f"Passes found: {len(original_passes)}")

    # Test optimized implementation
    print("\n" + "-" * 40)
    print("TESTING OPTIMIZED IMPLEMENTATION")
    print("-" * 40)
    start_time = time.time()
    optimized_passes = compute_passes_optimized(sat, lat, lon, alt_m, hours, min_elev)
    optimized_time = time.time() - start_time

    print(f"Execution time: {optimized_time:.3f} seconds")
    print(f"Passes found: {len(optimized_passes)}")

    # Calculate improvement
    if optimized_time > 0:
        speedup = original_time / optimized_time
        time_saved = original_time - optimized_time
        print(f"\nSPEEDUP: {speedup:.2f}x faster")
        print(f"TIME SAVED: {time_saved:.3f} seconds")

    # Verify accuracy
    passes_match = len(original_passes) == len(optimized_passes)
    if passes_match and original_passes:
        # Check timing accuracy (within 2 minutes tolerance)
        tolerance_minutes = 2
        for orig, opt in zip(original_passes, optimized_passes):
            start_diff = abs((orig.start - opt.start).total_seconds() / 60)
            if start_diff > tolerance_minutes:
                passes_match = False
                break

    print(f"ACCURACY: {'VERIFIED' if passes_match else 'MISMATCH'}")

    # Display passes
    if optimized_passes:
        print("\n" + "-" * 40)
        print("UPCOMING PASSES (Optimized Results)")
        print("-" * 40)
        for i, p in enumerate(optimized_passes, 1):
            duration = (p.end - p.start).total_seconds() / 60
            print(f"Pass {i}:")
            print(f"  Start: {p.start.strftime('%Y-%m-%d %H:%M')} UTC")
            print(f"  Peak:  {p.peak.strftime('%Y-%m-%d %H:%M')} UTC")
            print(f"  End:   {p.end.strftime('%Y-%m-%d %H:%M')} UTC")
            print(f"  Max Elevation: {p.max_elevation_deg:.1f}°")
            print(f"  Duration: {duration:.1f} minutes")
            print()

    print("=" * 60)
    print("OPTIMIZATION SUMMARY")
    print("=" * 60)
    print("✓ Adaptive time stepping algorithm")
    print("✓ Vectorized computations with NumPy")
    print("✓ TLE data caching with TTL")
    print("✓ Enhanced input validation")
    print("✓ Improved error handling")
    print("✓ Memory optimization")
    print("=" * 60)

if __name__ == "__main__":
    try:
        test_performance()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
