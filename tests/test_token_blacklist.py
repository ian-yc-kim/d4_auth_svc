import datetime
import pytest

from d4_auth_svc.models.token_blacklist import TokenBlacklist
from d4_auth_svc.models.base import SessionLocal, Base, engine

# Ensure that the new table is created in the test database
@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_insert_and_retrieve_token_blacklist(db_session):
    session = db_session
    token_value = "dummy_token_123"
    expires = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    
    # Create new token blacklist record
    record = TokenBlacklist(token=token_value, expires_at=expires)
    session.add(record)
    session.commit()
    
    # Retrieve record
    retrieved = session.get(TokenBlacklist, token_value)
    
    assert retrieved is not None
    assert retrieved.token == token_value
    # Allow slight difference in timestamp due to DB precision
    assert abs((retrieved.expires_at - expires).total_seconds()) < 1


def test_token_blacklist_deletion(db_session):
    session = db_session
    token_value = "delete_token_456"
    expires = datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    
    record = TokenBlacklist(token=token_value, expires_at=expires)
    session.add(record)
    session.commit()

    # Delete the record
    session.delete(record)
    session.commit()
    
    # Ensure the record is deleted
    retrieved = session.get(TokenBlacklist, token_value)
    assert retrieved is None
