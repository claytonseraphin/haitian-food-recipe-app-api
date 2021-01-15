from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient
from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')


class PublicIngredientsApiTest(TestCase):
    """Test Publicly available API."""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test Login is required to retrieve ingredient."""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTest(TestCase):
    """Test Privately available API."""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@gmail.com',
            password='123test',
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients_list_success(self):
        """Test retrieve ingredients list successfuly."""
        Ingredient.objects.create(name='onion', user=self.user)
        Ingredient.objects.create(name='sugar', user=self.user)
        res = self.client.get(INGREDIENTS_URL)

        ingredient = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredient, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_user(self):
        """Test Ingredients are returned to authenticated user only."""
        user2 = get_user_model().objects.create_user(
            email='user@gmail.com',
            password='pass123'
        )
        Ingredient.objects.create(user=user2, name='vinegar')
        ingredient = Ingredient.objects.create(user=self.user, name='butter')
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)
