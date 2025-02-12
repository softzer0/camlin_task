from decimal import Decimal

from app.core.exceptions import InsufficientFundsError, InvalidCurrencyError
from app.models.domain.wallet import Wallet
from app.models.schemas.wallet import WalletOperation, WalletResponse
from app.models.utils import quantize_decimal
from app.repositories.wallet import WalletRepository
from app.services.exchange import ExchangeRateService


class WalletService:
    def __init__(self, wallet_repository: WalletRepository, exchange_service: ExchangeRateService):
        self.wallet_repository = wallet_repository
        self.exchange_service = exchange_service

    async def get_wallet(self, user_id: str) -> WalletResponse:
        wallet = await self.wallet_repository.get_wallet(user_id)
        if not wallet:
            wallet = await self._create_wallet(user_id)

        pln_values = await self.exchange_service.calculate_wallet_pln_values(wallet.balances)

        total_pln = quantize_decimal(sum(pln_values.values(), Decimal("0")))

        return WalletResponse(balances=wallet.balances, pln_values=pln_values, total_pln=total_pln)

    async def add_funds(self, user_id: str, operation: WalletOperation) -> WalletResponse:
        await self._validate_currency(operation.currency)

        await self.wallet_repository.update_balance(
            user_id=user_id,
            currency=operation.currency,
            amount=operation.amount,
        )

        return await self.get_wallet(user_id)

    async def subtract_funds(self, user_id: str, operation: WalletOperation) -> WalletResponse:
        await self._validate_currency(operation.currency)

        try:
            await self.wallet_repository.update_balance(
                user_id=user_id,
                currency=operation.currency,
                amount=operation.amount,
                subtract=True,
            )
        except ValueError:
            raise InsufficientFundsError(operation.currency)

        return await self.get_wallet(user_id)

    async def _create_wallet(self, user_id: str) -> Wallet:
        wallet = Wallet(user_id=user_id)
        wallet = await self.wallet_repository.update_balance(
            user_id=user_id,
            currency="PLN",
            amount=Decimal("0"),
        )
        return wallet

    async def _validate_currency(self, currency: str) -> None:
        if currency == "PLN":
            return

        rates = await self.exchange_service.get_current_rates()
        if currency not in rates:
            raise InvalidCurrencyError(currency)
