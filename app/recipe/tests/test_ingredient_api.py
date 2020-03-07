from rest_framework import status
from core.models import Ingredient, Recipe
from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.urls import reverse
from recipe.serializers import IngredientSerializer


INGREDIENTS_URL = reverse('recipe:ingredient-list')


class PublicIngredientsApiTests(TestCase):
    """Tests for unauthenticated user"""

    def setUp(self):
        self.client = APIClient()

    def test_required_login_for_retrieving_ingredients(self):
        """Test that login is required for getting ingredients"""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """Tests for ingredients for authenticated user"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@user.com',
            password='Password123'
        )
        self.client.force_authenticate(user=self.user)

    def test_retrieving_ingredients_list_successful(self):
        """Test for getting ingredients list"""
        Ingredient.objects.create(name='Ingredient1', user=self.user)
        Ingredient.objects.create(name='Ingredient2', user=self.user)
        res = self.client.get(INGREDIENTS_URL)
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieved_only_ingredients_for_authenticated_user(self):
        """Test that the retrieved ingredients are
        only for this authenticated user"""
        user2 = get_user_model().objects. \
            create_user(email='user2@test.com', password='Testpass321')
        ingredient = Ingredient.objects.create(
            name='Ingredient1', user=self.user)
        Ingredient.objects.create(name='Ingredient2', user=user2)
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_create_new_ingredient_successful(self):
        """Test for successful creation of new Ingredient"""
        payload = {'name': 'New Ingredient'}
        res = self.client.post(INGREDIENTS_URL, payload)
        ingredient_exists = Ingredient.objects.filter(
            name=payload['name'],
            user=self.user
        ).exists()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(ingredient_exists)

    def test_create_invalid_ingredient(self):
        """Test creation of Ingredient with invalid name parameter"""
        payload = {'name': ''}
        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_ingredients_assigned_to_recipes(self):
        """Test filtering ingredients by those assigned to recipes"""
        ingredient1 = Ingredient.objects.create(
            user=self.user, name='Apples'
        )
        ingredient2 = Ingredient.objects.create(
            user=self.user, name='Turkey'
        )
        recipe = Recipe.objects.create(
            title='Apple crumble',
            time_minutes=5,
            price=10.00,
            user=self.user
        )
        recipe.ingredients.add(ingredient1)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)
