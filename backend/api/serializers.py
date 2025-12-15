"""Serializers for the Networth Tracker API."""

from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import (
    UserPreferences,
    BankAccount,
    SuperannuationAccount,
    ETFHolding,
    ETFTransaction,
    CryptoHolding,
    CryptoTransaction,
    StockHolding,
    StockTransaction,
)


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id', 'username']


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile."""

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name']

    def validate_email(self, value):
        user = self.context['request'].user
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError(
                "A user with this email already exists."
            )
        return value


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change."""

    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(
        required=True, write_only=True, validators=[validate_password]
    )
    new_password2 = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError(
                {"new_password": "Password fields didn't match."}
            )
        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value


class UserPreferencesSerializer(serializers.ModelSerializer):
    """Serializer for UserPreferences model."""

    class Meta:
        model = UserPreferences
        fields = [
            'date_of_birth', 'address_line1', 'address_line2',
            'city', 'state', 'postcode', 'country',
            'currency', 'timezone'
        ]


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""

    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            'username', 'password', 'password2', 'email',
            'first_name', 'last_name'
        ]

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError(
                {"email": "A user with this email already exists."}
            )
        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class BankAccountSerializer(serializers.ModelSerializer):
    """Serializer for BankAccount model."""

    class Meta:
        model = BankAccount
        exclude = ['user']


class SuperannuationAccountSerializer(serializers.ModelSerializer):
    """Serializer for SuperannuationAccount model."""

    class Meta:
        model = SuperannuationAccount
        exclude = ['user']


class ETFTransactionSerializer(serializers.ModelSerializer):
    """Serializer for ETFTransaction model."""

    class Meta:
        model = ETFTransaction
        fields = '__all__'


class ETFHoldingSerializer(serializers.ModelSerializer):
    """Serializer for ETFHolding model."""

    transactions = ETFTransactionSerializer(many=True, read_only=True)
    market_value = serializers.DecimalField(
        max_digits=15, decimal_places=2, read_only=True
    )
    cost_basis = serializers.DecimalField(
        max_digits=15, decimal_places=2, read_only=True
    )
    unrealised_gain = serializers.DecimalField(
        max_digits=15, decimal_places=2, read_only=True
    )

    class Meta:
        model = ETFHolding
        exclude = ['user']


class ETFHoldingListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for ETFHolding list view."""

    market_value = serializers.DecimalField(
        max_digits=15, decimal_places=2, read_only=True
    )
    cost_basis = serializers.DecimalField(
        max_digits=15, decimal_places=2, read_only=True
    )
    unrealised_gain = serializers.DecimalField(
        max_digits=15, decimal_places=2, read_only=True
    )

    class Meta:
        model = ETFHolding
        fields = [
            'id', 'symbol', 'name', 'units', 'average_price',
            'current_price', 'market_value', 'cost_basis',
            'unrealised_gain', 'notes', 'created_at', 'updated_at'
        ]


class CryptoTransactionSerializer(serializers.ModelSerializer):
    """Serializer for CryptoTransaction model."""

    class Meta:
        model = CryptoTransaction
        fields = '__all__'


class CryptoHoldingSerializer(serializers.ModelSerializer):
    """Serializer for CryptoHolding model."""

    transactions = CryptoTransactionSerializer(many=True, read_only=True)
    market_value = serializers.DecimalField(
        max_digits=15, decimal_places=2, read_only=True
    )
    cost_basis = serializers.DecimalField(
        max_digits=15, decimal_places=2, read_only=True
    )
    unrealised_gain = serializers.DecimalField(
        max_digits=15, decimal_places=2, read_only=True
    )

    class Meta:
        model = CryptoHolding
        exclude = ['user']


class CryptoHoldingListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for CryptoHolding list view."""

    market_value = serializers.DecimalField(
        max_digits=15, decimal_places=2, read_only=True
    )
    cost_basis = serializers.DecimalField(
        max_digits=15, decimal_places=2, read_only=True
    )
    unrealised_gain = serializers.DecimalField(
        max_digits=15, decimal_places=2, read_only=True
    )

    class Meta:
        model = CryptoHolding
        fields = [
            'id', 'symbol', 'name', 'quantity', 'average_price',
            'current_price', 'market_value', 'cost_basis',
            'unrealised_gain', 'wallet_address', 'exchange',
            'notes', 'created_at', 'updated_at'
        ]


class StockTransactionSerializer(serializers.ModelSerializer):
    """Serializer for StockTransaction model."""

    class Meta:
        model = StockTransaction
        fields = '__all__'


class StockHoldingSerializer(serializers.ModelSerializer):
    """Serializer for StockHolding model."""

    transactions = StockTransactionSerializer(many=True, read_only=True)
    market_value = serializers.DecimalField(
        max_digits=15, decimal_places=2, read_only=True
    )
    cost_basis = serializers.DecimalField(
        max_digits=15, decimal_places=2, read_only=True
    )
    unrealised_gain = serializers.DecimalField(
        max_digits=15, decimal_places=2, read_only=True
    )

    class Meta:
        model = StockHolding
        exclude = ['user']


class StockHoldingListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for StockHolding list view."""

    market_value = serializers.DecimalField(
        max_digits=15, decimal_places=2, read_only=True
    )
    cost_basis = serializers.DecimalField(
        max_digits=15, decimal_places=2, read_only=True
    )
    unrealised_gain = serializers.DecimalField(
        max_digits=15, decimal_places=2, read_only=True
    )

    class Meta:
        model = StockHolding
        fields = [
            'id', 'symbol', 'name', 'exchange', 'units', 'average_price',
            'current_price', 'market_value', 'cost_basis',
            'unrealised_gain', 'notes', 'created_at', 'updated_at'
        ]
