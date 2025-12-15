"""Models for the Networth Tracker application."""

from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal


class UserPreferences(models.Model):
    """Model for storing user preferences."""

    CURRENCY_CHOICES = [
        ('AUD', 'Australian Dollar (AUD)'),
        ('USD', 'US Dollar (USD)'),
        ('EUR', 'Euro (EUR)'),
        ('GBP', 'British Pound (GBP)'),
        ('NZD', 'New Zealand Dollar (NZD)'),
        ('CAD', 'Canadian Dollar (CAD)'),
        ('JPY', 'Japanese Yen (JPY)'),
        ('SGD', 'Singapore Dollar (SGD)'),
        ('HKD', 'Hong Kong Dollar (HKD)'),
        ('CHF', 'Swiss Franc (CHF)'),
    ]

    TIMEZONE_CHOICES = [
        ('Australia/Sydney', 'Sydney (AEST/AEDT)'),
        ('Australia/Melbourne', 'Melbourne (AEST/AEDT)'),
        ('Australia/Brisbane', 'Brisbane (AEST)'),
        ('Australia/Perth', 'Perth (AWST)'),
        ('Australia/Adelaide', 'Adelaide (ACST/ACDT)'),
        ('Australia/Darwin', 'Darwin (ACST)'),
        ('Australia/Hobart', 'Hobart (AEST/AEDT)'),
        ('Pacific/Auckland', 'Auckland (NZST/NZDT)'),
        ('Asia/Singapore', 'Singapore (SGT)'),
        ('Asia/Hong_Kong', 'Hong Kong (HKT)'),
        ('Asia/Tokyo', 'Tokyo (JST)'),
        ('Europe/London', 'London (GMT/BST)'),
        ('Europe/Paris', 'Paris (CET/CEST)'),
        ('America/New_York', 'New York (EST/EDT)'),
        ('America/Los_Angeles', 'Los Angeles (PST/PDT)'),
        ('UTC', 'UTC'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='preferences'
    )
    # Profile fields
    date_of_birth = models.DateField(null=True, blank=True)
    address_line1 = models.CharField(max_length=255, blank=True)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postcode = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, default='Australia', blank=True)
    # Preferences
    currency = models.CharField(
        max_length=3, choices=CURRENCY_CHOICES, default='AUD'
    )
    timezone = models.CharField(
        max_length=50, choices=TIMEZONE_CHOICES, default='Australia/Sydney'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'User preferences'

    def __str__(self):
        return f"{self.user.username} preferences"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_preferences(sender, instance, created, **kwargs):
    """Create UserPreferences when a new user is created."""
    if created:
        UserPreferences.objects.create(user=instance)


class BankAccount(models.Model):
    """Model for tracking bank account balances."""

    ACCOUNT_TYPES = [
        ('savings', 'Savings'),
        ('transaction', 'Transaction'),
        ('term_deposit', 'Term Deposit'),
        ('offset', 'Offset'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='bank_accounts'
    )
    name = models.CharField(max_length=100)
    bank_name = models.CharField(max_length=100)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    balance = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0.00')
    )
    interest_rate = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-balance']

    def __str__(self):
        return f"{self.bank_name} - {self.name}"


class SuperannuationAccount(models.Model):
    """Model for tracking superannuation account balances."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='superannuation_accounts'
    )
    fund_name = models.CharField(max_length=100)
    account_name = models.CharField(max_length=100, blank=True)
    member_number = models.CharField(max_length=50, blank=True)
    balance = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0.00')
    )
    employer_contribution = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0.00')
    )
    personal_contribution = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0.00')
    )
    investment_option = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-balance']

    def __str__(self):
        return f"{self.fund_name} - {self.account_name or self.member_number}"


class SuperannuationSnapshot(models.Model):
    """Monthly snapshot of superannuation balance for tracking gain/loss."""

    account = models.ForeignKey(
        SuperannuationAccount, on_delete=models.CASCADE,
        related_name='snapshots'
    )
    date = models.DateField()
    balance = models.DecimalField(max_digits=15, decimal_places=2)
    employer_contribution = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0.00'),
        help_text="Employer contributions this month"
    )
    personal_contribution = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('0.00'),
        help_text="Personal contributions this month"
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        unique_together = ['account', 'date']

    def __str__(self):
        return f"{self.account} - {self.date}"

    @property
    def total_contributions(self):
        """Total contributions for this period."""
        return self.employer_contribution + self.personal_contribution

    @property
    def investment_gain(self):
        """
        Calculate investment gain/loss.
        This is the change in balance minus contributions.
        Requires comparing to previous snapshot.
        """
        previous = SuperannuationSnapshot.objects.filter(
            account=self.account,
            date__lt=self.date
        ).first()

        if previous:
            balance_change = self.balance - previous.balance
            return balance_change - self.total_contributions
        return Decimal('0.00')


class ETFHolding(models.Model):
    """Model for tracking ETF holdings."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='etf_holdings'
    )
    symbol = models.CharField(max_length=20)
    name = models.CharField(max_length=200)
    units = models.DecimalField(max_digits=15, decimal_places=6)
    average_price = models.DecimalField(max_digits=15, decimal_places=4)
    current_price = models.DecimalField(
        max_digits=15, decimal_places=4, default=Decimal('0.00')
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['symbol']

    @property
    def market_value(self):
        return self.units * self.current_price

    @property
    def cost_basis(self):
        return self.units * self.average_price

    @property
    def unrealised_gain(self):
        return self.market_value - self.cost_basis

    def __str__(self):
        return f"{self.symbol} - {self.units} units"


class ETFTransaction(models.Model):
    """Model for tracking ETF transactions."""

    TRANSACTION_TYPES = [
        ('buy', 'Buy'),
        ('sell', 'Sell'),
        ('dividend', 'Dividend'),
        ('distribution', 'Distribution'),
        ('drp', 'Dividend Reinvestment'),
    ]

    etf = models.ForeignKey(
        ETFHolding, on_delete=models.CASCADE, related_name='transactions'
    )
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    date = models.DateField()
    units = models.DecimalField(
        max_digits=15, decimal_places=6, null=True, blank=True
    )
    price_per_unit = models.DecimalField(
        max_digits=15, decimal_places=4, null=True, blank=True
    )
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    brokerage = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('0.00')
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.etf.symbol} - {self.transaction_type} - {self.date}"


