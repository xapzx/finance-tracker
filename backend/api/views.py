"""Views for the Networth Tracker API."""

from rest_framework import viewsets, status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import (
    BankAccount,
    SuperannuationAccount,
    ETFHolding,
    ETFTransaction,
    CryptoHolding,
    CryptoTransaction,
    StockHolding,
    StockTransaction,
)
from .serializers import (
    BankAccountSerializer,
    SuperannuationAccountSerializer,
    SuperannuationSnapshotSerializer,
    ETFHoldingSerializer,
    ETFHoldingListSerializer,
    ETFTransactionSerializer,
    CryptoHoldingSerializer,
    CryptoHoldingListSerializer,
    CryptoTransactionSerializer,
    StockHoldingSerializer,
    StockHoldingListSerializer,
    StockTransactionSerializer,
    UserSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer,
    UserPreferencesSerializer,
    RegisterSerializer,
)
from .models import UserPreferences, SuperannuationSnapshot


class RegisterView(generics.CreateAPIView):
    """View for user registration."""

    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    """Get current authenticated user with preferences."""
    user = request.user
    # Ensure preferences exist
    preferences, _ = UserPreferences.objects.get_or_create(user=user)
    
    user_data = UserSerializer(user).data
    user_data['preferences'] = UserPreferencesSerializer(preferences).data
    return Response(user_data)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """Update user profile (name, email)."""
    serializer = UserUpdateSerializer(
        request.user, data=request.data,
        partial=True, context={'request': request}
    )
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request):
    """Change user password."""
    serializer = ChangePasswordSerializer(
        data=request.data, context={'request': request}
    )
    if serializer.is_valid():
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response({'message': 'Password changed successfully.'})
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def user_preferences(request):
    """Get or update user preferences."""
    preferences, _ = UserPreferences.objects.get_or_create(user=request.user)
    
    if request.method == 'GET':
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
        account_id = self.request.query_params.get('account', None)
        if account_id:
            queryset = queryset.filter(account_id=account_id)
        return queryset


class ETFHoldingViewSet(viewsets.ModelViewSet):
    """ViewSet for ETFHolding CRUD operations."""

    def get_queryset(self):
        return ETFHolding.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return ETFHoldingListSerializer
        return ETFHoldingSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ETFTransactionViewSet(viewsets.ModelViewSet):
    """ViewSet for ETFTransaction CRUD operations."""

    serializer_class = ETFTransactionSerializer

    def get_queryset(self):
        queryset = ETFTransaction.objects.filter(etf__user=self.request.user)
        etf_id = self.request.query_params.get('etf', None)
        if etf_id is not None:
            queryset = queryset.filter(etf_id=etf_id)
        return queryset


class CryptoHoldingViewSet(viewsets.ModelViewSet):
    """ViewSet for CryptoHolding CRUD operations."""

    def get_queryset(self):
        return CryptoHolding.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
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
        crypto_id = self.request.query_params.get('crypto', None)
        if crypto_id is not None:
            queryset = queryset.filter(crypto_id=crypto_id)
        return queryset


class StockHoldingViewSet(viewsets.ModelViewSet):
    """ViewSet for StockHolding CRUD operations."""

    def get_queryset(self):
        return StockHolding.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
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
        stock_id = self.request.query_params.get('stock', None)
        if stock_id is not None:
            queryset = queryset.filter(stock_id=stock_id)
        return queryset


@api_view(['GET'])
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
        t.total_amount for t in ETFTransaction.objects.filter(
            etf__user=user,
            transaction_type__in=['dividend', 'distribution']
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
        t.total_amount for t in StockTransaction.objects.filter(
            stock__user=user,
            transaction_type='dividend'
        )
    )

    total_networth = (
        bank_total + super_total + etf_total + crypto_total + stock_total
    )

    total_invested = etf_cost + crypto_cost + stock_cost
    total_unrealised_gain = (
        (etf_total - etf_cost) +
        (crypto_total - crypto_cost) +
        (stock_total - stock_cost)
    )

    return Response({
        'total_networth': str(total_networth),
        'breakdown': {
            'bank_accounts': {
                'total': str(bank_total),
                'count': BankAccount.objects.count(),
            },
            'superannuation': {
                'total': str(super_total),
                'count': SuperannuationAccount.objects.count(),
            },
            'etf': {
                'market_value': str(etf_total),
                'cost_basis': str(etf_cost),
                'unrealised_gain': str(etf_total - etf_cost),
                'dividends_received': str(etf_dividends),
                'count': etf_holdings.count(),
            },
            'crypto': {
                'market_value': str(crypto_total),
                'cost_basis': str(crypto_cost),
                'unrealised_gain': str(crypto_total - crypto_cost),
                'count': crypto_holdings.count(),
            },
            'stocks': {
                'market_value': str(stock_total),
                'cost_basis': str(stock_cost),
                'unrealised_gain': str(stock_total - stock_cost),
                'dividends_received': str(stock_dividends),
                'count': stock_holdings.count(),
            },
        },
        'investment_summary': {
            'total_invested': str(total_invested),
            'total_unrealised_gain': str(total_unrealised_gain),
            'total_dividends': str(etf_dividends + stock_dividends),
        },
        'currency': 'AUD',
    })
