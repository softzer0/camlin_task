from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from motor.motor_asyncio import AsyncIOMotorClient

from app.config import get_settings
from app.core.exceptions import AuthenticationError
from app.core.security import verify_token
from app.models.domain.user import User
from app.repositories.base import BaseRepository
from app.repositories.wallet import WalletRepository
from app.services.auth import AuthService
from app.services.exchange import ExchangeRateService
from app.services.wallet import WalletService

settings = get_settings()
security = HTTPBearer()


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> str:
    try:
        payload = verify_token(credentials.credentials)
        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationError()
        return user_id
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_db_client() -> AsyncGenerator[AsyncIOMotorClient, None]:
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    try:
        yield client
    finally:
        client.close()


async def get_wallet_collection(client: AsyncIOMotorClient = Depends(get_db_client)):
    return client.wallet_app.wallets


async def get_user_collection(client: AsyncIOMotorClient = Depends(get_db_client)):
    return client.wallet_app.users


async def get_user_repository(collection=Depends(get_user_collection)) -> BaseRepository[User]:
    return BaseRepository[User](collection, User)


async def get_wallet_repository(collection=Depends(get_wallet_collection)) -> WalletRepository:
    return WalletRepository(collection)


async def get_exchange_service() -> AsyncGenerator[ExchangeRateService, None]:
    service = ExchangeRateService()
    try:
        yield service
    finally:
        await service.close()


async def get_auth_service(
    user_repository: BaseRepository[User] = Depends(get_user_repository),
) -> AuthService:
    return AuthService(user_repository)


async def get_wallet_service(
    wallet_repository: WalletRepository = Depends(get_wallet_repository),
    exchange_service: ExchangeRateService = Depends(get_exchange_service),
) -> WalletService:
    return WalletService(wallet_repository, exchange_service)


CurrentUser = Annotated[str, Depends(get_current_user_id)]
