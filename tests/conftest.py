import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.session import engine, get_db


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def db_session():
    """
    Transactional fixture (SQLAlchemy 2.0 pattern): binds a Session to a
    Connection already inside a transaction, using join_transaction_mode=
    "create_savepoint" so the route's own db.commit() calls only end a
    SAVEPOINT (restarted automatically) rather than the outer transaction.
    Rolling back the outer transaction at teardown undoes everything,
    regardless of how many inner commits occurred.
    """
    connection = engine.connect()
    transaction = connection.begin()

    TestSessionLocal = sessionmaker(
        bind=connection,
        autoflush=False,
        join_transaction_mode="create_savepoint",
    )
    session = TestSessionLocal()

    def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db

    yield session

    session.rollback()
    session.close()
    transaction.rollback()
    connection.close()
    app.dependency_overrides.pop(get_db, None)


@pytest.fixture()
def auth_token(client, db_session):
    """Registers a throwaway user (rolled back after the test) and returns a valid Bearer token."""
    email = "pytest_user@example.com"
    password = "pytestpass123"

    client.post("/api/v1/auth/register", json={"email": email, "password": password})
    response = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )
    return response.json()["access_token"]