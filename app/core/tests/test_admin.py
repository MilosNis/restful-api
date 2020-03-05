from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class TestAdminPages(TestCase):

    def setUp(self):
        """Creating superuser, regular user and client for testing"""
        self.superuser = get_user_model().objects.create_superuser(
            email='test@superuser.com',
            password='Password123'
        )
        self.client = Client()
        self.client.force_login(self.superuser)
        self.user = get_user_model().objects.create_user(
            email='test@reguser.com',
            password='Pass123',
            name='Full name of user'
        )

    def test_users_are_listed(self):
        """Testing getting user email and name in user page"""
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)
        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_users_update_successful(self):
        """Testing user edit page works"""
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)

    def test_users_adding_successful(self):
        """Test that the add user page works"""
        url = reverse('admin:core_user_add')
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
