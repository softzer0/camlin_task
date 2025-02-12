from fastapi import APIRouter, Depends, status

from app.api.deps import get_auth_service
from app.models.schemas.auth import TokenResponse, UserCreate, UserLogin
from app.services.auth import AuthService

router = APIRouter()


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=TokenResponse)
async def register(user_data: UserCreate, auth_service: AuthService = Depends(get_auth_service)):
    user, token = await auth_service.register_user(user_data)
    return TokenResponse(access_token=token)


@router.post("/token", response_model=TokenResponse)
async def login(user_data: UserLogin, auth_service: AuthService = Depends(get_auth_service)):
    user, token = await auth_service.authenticate_user(user_data)
    return TokenResponse(access_token=token)
