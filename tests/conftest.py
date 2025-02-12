import asyncio
import uuid
from typing import AsyncGenerator
import pytest
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient
from redis import asyncio as aioredis
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from app.main import create_application
from app.core.security import get_password_hash
from app.repositories.wallet import WalletRepository
from app.services.exchange import ExchangeRateService
from app.services.wallet import WalletService
from app.config import Settings, get_settings


# Override settings for testing
def get_test_settings() -> Settings:
    return Settings(
        MONGODB_URL="mongodb://localhost:27017/test_wallet_app",
        REDIS_URL="redis://localhost:6379/1",
        JWT_SECRET_KEY="test-secret-key",
    )


# Patch settings before importing app
pytest.MonkeyPatch().setattr("app.config.get_settings", get_test_settings)


@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def app() -> FastAPI:
    """Create a FastAPI app for testing."""
    return create_application()


@pytest.fixture(scope="session")
async def redis(event_loop):
    settings = get_test_settings()
    client = aioredis.from_url(settings.REDIS_URL, decode_responses=False)
    await client.flushdb()

    # Initialize FastAPI cache with Redis backend
    FastAPICache.init(RedisBackend(client), prefix="fastapi-cache")

    yield client

    # Cleanup
    await client.flushdb()
    await client.close()


@pytest.fixture(scope="session")
async def mongodb(event_loop):
    settings = get_test_settings()
    client = AsyncIOMotorClient(settings.MONGODB_URL, io_loop=event_loop)
    db = client.get_database("test_wallet_app")

    # Create indexes
    await db.users.create_index("email", unique=True)
    await db.wallets.create_index("user_id", unique=True)

    yield client

    # Cleanup
    await client.drop_database("test_wallet_app")
    client.close()


@pytest.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """Create an HTTP client for testing."""
    async with AsyncClient(
        app=app, base_url="http://testserver", headers={"Content-Type": "application/json"}
    ) as ac:
        yield ac


@pytest.fixture
async def test_user(mongodb: AsyncIOMotorClient) -> dict:
    """Create a test user."""
    email = f"test_{uuid.uuid4()}@example.com"
    user_data = {"email": email, "hashed_password": get_password_hash("testpassword")}
    result = await mongodb.test_wallet_app.users.insert_one(user_data)
    user_data["id"] = str(result.inserted_id)
    return user_data


@pytest.fixture
async def wallet_repository(mongodb: AsyncIOMotorClient) -> WalletRepository:
    return WalletRepository(mongodb.test_wallet_app.wallets)


@pytest.fixture
async def exchange_service() -> AsyncGenerator[ExchangeRateService, None]:
    service = ExchangeRateService()
    yield service
    await service.close()


@pytest.fixture
async def wallet_service(
    wallet_repository: WalletRepository, exchange_service: ExchangeRateService
) -> WalletService:
    return WalletService(wallet_repository, exchange_service)


@pytest.fixture
async def auth_token(client: AsyncClient, test_user: dict) -> str:
    """Get authentication token for test user."""
    response = await client.post(
        "/api/v1/auth/token", json={"email": test_user["email"], "password": "testpassword"}
    )
    return response.json()["access_token"]


@pytest.fixture
async def authorized_client(client: AsyncClient, auth_token: str) -> AsyncClient:
    """Create an authenticated HTTP client."""
    client.headers["Authorization"] = f"Bearer {auth_token}"
    return client
