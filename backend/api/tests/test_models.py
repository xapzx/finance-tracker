"""Unit tests for API models."""

from datetime import date
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.db import IntegrityError

from api.models import (
    AssetSnapshot,
    NetWorthSnapshot,
    SuperannuationSnapshot,
    UserPreferences,
)


@pytest.mark.django_db
class TestUserPreferences:
    """Tests for UserPreferences model."""

    def test_user_preferences_created_on_user_creation(self):
        """UserPreferences should be auto-created when a user is created."""
        user = User.objects.create_user(
            username="newuser", email="new@example.com", password="pass123"
        )
        assert UserPreferences.objects.filter(user=user).exists()

    def test_user_preferences_defaults(self, user):
        """UserPreferences should have correct default values."""
        prefs = UserPreferences.objects.get(user=user)
        assert prefs.currency == "AUD"
        assert prefs.timezone == "Australia/Sydney"
        assert prefs.country == "Australia"

    def test_user_preferences_str(self, user):
        """UserPreferences __str__ should return username preferences."""
        prefs = UserPreferences.objects.get(user=user)
        assert str(prefs) == f"{user.username} preferences"


@pytest.mark.django_db
class TestBankAccount:
    """Tests for BankAccount model."""

    def test_bank_account_creation(self, bank_account):
        """BankAccount should be created with correct values."""
        assert bank_account.name == "Test Savings"
        assert bank_account.bank_name == "Test Bank"
        assert bank_account.account_type == "savings"
        assert bank_account.balance == Decimal("10000.00")

    def test_bank_account_str(self, bank_account):
        """BankAccount __str__ should return bank and name."""
        assert str(bank_account) == "Test Bank - Test Savings"


@pytest.mark.django_db
class TestSuperannuationAccount:
    """Tests for SuperannuationAccount model."""

    def test_super_account_creation(self, super_account):
        """SuperannuationAccount should be created with correct values."""
        assert super_account.fund_name == "Test Super Fund"
        assert super_account.balance == Decimal("50000.00")

    def test_super_account_str(self, super_account):
        """SuperannuationAccount __str__ should return fund and account name."""
        assert str(super_account) == "Test Super Fund - My Super"


@pytest.mark.django_db
class TestSuperannuationSnapshot:
    """Tests for SuperannuationSnapshot model."""

    def test_snapshot_total_contributions(self, super_account):
        """Snapshot should calculate total contributions correctly."""
        snapshot = SuperannuationSnapshot.objects.create(
            account=super_account,
            date="2024-01-31",
            balance=Decimal("51000.00"),
            employer_contribution=Decimal("500.00"),
            personal_contribution=Decimal("200.00"),
        )
        assert snapshot.total_contributions == Decimal("700.00")

    def test_snapshot_investment_gain_first_snapshot(self, super_account):
        """First snapshot should have zero investment gain."""
        snapshot = SuperannuationSnapshot.objects.create(
            account=super_account,
            date="2024-01-31",
            balance=Decimal("51000.00"),
            employer_contribution=Decimal("500.00"),
            personal_contribution=Decimal("200.00"),
        )
        assert snapshot.investment_gain == Decimal("0.00")

    def test_snapshot_investment_gain_subsequent(self, super_account):
        """Subsequent snapshots should calculate investment gain correctly."""
        # First snapshot
        SuperannuationSnapshot.objects.create(
            account=super_account,
            date="2024-01-31",
            balance=Decimal("50000.00"),
            employer_contribution=Decimal("0.00"),
            personal_contribution=Decimal("0.00"),
        )
        # Second snapshot with contributions and market gain
        snapshot2 = SuperannuationSnapshot.objects.create(
            account=super_account,
            date="2024-02-29",
            balance=Decimal("52000.00"),
            employer_contribution=Decimal("500.00"),
            personal_contribution=Decimal("200.00"),
        )
        # Balance change: 52000 - 50000 = 2000
        # Contributions: 500 + 200 = 700
        # Investment gain: 2000 - 700 = 1300
        assert snapshot2.investment_gain == Decimal("1300.00")


