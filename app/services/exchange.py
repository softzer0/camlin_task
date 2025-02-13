from decimal import Decimal

import httpx
from fastapi_cache.decorator import cache

from app.config import get_settings
from app.core.exceptions import ExchangeRateError
from app.models.utils import quantize_decimal

settings = get_settings()


class ExchangeRateService:
    def __init__(self):
        self.base_url = f"{settings.NBP_API_BASE_URL}/exchangerates/tables/C"
        self.client = httpx.AsyncClient(timeout=10.0)

    async def close(self):
        await self.client.aclose()

    @cache(expire=1800, key_builder=lambda *args, **kwargs: "exchange_rates")
    async def get_current_rates(self) -> dict[str, Decimal]:
        try:
            response = await self.client.get(self.base_url, headers={"Accept": "application/json"})
            response.raise_for_status()

            data = response.json()[0]
            return {rate["code"]: quantize_decimal(rate["ask"]) for rate in data["rates"]}

        except (httpx.HTTPError, IndexError, KeyError) as e:
            raise ExchangeRateError() from e

    async def convert_to_pln(self, currency: str, amount: Decimal) -> Decimal | None:
        if currency == "PLN":
            return amount

        rates = await self.get_current_rates()
        rate = rates.get(currency)

        if not rate:
            return None

        return quantize_decimal(amount * rate)

    async def calculate_wallet_pln_values(self, balances: dict[str, Decimal]) -> dict[str, Decimal]:
        if not balances:
            return {}

        rates = await self.get_current_rates()
        pln_values = {}

        for currency, amount in balances.items():
            if currency == "PLN":
                pln_values[currency] = amount
            elif rate := rates.get(currency):
                pln_values[currency] = quantize_decimal(amount * rate)

        return pln_values
