import bcrypt
from fastapi import status

from d4_auth_svc.models.user import User

def test_successful_registration(client, db_session, monkeypatch):
    # Flag to verify if email integration is triggered
    email_triggered = False

    def fake_send_email(email, full_name):
        nonlocal email_triggered
        email_triggered = True

    # Monkey patch the email integration function
    monkeypatch.setattr("d4_auth_svc.routers.user_registration.send_welcome_email", fake_send_email)

    payload = {
        "email": "test@example.com",
        "full_name": "Test User",
        "password": "Password1"
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["message"] == "User registered successfully"

    # Verify that the user is stored in the database and the password is hashed
    user = db_session.query(User).filter(User.email == payload["email"]).first()
    assert user is not None
    assert user.hashed_password != payload["password"]
    assert bcrypt.checkpw(payload["password"].encode('utf-8'), user.hashed_password.encode('utf-8'))
    assert email_triggered


def test_duplicate_email_registration(client, db_session):
    payload = {
        "email": "dup@example.com",
        "full_name": "Dup User",
        "password": "Password1"
    }
    # First registration
    response = client.post("/auth/register", json=payload)
    assert response.status_code == status.HTTP_200_OK

    # Second registration with the same email should fail
    response = client.post("/auth/register", json=payload)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    data = response.json()
    assert data["detail"] == "Email already registered"


def test_invalid_email(client):
    payload = {
        "email": "invalid-email",
        "full_name": "Test User",
        "password": "Password1"
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_weak_password(client):
    # Test with a password that is too short
    payload = {
        "email": "weak@example.com",
        "full_name": "Weak Pass",
        "password": "Pass1"
    }
    response = client.post("/auth/register", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Test password missing uppercase letter
    payload["password"] = "password1"
    response = client.post("/auth/register", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Test password missing lowercase letter
    payload["password"] = "PASSWORD1"
    response = client.post("/auth/register", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Test password missing digit
    payload["password"] = "Password"
    response = client.post("/auth/register", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
