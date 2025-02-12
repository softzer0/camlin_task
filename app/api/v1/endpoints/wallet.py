from fastapi import APIRouter, Depends
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache

from app.api.deps import CurrentUser, get_wallet_service
from app.models.schemas.wallet import WalletOperation, WalletResponse
from app.services.wallet import WalletService

router = APIRouter()


@router.get(
    "", response_model=WalletResponse, description="Get current wallet status with PLN values"
)
@cache(expire=60, key_builder=lambda *args, **kwargs: f"wallet:{kwargs['kwargs']['current_user']}")
async def get_wallet(
    current_user: CurrentUser, wallet_service: WalletService = Depends(get_wallet_service)
) -> WalletResponse:
    return await wallet_service.get_wallet(current_user)


@router.post("/add", response_model=WalletResponse, description="Add funds to wallet")
async def add_funds(
    operation: WalletOperation,
    current_user: CurrentUser,
    wallet_service: WalletService = Depends(get_wallet_service),
) -> WalletResponse:
    result = await wallet_service.add_funds(current_user, operation)
    await FastAPICache.get_backend().clear(key=f"wallet:{current_user}")
    return result


@router.post("/subtract", response_model=WalletResponse, description="Subtract funds from wallet")
async def subtract_funds(
    operation: WalletOperation,
    current_user: CurrentUser,
    wallet_service: WalletService = Depends(get_wallet_service),
) -> WalletResponse:
    result = await wallet_service.subtract_funds(current_user, operation)
    await FastAPICache.get_backend().clear(key=f"wallet:{current_user}")
    return result
