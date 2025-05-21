import datetime
import pytest

from fastapi.testclient import TestClient
from d4_auth_svc.models.token_blacklist import TokenBlacklist
from d4_auth_svc.app import app

client = TestClient(app)


def test_logout_missing_header():
    response = client.post("/auth/logout")
    assert response.status_code == 400
    assert response.json()["detail"] == "Missing or malformed Authorization header"


def test_logout_malformed_header():
    headers = {"Authorization": "InvalidToken"}
    response = client.post("/auth/logout", headers=headers)
    assert response.status_code == 400
    assert response.json()["detail"] == "Missing or malformed Authorization header"


@pytest.fixture
def db_session(client):
    # Retrieve the dependency overrode in the client, which is our session fixture
    # This assumes the same underlying session is used by the client.
    from d4_auth_svc.models.base import get_db
    generator = app.dependency_overrides.get(get_db)()
    session = next(generator)
    yield session
    try:
        session.rollback()
    except Exception:
        pass


def test_logout_success(db_session):
    token = "valid_token_123"
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/auth/logout", headers=headers)
    assert response.status_code == 200
    response_data = response.json()
    assert "Logout successful" in response_data.get("message", "")

    # Verify that the token has been inserted in the token_blacklist
    record = db_session.get(TokenBlacklist, token)
    assert record is not None


def test_logout_already_blacklisted(db_session):
    token = "blacklisted_token_456"
    # Insert token into blacklist
    expires = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    record = TokenBlacklist(token=token, expires_at=expires)
    db_session.add(record)
    db_session.commit()

    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/auth/logout", headers=headers)
    assert response.status_code == 401
    assert response.json()["detail"] == "Token already invalidated"
