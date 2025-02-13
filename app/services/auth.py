from app.core.exceptions import AuthenticationError
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.domain.user import User
from app.models.schemas.auth import UserCreate, UserLogin
from app.repositories.base import BaseRepository


class AuthService:
    def __init__(self, user_repository: BaseRepository[User]):
        self.user_repository = user_repository

    async def register_user(self, user_data: UserCreate) -> tuple[User, str]:
        existing_user = await self.user_repository.find_one({"email": user_data.email})
        if existing_user:
            raise AuthenticationError()

        hashed_password = get_password_hash(user_data.password)
        user = User(email=user_data.email, hashed_password=hashed_password)

        await self.user_repository.create(user)

        return await self.authenticate_user(
            UserLogin(email=user_data.email, password=user_data.password)
        )

    async def authenticate_user(self, user_data: UserLogin) -> tuple[User, str]:
        user = await self.user_repository.find_one({"email": user_data.email})
        if not user:
            raise AuthenticationError()

        if not verify_password(user_data.password, user.hashed_password):
            raise AuthenticationError()

        access_token = create_access_token({"sub": str(user.id), "email": user.email})

        return user, access_token

    async def get_current_user(self, user_id: str) -> User | None:
        return await self.user_repository.find_one({"id": user_id})
