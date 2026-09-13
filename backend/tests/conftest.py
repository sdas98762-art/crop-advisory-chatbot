import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import os

# Set dummy env vars before importing the app
os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("OPENWEATHER_API_KEY", "test-key")
os.environ.setdefault("CHROMA_PERSIST_DIR", "./test_chroma_db")

from main import app  # noqa: E402


@pytest.fixture
def client():
    return TestClient(app)
