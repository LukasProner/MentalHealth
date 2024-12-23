from django.test import TestCase
from .models import QuestionAnswer, Scale, User,Test
from rest_framework import status
from django.test import TestCase
from .models import User, Test
from rest_framework import status
from rest_framework.test import APIClient


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
        test_user = User.objects.get(email='test@example.com')  # Predpokladáme, že používateľ existuje
        Test.objects.create(name="Test názov", created_by=test_user)  # Uisti sa, že je nastavený `created_by`
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
    
    def test_delete_question_successfully(self):
        self.questions_data = [
            {"text": "Is the sky blue?", "question_type": "text", "options": "", "category": "Nezaradená"}
        ]
        test_response = self.client.post('/api/tests/', self.test_data, format='json')
        self.assertEqual(test_response.status_code, status.HTTP_201_CREATED)
        test_id = test_response.data['id']  # Uložíme ID testu

        for question in self.questions_data:
            response = self.client.post(f'/api/tests/{test_id}/questions/', question, format='json')

        # Vymazať otázku
        delete_response = self.client.delete(f'/api/questions/{response.data['id']}/', format='json')
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

        # Overiť, že otázka už neexistuje
        question_response_after_delete = self.client.get(f'/api/questions/{response.data['id']}/', format='json')
        self.assertEqual(question_response_after_delete.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_test_successfully_with_more_options_of_answeqr(self):
        self.questions_data = [
            {"text": "Is the sky blue?", "question_type": "text", "options": "", "category": "Nezaradená"},
            {"text": "Question text?", "question_type": "text", "options": "", "category": "1"},
            {
                "text": "another question",
                "question_type": "choice",
                "options": [
                    {
                        "text": "kokso",
                        "value": None,
                        "hasValue": False
                    },
                    {
                        "text": "super",
                        "value": None,
                        "hasValue": False
                    },
                    {
                        "text": "pecka",
                        "value": None,
                        "hasValue": False
                    }
                ],
                "category": "1"
            },
            {"text": "Is the sky green?", "question_type": "boolean", "options": "", "category": "Nezaradená"},

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

    
class TestScaleCreationTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Vytvorenie používateľa a prihlásenie
        self.user = User.objects.create(email="test@example.com", name="Test User")
        self.user.set_password("securepassword123")
        self.user.save()
        self.client.post('/api/login/', {'email': 'test@example.com', 'password': 'securepassword123'}, format='json')

        # Vytvorenie testu
        self.test_data = {"name": "Sample Test"}
        test_response = self.client.post('/api/tests/', self.test_data, format='json')
        self.assertEqual(test_response.status_code, status.HTTP_201_CREATED)
        self.test_id = test_response.data['id']

    def test_save_scales_successfully(self):
        self.scales_data = [
            {"min_points": 0, "max_points": 10, "response": "Low", "category": "1"},
            {"min_points": 11, "max_points": 20, "response": "Medium", "category": "1"},
            {"min_points": 21, "max_points": 30, "response": "High", "category": "1"},
        ]
        # Uloženie škál pre test
        response = self.client.post(
            f'/api/tests/{self.test_id}/scales/',
            self.scales_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Overenie, že škály boli uložené
        test_scales = Scale.objects.filter(test_id=self.test_id)
        self.assertEqual(len(test_scales), len(self.scales_data))

        for scale, original_data in zip(test_scales, self.scales_data):
            self.assertEqual(scale.min_points, original_data["min_points"])
            self.assertEqual(scale.max_points, original_data["max_points"])
            self.assertEqual(scale.response, original_data["response"])
            self.assertEqual(scale.category, original_data["category"])

    
class SubmitAnswersTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Vytvorenie používateľa a prihlásenie
        self.user = User.objects.create(email="test@example.com", name="Test User")
        self.user.set_password("securepassword123")
        self.user.save()
        self.client.post('/api/login/', {'email': 'test@example.com', 'password': 'securepassword123'}, format='json')

        # Vytvorenie testu a otázok
        self.test_data = {"name": "Sample Test"}
        test_response = self.client.post('/api/tests/', self.test_data, format='json')
        self.assertEqual(test_response.status_code, status.HTTP_201_CREATED)
        self.test_id = test_response.data['id']
        test_detailed = self.client.get(f'http://localhost:8000/api/tests/{self.test_id}/')
        self.assertEqual(test_detailed.status_code, status.HTTP_200_OK)  # Over, že request bol úspešný
        self.test_code = test_detailed.data.get('test_code')

        # Pridanie otázok k testu
        self.questions_data = [
            {"text": "Is the sky blue?", "question_type": "text", "options": "", "category": "1"},
            {"text": "What is 2 + 2?", "question_type": "text", "options": "", "category": "1"},
        ]
        for question in self.questions_data:
            self.client.post(f'/api/tests/{self.test_id}/questions/', question, format='json')

        # Dáta pre odpovede
        self.answers_data = {
            str(1): "Yes",   # Odpoveď na prvú otázku
            str(2): "4",     # Odpoveď na druhú otázku
        }


    def test_submit_answers_successfully(self):
        print("Test ID:", self.test_id)
        print("Test Code:", self.test_code)
        # Simulácia odoslania odpovedí
        response = self.client.post(
            f'/api/tests/{self.test_id}/submit/',
            {
                'test_code': self.test_code,
                'answers': [
                    {'question_id': 1, 'answer': "Yes"},
                    {'question_id': 2, 'answer': "4"},
                ],
            },
            format='json'
        )
        print("Test Response Data:", response.data)

        # Overiť, že odpovede boli úspešne odoslané
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Overiť, že odpovede boli uložené v databáze
        for question_id, answer in self.answers_data.items():
            answer_obj = QuestionAnswer.objects.filter( question_id=question_id).first()
            self.assertIsNotNone(answer_obj)
            self.assertEqual(answer_obj.answer, answer)

    def test_submit_answers_with_invalid_test_code(self):
        # Simulácia odoslania odpovedí s neplatným testovým kódom
        response = self.client.post(
            f'/api/tests/{self.test_id}/submit/',
            {
                'test_code': "INVALIDCODE",
                'answers': [
                    {'question_id': 1, 'answer': "Yes"},
                    {'question_id': 2, 'answer': "4"},
                ],
            },
            format='json'
        )

        # Overiť, že odpovede neboli odoslané kvôli neplatnému testovému kódu
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        #self.assertIn('detail', response.data)

    # def test_submit_answers_with_missing_answers(self):
    #     # Simulácia odoslania odpovedí s chýbajúcimi odpoveďami
    #     response = self.client.post(
    #         f'/api/tests/{self.test_id}/submit/',
    #         {
    #             'test_code': self.test_code,
    #             'answers': [],
    #         },
    #         format='json'
    #     )

    #     # Overiť, že odpovede neboli odoslané kvôli chýbajúcim odpovediam
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertIn('detail', response.data)
        
class TestEvaluationOfAnswears(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create(email="test@example.com", name="Test User")
        self.user.set_password("securepassword123")
        self.user.save()
        self.client.post('/api/login/', {'email': 'test@example.com', 'password': 'securepassword123'}, format='json')

        self.test_data = {"name": "Sample Test"}
        test_response = self.client.post('/api/tests/', self.test_data, format='json')
        self.assertEqual(test_response.status_code, status.HTTP_201_CREATED)
        self.test_id = test_response.data['id']

        test_detailed = self.client.get(f'http://localhost:8000/api/tests/{self.test_id}/')
        self.assertEqual(test_detailed.status_code, status.HTTP_200_OK)  # Over, že request bol úspešný
        self.test_code = test_detailed.data.get('test_code')

               

    def test_evaluate_test_successfully(self):
        self.questions_data = [
            {
                "text": "another question",
                "question_type": "choice",
                "options": [
                    {
                        "text": "kokso",
                        "value": None,
                        "hasValue": False
                    },
                    {
                        "text": "super",
                        "value": 5,
                        "hasValue": True
                    },
                    {
                        "text": "pecka",
                        "value": None,
                        "hasValue": False
                    }
                ],
                "category": "1"
            },
        ]
        self.question_ids = []
        for question in self.questions_data:
            response = self.client.post(f'/api/tests/{self.test_id}/questions/', question, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.data['text'], question['text'])
            self.question_ids.append(response.data['id'])
        
        answers = [
            {'question_id': self.question_ids[0], 'answer': {'text': 'super', 'value': 5, 'hasValue': True}},
        ]
        self.scales_data = [
            {"min_points": 0, "max_points": 10, "response": "Low", "category": "1"},
            {"min_points": 11, "max_points": 20, "response": "Medium", "category": "1"},
            {"min_points": 21, "max_points": 30, "response": "High", "category": "1"},
        ]
        response = self.client.post(
            f'/api/tests/{self.test_id}/scales/',
            self.scales_data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(
            f'/api/tests/{self.test_id}/submit/',
            {
                'test_code': self.test_code,
                'answers': answers
            },
            format='json'
        )
        print("Test Response Data:", response.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        response = self.client.post(
            f'/api/tests/{self.test_id}/evaluate/',
            {
                "test_code": self.test_code,  # Testovací kód
                "answers": answers,
            },
            format='json'
        )
        print('respone in evaluation', response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Overenie výstupu
        evaluation_data = response.data
        self.assertIn("total_score", evaluation_data)
        self.assertEqual(evaluation_data["total_score"], [{'category': '1', 'total_points': 5, 'response': 'Low'}]) 


    def test_evaluate_divv_categories(self):
        self.questions_data = [
            {
                "text": "another question",
                "question_type": "choice",
                "options": [
                    {
                        "text": "kokso",
                        "value": None,
                        "hasValue": False
                    },
                    {
                        "text": "super",
                        "value": 5,
                        "hasValue": True
                    },
                    {
                        "text": "pecka",
                        "value": None,
                        "hasValue": False
                    }
                ],
                "category": "1"
            },
            {
                "text": "another question",
                "question_type": "choice",
                "options": [
                    {
                        "text": "kokso",
                        "value": None,
                        "hasValue": False
                    },
                    {
                        "text": "super",
                        "value": 6,
                        "hasValue": True
                    },
                    {
                        "text": "pecka",
                        "value": None,
                        "hasValue": False
                    }
                ],
                "category": "1"
            },
            {
                "text": "another question",
                "question_type": "choice",
                "options": [
                    {
                        "text": "kokso",
                        "value": None,
                        "hasValue": False
                    },
                    {
                        "text": "super",
                        "value": 5,
                        "hasValue": True
                    },
                    {
                        "text": "pecka",
                        "value": 2,
                        "hasValue": True
                    }
                ],
                "category": "2"
            },
            {"text": "Is the sky blue?", "question_type": "text", "options": "", "category": "1"},
            {"text": "What is 2 + 2?", "question_type": "text", "options": "", "category": "1"},
        ]
        self.question_ids = []
        for question in self.questions_data:
            response = self.client.post(f'/api/tests/{self.test_id}/questions/', question, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.data['text'], question['text'])
            self.question_ids.append(response.data['id'])
        
        answers = [
            {'question_id': self.question_ids[0], 'answer': {'text': 'super', 'value': 5, 'hasValue': True}},
            {'question_id': self.question_ids[1], 'answer': {'text': 'super', 'value': 6, 'hasValue': True}},
            {'question_id': self.question_ids[2], 'answer': {'text': 'super', 'value': 5, 'hasValue': True}},
            {'question_id': self.question_ids[3], 'answer': {'text': 'yes'}},
            {'question_id': self.question_ids[4], 'answer': {'text': '4'}},

        ]
        self.scales_data = [
            {"min_points": 0, "max_points": 10, "response": "Low", "category": "1"},
            {"min_points": 11, "max_points": 20, "response": "Medium", "category": "1"},
            {"min_points": 21, "max_points": 30, "response": "High", "category": "1"},
            {"min_points": 0, "max_points": 10, "response": "Low", "category": "2"},
            {"min_points": 11, "max_points": 20, "response": "Medium", "category": "2"},
            {"min_points": 21, "max_points": 30, "response": "High", "category": "2"},
        ]
        response = self.client.post(
            f'/api/tests/{self.test_id}/scales/',
            self.scales_data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(
            f'/api/tests/{self.test_id}/submit/',
            {
                'test_code': self.test_code,
                'answers': answers
            },
            format='json'
        )
        print("Test Response Data:", response.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        response = self.client.post(
            f'/api/tests/{self.test_id}/evaluate/',
            {
                "test_code": self.test_code,  # Testovací kód
                "answers": answers,
            },
            format='json'
        )
        print('respone in evaluation', response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Overenie výstupu
        evaluation_data = response.data
        self.assertIn("total_score", evaluation_data)
        self.assertEqual(evaluation_data["total_score"], [{'category': '1', 'total_points': 5, 'response': 'Low'}, {'category': '2', 'total_points': 5, 'response': 'Low'}]) 

    
    