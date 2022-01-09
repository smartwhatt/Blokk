from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.core.signing import Signer
from .models import *

# Create your tests here.

class UserModelTestCase(TestCase):
    """This class defines the test suite for the user model."""

    def setUp(self):
        """Define the test client and other test variables."""
        self.user_name = "testuser"
        self.email = "test@example.com"
        self.password = "testpass"
        self.user = User.objects.create_user(
            self.user_name, self.email, self.password)
        
    def test_model_can_create_a_user(self):
        """Test the user model can create a user."""
        old_count = User.objects.count()
        self.user.save()
        new_count = User.objects.count()
        self.assertNotEqual(old_count, new_count)
    
    def test_model_can_create_a_user_with_username(self):
        """Test the user model can create a user with a username."""
        self.assertEqual(self.user.username, self.user_name)
    
    def test_model_can_create_a_user_with_email(self):
        """Test the user model can create a user with an email."""
        self.assertEqual(self.user.email, self.email)
    
    def test_model_can_create_a_user_with_password(self):
        """Test the user model can create a user with a password."""
        self.assertEqual(self.user.password, self.password)

class CurrencyTestCase(TestCase):
    """This class defines the test suite for the currency model."""

    def setUp(self):
        """Define the test client and other test variables."""
        self.currency_name = "Bitcoin"
        self.currency_symbol = "BTC"
        self.currency_admin = User.objects.create_user(
            "testuser", "test@example.com", "testpass")
        self.currency = Currency.objects.create(
            name=self.currency_name, symbol=self.currency_symbol, admin=self.currency_admin, market_cap=1e6)
        
    def test_model_can_create_a_currency(self):
        """Test the currency model can create a currency."""
        old_count = Currency.objects.count()
        self.currency.save()
        new_count = Currency.objects.count()
        self.assertNotEqual(old_count, new_count)
    
    def test_model_can_create_a_currency_with_name(self):
        """Test the currency model can create a currency with a name."""
        self.assertEqual(self.currency.name, self.currency_name)
    
    def test_model_can_create_a_currency_with_symbol(self):
        """Test the currency model can create a currency with a symbol."""
        self.assertEqual(self.currency.symbol, self.currency_symbol)

    def test_model_can_create_a_currency_with_admin(self):
        """Test the currency model can create a currency with an admin."""
        self.assertEqual(self.currency.admin, self.currency_admin)
    
    def test_model_can_create_a_currency_with_market_cap(self):
        """Test the currency model can create a currency with a market cap."""
        self.assertEqual(self.currency.market_cap, 1e6)
    
    def test_model_can_create_a_currency_with_invite_code(self):
        """Test the currency model can create a currency with an invite code."""
        self.assertEqual(self.currency.invite_code, Signer().sign(f"{self.currency.id}-{self.currency.name}-{self.currency.symbol}"))