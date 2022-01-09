from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse
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

    