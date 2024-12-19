from django.test import TestCase
from .models import User,Test
from rest_framework import status


class LoginTest(TestCase):

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

class PublicTests(TestCase):
    def setUp(self):
        user = User.objects.create(name="testuser", password="testpassword")
        self.test = Test.objects.create(id= 1,name="Test for Public", created_by=user,  test_code="G12345")

    def test_valid_test_code(self):
        response = self.client.post('/api/tests/1/public/', {'test_code': 'G12345'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test for Public')

    def test_invalid_test_code(self):
        response = self.client.post('/api/tests/1/public/', {'test_code': 'INVALIDCODE'})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Invalid test code')

    def test_non_existent_test_code(self):
        response = self.client.post('/api/tests/999/public/', {'test_code': 'G12345'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
