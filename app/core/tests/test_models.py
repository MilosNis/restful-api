from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email='test@user.com', password='TestPass123'):
    """Creating  a sample of user model"""
    return get_user_model().objects.create_user(email=email, password=password)


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

    def test_str_for_tag_model(self):
        """Testing correct string representation of Tag model"""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Test Tag'
        )
        self.assertEqual(str(tag), tag.name)

    def test_str_for_ingredient_model(self):
        """Testing for string representation
         of Ingredient model"""
        ingredient = models.Ingredient.objects.create(
            name='Cucumber',
            user=sample_user()
        )
        self.assertEqual(str(ingredient), ingredient.name)

    def test_str_for_recipe_model(self):
        """Testing for string representation
         of Recipe model"""
        recipe = models.Recipe.objects.create(
            title='Recipe 1',
            user=sample_user(),
            price=5.00,
            time_minutes=5
        )
        self.assertEqual(str(recipe), recipe.title)

    @patch('uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test that image is saved in the correct location"""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, 'myimage.jpg')

        exp_path = f'uploads/recipe/{uuid}.jpg'
        self.assertEqual(file_path, exp_path)
