from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPE_URLS = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Return the url of a specific recipe based on its id."""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_recipe(user, **params):
    """create a dictionnary of a recipe object."""
    defaults = {
        'title': 'Pitimi ak Pwa Kongo',
        'time_minutes': '10',
        'price': '5',
        'description': 'Manje Ayisyen'
    }
    defaults.update(params)
    return Recipe.objects.create(user=user, **defaults)


def sample_tag(user, name='breakfast'):
    """Create a sample tag for a specific recipe."""
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='butter'):
    """Return a sample ingredient for a specific recipe."""
    return Ingredient.objects.create(user=user, name=name)


class PublicRecipeApiTests(TestCase):
    """Test Publicly available API."""

    def setUp(self):
        self.client = APIClient()

    def test_login_required_to_retrieve_recipe(self):
        """ Test user shoould log in to retrieve recipes."""
        res = self.client.get(RECIPE_URLS)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTest(TestCase):
    """Test Privately available API."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'clayton@gmail.com',
            'test123'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes_successfully(self):
        """Test Recipes can be retrieved when user is authenticated."""
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)
        res = self.client.get(RECIPE_URLS)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_authenticated_user(self):
        """Test Recipe can only be retireved to an authenticated user."""
        user2 = get_user_model().objects.create_user(
            'wrong@gmail.com',
            'wrong123'
        )
        sample_recipe(user=user2)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPE_URLS)
        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_detail(self):
        """Test a recipe detail can be viewed."""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(recipe.id)

        res = self.client.get(url)
        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.data, serializer.data)
