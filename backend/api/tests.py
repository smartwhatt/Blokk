from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
from django.core.signing import Signer
# from django.contrib.auth.
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
        new_count = User.objects.count()
        self.assertNotEqual(0, new_count)

    def test_model_can_create_a_user_with_username(self):
        """Test the user model can create a user with a username."""
        self.assertEqual(self.user.username, self.user_name)

    def test_model_can_create_a_user_with_email(self):
        """Test the user model can create a user with an email."""
        self.assertEqual(self.user.email, self.email)

    def test_model_can_create_a_user_with_password_hash(self):
        """Test the user model can create a user with a password hash."""
        self.assertIsNotNone(self.user.password)
        self.assertNotEqual(self.user.password, self.password)


class AuthendicationTestCase(TestCase):
    """Test suite for the authentication views."""

    def setUp(self):
        """Define the test client and other test variables."""
        self.user_name = "testuser"
        self.email = "test@example.com"
        self.password = "testpass"
        self.user = User.objects.create_user(
            self.user_name, self.email, self.password)
        self.client = APIClient()

    def test_register_api_view(self):
        """Test that the registration API view creates a new user."""
        url = reverse('register')
        data = {
            'username': 'foobar',
            'email': 'foobar@example.com',
            'password': 'somepassword'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(User.objects.get(id=2).username, 'foobar')

    def test_login_api_view(self):
        """Test that the login API view login an existing user."""
        url = reverse('login')
        data = {
            'username': 'testuser',
            'password': 'testpass'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data['refresh'], '')
        self.assertNotEqual(response.data['access'], '')

        url = reverse('verify')
        data = {
            'access': response.data['access']
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')

    def test_refresh_api_view(self):
        """Test that the refresh API view refresh an existing user."""
        url = reverse('login')

        # Obtain a token
        data = {
            'username': 'testuser',
            'password': 'testpass'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        old_token = response.data['access']

        # Refresh the token
        url = reverse('refresh')
        data = {
            'refresh': response.data['refresh']
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(response.data['access'], '')
        self.assertNotEqual(response.data['access'], old_token)

    def test_logout_api_view(self):
        """Test that the logout API view logout an existing user."""
        url = reverse('login')

        # Obtain a token
        data = {
            'username': 'testuser',
            'password': 'testpass'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        old_token = response.data['refresh']

        # Refresh the token
        url = reverse('logout')
        data = {
            'refresh': response.data['refresh']
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)

        url = reverse('refresh')
        data = {
            'refresh': old_token
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_verify_api_view(self):
        """Test that the verify API view verify an existing user."""
        url = reverse('login')

        # Obtain a token
        data = {
            'username': 'testuser',
            'password': 'testpass'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        old_token = response.data['access']

        # Refresh the token
        url = reverse('verify')
        data = {
            'access': response.data['access']
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')


class CurrencyModelTestCase(TestCase):
    """Test suite for the currency model."""

    def setUp(self):
        """Define the test client and other test variables."""
        self.currency_name = "Bitcoin"
        self.currency_symbol = "BTC"

        username = "testuser"
        email = "test@example.com"
        password = "testpass"
        self.user = User.objects.create_user(
            username, email, password)

        self.currency = Currency(
            name=self.currency_name, symbol=self.currency_symbol, admin=self.user)

        self.signer = Signer()

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
        self.assertEqual(self.currency.admin, self.user)

    def test_model_can_create_a_currency_with_invite_code(self):
        """Test the currency model can create a currency with an invite code."""
        self.currency.save()
        self.assertEqual(self.currency.invite_code, self.signer.sign(
            f"{self.currency.id}-{self.currency.name}-{self.currency.symbol}"))
        self.assertTrue(self.currency.validate_invite)

    def test_model_can_create_a_currency_with_market_cap(self):
        """Test the currency model can create a currency with a market cap."""
        self.currency.save()
        # print(self.currency.market_cap)
        self.assertEqual(self.currency.market_cap, -1)
        self.assertTrue(self.currency.validate_cap())

    def test_model_can_create_wallet_for_admin(self):
        """Test the currency model can create a wallet for the admin."""
        self.currency.save()
        adminWallet = Wallet.objects.filter(
            user=self.user, currency=self.currency).first()
        self.assertEqual(adminWallet.currency, self.currency)
        self.assertEqual(adminWallet.balance, 0)


class CurrencyAPITestCase(TestCase):
    """Test suite for the currency API."""

    def setUp(self):
        """Define the test client and other test variables."""
        username = "testuser"
        email = "test@example.com"
        password = "testpass"
        self.user = User.objects.create_user(
            username, email, password)

        username2 = "testuser2"
        email2 = "test2@example.com"
        password2 = "testpass2"
        self.user2 = User.objects.create_user(
            username2, email2, password2)

        self.currency_name = "Bitcoin"
        self.currency_symbol = "BTC"
        self.currency = Currency(
            name=self.currency_name, symbol=self.currency_symbol, admin=self.user)
        self.currency.save()

        self.client = APIClient()

        self.auth_token = self.client.post(
            reverse('login'),
            {'username': 'testuser', 'password': 'testpass'},
            format='json'
        )

        self.auth_token2 = self.client.post(
            reverse('login'),
            {'username': 'testuser2', 'password': 'testpass2'},
            format='json'
        )

    def test_api_can_create_a_currency_with_market_cap(self):
        """Test the api has currency creation capability."""
        url = reverse('currency')
        data = {
            'name': "Ethereum",
            'symbol': "ETH",
            'market_cap': 100
        }
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.auth_token.data['access'])
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], "Ethereum")
        self.assertEqual(response.data['symbol'], "ETH")
        self.assertEqual(response.data['admin'], self.user.id)
        self.assertEqual(response.data['market_cap'], 100)
    
    def test_api_can_create_a_currency_with_initial_balance(self):
        """Test the api has currency creation capability."""
        url = reverse('currency')
        data = {
            'name': "Ethereum",
            'symbol': "ETH",
            'initial_balance': 100
        }
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.auth_token.data['access'])
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], "Ethereum")
        self.assertEqual(response.data['symbol'], "ETH")
        self.assertEqual(response.data['admin'], self.user.id)
        self.assertEqual(response.data['initial_balance'], 100)

    def test_api_try_create_a_currency_without_login(self):
        """Test the api has currency creation capability."""
        url = reverse('currency')
        data = {
            'name': "Ethereum",
            'symbol': "ETH"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_join_currency_api(self):
        """Test the api has currency creation capability."""
        url = reverse('currency_join')
        data = {
            'invite_code': self.currency.invite_code
        }
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.auth_token2.data['access'])
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['currency']['id'], self.currency.id)
        self.assertEqual(response.data['wallet']['user'], self.user2.id)

    def test_join_currency_api_without_login(self):
        """Test the api has currency creation capability."""
        url = reverse('currency_join')
        data = {
            'invite_code': self.currency.invite_code
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_join_currency_api_with_invalid_invite_code(self):
        """Test the api has currency creation capability."""
        url = reverse('currency_join')
        data = {
            'invite_code': "invalid_code"
        }
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.auth_token2.data['access'])
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_leave_currency_api(self):
        """Test the api has currency creation capability."""
        url = reverse('currency_join')
        data = {
            'invite_code': self.currency.invite_code
        }
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.auth_token.data['access'])
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = reverse('currency_leave')

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.auth_token.data['access'])
        data = {
            'wallet': response.data['wallet']['id']
        }
        response = self.client.post(url, data=data, format='json')

    def test_leave_currency_api_with_invalid_wallet(self):
        """Test the api has currency creation capability."""
        url = reverse('currency_join')
        data = {
            'invite_code': self.currency.invite_code
        }
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.auth_token.data['access'])
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = reverse('currency_leave')

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.auth_token.data['access'])
        data = {
            'wallet': 10
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_leave_currency_api_with_wrong_wallet(self):
        """Test the api has currency creation capability."""
        url = reverse('currency_join')
        data = {
            'invite_code': self.currency.invite_code
        }
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.auth_token.data['access'])
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = reverse('currency_leave')

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.auth_token.data['access'])
        wallet = Wallet(user=self.user2, currency=self.currency)
        wallet.save()
        data = {
            'wallet': wallet.id
        }

        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_leave_currency_api_with_balance_in_wallet(self):
        """Test the api has currency creation capability."""
        url = reverse('currency_join')
        data = {
            'invite_code': self.currency.invite_code
        }
        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.auth_token.data['access'])
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        url = reverse('currency_leave')

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + self.auth_token.data['access'])
        wallet = Wallet.objects.get(id=response.data['wallet']['id'])
        wallet.balance = 1
        wallet.save()
        data = {
            'wallet': response.data['wallet']['id']
        }
        response = self.client.post(url, data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
