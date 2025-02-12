from decimal import Decimal

import pytest

from app.core.exceptions import InsufficientFundsError, InvalidCurrencyError
from app.models.schemas.wallet import WalletOperation
from app.services.exchange import ExchangeRateService
from app.services.wallet import WalletService

pytestmark = pytest.mark.asyncio


class TestWalletService:
    async def test_get_empty_wallet(self, wallet_service: WalletService):
        wallet = await wallet_service.get_wallet("test_user")
        assert wallet.balances == {"PLN": Decimal("0.00")}
        assert wallet.pln_values == {"PLN": Decimal("0.00")}
        assert wallet.total_pln == Decimal("0.00")

    async def test_add_funds(self, wallet_service: WalletService):
        operation = WalletOperation(currency="EUR", amount=Decimal("100.00"))

        result = await wallet_service.add_funds("test_user", operation)
        assert result.balances["EUR"] == Decimal("100.00")
        assert "EUR" in result.pln_values
        assert result.total_pln > Decimal("0")

    async def test_insufficient_funds(self, wallet_service: WalletService):
        operation = WalletOperation(currency="USD", amount=Decimal("50.00"))

        with pytest.raises(InsufficientFundsError):
            await wallet_service.subtract_funds("test_user", operation)

    async def test_invalid_currency(self, wallet_service: WalletService):
        operation = WalletOperation(currency="INVALID", amount=Decimal("100.00"))

        with pytest.raises(InvalidCurrencyError):
            await wallet_service.add_funds("test_user", operation)


class TestExchangeService:
    async def test_get_current_rates(self, exchange_service: ExchangeRateService):
        rates = await exchange_service.get_current_rates()
        assert isinstance(rates, dict)
        assert all(isinstance(rate, Decimal) for rate in rates.values())
        assert "EUR" in rates
        assert "USD" in rates

    async def test_convert_to_pln(self, exchange_service: ExchangeRateService):
        amount = Decimal("100.00")
        pln_value = await exchange_service.convert_to_pln("EUR", amount)

        assert isinstance(pln_value, Decimal)
        assert pln_value > Decimal("0")

    async def test_calculate_wallet_pln_values(self, exchange_service: ExchangeRateService):
        balances = {"EUR": Decimal("100.00"), "USD": Decimal("50.00")}

        pln_values = await exchange_service.calculate_wallet_pln_values(balances)

        assert isinstance(pln_values, dict)
        assert "EUR" in pln_values
        assert "USD" in pln_values
        assert all(isinstance(v, Decimal) for v in pln_values.values())
