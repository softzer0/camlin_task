from typing import Any, Optional

from fastapi import HTTPException, status


class WalletException(HTTPException):
    def __init__(
        self, status_code: int, detail: str, code: str, headers: Optional[dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.code = code


class InsufficientFundsError(WalletException):
    def __init__(self, currency: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient funds in {currency}",
            code="INSUFFICIENT_FUNDS",
        )


class InvalidCurrencyError(WalletException):
    def __init__(self, currency: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid currency: {currency}",
            code="INVALID_CURRENCY",
        )


class ExchangeRateError(WalletException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Exchange rate service temporarily unavailable",
            code="EXCHANGE_SERVICE_UNAVAILABLE",
        )


class AuthenticationError(WalletException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            code="INVALID_CREDENTIALS",
            headers={"WWW-Authenticate": "Bearer"},
        )
