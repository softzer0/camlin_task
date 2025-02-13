from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

from app.models.utils import generate_objectid, get_current_time, quantize_decimal


class Wallet(BaseModel):
    id: str = Field(default_factory=generate_objectid)
    user_id: str
    balances: dict[str, Decimal] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=get_current_time)
    updated_at: datetime = Field(default_factory=get_current_time)

    @field_validator("balances")
    @classmethod
    def validate_balances(cls, v: dict[str, Decimal]) -> dict[str, Decimal]:
        return {currency: quantize_decimal(amount) for currency, amount in v.items()}
