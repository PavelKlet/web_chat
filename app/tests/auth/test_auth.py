
def test_create_token(mock_auth_manager):
    user_data = {"sub": "testuser@example.com"}

    token = mock_auth_manager.create_access_token(user_data)

    assert token == "mock_token"
    mock_auth_manager.create_access_token.assert_called_once_with(user_data)