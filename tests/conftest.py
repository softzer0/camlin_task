import asyncio
import uuid
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fakeredis.aioredis import FakeRedis
from fastapi import FastAPI, status
from fastapi_cache import FastAPICache
from httpx import AsyncClient
from mongomock_motor import AsyncMongoMockClient

MOCK_CLIENT = AsyncMongoMockClient()

pytest.MonkeyPatch().setattr(
    "motor.motor_asyncio.AsyncIOMotorClient", lambda *args, **kwargs: MOCK_CLIENT, raising=False
)

MOCK_REDIS = FakeRedis()

pytest.MonkeyPatch().setattr("redis.asyncio", lambda *args, **kwargs: MOCK_REDIS, raising=False)

from fastapi_cache.backends.redis import RedisBackend  # noqa: E402

from app.core.security import get_password_hash  # noqa: E402
from app.main import create_application  # noqa: E402
from app.repositories.wallet import WalletRepository  # noqa: E402
from app.services.exchange import ExchangeRateService  # noqa: E402
from app.services.wallet import WalletService  # noqa: E402


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def mock_db_client() -> AsyncGenerator[AsyncMongoMockClient, None]:
    client = MOCK_CLIENT
    db = client.wallet_app

    await db.users.create_index("email", unique=True)
    await db.wallets.create_index("user_id", unique=True)

    yield client


@pytest.fixture
async def app() -> AsyncGenerator[FastAPI, None]:
    with patch(
        "app.services.exchange.httpx.AsyncClient",
        return_value=get_mock_exchange_rates_httpx_client(),
    ):
        app = create_application()
        FastAPICache.init(RedisBackend(MOCK_REDIS), prefix="fastapi-cache")
        yield app


@pytest.fixture
async def client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        app=app, base_url="http://testserver", headers={"Content-Type": "application/json"}
    ) as ac:
        yield ac


def generate_user_data() -> dict:
    email = f"test_{uuid.uuid4()}@example.com"
    password = "testpassword"
    return {"email": email, "password": password, "hashed_password": get_password_hash(password)}


@pytest.fixture
async def test_user(mock_db_client: AsyncMongoMockClient) -> dict:
    user_data = generate_user_data()
    result = await mock_db_client.wallet_app.users.insert_one(user_data)
    user_data["id"] = str(result.inserted_id)
    return user_data


@pytest.fixture
async def wallet_repository(mock_db_client: AsyncMongoMockClient) -> WalletRepository:
    return WalletRepository(mock_db_client.wallet_app.wallets)


MOCK_EXCHANGE_RATES = [
    {
        "rates": [
            {"code": "EUR", "ask": 4.50},
            {"code": "USD", "ask": 4.00},
            {"code": "GBP", "ask": 5.20},
        ]
    }
]


def get_mock_exchange_rates_httpx_client() -> AsyncMock:
    mock_client = AsyncMock()
    mock_client.get.return_value.json = Mock(return_value=MOCK_EXCHANGE_RATES)
    mock_client.get.return_value.raise_for_status = Mock()

    return mock_client


@pytest.fixture
async def exchange_service() -> AsyncGenerator[ExchangeRateService, None]:
    service = ExchangeRateService()

    mock_client = get_mock_exchange_rates_httpx_client()
    service.client = mock_client

    yield service
    await service.close()


@pytest.fixture
async def wallet_service(
    wallet_repository: WalletRepository, exchange_service: ExchangeRateService
) -> WalletService:
    return WalletService(wallet_repository, exchange_service)


@pytest.fixture
async def auth_token(client: AsyncClient, test_user: dict) -> str:
    response = await client.post(
        "/api/v1/auth/token", json={"email": test_user["email"], "password": test_user["password"]}
    )
    assert (
        response.status_code == status.HTTP_200_OK
    ), f"Failed to get auth token: {response.json()}"
    return response.json()["access_token"]


@pytest.fixture
async def authorized_client(client: AsyncClient, auth_token: str) -> AsyncClient:
    client.headers["Authorization"] = f"Bearer {auth_token}"
    return client
