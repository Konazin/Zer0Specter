"""Pytest configuration and fixtures for ZeroSpecter."""

import pytest
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from zer0specter.utils.logger import setup_logger

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Setup test environment."""
    # Configure logging for tests
    setup_logger(level="WARNING")

@pytest.fixture
def sample_wordlist(tmp_path):
    """Create a sample wordlist file for testing."""
    wordlist = tmp_path / "wordlist.txt"
    wordlist.write_text("password\n123456\nadmin\nletmein\nqwerty\n")
    return str(wordlist)

@pytest.fixture
def mock_ip_response():
    """Mock response for IP geolocation API."""
    return {
        "ip": "8.8.8.8",
        "country": "United States",
        "city": "Mountain View",
        "region": "California",
        "loc": "37.3860,-122.0840",
        "org": "AS15169 Google LLC",
        "timezone": "America/Los_Angeles"
    }
