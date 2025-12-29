"""Views for the Networth Tracker API."""

from decimal import Decimal

import requests
import yfinance as yf
from django.contrib.auth.models import User
from rest_framework import generics, status, viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

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
from .serializers import (
    BankAccountSerializer,
    ChangePasswordSerializer,
    CryptoHoldingListSerializer,
    CryptoHoldingSerializer,
    CryptoTransactionSerializer,
    ETFHoldingListSerializer,
    ETFHoldingSerializer,
    ETFTransactionSerializer,
    RegisterSerializer,
    StockHoldingListSerializer,
    StockHoldingSerializer,
    StockTransactionSerializer,
    SuperannuationAccountSerializer,
    SuperannuationSnapshotSerializer,
    UserPreferencesSerializer,
    UserSerializer,
    UserUpdateSerializer,
)


class RegisterView(generics.CreateAPIView):
    """View for user registration."""

    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def current_user(request):
    """Get current authenticated user with preferences."""
    user = request.user
    # Ensure preferences exist
    preferences, _ = UserPreferences.objects.get_or_create(user=user)

    user_data = UserSerializer(user).data
    user_data["preferences"] = UserPreferencesSerializer(preferences).data
    return Response(user_data)


@api_view(["PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """Update user profile (name, email)."""
    serializer = UserUpdateSerializer(
        request.user,
        data=request.data,
        partial=True,
        context={"request": request},
    )
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_password(request):
    """Change user password."""
    serializer = ChangePasswordSerializer(
        data=request.data, context={"request": request}
    )
    if serializer.is_valid():
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save()
        return Response({"message": "Password changed successfully."})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def user_preferences(request):
    """Get or update user preferences."""
    preferences, _ = UserPreferences.objects.get_or_create(user=request.user)

    if request.method == "GET":
        serializer = UserPreferencesSerializer(preferences)
        return Response(serializer.data)

    serializer = UserPreferencesSerializer(
        preferences, data=request.data, partial=True
    )
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BankAccountViewSet(viewsets.ModelViewSet):
    """ViewSet for BankAccount CRUD operations."""

    serializer_class = BankAccountSerializer

    def get_queryset(self):
        return BankAccount.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SuperannuationAccountViewSet(viewsets.ModelViewSet):
    """ViewSet for SuperannuationAccount CRUD operations."""

    serializer_class = SuperannuationAccountSerializer

    def get_queryset(self):
        return SuperannuationAccount.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SuperannuationSnapshotViewSet(viewsets.ModelViewSet):
    """ViewSet for SuperannuationSnapshot CRUD operations."""

    serializer_class = SuperannuationSnapshotSerializer

    def get_queryset(self):
        queryset = SuperannuationSnapshot.objects.filter(
            account__user=self.request.user
        )
        account_id = self.request.query_params.get("account", None)
        if account_id:
            queryset = queryset.filter(account_id=account_id)
        return queryset


class ETFHoldingViewSet(viewsets.ModelViewSet):
    """ViewSet for ETFHolding CRUD operations."""

    def get_queryset(self):
        return ETFHolding.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return ETFHoldingListSerializer
        return ETFHoldingSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ETFTransactionViewSet(viewsets.ModelViewSet):
    """ViewSet for ETFTransaction CRUD operations."""

    serializer_class = ETFTransactionSerializer

    def get_queryset(self):
        queryset = ETFTransaction.objects.filter(etf__user=self.request.user)
        etf_id = self.request.query_params.get("etf", None)
        if etf_id is not None:
            queryset = queryset.filter(etf_id=etf_id)
        return queryset


class CryptoHoldingViewSet(viewsets.ModelViewSet):
    """ViewSet for CryptoHolding CRUD operations."""

    def get_queryset(self):
        return CryptoHolding.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return CryptoHoldingListSerializer
        return CryptoHoldingSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CryptoTransactionViewSet(viewsets.ModelViewSet):
    """ViewSet for CryptoTransaction CRUD operations."""

    serializer_class = CryptoTransactionSerializer

    def get_queryset(self):
        queryset = CryptoTransaction.objects.filter(
            crypto__user=self.request.user
        )
        crypto_id = self.request.query_params.get("crypto", None)
        if crypto_id is not None:
            queryset = queryset.filter(crypto_id=crypto_id)
        return queryset


class StockHoldingViewSet(viewsets.ModelViewSet):
    """ViewSet for StockHolding CRUD operations."""

    def get_queryset(self):
        return StockHolding.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return StockHoldingListSerializer
        return StockHoldingSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class StockTransactionViewSet(viewsets.ModelViewSet):
    """ViewSet for StockTransaction CRUD operations."""

    serializer_class = StockTransactionSerializer

    def get_queryset(self):
        queryset = StockTransaction.objects.filter(
            stock__user=self.request.user
        )
        stock_id = self.request.query_params.get("stock", None)
        if stock_id is not None:
            queryset = queryset.filter(stock_id=stock_id)
        return queryset


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def networth_summary(request):
    """Get a summary of total networth across all asset types."""
    user = request.user

    # Bank accounts total
    bank_accounts = BankAccount.objects.filter(user=user)
    bank_total = sum(account.balance for account in bank_accounts)

    # Superannuation total
    super_accounts = SuperannuationAccount.objects.filter(user=user)
    super_total = sum(account.balance for account in super_accounts)

    # ETF total (market value)
    etf_holdings = ETFHolding.objects.filter(user=user)
    etf_total = sum(holding.market_value for holding in etf_holdings)
    etf_cost = sum(holding.cost_basis for holding in etf_holdings)

    # ETF dividends/distributions
    etf_dividends = sum(
        t.total_amount
        for t in ETFTransaction.objects.filter(
            etf__user=user, transaction_type__in=["dividend", "distribution"]
        )
    )

    # Crypto total (market value)
    crypto_holdings = CryptoHolding.objects.filter(user=user)
    crypto_total = sum(holding.market_value for holding in crypto_holdings)
    crypto_cost = sum(holding.cost_basis for holding in crypto_holdings)

    # Stock total (market value)
    stock_holdings = StockHolding.objects.filter(user=user)
    stock_total = sum(holding.market_value for holding in stock_holdings)
    stock_cost = sum(holding.cost_basis for holding in stock_holdings)

    # Stock dividends
    stock_dividends = sum(
        t.total_amount
        for t in StockTransaction.objects.filter(
            stock__user=user, transaction_type="dividend"
        )
    )

    total_networth = (
        bank_total + super_total + etf_total + crypto_total + stock_total
    )

    total_invested = etf_cost + crypto_cost + stock_cost
    total_unrealised_gain = (
        (etf_total - etf_cost)
        + (crypto_total - crypto_cost)
        + (stock_total - stock_cost)
    )

    return Response(
        {
            "total_networth": str(total_networth),
            "breakdown": {
                "bank_accounts": {
                    "total": str(bank_total),
                    "count": BankAccount.objects.count(),
                },
                "superannuation": {
                    "total": str(super_total),
                    "count": SuperannuationAccount.objects.count(),
                },
                "etf": {
                    "market_value": str(etf_total),
                    "cost_basis": str(etf_cost),
                    "unrealised_gain": str(etf_total - etf_cost),
                    "dividends_received": str(etf_dividends),
                    "count": etf_holdings.count(),
                },
                "crypto": {
                    "market_value": str(crypto_total),
                    "cost_basis": str(crypto_cost),
                    "unrealised_gain": str(crypto_total - crypto_cost),
                    "count": crypto_holdings.count(),
                },
                "stocks": {
                    "market_value": str(stock_total),
                    "cost_basis": str(stock_cost),
                    "unrealised_gain": str(stock_total - stock_cost),
                    "dividends_received": str(stock_dividends),
                    "count": stock_holdings.count(),
                },
            },
            "investment_summary": {
                "total_invested": str(total_invested),
                "total_unrealised_gain": str(total_unrealised_gain),
                "total_dividends": str(etf_dividends + stock_dividends),
            },
            "currency": "AUD",
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def refresh_crypto_prices(request):
    """Fetch current crypto prices from CoinGecko and update holdings."""
    user = request.user
    holdings = CryptoHolding.objects.filter(user=user)

    if not holdings.exists():
        return Response({"message": "No crypto holdings to update"})

    # Get unique coingecko_ids
    coingecko_ids = [h.coingecko_id for h in holdings if h.coingecko_id]

    if not coingecko_ids:
        return Response(
            {
                "error": "No CoinGecko IDs configured for your holdings. "
                "Edit each holding and add its CoinGecko ID."
            },
            status=400,
        )

    # Fetch prices from CoinGecko
    try:
        ids_param = ",".join(set(coingecko_ids))
        url = "https://api.coingecko.com/api/v3/simple/price"
        response = requests.get(
            url, params={"ids": ids_param, "vs_currencies": "aud"}, timeout=10
        )
        response.raise_for_status()
        prices = response.json()
    except requests.RequestException as e:
        return Response(
            {"error": f"Failed to fetch prices from CoinGecko: {str(e)}"},
            status=503,
        )

    # Update holdings with new prices
    updated = []
    for holding in holdings:
        if holding.coingecko_id and holding.coingecko_id in prices:
            price_data = prices[holding.coingecko_id]
            if "aud" in price_data:
                holding.current_price = Decimal(str(price_data["aud"]))
                holding.save()
                updated.append(
                    {
                        "symbol": holding.symbol,
                        "price": str(holding.current_price),
                    }
                )

    return Response(
        {
            "message": f"Updated {len(updated)} holdings",
            "updated": updated,
            "prices": prices,
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_crypto_price(request):
    """Fetch current price for a single crypto from CoinGecko."""
    coingecko_id = request.query_params.get("coingecko_id")

    if not coingecko_id:
        return Response(
            {"error": "coingecko_id parameter is required"}, status=400
        )

    # Fetch price from CoinGecko
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        response = requests.get(
            url,
            params={"ids": coingecko_id, "vs_currencies": "aud"},
            timeout=10,
        )
        response.raise_for_status()
        prices = response.json()

        if coingecko_id in prices and "aud" in prices[coingecko_id]:
            return Response(
                {
                    "coingecko_id": coingecko_id,
                    "price": prices[coingecko_id]["aud"],
                }
            )
        else:
            return Response(
                {"error": f"Price not found for {coingecko_id}"}, status=404
            )
    except requests.RequestException as e:
        return Response(
            {"error": f"Failed to fetch price from CoinGecko: {str(e)}"},
            status=503,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_etf_price(request):
    """Fetch current price for an ETF using yfinance."""
    ticker = request.query_params.get("ticker")
    exchange = request.query_params.get("exchange", "ASX")

    if not ticker:
        return Response({"error": "ticker parameter is required"}, status=400)

    try:
        # Format ticker based on exchange
        ticker_symbol = ticker.upper()
        if exchange.upper() == "ASX" and not ticker_symbol.endswith(".AX"):
            ticker_symbol = f"{ticker_symbol}.AX"
        # US ETFs (NYSE, NASDAQ) don't need suffix
        # Other exchanges use ticker as-is

        # Fetch data from yfinance
        etf = yf.Ticker(ticker_symbol)
        info = etf.info

        # Try to get current price from different fields
        price = (
            info.get("currentPrice")
            or info.get("regularMarketPrice")
            or info.get("previousClose")
        )

        if price:
            return Response(
                {
                    "ticker": ticker,
                    "price": float(price),
                    "currency": info.get("currency", "AUD"),
                }
            )
        else:
            return Response(
                {"error": f"Price not found for ticker {ticker_symbol}"},
                status=404,
            )
    except Exception as e:
        return Response(
            {"error": f"Failed to fetch price from yfinance: {str(e)}"},
            status=503,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_stock_price(request):
    """Fetch current price for a stock using yfinance."""
    ticker = request.query_params.get("ticker")
    exchange = request.query_params.get("exchange", "ASX")

    if not ticker:
        return Response({"error": "ticker parameter is required"}, status=400)

    try:
        # Format ticker based on exchange
        ticker_symbol = ticker.upper()
        if exchange.upper() == "ASX" and not ticker_symbol.endswith(".AX"):
            ticker_symbol = f"{ticker_symbol}.AX"
        # US stocks (NYSE, NASDAQ) don't need suffix
        # Other exchanges use ticker as-is

        # Fetch data from yfinance
        stock = yf.Ticker(ticker_symbol)
        info = stock.info

        # Try to get current price from different fields
        price = (
            info.get("currentPrice")
            or info.get("regularMarketPrice")
            or info.get("previousClose")
        )

        if price:
            return Response(
                {
                    "ticker": ticker,
                    "price": float(price),
                    "currency": info.get("currency", "AUD"),
                }
            )
        else:
            return Response(
                {"error": f"Price not found for ticker {ticker_symbol}"},
                status=404,
            )
    except Exception as e:
        return Response(
            {"error": f"Failed to fetch price from yfinance: {str(e)}"},
            status=503,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def refresh_etf_prices(request):
    """Fetch current ETF prices from yfinance and update holdings."""
    user = request.user
    holdings = ETFHolding.objects.filter(user=user)

    if not holdings.exists():
        return Response({"message": "No ETF holdings to update"})

    # Get unique symbols with their exchanges
    symbol_data = {}
    for h in holdings:
        if h.symbol:
            key = f"{h.symbol}:{h.exchange}"
            symbol_data[key] = {"symbol": h.symbol, "exchange": h.exchange}

    if not symbol_data:
        return Response(
            {"error": "No symbols configured for your ETF holdings."},
            status=400,
        )

    # Format tickers based on exchange
    ticker_symbols = []
    for data in symbol_data.values():
        ticker_symbol = data["symbol"].upper()
        if data["exchange"].upper() == "ASX" and not ticker_symbol.endswith(
            ".AX"
        ):
            ticker_symbol = f"{ticker_symbol}.AX"
        # US ETFs (NYSE, NASDAQ) don't need suffix
        # Other exchanges use ticker as-is
        ticker_symbols.append(ticker_symbol)

    # Fetch prices from yfinance
    try:
        tickers_str = " ".join(ticker_symbols)
        data = yf.download(tickers_str, period="1d", interval="1d")

        updated = []
        for holding in holdings:
            # Format ticker symbol based on exchange for matching
            ticker_symbol = holding.symbol.upper()
            if (
                holding.exchange.upper() == "ASX"
                and not ticker_symbol.endswith(".AX")
            ):
                ticker_symbol = f"{ticker_symbol}.AX"
            # US ETFs (NYSE, NASDAQ) don't need suffix
            # Other exchanges use ticker as-is

            if ticker_symbol in data.columns:
                # Get the most recent price (last row)
                price_series = data[ticker_symbol]["Close"].dropna()
                if not price_series.empty:
                    current_price = price_series.iloc[-1]
                    holding.current_price = Decimal(str(current_price))
                    holding.save()
                    updated.append(
                        {
                            "symbol": holding.symbol,
                            "exchange": holding.exchange,
                            "price": str(holding.current_price),
                        }
                    )

        return Response(
            {
                "message": f"Updated {len(updated)} ETF holdings",
                "updated": updated,
            }
        )
    except Exception as e:
        return Response(
            {"error": f"Failed to fetch prices from yfinance: {str(e)}"},
            status=503,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def refresh_stock_prices(request):
    """Fetch current stock prices from yfinance and update holdings."""
    user = request.user
    holdings = StockHolding.objects.filter(user=user)

    if not holdings.exists():
        return Response({"message": "No stock holdings to update"})

    # Get unique symbols with their exchanges
    symbol_data = {}
    for h in holdings:
        if h.symbol:
            key = f"{h.symbol}:{h.exchange}"
            symbol_data[key] = {"symbol": h.symbol, "exchange": h.exchange}

    if not symbol_data:
        return Response(
            {"error": "No symbols configured for your stock holdings."},
            status=400,
        )

        # Format tickers based on exchange
    ticker_symbols = []
    for data in symbol_data.values():
        ticker_symbol = data["symbol"].upper()
        if data["exchange"].upper() == "ASX" and not ticker_symbol.endswith(
            ".AX"
        ):
            ticker_symbol = f"{ticker_symbol}.AX"
        # US stocks (NYSE, NASDAQ) don't need suffix
        # Other exchanges use ticker as-is
        ticker_symbols.append(ticker_symbol)

    # Fetch prices from yfinance
    try:
        tickers_str = " ".join(ticker_symbols)
        data = yf.download(tickers_str, period="1d", interval="1d")

        updated = []
        for holding in holdings:
            # Format ticker symbol based on exchange for matching
            ticker_symbol = holding.symbol.upper()
            if (
                holding.exchange.upper() == "ASX"
                and not ticker_symbol.endswith(".AX")
            ):
                ticker_symbol = f"{ticker_symbol}.AX"
            # US stocks (NYSE, NASDAQ) don't need suffix
            # Other exchanges use ticker as-is

            if ticker_symbol in data.columns:
                # Get the most recent price (last row)
                price_series = data[ticker_symbol]["Close"].dropna()
                if not price_series.empty:
                    current_price = price_series.iloc[-1]
                    holding.current_price = Decimal(str(current_price))
                    holding.save()
                    updated.append(
                        {
                            "symbol": holding.symbol,
                            "exchange": holding.exchange,
                            "price": str(holding.current_price),
                        }
                    )

        return Response(
            {
                "message": f"Updated {len(updated)} stock holdings",
                "updated": updated,
            }
        )
    except Exception as e:
        return Response(
            {"error": f"Failed to fetch prices from yfinance: {str(e)}"},
            status=503,
        )
