# test_scripts/test_excel_serial_date_conversion.py
import sys
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest

sys.path.append(".")
from main import format_date


class TestExcelSerialDateConversion:
    """Test suite for Excel serial date conversion enhancement"""

    def test_converts_excel_serial_45674_to_january_17_2025(self):
        """Test actual Creative Co-op issue: 45674 -> 01/17/2025"""
        # Arrange
        excel_serial = "45674"
        expected_date = "1/17/2025"

        # Act
        result = format_date(excel_serial)

        # Assert
        assert result == expected_date, f"Expected {expected_date}, got {result}"

    def test_converts_various_excel_serial_dates(self):
        """Test multiple Excel serial date conversions"""
        # Arrange
        test_cases = [
            ("44927", "1/1/2023"),  # New Year 2023
            ("44562", "1/1/2022"),  # New Year 2022
            ("44197", "1/1/2021"),  # New Year 2021
            ("45292", "1/1/2024"),  # New Year 2024
            ("1", "12/31/1899"),  # Excel epoch + 1
            ("59999", "2/6/2064"),  # Near upper limit
        ]

        # Act & Assert
        for serial, expected in test_cases:
            result = format_date(serial)
            assert (
                result == expected
            ), f"Serial {serial}: Expected {expected}, got {result}"

    def test_handles_numeric_integer_serial_dates(self):
        """Test conversion when serial date is passed as integer"""
        # Arrange
        serial_int = 45674
        expected = "1/17/2025"

        # Act
        result = format_date(serial_int)

        # Assert
        assert result == expected

    def test_maintains_backward_compatibility_with_iso_dates(self):
        """Test existing ISO date format still works"""
        # Arrange
        test_cases = [
            ("2025-01-17", "1/17/2025"),
            ("2023-12-31", "12/31/2023"),
            ("2022-06-15", "6/15/2022"),
        ]

        # Act & Assert
        for iso_date, expected in test_cases:
            result = format_date(iso_date)
            assert result == expected

    def test_maintains_backward_compatibility_with_us_dates(self):
        """Test existing US date formats still work"""
        # Arrange
        test_cases = [
            ("01/17/2025", "1/17/2025"),  # Already correct
            ("12/31/2023", "12/31/2023"),
            ("06-15-2022", "6/15/2022"),  # Hyphenated
        ]

        # Act & Assert
        for us_date, expected in test_cases:
            result = format_date(us_date)
            assert result == expected

    def test_handles_empty_and_none_dates(self):
        """Test graceful handling of empty/None dates"""
        # Arrange & Act & Assert
        assert format_date("") == ""
        assert format_date(None) == ""
        assert format_date("   ") == ""

    def test_handles_invalid_dates_gracefully(self):
        """Test fallback for unparseable dates"""
        # Arrange
        invalid_dates = [
            "invalid",
            "not-a-date",
            "ABC123",
            "99999999",  # Out of range serial
            "-100",  # Negative serial
        ]

        # Act & Assert
        for invalid in invalid_dates:
            result = format_date(invalid)
            # Should return original value when unparseable
            assert result == invalid or result == ""

    def test_performance_under_1ms_per_conversion(self):
        """Test date conversion performance requirement"""
        import time

        # Arrange
        serial_dates = ["45674", "44927", "44562", "44197", "45292"]

        # Act
        start = time.time()
        for serial in serial_dates * 100:  # Test 500 conversions
            format_date(serial)
        elapsed = time.time() - start

        # Assert
        avg_time_ms = (elapsed / 500) * 1000
        assert (
            avg_time_ms < 1
        ), f"Average conversion time {avg_time_ms:.3f}ms exceeds 1ms limit"

    def test_handles_excel_1900_leap_year_bug(self):
        """Test handling of Excel's 1900 leap year bug"""
        # Excel incorrectly treats 1900 as a leap year
        # Serial 60 = February 29, 1900 (doesn't exist)
        # Serial 61 = March 1, 1900

        # Arrange
        serial_60 = "60"
        serial_61 = "61"

        # Act
        result_60 = format_date(serial_60)
        result_61 = format_date(serial_61)

        # Assert - Should handle the leap year bug gracefully
        assert result_61 == "3/1/1900"
        # Serial 60 should either be 2/28/1900 or 2/29/1900 (handling varies)
        assert result_60 in ["2/28/1900", "2/29/1900"]

    def test_integration_with_creative_coop_processing(self):
        """Test format_date integration in Creative Co-op context"""
        # Arrange
        mock_entities = {"invoice_date": "45674", "vendor": "Creative Co-op"}

        # Act
        formatted_date = format_date(mock_entities.get("invoice_date", ""))

        # Assert
        assert formatted_date == "1/17/2025"
        assert "/" in formatted_date  # Has slashes
        assert len(formatted_date.split("/")) == 3  # Has 3 parts
