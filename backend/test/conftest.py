import pytest
from unittest.mock import AsyncMock, Mock
from fastapi.testclient import TestClient

from backend.main import app
from backend.models.db import get_db

mock_db = AsyncMock()
mock_user_service = AsyncMock()

fake_result = Mock()
fake_scalars = Mock()
fake_scalars.first.return_value = None
fake_result.scalars.return_value = fake_scalars
mock_db.execute.return_value = fake_result

def mock_get_db():
    yield mock_db

app.dependency_overrides[get_db] = mock_get_db

@pytest.fixture
def fake_db():
    yield mock_db

@pytest.fixture
def fake_user_service():
    yield mock_user_service


@pytest.fixture
def test_client():
    with TestClient(app) as c:
        yield c