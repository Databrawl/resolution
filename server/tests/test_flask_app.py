from unittest.mock import patch
from uuid import uuid4


class TestAuth:
    @patch('flask_app.create_client')
    def test_successful_authentication(self, mock_create_client, client):
        mock_create_client.return_value.auth.get_user.return_value = {"user": {"id": str(uuid4())}}
        valid_headers = {
            "Authorization": "Bearer your_valid_jwt_token_here"}  # Replace with your actual valid JWT token
        response = client.get("onboarding", headers=valid_headers)
        assert response.status_code == 200

    def test_wrong_token(self, client):
        valid_headers = {"Authorization": "Bearer incorrect_token"}
        response = client.get("onboarding", headers=valid_headers)
        assert response.status_code == 401

    def test_no_token(self, client):
        response = client.get("onboarding")
        assert response.status_code == 401
