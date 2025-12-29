"""Unit tests for API views."""

from decimal import Decimal

import pytest
from rest_framework import status

from api.models import BankAccount


@pytest.mark.django_db
class TestAuthentication:
    """Tests for authentication endpoints."""

    def test_register_user(self, api_client):
        """Should register a new user successfully."""
        response = api_client.post(
            "/api/auth/register/",
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "securepass123",
                "password2": "securepass123",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert "username" in response.data

    def test_register_user_password_mismatch(self, api_client):
        """Should reject registration with mismatched passwords."""
        response = api_client.post(
            "/api/auth/register/",
            {
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "securepass123",
                "password2": "differentpass",
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_user(self, api_client, user):
        """Should login and return tokens."""
        response = api_client.post(
            "/api/auth/login/",
            {"username": "testuser", "password": "testpass123"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

    def test_get_current_user(self, auth_client, user):
        """Should return current authenticated user."""
        response = auth_client.get("/api/auth/user/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == "testuser"
        assert response.data["email"] == "test@example.com"

    def test_unauthenticated_access_denied(self, api_client):
        """Should deny access to protected endpoints."""
        response = api_client.get("/api/bank-accounts/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestBankAccountViews:
    """Tests for BankAccount API views."""

    def test_list_bank_accounts(self, auth_client, bank_account):
        """Should list user's bank accounts."""
        response = auth_client.get("/api/bank-accounts/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["name"] == "Test Savings"

    def test_create_bank_account(self, auth_client):
        """Should create a new bank account."""
        response = auth_client.post(
            "/api/bank-accounts/",
            {
                "name": "New Account",
                "bank_name": "New Bank",
                "account_type": "transaction",
                "balance": "5000.00",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "New Account"

    def test_update_bank_account(self, auth_client, bank_account):
        """Should update a bank account."""
        response = auth_client.put(
            f"/api/bank-accounts/{bank_account.id}/",
            {
                "name": "Updated Savings",
                "bank_name": "Test Bank",
                "account_type": "savings",
                "balance": "15000.00",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Updated Savings"
        assert response.data["balance"] == "15000.00"

    def test_delete_bank_account(self, auth_client, bank_account):
        """Should delete a bank account."""
        response = auth_client.delete(f"/api/bank-accounts/{bank_account.id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not BankAccount.objects.filter(id=bank_account.id).exists()

    def test_user_isolation(self, auth_client, another_user):
        """Should not see other user's bank accounts."""
        BankAccount.objects.create(
            user=another_user,
            name="Other Account",
            bank_name="Other Bank",
            account_type="savings",
            balance=Decimal("1000.00"),
        )
        response = auth_client.get("/api/bank-accounts/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0


@pytest.mark.django_db
class TestSuperannuationViews:
    """Tests for Superannuation API views."""

    def test_list_super_accounts(self, auth_client, super_account):
        """Should list user's superannuation accounts."""
        response = auth_client.get("/api/superannuation/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["fund_name"] == "Test Super Fund"

    def test_create_super_account(self, auth_client):
        """Should create a new superannuation account."""
        response = auth_client.post(
            "/api/superannuation/",
            {
                "fund_name": "New Super Fund",
                "account_name": "New Account",
                "member_number": "87654321",
                "balance": "25000.00",
                "employer_contribution": "300.00",
                "personal_contribution": "100.00",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["fund_name"] == "New Super Fund"


@pytest.mark.django_db
class TestCryptoViews:
    """Tests for Crypto API views."""

    def test_list_crypto_holdings(self, auth_client, crypto_holding):
        """Should list user's crypto holdings."""
        response = auth_client.get("/api/crypto-holdings/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["symbol"] == "BTC"

    def test_create_crypto_holding(self, auth_client):
        """Should create a new crypto holding."""
        response = auth_client.post(
            "/api/crypto-holdings/",
            {
                "symbol": "ETH",
                "name": "Ethereum",
                "coingecko_id": "ethereum",
                "quantity": "2.5",
                "average_price": "3000.00",
                "current_price": "3500.00",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["symbol"] == "ETH"
        assert response.data["coingecko_id"] == "ethereum"


@pytest.mark.django_db
class TestNetworthSummary:
    """Tests for networth summary endpoint."""

    def test_networth_summary(
        self,
        auth_client,
        bank_account,
        super_account,
        etf_holding,
        crypto_holding,
        stock_holding,
    ):
        """Should return correct networth summary."""
        response = auth_client.get("/api/summary/")
        assert response.status_code == status.HTTP_200_OK
        assert "total_networth" in response.data
        assert "breakdown" in response.data
        assert "bank_accounts" in response.data["breakdown"]
        assert "superannuation" in response.data["breakdown"]
        assert "etf" in response.data["breakdown"]
        assert "crypto" in response.data["breakdown"]
        assert "stocks" in response.data["breakdown"]

    def test_networth_summary_empty(self, auth_client):
        """Should return zero networth for user with no assets."""
        response = auth_client.get("/api/summary/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["total_networth"] == "0"
