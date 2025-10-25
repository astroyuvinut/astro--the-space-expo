#!/usr/bin/env python3
"""
Unit tests for satellite pass predictor functionality.
"""

import datetime as dt
import unittest
from unittest.mock import Mock, patch
import requests

from skyfield.api import EarthSatellite, load

from src.orbits.pass_predictor_optimized import (
    PassEvent,
    compute_passes_optimized,
    fetch_tle_cached,
    validate_coordinates,
)


class TestCoordinateValidation(unittest.TestCase):
    """Test coordinate validation functions."""

    def test_valid_coordinates(self):
        """Test that valid coordinates pass validation."""
        validate_coordinates(28.6139, 77.2090, 0.0)
        validate_coordinates(-90.0, -180.0, -1000.0)
        validate_coordinates(90.0, 180.0, 10000.0)

    def test_invalid_latitude(self):
        """Test invalid latitude values."""
        with self.assertRaises(ValueError):
            validate_coordinates(91.0, 77.2090, 0.0)
        with self.assertRaises(ValueError):
            validate_coordinates(-91.0, 77.2090, 0.0)

    def test_invalid_longitude(self):
        """Test invalid longitude values."""
        with self.assertRaises(ValueError):
            validate_coordinates(28.6139, 181.0, 0.0)
        with self.assertRaises(ValueError):
            validate_coordinates(28.6139, -181.0, 0.0)

    def test_invalid_altitude(self):
        """Test invalid altitude values."""
        with self.assertRaises(ValueError):
            validate_coordinates(28.6139, 77.2090, -1001.0)


class TestPassComputation(unittest.TestCase):
    """Test pass computation functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.ts = load.timescale()
        # Create a mock satellite (ISS-like orbit)
        self.mock_tle = (
            "ISS (ZARYA)",
            "1 25544U 98067A   24301.50000000  .00000000  00000-0  00000-0 0  9999",
            "2 25544  51.6400  90.0000 0002000   0.0000 000.0000 15.50000000    01"
        )
        self.sat = EarthSatellite(self.mock_tle[1], self.mock_tle[2], self.mock_tle[0], self.ts)

    @patch('src.orbits.pass_predictor_optimized.fetch_tle_cached')
    def test_compute_passes_basic(self, mock_fetch):
        """Test basic pass computation."""
        mock_fetch.return_value = self.mock_tle

        passes = compute_passes_optimized(
            self.sat, 28.6139, 77.2090, 0.0, 6, 5.0
        )

        self.assertIsInstance(passes, list)
        if passes:
            self.assertIsInstance(passes[0], PassEvent)
            self.assertTrue(hasattr(passes[0], 'start'))
            self.assertTrue(hasattr(passes[0], 'peak'))
            self.assertTrue(hasattr(passes[0], 'end'))
            self.assertTrue(hasattr(passes[0], 'max_elevation_deg'))

    def test_invalid_parameters(self):
        """Test invalid computation parameters."""
        # Invalid hours ahead
        with self.assertRaises(ValueError):
            compute_passes_optimized(self.sat, 28.6139, 77.2090, 0.0, 0, 5.0)

        with self.assertRaises(ValueError):
            compute_passes_optimized(self.sat, 28.6139, 77.2090, 0.0, 169, 5.0)

        # Invalid elevation
        with self.assertRaises(ValueError):
            compute_passes_optimized(self.sat, 28.6139, 77.2090, 0.0, 6, -1.0)

        with self.assertRaises(ValueError):
            compute_passes_optimized(self.sat, 28.6139, 77.2090, 0.0, 6, 91.0)


class TestTLEFetching(unittest.TestCase):
    """Test TLE fetching and caching."""

    @patch('requests.get')
    def test_fetch_tle_success(self, mock_get):
        """Test successful TLE fetching."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.text = """ISS (ZARYA)
1 25544U 98067A   24301.50000000  .00000000  00000-0  00000-0 0  9999
2 25544  51.6400  90.0000 0002000   0.0000 000.0000 15.50000000    01"""
        mock_get.return_value = mock_response

        name, l1, l2 = fetch_tle_cached(25544)

        self.assertEqual(name, "ISS (ZARYA)")
        self.assertIn("1 25544U", l1)
        self.assertIn("2 25544", l2)

    @patch('requests.get')
    def test_fetch_tle_network_error(self, mock_get):
        """Test TLE fetching with network error."""
        mock_get.side_effect = requests.RequestException("Network error")

        with self.assertRaises(ValueError):
            fetch_tle_cached(25544)

    @patch('requests.get')
    def test_fetch_tle_invalid_response(self, mock_get):
        """Test TLE fetching with invalid response."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.text = "Invalid TLE data"
        mock_get.return_value = mock_response

        with self.assertRaises(ValueError):
            fetch_tle_cached(25544)


class TestPassEvent(unittest.TestCase):
    """Test PassEvent dataclass."""

    def test_pass_event_creation(self):
        """Test PassEvent creation and attributes."""
        start = dt.datetime.now(dt.timezone.utc).replace(tzinfo=None)
        peak = start + dt.timedelta(minutes=5)
        end = start + dt.timedelta(minutes=10)

        pass_event = PassEvent(start, peak, end, 45.5)

        self.assertEqual(pass_event.start, start)
        self.assertEqual(pass_event.peak, peak)
        self.assertEqual(pass_event.end, end)
        self.assertEqual(pass_event.max_elevation_deg, 45.5)

    def test_pass_event_duration(self):
        """Test pass duration calculation."""
        start = dt.datetime(2025, 1, 1, 12, 0, 0)
        end = dt.datetime(2025, 1, 1, 12, 10, 0)
        peak = dt.datetime(2025, 1, 1, 12, 5, 0)

        pass_event = PassEvent(start, peak, end, 30.0)
        duration = pass_event.end - pass_event.start

        self.assertEqual(duration.total_seconds(), 600)  # 10 minutes


if __name__ == '__main__':
    unittest.main()
