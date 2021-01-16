from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models


def sample_user(email='test@gmail.com', password='test123'):
    """Create a sample user to test our enpoints."""
    return get_user_model().objects.create_user(email, password)


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test create a new user with an email is succesful."""
        email = 'clayton@gmail.com'
        password = 'test123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized."""
        email = 'clayton@GMAIL.COM'
        user = get_user_model().objects.create_user(
            email=email
        )
        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user with no email raises error."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')

    def test_create_new_superuser(self):
        """Test new super user is created."""
        user = get_user_model().objects.create_superuser(
            'test@gmail.com', 'test123'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """Test the tag string representation."""
        tag = models.Tag.objects.create(
            user=sample_user(),
            name='Vegan',
        )

        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """Test the recipient string representation."""
        ingredient = models.Ingredient.objects.create(
            name='salt',
            user=sample_user()
        )

        self.assertEqual(str(ingredient), ingredient.name)