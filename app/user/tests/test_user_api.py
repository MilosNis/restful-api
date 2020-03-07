from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

USER_CREATE_URL = reverse('user:create')
CREATE_TOKEN_URL = reverse('user:token')
MY_PROFILE_URL = reverse('user:me')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApi(TestCase):
    """Tests for public APIs of user"""

    def setUp(self):
        self.client = APIClient()

    def test_user_create_successful(self):
        """Testing successfully creating user works"""
        payload = {'email': 'test@user.com',
                   'password': 'Password12345', 'name': 'Test name'}
        res = self.client.post(USER_CREATE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_duplicate_user_creation(self):
        """Test that creation user with existing email is not allowed"""
        payload = {'email': 'test@user.com', 'password': 'test12345'}
        create_user(**payload)
        res = self.client.post(USER_CREATE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Test when password in payload is shorter then 5 characters"""
        payload = {'email': 'test@user.com', 'password': '12'}
        res = self.client.post(USER_CREATE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()

        self.assertFalse(user_exists)

    def test_create_token_successful(self):
        """Test for successful creation of token for user"""
        payload = {'email': 'test@user.com', 'password': 'Password123'}
        create_user(**payload)
        res = self.client.post(CREATE_TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)

    def test_create_token_no_user(self):
        """Test for trying to get token for non existing user"""
        payload = {'email': 'test@user', 'password': 'Password123'}
        res = self.client.post(CREATE_TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_create_token_invalid_credentials(self):
        """Trying to get token with invalid credentials """
        payload = {'email': 'test@user.com', 'password': 'Testpassword'}
        create_user(**payload)
        res = self.client.post(CREATE_TOKEN_URL,
                               {'email': 'test@user.com', 'password': 'wrong'})

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_create_token_no_password(self):
        """Trying to get token without password field"""
        payload = {'email': 'test@user.com', 'password': 'Testpassword'}
        create_user(**payload)
        res = self.client.post(CREATE_TOKEN_URL,
                               {'email': 'test@user.com', 'password': ''})

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_get_my_profile_unauthenticated(self):
        """Test requesting profile page unauthenticating"""
        res = self.client.get(MY_PROFILE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApi(TestCase):
    """Testing user api for which is necessary authentication"""

    def setUp(self):
        self.client = APIClient()
        payload = {
            'email': 'test@user.com',
            'password': 'Testpassword123',
            'name': 'name'
        }
        self.user = create_user(**payload)
        self.client.force_authenticate(user=self.user)

    def test_get_my_profile_authenticated(self):
        """Test for getting my profile page"""
        res = self.client.get(MY_PROFILE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'email': self.user.email,
            'name': self.user.name
        })

    def test_update_user_data(self):
        """Test for successful update user data"""
        payload = {'email': 'new_email@user.com', 'password': 'newpass123'}
        res = self.client.patch(MY_PROFILE_URL, payload)
        self.user.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.email, payload['email'])
        self.assertTrue(self.user.check_password(payload['password']))

    def test_post_user_data_not_allowed(self):
        """Posting data on My Profile URL not allowed method"""
        payload = {'email': 'email@me.com', 'password': 'mypassword'}
        res = self.client.post(MY_PROFILE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
