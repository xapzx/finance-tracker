"""Pytest fixtures for API tests."""

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from decimal import Decimal

from api.models import (
    BankAccount,
    SuperannuationAccount,
    ETFHolding,
    CryptoHolding,
    StockHolding,
)


@pytest.fixture
def api_client():
    """Return an API client instance."""
    return APIClient()


@pytest.fixture
def user(db):
    """Create and return a test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )


@pytest.fixture
def another_user(db):
    """Create and return another test user for isolation tests."""
    return User.objects.create_user(
        username='anotheruser',
        email='another@example.com',
        password='anotherpass123'
    )


@pytest.fixture
def auth_client(api_client, user):
    """Return an authenticated API client."""
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def bank_account(user):
    """Create and return a test bank account."""
    return BankAccount.objects.create(
        user=user,
        name='Test Savings',
        bank_name='Test Bank',
        account_type='savings',
        balance=Decimal('10000.00')
    )


@pytest.fixture
def super_account(user):
    """Create and return a test superannuation account."""
    return SuperannuationAccount.objects.create(
        user=user,
        fund_name='Test Super Fund',
        account_name='My Super',
        member_number='12345678',
        balance=Decimal('50000.00'),
        employer_contribution=Decimal('500.00'),
        personal_contribution=Decimal('200.00')
    )


@pytest.fixture
def etf_holding(user):
    """Create and return a test ETF holding."""
    return ETFHolding.objects.create(
        user=user,
        symbol='VAS',
        name='Vanguard Australian Shares',
        units=Decimal('100.000000'),
        average_price=Decimal('90.0000'),
        current_price=Decimal('95.0000')
    )


@pytest.fixture
def crypto_holding(user):
    """Create and return a test crypto holding."""
    return CryptoHolding.objects.create(
        user=user,
        symbol='BTC',
        name='Bitcoin',
        coingecko_id='bitcoin',
        quantity=Decimal('0.5000000000'),
        average_price=Decimal('80000.0000'),
        current_price=Decimal('100000.0000')
    )


@pytest.fixture
def stock_holding(user):
    """Create and return a test stock holding."""
    return StockHolding.objects.create(
        user=user,
        symbol='CBA',
        name='Commonwealth Bank',
        units=Decimal('50.000000'),
        average_price=Decimal('100.0000'),
        current_price=Decimal('120.0000')
    )
