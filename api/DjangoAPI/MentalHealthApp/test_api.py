from django.test import TestCase
from .models import User

class UserModelTest(TestCase):

    def test_create_user(self):
        # Vytvorenie používateľa
        user = User.objects.create(email="test@example.com", name="Test User")
        user.set_password("securepassword123")
        user.save()

        # Overenie, že používateľ bol správne vytvorený
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.name, "Test User")
        self.assertTrue(user.check_password("securepassword123"))  # Overenie šifrovania hesla
        
    def test_duplicate_email(self):
        # Pokus o vytvorenie používateľa s rovnakým emailom
        User.objects.create(email="test@example.com", name="Test User", password="password123")
        with self.assertRaises(Exception):
            User.objects.create(email="test@example.com", name="Another User", password="password456")
