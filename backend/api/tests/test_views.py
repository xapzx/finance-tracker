"""Unit tests for API views."""

from datetime import date
from decimal import Decimal

import pytest
from rest_framework import status

from api.models import (
    AssetSnapshot,
    BankAccount,
    NetWorthSnapshot,
)


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


@pytest.mark.django_db
class TestAssetSnapshotViews:
    """Tests for AssetSnapshot API views."""

    def test_list_asset_snapshots(self, auth_client, user):
        """Should list user's asset snapshots."""
        AssetSnapshot.objects.create(
            user=user,
            date=date(2024, 1, 31),
            asset_type="bank",
            asset_name="ANZ",
            value=Decimal("10000.00"),
        )
        response = auth_client.get("/api/asset-snapshots/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["asset_name"] == "ANZ"

    def test_create_asset_snapshot(self, auth_client):
        """Should create a new asset snapshot."""
        response = auth_client.post(
            "/api/asset-snapshots/",
            {
                "date": "2024-01-31",
                "asset_type": "bank",
                "asset_name": "ANZ - Savings",
                "asset_identifier": "savings",
                "value": "10000.00",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["asset_name"] == "ANZ - Savings"
        assert response.data["value"] == "10000.00"

    def test_create_asset_snapshot_with_quantity(self, auth_client):
        """Should create asset snapshot with quantity and price."""
        response = auth_client.post(
            "/api/asset-snapshots/",
            {
                "date": "2024-01-31",
                "asset_type": "etf",
                "asset_name": "VAS",
                "asset_identifier": "VAS",
                "value": "9500.00",
                "quantity": "100.000000",
                "price_per_unit": "95.0000",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["quantity"] == "100.0000000000"
        assert response.data["price_per_unit"] == "95.0000"

    def test_user_isolation_asset_snapshots(self, auth_client, another_user):
        """Should not see other user's asset snapshots."""
        AssetSnapshot.objects.create(
            user=another_user,
            date=date(2024, 1, 31),
            asset_type="bank",
            asset_name="Other Bank",
            value=Decimal("5000.00"),
        )
        response = auth_client.get("/api/asset-snapshots/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0


@pytest.mark.django_db
class TestNetWorthSnapshotViews:
    """Tests for NetWorthSnapshot API views."""

    def test_list_networth_snapshots(self, auth_client, user):
        """Should list user's net worth snapshots."""
        NetWorthSnapshot.objects.create(
            user=user, date=date(2024, 1, 31), notes="January snapshot"
        )
        AssetSnapshot.objects.create(
            user=user,
            date=date(2024, 1, 31),
            asset_type="bank",
            asset_name="ANZ",
            value=Decimal("10000.00"),
        )

        response = auth_client.get("/api/networth-snapshots/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["notes"] == "January snapshot"
        assert response.data[0]["total_assets"] == "10000.00"

    def test_networth_snapshot_includes_asset_snapshots(
        self, auth_client, user
    ):
        """Should include asset snapshots in response."""
        NetWorthSnapshot.objects.create(user=user, date=date(2024, 1, 31))
        AssetSnapshot.objects.create(
            user=user,
            date=date(2024, 1, 31),
            asset_type="bank",
            asset_name="ANZ",
            value=Decimal("10000.00"),
        )
        AssetSnapshot.objects.create(
            user=user,
            date=date(2024, 1, 31),
            asset_type="super",
            asset_name="Super Fund",
            value=Decimal("50000.00"),
        )

        response = auth_client.get("/api/networth-snapshots/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data[0]["asset_snapshots"]) == 2

    def test_networth_snapshot_calculated_fields(self, auth_client, user):
        """Should include calculated category totals."""
        NetWorthSnapshot.objects.create(user=user, date=date(2024, 1, 31))
        AssetSnapshot.objects.create(
            user=user,
            date=date(2024, 1, 31),
            asset_type="bank",
            asset_name="ANZ",
            value=Decimal("10000.00"),
        )
        AssetSnapshot.objects.create(
            user=user,
            date=date(2024, 1, 31),
            asset_type="super",
            asset_name="Super",
            value=Decimal("50000.00"),
        )

        response = auth_client.get("/api/networth-snapshots/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data[0]["bank_accounts"] == "10000.00"
        assert response.data[0]["superannuation"] == "50000.00"
        assert response.data[0]["total_assets"] == "60000.00"

    def test_create_networth_snapshot_auto_captures_assets(
        self,
        auth_client,
        bank_account,
        super_account,
        etf_holding,
        crypto_holding,
        stock_holding,
    ):
        """Should automatically capture all current holdings."""
        response = auth_client.post(
            "/api/networth-snapshots/create/",
            {"date": "2024-01-31", "notes": "End of January"},
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["message"] == "Snapshot created successfully"
        assert response.data["assets_captured"] == 5

        # Verify asset snapshots were created
        asset_snapshots = AssetSnapshot.objects.filter(date=date(2024, 1, 31))
        assert asset_snapshots.count() == 5

        # Verify snapshot totals
        snapshot = response.data["snapshot"]
        assert Decimal(snapshot["total_assets"]) > 0
        assert Decimal(snapshot["bank_accounts"]) == bank_account.balance
        assert Decimal(snapshot["superannuation"]) == super_account.balance

    def test_create_networth_snapshot_requires_date(self, auth_client):
        """Should require date field."""
        response = auth_client.post("/api/networth-snapshots/create/", {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Date is required" in response.data["error"]

    def test_create_networth_snapshot_updates_existing(
        self, auth_client, bank_account
    ):
        """Should update existing snapshot for same date."""
        # Create first snapshot
        response1 = auth_client.post(
            "/api/networth-snapshots/create/",
            {"date": "2024-01-31", "notes": "First note"},
        )
        assert response1.status_code == status.HTTP_201_CREATED

        # Update bank balance
        bank_account.balance = Decimal("20000.00")
        bank_account.save()

        # Create snapshot for same date
        response2 = auth_client.post(
            "/api/networth-snapshots/create/",
            {"date": "2024-01-31", "notes": "Updated note"},
        )
        assert response2.status_code == status.HTTP_200_OK
        assert response2.data["message"] == "Snapshot updated successfully"

        # Should only have one snapshot for this date
        assert (
            NetWorthSnapshot.objects.filter(date=date(2024, 1, 31)).count()
            == 1
        )

        # Asset snapshots should be updated
        asset_snapshots = AssetSnapshot.objects.filter(date=date(2024, 1, 31))
        bank_snapshot = asset_snapshots.get(asset_type="bank")
        assert bank_snapshot.value == Decimal("20000.00")

    def test_delete_networth_snapshot(self, auth_client, user):
        """Should delete net worth snapshot."""
        snapshot = NetWorthSnapshot.objects.create(
            user=user, date=date(2024, 1, 31)
        )
        AssetSnapshot.objects.create(
            user=user,
            date=date(2024, 1, 31),
            asset_type="bank",
            asset_name="ANZ",
            value=Decimal("10000.00"),
        )

        response = auth_client.delete(
            f"/api/networth-snapshots/{snapshot.id}/"
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not NetWorthSnapshot.objects.filter(id=snapshot.id).exists()

    def test_networth_snapshot_change_calculation(self, auth_client, user):
        """Should calculate change from previous snapshot."""
        # First snapshot
        NetWorthSnapshot.objects.create(user=user, date=date(2024, 1, 31))
        AssetSnapshot.objects.create(
            user=user,
            date=date(2024, 1, 31),
            asset_type="bank",
            asset_name="ANZ",
            value=Decimal("10000.00"),
        )

        # Second snapshot
        NetWorthSnapshot.objects.create(user=user, date=date(2024, 2, 29))
        AssetSnapshot.objects.create(
            user=user,
            date=date(2024, 2, 29),
            asset_type="bank",
            asset_name="ANZ",
            value=Decimal("12000.00"),
        )

        response = auth_client.get("/api/networth-snapshots/")
        assert response.status_code == status.HTTP_200_OK

        # Find the February snapshot in response
        feb_snapshot = next(
            s for s in response.data if s["date"] == "2024-02-29"
        )
        assert feb_snapshot["change_from_previous"] == "2000.00"
        assert feb_snapshot["change_percentage"] == "20.00"

    def test_user_isolation_networth_snapshots(
        self, auth_client, another_user
    ):
        """Should not see other user's net worth snapshots."""
        NetWorthSnapshot.objects.create(
            user=another_user, date=date(2024, 1, 31)
        )
        AssetSnapshot.objects.create(
            user=another_user,
            date=date(2024, 1, 31),
            asset_type="bank",
            asset_name="Other",
            value=Decimal("5000.00"),
        )

        response = auth_client.get("/api/networth-snapshots/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0
