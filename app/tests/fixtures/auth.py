from unittest.mock import MagicMock

import pytest

from app.application.services.auth.auth_manager import AuthManager


@pytest.fixture
def mock_auth_manager():
    mock_manager = MagicMock(spec=AuthManager)
    mock_manager.create_access_token.return_value = "mock_token"
    return mock_manager