class CryptoHolding(models.Model):
    """Model for tracking cryptocurrency holdings."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='crypto_holdings'
    )
    symbol = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    quantity = models.DecimalField(max_digits=20, decimal_places=10)
    average_price = models.DecimalField(max_digits=15, decimal_places=4)
    current_price = models.DecimalField(
        max_digits=15, decimal_places=4, default=Decimal('0.00')
    )
    wallet_address = models.CharField(max_length=200, blank=True)
    exchange = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['symbol']

    @property
    def market_value(self):
        return self.quantity * self.current_price

    @property
    def cost_basis(self):
        return self.quantity * self.average_price

    @property
    def unrealised_gain(self):
        return self.market_value - self.cost_basis

    def __str__(self):
        return f"{self.symbol} - {self.quantity}"


class CryptoTransaction(models.Model):
    """Model for tracking cryptocurrency transactions."""

    TRANSACTION_TYPES = [
        ('buy', 'Buy'),
        ('sell', 'Sell'),
        ('transfer_in', 'Transfer In'),
        ('transfer_out', 'Transfer Out'),
        ('staking_reward', 'Staking Reward'),
        ('airdrop', 'Airdrop'),
    ]

    crypto = models.ForeignKey(
        CryptoHolding, on_delete=models.CASCADE, related_name='transactions'
    )
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    date = models.DateField()
    quantity = models.DecimalField(max_digits=20, decimal_places=10)
    price_per_unit = models.DecimalField(
        max_digits=15, decimal_places=4, null=True, blank=True
    )
    total_amount = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True
    )
    fee = models.DecimalField(
        max_digits=10, decimal_places=4, default=Decimal('0.00')
    )
    exchange = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.crypto.symbol} - {self.transaction_type} - {self.date}"


class StockHolding(models.Model):
    """Model for tracking stock holdings."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='stock_holdings'
    )
    symbol = models.CharField(max_length=20)
    name = models.CharField(max_length=200)
    exchange = models.CharField(max_length=20, default='ASX')
    units = models.DecimalField(max_digits=15, decimal_places=6)
    average_price = models.DecimalField(max_digits=15, decimal_places=4)
    current_price = models.DecimalField(
        max_digits=15, decimal_places=4, default=Decimal('0.00')
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['symbol']

    @property
    def market_value(self):
        return self.units * self.current_price

    @property
    def cost_basis(self):
        return self.units * self.average_price

    @property
    def unrealised_gain(self):
        return self.market_value - self.cost_basis

    def __str__(self):
        return f"{self.symbol} - {self.units} units"


class StockTransaction(models.Model):
    """Model for tracking stock transactions."""

    TRANSACTION_TYPES = [
        ('buy', 'Buy'),
        ('sell', 'Sell'),
        ('dividend', 'Dividend'),
        ('drp', 'Dividend Reinvestment'),
    ]

    stock = models.ForeignKey(
        StockHolding, on_delete=models.CASCADE, related_name='transactions'
    )
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    date = models.DateField()
    units = models.DecimalField(
        max_digits=15, decimal_places=6, null=True, blank=True
    )
    price_per_unit = models.DecimalField(
        max_digits=15, decimal_places=4, null=True, blank=True
    )
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    brokerage = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('0.00')
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.stock.symbol} - {self.transaction_type} - {self.date}"
