from decimal import Decimal
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorCollection

from app.models.domain.wallet import Wallet
from app.models.utils import get_current_time


class WalletRepository:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def get_wallet(self, user_id: str) -> Optional[Wallet]:
        result = await self.collection.find_one({"user_id": user_id})
        return Wallet.model_validate(result) if result else None

    async def update_balance(
        self, user_id: str, currency: str, amount: Decimal, subtract: bool = False
    ) -> Wallet:
        amount_float = float(amount)

        if not subtract:
            update = {
                "$inc": {f"balances.{currency}": amount_float},
                "$set": {"updated_at": get_current_time()},
                "$setOnInsert": {"user_id": user_id, "created_at": get_current_time()},
            }
            result = await self.collection.find_one_and_update(
                {"user_id": user_id}, update, upsert=True, return_document=True
            )
        else:  # subtract
            result = await self.collection.find_one_and_update(
                {"user_id": user_id, f"balances.{currency}": {"$gte": amount_float}},
                {
                    "$inc": {f"balances.{currency}": -amount_float},
                    "$set": {"updated_at": get_current_time()},
                },
                return_document=True,
            )

            if not result:
                raise ValueError("Insufficient funds")

        return Wallet.model_validate(result)