@pytest.mark.django_db
class TestETFHolding:
    """Tests for ETFHolding model."""

    def test_etf_holding_market_value(self, etf_holding):
        """ETFHolding should calculate market value correctly."""
        # 100 units * $95 = $9500
        assert etf_holding.market_value == Decimal("9500.000000")

    def test_etf_holding_cost_basis(self, etf_holding):
        """ETFHolding should calculate cost basis correctly."""
        # 100 units * $90 = $9000
        assert etf_holding.cost_basis == Decimal("9000.000000")

    def test_etf_holding_unrealised_gain(self, etf_holding):
        """ETFHolding should calculate unrealised gain correctly."""
        # $9500 - $9000 = $500
        assert etf_holding.unrealised_gain == Decimal("500.000000")

    def test_etf_holding_str(self, etf_holding):
        """ETFHolding __str__ should return symbol and units."""
        assert str(etf_holding) == "VAS - 100.000000 units"


@pytest.mark.django_db
class TestCryptoHolding:
    """Tests for CryptoHolding model."""

    def test_crypto_holding_market_value(self, crypto_holding):
        """CryptoHolding should calculate market value correctly."""
        # 0.5 BTC * $100,000 = $50,000
        assert crypto_holding.market_value == Decimal("50000.0000000000")

    def test_crypto_holding_cost_basis(self, crypto_holding):
        """CryptoHolding should calculate cost basis correctly."""
        # 0.5 BTC * $80,000 = $40,000
        assert crypto_holding.cost_basis == Decimal("40000.0000000000")

    def test_crypto_holding_unrealised_gain(self, crypto_holding):
        """CryptoHolding should calculate unrealised gain correctly."""
        # $50,000 - $40,000 = $10,000
        assert crypto_holding.unrealised_gain == Decimal("10000.0000000000")

    def test_crypto_holding_str(self, crypto_holding):
        """CryptoHolding __str__ should return symbol and quantity."""
        assert str(crypto_holding) == "BTC - 0.5000000000"


@pytest.mark.django_db
class TestStockHolding:
    """Tests for StockHolding model."""

    def test_stock_holding_market_value(self, stock_holding):
        """StockHolding should calculate market value correctly."""
        # 50 units * $120 = $6000
        assert stock_holding.market_value == Decimal("6000.000000")

    def test_stock_holding_cost_basis(self, stock_holding):
        """StockHolding should calculate cost basis correctly."""
        # 50 units * $100 = $5000
        assert stock_holding.cost_basis == Decimal("5000.000000")

    def test_stock_holding_unrealised_gain(self, stock_holding):
        """StockHolding should calculate unrealised gain correctly."""
        # $6000 - $5000 = $1000
        assert stock_holding.unrealised_gain == Decimal("1000.000000")

    def test_stock_holding_str(self, stock_holding):
        """StockHolding __str__ should return symbol and units."""
        assert str(stock_holding) == "CBA - 50.000000 units"


@pytest.mark.django_db
class TestAssetSnapshot:
    """Tests for AssetSnapshot model."""

    def test_asset_snapshot_creation_bank(self, user):
        """AssetSnapshot should be created for bank account."""
        snapshot = AssetSnapshot.objects.create(
            user=user,
            date=date(2024, 1, 31),
            asset_type="bank",
            asset_name="ANZ - Savings",
            asset_identifier="savings",
            value=Decimal("10000.00"),
        )
        assert snapshot.asset_type == "bank"
        assert snapshot.asset_name == "ANZ - Savings"
        assert snapshot.value == Decimal("10000.00")
        assert snapshot.quantity is None
        assert snapshot.price_per_unit is None

    def test_asset_snapshot_creation_investment(self, user):
        """AssetSnapshot should be created for investment with quantity and price."""
        snapshot = AssetSnapshot.objects.create(
            user=user,
            date=date(2024, 1, 31),
            asset_type="etf",
            asset_name="Vanguard Australian Shares",
            asset_identifier="VAS",
            value=Decimal("9500.00"),
            quantity=Decimal("100.000000"),
            price_per_unit=Decimal("95.0000"),
        )
        assert snapshot.asset_type == "etf"
        assert snapshot.quantity == Decimal("100.000000")
        assert snapshot.price_per_unit == Decimal("95.0000")
        assert snapshot.value == Decimal("9500.00")

    def test_asset_snapshot_str(self, user):
        """AssetSnapshot __str__ should return formatted string."""
        snapshot = AssetSnapshot.objects.create(
            user=user,
            date=date(2024, 1, 31),
            asset_type="bank",
            asset_name="ANZ - Savings",
            asset_identifier="savings",
            value=Decimal("10000.00"),
        )
        expected = f"{user.username} - 2024-01-31 - ANZ - Savings: $10000.00"
        assert str(snapshot) == expected

    def test_asset_snapshot_ordering(self, user):
        """AssetSnapshots should be ordered by date desc, type, name."""
        AssetSnapshot.objects.create(
            user=user,
            date=date(2024, 1, 31),
            asset_type="bank",
            asset_name="ANZ",
            value=Decimal("1000.00"),
        )
        AssetSnapshot.objects.create(
            user=user,
            date=date(2024, 2, 29),
            asset_type="bank",
            asset_name="ANZ",
            value=Decimal("2000.00"),
        )
        AssetSnapshot.objects.create(
            user=user,
            date=date(2024, 2, 29),
            asset_type="etf",
            asset_name="VAS",
            value=Decimal("3000.00"),
        )

        snapshots = list(AssetSnapshot.objects.all())
        # Should be ordered by date desc first
        assert snapshots[0].date == date(2024, 2, 29)
        assert snapshots[1].date == date(2024, 2, 29)
        assert snapshots[2].date == date(2024, 1, 31)
        # Within same date, ordered by type then name
        assert snapshots[0].asset_type == "bank"
        assert snapshots[1].asset_type == "etf"


