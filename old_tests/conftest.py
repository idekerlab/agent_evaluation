import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Database
from app.temporary_database import TemporaryDatabase
from app.test_loaders import load_test_data


@pytest.fixture(scope="session")
def test_db():
    # Create a temporary in-memory database for testing
    db = TemporaryDatabase()
    # Load test data into the temporary database
    load_test_data(db)
    yield db
    # Clean up the database after all tests are finished
    db.close()

@pytest.fixture(scope="session")
def test_client(test_db):
    # Create a test client for the FastAPI application
    with TestClient(app) as client:
        # Set the test database as a dependency override
        app.dependency_overrides[Database] = lambda: test_db
        yield client

@pytest.fixture(scope="function")
def test_data(test_db):
    # Insert test data into the temporary database before each test
    load_test_data(test_db) 
    yield
    # Clean up the test data after each test
    test_db.close()