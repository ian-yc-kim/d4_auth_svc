import bcrypt

from d4_auth_svc.models.user import User


def test_valid_login(client, db_session):
    # Prepare a valid user in the database
    password = "correctpassword"
    try:
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    except Exception as e:
        raise Exception(f"Error hashing password: {e}")

    # Include full_name field to satisfy NOT NULL constraint
    user = User(email="valid@example.com", full_name="Valid User", hashed_password=hashed)
    db_session.add(user)
    db_session.commit()

    response = client.post("/auth/login", json={"email": "valid@example.com", "password": password})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data


def test_nonexistent_email(client):
    # Test login with an email that does not exist in the DB
    response = client.post("/auth/login", json={"email": "nonexistent@example.com", "password": "whatever"})
    assert response.status_code == 401
    data = response.json()
    assert data.get("detail") == "Invalid credentials"


def test_wrong_password(client, db_session):
    # Insert a user with known password
    password = "correctpassword"
    try:
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    except Exception as e:
        raise Exception(f"Error hashing password: {e}")

    # Include full_name field to satisfy NOT NULL constraint
    user = User(email="user@example.com", full_name="Test User", hashed_password=hashed)
    db_session.add(user)
    db_session.commit()

    # Attempt login with wrong password
    response = client.post("/auth/login", json={"email": "user@example.com", "password": "wrongpassword"})
    assert response.status_code == 401
    data = response.json()
    assert data.get("detail") == "Invalid credentials"


def test_missing_fields(client):
    # Missing password field
    response = client.post("/auth/login", json={"email": "user@example.com"})
    assert response.status_code == 422

    # Missing email field
    response = client.post("/auth/login", json={"password": "somepassword"})
    assert response.status_code == 422


def test_malformed_json(client):
    # Malformed JSON payload
    response = client.post("/auth/login", data="not a json", headers={"Content-Type": "application/json"})
    assert response.status_code == 422
