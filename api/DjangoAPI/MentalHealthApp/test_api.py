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

    def test_non_existent_test_code(self):
        response = self.client.post('/api/tests/999/public/', {'test_code': 'G12345'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

from django.test import TestCase
from .models import User, Test
from rest_framework import status
from rest_framework.test import APIClient

class LoginTest(TestCase):

    def setUp(self):
        # Vytvorenie používateľa
        self.user = User.objects.create(email="test@example.com", name="Test User")
        self.user.set_password("securepassword123")  # Nastavenie hesla
        self.user.save()  # Uloženie používateľa do databázy
        self.client = APIClient()

    def test_login_success(self):
        # Otestovanie úspešného prihlásenia
        response = self.client.post('/api/login/', {'email': 'test@example.com', 'password': 'securepassword123'}, format='json')
        
        # Overenie správneho status kódu a prihlásenia
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('jwt', response.data) 

    def test_login_invalid_credentials(self):
        response = self.client.post('/api/login/', {'email': 'test@example.com', 'password': 'wrongpassword'}, format='json')
        
        # Overenie, že odpoveď obsahuje chybu
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # self.assertEqual(response.data['error'], 'Invalid credentials')  # Očakávaný chybový message

    def test_login_user_not_found(self):
        # Pokus o prihlásenie s neexistujúcim e-mailom
        response = self.client.post('/api/login/', {'email': 'nonexistent@example.com', 'password': 'anyPassword'}, format='json')
        
        # Overenie, že odpoveď obsahuje chybu
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # self.assertEqual(response.data['error'], 'User not found')  # Očakávaný chybový message


class RegistrationTest(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_registration_success(self):
        # Úspešná registrácia
        data = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "securepassword123"
        }
        response = self.client.post('/api/register/', data, format='json')
        
        # Overenie správneho status kódu a odpovede
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Overenie, že používateľ bol uložený v databáze
        user = User.objects.get(email="test@example.com")
        self.assertEqual(user.name, "Test User")
        self.assertTrue(user.check_password("securepassword123"))  # Heslo musí byť správne zašifrované

    def test_registration_missing_fields(self):
        # Chýbajúce polia
        data = {
            "name": "",
            "email": "test@example.com",
            "password": "securepassword123"
        }
        response = self.client.post('/api/register/', data, format='json')
        
        # Overenie chybového status kódu a správy
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
        self.assertEqual(response.data['name'][0], 'This field may not be blank.')

    def test_registration_duplicate_email(self):
        # Duplicitný email
        User.objects.create(email="test@example.com", name="Existing User", password="securepassword123")
        
        data = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "securepassword123"
        }
        response = self.client.post('/api/register/', data, format='json')
        
        # Overenie chybového status kódu a správy
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        self.assertEqual(str(response.data['email'][0]), 'user with this email already exists.')

class CreateTestTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.test_data = {
            "name": "Test názov",
        }
        self.user = User.objects.create(email="test@example.com", name="Test User")
        self.user.set_password("securepassword123")  # Nastavenie hesla
        self.user.save()

    def test_create_test_success(self):
        response = self.client.post('/api/login/', {'email': 'test@example.com', 'password': 'securepassword123'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('jwt', response.data)

        response = self.client.post('/api/tests/', self.test_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], self.test_data['name'])

    def test_create_test_duplicate_name(self):
        self.client.post('/api/login/', {'email': 'test@example.com', 'password': 'securepassword123'}, format='json')
        Test.objects.create(name="Test názov")
        response = self.client.post('/api/tests/', self.test_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_test_invalid_data(self):
        self.client.post('/api/login/', {'email': 'test@example.com', 'password': 'securepassword123'}, format='json')
        invalid_data = {"name": ""}
        response = self.client.post('/api/tests/', invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class TestCreationTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(email="test@example.com", name="Test User")
        self.user.set_password("securepassword123")  # Nastavenie hesla
        self.user.save()

        # Test data
        self.test_data = {"name": "Sample Test"}
        self.client.post('/api/login/', {'email': 'test@example.com', 'password': 'securepassword123'}, format='json')
    

    def test_create_test_successfully(self):
        self.questions_data = [
            {"text": "Is the sky blue?", "question_type": "text", "options": "", "category": "Nezaradená"}
        ]
        test_response = self.client.post('/api/tests/', self.test_data, format='json')
        self.assertEqual(test_response.status_code, status.HTTP_201_CREATED)
        test_id = test_response.data['id']  # Uložíme ID testu

        for question in self.questions_data:
            response = self.client.post(f'/api/tests/{test_id}/questions/', question, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.data['text'], question['text'])

        test_with_questions = self.client.get(f'http://localhost:8000/api/tests/{test_id}/', format='json')
        self.assertEqual(test_with_questions.status_code, status.HTTP_200_OK)
        self.assertEqual(len(test_with_questions.data['questions']), len(self.questions_data))

        
        