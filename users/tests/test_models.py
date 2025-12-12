# users/tests/test_models.py
from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class UserModelTest(TestCase):
    """Test cases for User model"""

    def test_create_user(self):
        """Test creating a normal user"""
        user = User.objects.create_user(
            email="test@example.com", password="testpass123"
        )
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        """Test creating a superuser"""
        admin_user = User.objects.create_superuser(
            email="admin@example.com", password="testpass123"
        )
        self.assertEqual(admin_user.email, "admin@example.com")
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)
