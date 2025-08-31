from fastapi.testclient import TestClient

url_prefix = "/api/v1/auth"

def test_register_user(fake_db, fake_user_service,test_client: TestClient):
    user_data = {
        "email": "test19@example.com",
        "full_name": "Test User",
        "password": "strongpassword"
    }

    response = test_client.post(f"{url_prefix}/register/", json=user_data)

    assert fake_user_service.user_exist_called_once()
    assert fake_user_service.get_user_by_email_called_once_with(fake_db, "test19@example.com")

    assert response.status_code == 201
    assert response.json()["data"] == "User created successfully"

