from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

from app.models.utils import quantize_decimal


class WalletOperation(BaseModel):
    currency: str = Field(min_length=3, max_length=3)
    amount: Decimal = Field(gt=0)

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        return quantize_decimal(v)


class WalletResponse(BaseModel):
    balances: dict[str, Decimal]
    pln_values: dict[str, Decimal]
    total_pln: Decimal

    @field_validator("pln_values", "balances")
    @classmethod
    def validate_decimals(cls, v: dict[str, Decimal]) -> dict[str, Decimal]:
        return {currency: quantize_decimal(amount) for currency, amount in v.items()}

    @field_validator("total_pln")
    @classmethod
    def validate_total(cls, v: Decimal) -> Decimal:
        return quantize_decimal(v)


class WalletBalanceResponse(BaseModel):
    currency: str
    amount: Decimal
    pln_value: Decimal
