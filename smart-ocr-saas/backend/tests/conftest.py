"""
Pytest configuration and fixtures.
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Create authentication headers for testing."""
    # This would be replaced with actual token generation in real tests
    return {"Authorization": "Bearer test-token"}