@pytest.mark.django_db
class TestNetWorthSnapshot:
    """Tests for NetWorthSnapshot model."""

    def test_networth_snapshot_creation(self, user):
        """NetWorthSnapshot should be created with date and notes."""
        snapshot = NetWorthSnapshot.objects.create(
            user=user, date=date(2024, 1, 31), notes="End of January"
        )
        assert snapshot.date == date(2024, 1, 31)
        assert snapshot.notes == "End of January"
        assert snapshot.user == user

    def test_networth_snapshot_str(self, user):
        """NetWorthSnapshot __str__ should return formatted string."""
        snapshot = NetWorthSnapshot.objects.create(
            user=user, date=date(2024, 1, 31)
        )
        assert str(snapshot) == f"{user.username} - 2024-01-31"

    def test_networth_snapshot_unique_together(self, user):
        """NetWorthSnapshot should enforce unique user+date constraint."""
        NetWorthSnapshot.objects.create(user=user, date=date(2024, 1, 31))

        with pytest.raises(IntegrityError):
            NetWorthSnapshot.objects.create(user=user, date=date(2024, 1, 31))

    def test_total_assets_calculation_empty(self, user):
        """NetWorthSnapshot should calculate zero for no assets."""
        snapshot = NetWorthSnapshot.objects.create(
            user=user, date=date(2024, 1, 31)
        )
        assert snapshot.total_assets == Decimal("0.00")

    def test_total_assets_calculation_with_assets(self, user):
        """NetWorthSnapshot should calculate total from asset snapshots."""
        snapshot = NetWorthSnapshot.objects.create(
            user=user, date=date(2024, 1, 31)
        )

        # Create asset snapshots
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
        AssetSnapshot.objects.create(
            user=user,
            date=date(2024, 1, 31),
            asset_type="etf",
            asset_name="VAS",
            value=Decimal("9500.00"),
        )

        assert snapshot.total_assets == Decimal("69500.00")

    def test_category_totals_calculation(self, user):
        """NetWorthSnapshot should calculate category totals correctly."""
        snapshot = NetWorthSnapshot.objects.create(
            user=user, date=date(2024, 1, 31)
        )

        # Create various asset snapshots
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
            asset_type="bank",
            asset_name="Westpac",
            value=Decimal("5000.00"),
        )
        AssetSnapshot.objects.create(
            user=user,
            date=date(2024, 1, 31),
            asset_type="super",
            asset_name="Super Fund",
            value=Decimal("50000.00"),
        )
        AssetSnapshot.objects.create(
            user=user,
            date=date(2024, 1, 31),
            asset_type="etf",
            asset_name="VAS",
            value=Decimal("9500.00"),
        )
        AssetSnapshot.objects.create(
            user=user,
            date=date(2024, 1, 31),
            asset_type="stock",
            asset_name="CBA",
            value=Decimal("6000.00"),
        )
        AssetSnapshot.objects.create(
            user=user,
            date=date(2024, 1, 31),
            asset_type="crypto",
            asset_name="Bitcoin",
            value=Decimal("50000.00"),
        )

        assert snapshot.bank_accounts == Decimal("15000.00")
        assert snapshot.superannuation == Decimal("50000.00")
        assert snapshot.etf_holdings == Decimal("9500.00")
        assert snapshot.stock_holdings == Decimal("6000.00")
        assert snapshot.crypto_holdings == Decimal("50000.00")
        assert snapshot.total_assets == Decimal("130500.00")

    def test_change_from_previous_first_snapshot(self, user):
        """First snapshot should have zero change."""
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

        assert snapshot.change_from_previous == Decimal("0.00")

    def test_change_from_previous_subsequent_snapshot(self, user):
        """Subsequent snapshot should calculate change correctly."""
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
        snapshot2 = NetWorthSnapshot.objects.create(
            user=user, date=date(2024, 2, 29)
        )
        AssetSnapshot.objects.create(
            user=user,
            date=date(2024, 2, 29),
            asset_type="bank",
            asset_name="ANZ",
            value=Decimal("12000.00"),
        )

        assert snapshot2.change_from_previous == Decimal("2000.00")

    def test_change_percentage_first_snapshot(self, user):
        """First snapshot should have zero percentage change."""
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

        assert snapshot.change_percentage == Decimal("0.00")

    def test_change_percentage_subsequent_snapshot(self, user):
        """Subsequent snapshot should calculate percentage change correctly."""
        # First snapshot
        NetWorthSnapshot.objects.create(user=user, date=date(2024, 1, 31))
        AssetSnapshot.objects.create(
            user=user,
            date=date(2024, 1, 31),
            asset_type="bank",
            asset_name="ANZ",
            value=Decimal("10000.00"),
        )

        # Second snapshot - 20% increase
        snapshot2 = NetWorthSnapshot.objects.create(
            user=user, date=date(2024, 2, 29)
        )
        AssetSnapshot.objects.create(
            user=user,
            date=date(2024, 2, 29),
            asset_type="bank",
            asset_name="ANZ",
            value=Decimal("12000.00"),
        )

        # (12000 - 10000) / 10000 * 100 = 20%
        assert snapshot2.change_percentage == Decimal("20.00")

    def test_change_percentage_negative(self, user):
        """Snapshot should handle negative percentage change."""
        # First snapshot
        NetWorthSnapshot.objects.create(user=user, date=date(2024, 1, 31))
        AssetSnapshot.objects.create(
            user=user,
            date=date(2024, 1, 31),
            asset_type="bank",
            asset_name="ANZ",
            value=Decimal("10000.00"),
        )

        # Second snapshot - 10% decrease
        snapshot2 = NetWorthSnapshot.objects.create(
            user=user, date=date(2024, 2, 29)
        )
        AssetSnapshot.objects.create(
            user=user,
            date=date(2024, 2, 29),
            asset_type="bank",
            asset_name="ANZ",
            value=Decimal("9000.00"),
        )

        # (9000 - 10000) / 10000 * 100 = -10%
        assert snapshot2.change_percentage == Decimal("-10.00")

    def test_asset_snapshots_property(self, user):
        """NetWorthSnapshot should return correct asset snapshots."""
        snapshot = NetWorthSnapshot.objects.create(
            user=user, date=date(2024, 1, 31)
        )

        # Create asset snapshots for this date
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

        # Create asset snapshot for different date (should not be included)
        AssetSnapshot.objects.create(
            user=user,
            date=date(2024, 2, 29),
            asset_type="bank",
            asset_name="ANZ",
            value=Decimal("12000.00"),
        )

        asset_snapshots = snapshot.asset_snapshots.all()
        assert len(asset_snapshots) == 2
        assert all(a.date == date(2024, 1, 31) for a in asset_snapshots)

    def test_user_isolation(self, user, another_user):
        """NetWorthSnapshot should isolate data between users."""
        # Create snapshot for user1
        snapshot1 = NetWorthSnapshot.objects.create(
            user=user, date=date(2024, 1, 31)
        )
        AssetSnapshot.objects.create(
            user=user,
            date=date(2024, 1, 31),
            asset_type="bank",
            asset_name="ANZ",
            value=Decimal("10000.00"),
        )

        # Create snapshot for user2
        snapshot2 = NetWorthSnapshot.objects.create(
            user=another_user, date=date(2024, 1, 31)
        )
        AssetSnapshot.objects.create(
            user=another_user,
            date=date(2024, 1, 31),
            asset_type="bank",
            asset_name="Westpac",
            value=Decimal("20000.00"),
        )

        # Each snapshot should only see their own assets
        assert snapshot1.total_assets == Decimal("10000.00")
        assert snapshot2.total_assets == Decimal("20000.00")
        assert len(snapshot1.asset_snapshots.all()) == 1
        assert len(snapshot2.asset_snapshots.all()) == 1
