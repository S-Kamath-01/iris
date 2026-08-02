def test_register_creates_user(client, db_session):
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "newuser@example.com", "password": "somepassword123"},
    )
    assert response.status_code == 201
    assert response.json()["email"] == "newuser@example.com"


def test_register_rejects_duplicate_email(client, db_session):
    client.post("/api/v1/auth/register", json={"email": "dupe@example.com", "password": "pass12345"})
    response = client.post("/api/v1/auth/register", json={"email": "dupe@example.com", "password": "pass12345"})
    assert response.status_code == 400


def test_login_succeeds_with_correct_credentials(client, db_session):
    client.post("/api/v1/auth/register", json={"email": "logintest@example.com", "password": "correctpass"})
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "logintest@example.com", "password": "correctpass"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_rejects_wrong_password(client, db_session):
    client.post("/api/v1/auth/register", json={"email": "wrongpass@example.com", "password": "correctpass"})
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "wrongpass@example.com", "password": "wrongpass"},
    )
    assert response.status_code == 401