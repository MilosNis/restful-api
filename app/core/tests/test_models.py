from django.test import TestCase
from django.contrib.auth import get_user_model


class TestModels(TestCase):

    def test_creating_user_with_email_successful(self):
        """Function for testing creating user with email and password"""
        email = 'test@user.com'
        password = 'TestPass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_user_email_normalized(self):
        """Test that email address is normalized when creating new user"""
        email = 'test@USER.COM'
        user = get_user_model().objects.create_user(
            email=email,
            password='Pass123'
        )
        self.assertEqual(user.email, email.lower())

    def test_user_invalid_email_field(self):
        """Testing raises error for non valid email field"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'Pass123')

    def test_creating_superuser(self):
        """Testing creation of superuser
        with is_staff and is_superuser set to True"""
        user = get_user_model().objects.create_superuser(
            email='test@user.com',
            password='Pass123'
        )
        self.assertTrue(user.is_superuser, True)
        self.assertTrue(user.is_staff, True)
