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
        
