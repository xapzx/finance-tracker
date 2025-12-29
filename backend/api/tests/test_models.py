"""Unit tests for API models."""

from decimal import Decimal

import pytest
from django.contrib.auth.models import User

from api.models import SuperannuationSnapshot, UserPreferences


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
