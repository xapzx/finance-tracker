"""URL configuration for the API."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from . import views

router = DefaultRouter()
router.register(r'bank-accounts', views.BankAccountViewSet, basename='bank-account')
router.register(r'superannuation', views.SuperannuationAccountViewSet, basename='superannuation')
router.register(r'super-snapshots', views.SuperannuationSnapshotViewSet, basename='super-snapshot')
router.register(r'etf-holdings', views.ETFHoldingViewSet, basename='etf-holding')
router.register(r'etf-transactions', views.ETFTransactionViewSet, basename='etf-transaction')
router.register(r'crypto-holdings', views.CryptoHoldingViewSet, basename='crypto-holding')
router.register(r'crypto-transactions', views.CryptoTransactionViewSet, basename='crypto-transaction')
router.register(r'stock-holdings', views.StockHoldingViewSet, basename='stock-holding')
router.register(r'stock-transactions', views.StockTransactionViewSet, basename='stock-transaction')

urlpatterns = [
    path('', include(router.urls)),
    path('summary/', views.networth_summary, name='networth-summary'),
    path('crypto/refresh-prices/', views.refresh_crypto_prices, name='refresh-crypto-prices'),
    path('etf/refresh-prices/', views.refresh_etf_prices, name='refresh-etf-prices'),
    path('stock/refresh-prices/', views.refresh_stock_prices, name='refresh-stock-prices'),
    path('crypto/get-price/', views.get_crypto_price, name='get-crypto-price'),
    path('etf/get-price/', views.get_etf_price, name='get-etf-price'),
    path('stock/get-price/', views.get_stock_price, name='get-stock-price'),
    # Auth endpoints
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/user/', views.current_user, name='current_user'),
    path('auth/profile/', views.update_profile, name='update_profile'),
    path('auth/password/', views.change_password, name='change_password'),
    path('auth/preferences/', views.user_preferences, name='user_preferences'),
]
