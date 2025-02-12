from datetime import UTC, datetime
from decimal import Decimal

from bson import ObjectId


def generate_objectid() -> str:
    return str(ObjectId())


def get_current_time() -> datetime:
    return datetime.now(UTC)


def quantize_decimal(amount: Decimal | str | int | float) -> Decimal:
    if not isinstance(amount, Decimal):
        amount = Decimal(str(amount))
    return amount.quantize(Decimal("0.01"))
