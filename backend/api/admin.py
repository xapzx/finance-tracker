"""Admin configuration for the Networth Tracker."""

from django.contrib import admin

from .models import (
    BankAccount,
    CryptoHolding,
    CryptoTransaction,
    ETFHolding,
    ETFTransaction,
    StockHolding,
    StockTransaction,
    SuperannuationAccount,
    SuperannuationSnapshot,
    UserPreferences,
)


@admin.register(UserPreferences)
class UserPreferencesAdmin(admin.ModelAdmin):
    list_display = ["user", "currency", "timezone", "created_at", "updated_at"]
    list_filter = ["currency", "timezone"]
    search_fields = ["user__username"]


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "bank_name",
        "account_type",
        "balance",
        "updated_at",
    ]
    list_filter = ["bank_name", "account_type"]
    search_fields = ["name", "bank_name"]


@admin.register(SuperannuationAccount)
class SuperannuationAccountAdmin(admin.ModelAdmin):
    list_display = ["fund_name", "account_name", "balance", "updated_at"]
    list_filter = ["fund_name"]
    search_fields = ["fund_name", "account_name", "member_number"]


@admin.register(SuperannuationSnapshot)
class SuperannuationSnapshotAdmin(admin.ModelAdmin):
    list_display = [
        "account",
        "date",
        "balance",
        "employer_contribution",
        "personal_contribution",
        "notes",
    ]
    list_filter = ["account"]
    search_fields = ["account__fund_name", "account__account_name"]


@admin.register(ETFHolding)
class ETFHoldingAdmin(admin.ModelAdmin):
    list_display = ["symbol", "name", "units", "current_price", "updated_at"]
    search_fields = ["symbol", "name"]


@admin.register(ETFTransaction)
class ETFTransactionAdmin(admin.ModelAdmin):
    list_display = ["etf", "transaction_type", "date", "total_amount"]
    list_filter = ["transaction_type", "date"]
    search_fields = ["etf__symbol"]


@admin.register(CryptoHolding)
class CryptoHoldingAdmin(admin.ModelAdmin):
    list_display = [
        "symbol",
        "name",
        "quantity",
        "current_price",
        "updated_at",
    ]
    search_fields = ["symbol", "name"]


@admin.register(CryptoTransaction)
class CryptoTransactionAdmin(admin.ModelAdmin):
    list_display = ["crypto", "transaction_type", "date", "total_amount"]
    list_filter = ["transaction_type", "date"]
    search_fields = ["crypto__symbol"]


@admin.register(StockHolding)
class StockHoldingAdmin(admin.ModelAdmin):
    list_display = ["symbol", "name", "units", "current_price", "updated_at"]
    search_fields = ["symbol", "name"]


@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = ["stock", "transaction_type", "date", "total_amount"]
    list_filter = ["transaction_type", "date"]
    search_fields = ["stock__symbol"]
