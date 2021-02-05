from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

import tempfile
import os

from PIL import Image

RECIPE_URLS = reverse('recipe:recipe-list')


def image_upload_url(recipe_id):
    """Return URL for recipe image upload"""
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


def detail_url(recipe_id):
    """Return the url of a specific recipe based on its id."""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_recipe(user, **params):
    """create a dictionnary of a recipe object."""
    defaults = {
        'title': 'Pitimi ak Pwa Kongo',
        'time_minutes': 10,
        'price': 5.00,
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

    def test_create_basic_recipe(self):
        """Test create a basic recipe succesfully."""
        payload = {
            'title': 'Spageti ak Aransò',
            'time_minutes': 15,
            'price': 30.00,
            'description': 'Spageti kreyol.'
        }
        res = self.client.post(RECIPE_URLS, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """Test creating recipe with tags."""
        tag1 = sample_tag(user=self.user, name='chokola')
        tag2 = sample_tag(user=self.user, name='lèt bèf')

        payload = {
            'title': 'Chokola Peyi',
            'time_minutes': 30,
            'price': 50.00,
            'description': 'Chokola ki fèt ak chokola peyi.',
            'tags': [tag1.id, tag2.id]
        }
        res = self.client.post(RECIPE_URLS, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()

        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """Test creating recipe with ingredients."""
        ingredient1 = sample_ingredient(user=self.user, name='joumou')
        ingredient2 = sample_ingredient(user=self.user, name='seleri')
        payload = {
            'title': 'Soup Joumou',
            'time_minutes': 90,
            'price': 300.00,
            'description': 'Soup Joumou Tradisyonel Lakay.',
            'ingredients': [ingredient1.id, ingredient2.id]
        }
        res = self.client.post(RECIPE_URLS, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()

        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_partial_update_recipe(self):
        """Test updating a recipe partially with patch."""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name='Seleri')

        payload = {
            'title': 'Pitimi ak Kalalou',
            'tags': [new_tag.id],
        }
        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()

        self.assertEqual(recipe.title, payload['title'])
        tags = recipe.tags.all()
        self.assertEqual(len(tags), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_recipe(self):
        """Test fully update a recipe with put."""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))

        payload = {
            'title': 'Diri ak Pwa Kongo',
            'time_minutes': 55,
            'price': 25.00,
            'description': 'Mnaje Esklav, men wa gou paw.'
        }

        url = detail_url(recipe.id)
        self.client.put(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.time_minutes, payload['time_minutes'])
        self.assertEqual(recipe.price, payload['price'])
        self.assertEqual(recipe.description, payload['description'])


class RecipeImageUploadTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user('user', 'testpass')
        self.client.force_authenticate(self.user)
        self.recipe = sample_recipe(user=self.user)

    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_image_to_recipe(self):
        """Test uploading an image to recipe"""
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            ntf.seek(0)
            res = self.client.post(url, {'image': ntf}, format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_imgae_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.recipe.id)
        res = self.client.post(
            url, {'image': 'notimage'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
