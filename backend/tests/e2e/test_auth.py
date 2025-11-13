from fastapi.testclient import TestClient
from app.main import app
from app.core.database import get_db, Base, async_engine
from app.config import settings
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
import asyncio

# Create a separate test database
TEST_DATABASE_URL = settings.DATABASE_URL + "_test"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=True, future=True)
TestSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=test_engine, class_=AsyncSession)

async def override_get_db():
    async with TestSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

client = TestClient(app)

def test_signup():
    response = client.post(
        f"{settings.API_V1_STR}/auth/signup",
        json={"email": "test@example.com", "password": "testpassword"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data

def test_login():
    # First, sign up a user
    client.post(
        f"{settings.API_V1_STR}/auth/signup",
        json={"email": "login_test@example.com", "password": "testpassword"},
    )
    
    # Then, log in
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": "login_test@example.com", "password": "testpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert "refresh_token" in data
