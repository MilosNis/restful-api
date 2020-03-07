from rest_framework import status
from core.models import Recipe, Tag, Ingredient
from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.urls import reverse
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Compose recipe url for detail recipe data"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_recipe(user, **extra_fields):
    """Create sample recipe object"""
    defaults = {
        'title': 'Recipe 1',
        'price': 5.0,
        'time_minutes': 5
    }
    defaults.update(extra_fields)
    return Recipe.objects.create(user=user, **defaults)


def sample_tag(user, name='Tag1'):
    """Creates and returnes a sample tag"""
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='Ingredient1'):
    """Creates and returnes a sample ingredient"""
    return Ingredient.objects.create(user=user, name=name)


class PublicRecipeApiTests(TestCase):
    """API Tests for unauthenticated user"""

    def setUp(self):
        self.client = APIClient()

    def test_required_login_for_retrieving_recipes(self):
        """Test that login is required for getting recipes"""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Tests for recipe api for authenticated user"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@user.com',
            password='Password123'
        )
        self.client.force_authenticate(user=self.user)

    def test_retrieving_recipes_list_successful(self):
        """Test for getting recipes list"""
        sample_recipe(self.user)
        sample_recipe(self.user)
        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieved_only_recipes_for_authenticated_user(self):
        """Test that the retrieved recipes are
        only for this authenticated user"""
        user2 = get_user_model().objects. \
            create_user(email='user2@test.com', password='Testpass321')
        sample_recipe(self.user)
        sample_recipe(user=user2)
        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        res = self.client.get(RECIPES_URL)

        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_detail_recipe_successful(self):
        """Test for getting detail data for a recipe"""
        recipe = sample_recipe(self.user)
        recipe.tags.add(sample_tag(self.user))
        recipe.ingredients.add(sample_ingredient(self.user))

        serializer = RecipeDetailSerializer(recipe)

        url = detail_url(recipe.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe_base_data(self):
        """Test for creating recipe with just base data"""
        payload = {
            'title': 'Recipe 1',
            'price': 5.00,
            'time_minutes': 5
        }
        res = self.client.post(RECIPES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_creating_recipe_with_tags(self):
        """Test for creating recipe with tags assigned to it"""
        tag1 = sample_tag(user=self.user, name='tag one')
        tag2 = sample_tag(user=self.user, name='tag two')
        payload = {
            'title': 'Recipe 1',
            'price': 5.00,
            'time_minutes': 5,
            'tags': [tag1.id, tag2.id]
        }
        res = self.client.post(RECIPES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        tags = Tag.objects.all()

        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_creating_recipe_with_ingredients(self):
        """Test for creating recipe with ingredients assigned to it"""
        ingredient1 = sample_ingredient(user=self.user, name='ingredient one')
        ingredient2 = sample_ingredient(user=self.user, name='ingredient two')
        payload = {
            'title': 'Recipe 1',
            'price': 5.00,
            'time_minutes': 5,
            'ingredients': [ingredient1.id, ingredient2.id]
        }
        res = self.client.post(RECIPES_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = Ingredient.objects.all()

        self.assertEqual(recipe.ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_partial_update_recipe(self):
        """Test updating a recipe with patch"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name='Curry')

        payload = {'title': 'Chicken tikka', 'tags': [new_tag.id]}
        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_recipe(self):
        """Test updating a recipe with put"""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))

        payload = {
                'title': 'Spaghetti carbonara',
                'time_minutes': 25,
                'price': 5.00
            }
        url = detail_url(recipe.id)
        self.client.put(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])
        self.assertEqual(recipe.price, payload['price'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 0)
