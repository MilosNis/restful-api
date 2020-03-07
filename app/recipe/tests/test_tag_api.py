from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status

from core.models import Tag
from rest_framework.test import APIClient
from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')


class PublicTagApi(TestCase):
    """Unauthenticate user for tag ap"""

    def setUp(self):
        self.client = APIClient()

    def test_unauthenticate_user_retrieve_tags(self):
        """Test that unauthenticate user can't get tags"""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagApi(TestCase):
    """Authenticated user tests for tag api"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@user.com',
            password='TestPass123',
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_tags_successful(self):
        """Test that tags are retrieved successfully"""
        Tag.objects.create(name='Tag1', user=self.user)
        Tag.objects.create(name='Tag2', user=self.user)
        res = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieved_only_tags_for_authenticated_user(self):
        """Test that the retrieved tags are only for authenticated user"""
        user2 = get_user_model().objects.\
            create_user(email='user2@test.com', password='Testpass321')
        tag = Tag.objects.create(name='Tag1', user=self.user)
        Tag.objects.create(name='Tag2', user=user2)
        res = self.client.get(TAGS_URL)

        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_new_tag_successful(self):
        """Test for successful creation of new tag"""
        payload = {'name': 'New Tag'}
        res = self.client.post(TAGS_URL, payload)
        tag_exists = Tag.objects.filter(
            name=payload['name'],
            user=self.user
        ).exists()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(tag_exists)

    def test_create_invalid_tag(self):
        """Test creation of Tag with invalid name parameter"""
        payload = {'name': ''}
        res = self.client.post(TAGS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
