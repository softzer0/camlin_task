import pytest
from fastapi import status
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


class TestAuthAPI:
    test_user = {"email": "test@example.com", "password": "testpassword"}

    async def test_register(self, client: AsyncClient):
        response = await client.post("/api/v1/auth/register", json=self.test_user)
        assert response.status_code == status.HTTP_201_CREATED
        assert "access_token" in response.json()

    async def test_login(self, client: AsyncClient):
        response = await client.post("/api/v1/auth/token", json=self.test_user)
        assert response.status_code == status.HTTP_200_OK
        assert "access_token" in response.json()


class TestWalletAPI:
    async def test_get_wallet(self, authorized_client: AsyncClient):
        response = await authorized_client.get("/api/v1/wallet")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "balances" in data
        assert "pln_values" in data
        assert "total_pln" in data

    async def test_add_funds(self, authorized_client: AsyncClient):
        response = await authorized_client.post(
            "/api/v1/wallet/add", json={"currency": "EUR", "amount": "100.00"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["balances"]["EUR"] == "100.00"

    async def test_subtract_funds(self, authorized_client: AsyncClient):
        # First add funds
        await authorized_client.post(
            "/api/v1/wallet/add", json={"currency": "USD", "amount": "100.00"}
        )

        # Then subtract
        response = await authorized_client.post(
            "/api/v1/wallet/subtract", json={"currency": "USD", "amount": "50.00"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["balances"]["USD"] == "50.00"

    async def test_insufficient_funds(self, authorized_client: AsyncClient):
        response = await authorized_client.post(
            "/api/v1/wallet/subtract", json={"currency": "EUR", "amount": "1000.00"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["code"] == "INSUFFICIENT_FUNDS"

    async def test_invalid_currency(self, authorized_client: AsyncClient):
        response = await authorized_client.post(
            "/api/v1/wallet/add", json={"currency": "INVALID", "amount": "100.00"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json()["code"] == "INVALID_CURRENCY"

    @pytest.mark.parametrize(
        "amount,expected_status",
        [
            ("0.00", status.HTTP_400_BAD_REQUEST),
            ("-100.00", status.HTTP_400_BAD_REQUEST),
            ("abc", status.HTTP_422_UNPROCESSABLE_ENTITY),
        ],
    )
    async def test_invalid_amount(
        self, authorized_client: AsyncClient, amount: str, expected_status: int
    ):
        response = await authorized_client.post(
            "/api/v1/wallet/add", json={"currency": "EUR", "amount": amount}
        )
        assert response.status_code == expected_status
