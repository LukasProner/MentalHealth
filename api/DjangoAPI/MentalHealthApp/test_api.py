from django.test import TestCase
from .models import QuestionAnswer, Scale, User,Test,User, Test
from rest_framework import status
from rest_framework.test import APIClient
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile
import uuid
import os
import jwt
import datetime
from MentalHealthApp.models import User, Test, Question,QuestionAnswer,TestSubmission,RecordedVideo
from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from MentalHealthApp.models import User, Test, Question, TestSubmission, QuestionAnswer


class CreateUserTest(TestCase):
    def test_create_user(self):
        user = User.objects.create(email="test@gmail.sk", name="Jano")
        user.set_password("superpassword123")
        user.save()

        self.assertEqual(user.email, "test@gmail.sk")
        self.assertEqual(user.name, "Jano")
        self.assertTrue(user.check_password("superpassword123")) 
        
    def test_duplicated_email(self):
        User.objects.create(email="test@gmail.sk", name="Jano", password="password123")
        with self.assertRaises(Exception):
            User.objects.create(email="test@gmail.sk", name="NeJano", password="password456")

class PublicTests(TestCase):
    def setUp(self):
        user = User.objects.create(name="testuser", password="testpassword")
        self.test = Test.objects.create(id= 1,name="public", created_by=user,  test_code="I12345")

    def test_valid_test_code(self):
        response = self.client.post('/api/tests/1/public/', {'test_code': 'I12345'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'public')

    def test_invalid_test_code(self):
        response = self.client.post('/api/tests/1/public/', {'test_code': '5555'})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_non_existent_test_code(self):
        response = self.client.post('/api/tests/999/public/', {'test_code': 'I12345'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class LoginTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(email="janko@janko.com", name="Test User")
        self.user.set_password("heslo123") 
        self.user.save()  
        self.client = APIClient()

    def test_login_success(self):
        response = self.client.post('/api/login/', {'email': 'janko@janko.com', 'password': 'heslo123'}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('jwt', response.data) 

    def test_login_invalid_credentials(self):
        response = self.client.post('/api/login/', {'email': 'janko@janko.com', 'password': 'zleheslo321'}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_login_user_not_found(self):
        response = self.client.post('/api/login/', {'email': 'miro@super.com', 'password': 'hocco'}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

class RegistrationTest(TestCase):

    def setUp(self):
        self.client = APIClient()

    def test_registration_succes(self):
        data = {
            "name": "Kiko",
            "email": "kiko@gmail.com",
            "password": "securepassword123"
        }
        response = self.client.post('/api/register/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        user = User.objects.get(email="kiko@gmail.com")
        self.assertEqual(user.name, "Kiko")
        self.assertTrue(user.check_password("securepassword123"))  # Heslo musí byť správne zašifrované

    def test_registr_missing_fields(self):
        data = {
            "name": "",
            "email": "kiko@gmail.com",
            "password": "securepassword123"
        }
        response = self.client.post('/api/register/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
        self.assertEqual(response.data['name'][0], 'This field may not be blank.')

    def test_registration_duplicated_email(self):
        User.objects.create(email="kiko@gmail.com", name="Existing User", password="password123")
        
        data = {
            "name": "Tojejedno",
            "email": "kiko@gmail.com",
            "password": "odlisne"
        }
        response = self.client.post('/api/register/', data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
        self.assertEqual(str(response.data['email'][0]), 'user with this email already exists.')

class CreateTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.test_data = {
            "name": "test",
        }
        self.user = User.objects.create(email="kiko@gmail.com", name="kiko")
        self.user.set_password("password123")  # Nastavenie hesla
        self.user.save()

    def test_create_test_succ(self):
        response = self.client.post('/api/login/', {'email': 'kiko@gmail.com', 'password': 'password123'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('jwt', response.data)

        response = self.client.post('/api/tests/', self.test_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], self.test_data['name'])

class QuestionsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(email="kiko@gmail.com", name="kiko")
        self.user.set_password("password123")  
        self.user.save()

        # Test data
        self.test_data = {"name": "Sample Test"}
        self.client.post('/api/login/', {'email': 'kiko@gmail.com', 'password': 'password123'}, format='json')
    

    def test_create_test_successfully(self):
        self.questions_data = [
            {"text": "Je to tak??", "question_type": "text", "options": "", "category": "Nezaradená"}
        ]
        test_response = self.client.post('/api/tests/', self.test_data, format='json')
        self.assertEqual(test_response.status_code, status.HTTP_201_CREATED)
        test_id = test_response.data['id']  

        for question in self.questions_data:
            response = self.client.post(f'/api/tests/{test_id}/questions/', question, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.data['text'], question['text'])

        test_with_questions = self.client.get(f'http://localhost:8000/api/tests/{test_id}/', format='json')
        self.assertEqual(test_with_questions.status_code, status.HTTP_200_OK)
        self.assertEqual(len(test_with_questions.data['questions']), len(self.questions_data))
    
    def test_delete_question_successfully(self):
        self.questions_data = [
            {"text": "Is it?", "question_type": "text", "options": "", "category": "Nezaradená"}
        ]
        test_response = self.client.post('/api/tests/', self.test_data, format='json')
        self.assertEqual(test_response.status_code, status.HTTP_201_CREATED)
        test_id = test_response.data['id']  

        for question in self.questions_data:
            response = self.client.post(f'/api/tests/{test_id}/questions/', question, format='json')

        delete_response = self.client.delete(f'/api/questions/{response.data['id']}/', format='json')
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

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

class UpdateQuestionTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(email="user1@gmail.com", password="rnd")
        self.test = Test.objects.create(name="Test A", created_by=self.user)
        self.question = Question.objects.create(
            test=self.test,
            text="Original Question",
            question_type="choice",
            category="Category 1",
            options="Option1,Option2,Option3"
        )

        self.update_data = {
            "text": "Updated Question",
            "question_type": "boolean",
            "category": "Updated Category",
            "options": []
        }

        payload = {
            'id': self.user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }
        self.token = jwt.encode(payload, 'secret', algorithm='HS256')
        self.client.cookies['jwt'] = self.token

    def test_update_question_successfully(self):
        url = f'/api/questions/{self.question.id}/' 
        response = self.client.put(url, data=self.update_data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["text"], self.update_data["text"])
        self.assertEqual(response.data["question_type"], self.update_data["question_type"])
        self.assertEqual(response.data["category"], self.update_data["category"])
        self.assertEqual(response.data["options"], self.update_data["options"])


    def test_update_question_not_found(self):
        url = f'/api/questions/9989/' 
        response = self.client.put(url, data=self.update_data, format='json')
        self.assertEqual(response.status_code, 404)
        self.assertIn("Question not found", str(response.data))

    
class TestScaleCreationTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create(email="Fidrich@gmail.com", name="Frido")
        self.user.set_password("pass123")
        self.user.save()
        self.client.post('/api/login/', {'email': 'Fidrich@gmail.com', 'password': 'pass123'}, format='json')

        self.test_data = {"name": "testik"}
        test_response = self.client.post('/api/tests/', self.test_data, format='json')
        self.assertEqual(test_response.status_code, status.HTTP_201_CREATED)
        self.test_id = test_response.data['id']

    def test_save_scales_successfully(self):
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

        test_scales = Scale.objects.filter(test_id=self.test_id)
        self.assertEqual(len(test_scales), len(self.scales_data))

        for scale, original_data in zip(test_scales, self.scales_data):
            self.assertEqual(scale.min_points, original_data["min_points"])
            self.assertEqual(scale.max_points, original_data["max_points"])
            self.assertEqual(scale.response, original_data["response"])
            self.assertEqual(scale.category, original_data["category"])

        responseGet = self.client.get(f'/api/tests/{self.test_id}/scales/', format='json')
        self.assertEqual(responseGet.status_code, status.HTTP_200_OK)

    
class TestEvaluationOfAnswears(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create(email="g@g.com", name="g")
        self.user.set_password("h")
        self.user.save()
        self.client.post('/api/login/', {'email': 'g@g.com', 'password': 'h'}, format='json')

        self.test_data = {"name": "g"}
        test_response = self.client.post('/api/tests/', self.test_data, format='json')
        self.assertEqual(test_response.status_code, status.HTTP_201_CREATED)
        self.test_id = test_response.data['id']

        test_detailed = self.client.get(f'http://localhost:8000/api/tests/{self.test_id}/')
        self.assertEqual(test_detailed.status_code, status.HTTP_200_OK)  
        self.test_code = test_detailed.data.get('test_code')
               

    def test_evaluate_test_successfully(self):
        # print("----test_evaluate_test_successfully")
        self.questions_data = [{"text": "another question","question_type": "choice","options": [
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
        self.question_ids=[]
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
        # print("Test Response Data:", response.data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        response = self.client.post(
            f'/api/tests/{self.test_id}/evaluate/',
            {
                "test_code": self.test_code,  
                "answers": answers,
            },
            format='json'
        )
        # print('respone in evaluation', response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        evaluation_data = response.data
        self.assertIn("total_score", evaluation_data)
        self.assertEqual(evaluation_data["total_score"], [{'category': '1', 'total_points': 5, 'response': 'Low'}]) 


    def test_evaluate_diff_categories(self):
        print("test_evaluate_divv_categories")
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
            {"text": "Is?", "question_type": "text", "options": "", "category": "1"},
            {"text": "2 + 2?", "question_type": "text", "options": "", "category": "1"},
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
                "test_code": self.test_code,  
                "answers": answers,
            },
            format='json'
        )
        print('respone in evaluation', response.data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        evaluation_data = response.data
        self.assertIn("total_score", evaluation_data)
        self.assertEqual(evaluation_data["total_score"], [{'category': '1', 'total_points': 11, 'response': 'Medium'}, {'category': '2', 'total_points': 5, 'response': 'Low'}]) 

    
    def test_evaluate_smth_that_didnt_work(self):
        # print("***********")
        self.questions_data = [
            {
                "text": "1Q",
                "question_type": "choice",
                "options": [
                    {
                        "text": "1A",
                        "value": 5,
                        "hasValue": True
                    },
                    {
                        "text": "12A",
                        "value": 5,
                        "hasValue": True
                    },
                ],
                "category": "1"
            },
            {
                "text": "2Q",
                "question_type": "choice",
                "options": [
                    {
                        "text": "2A",
                        "value": 5,
                        "hasValue": True
                    },
                ],
                "category": "2"
            },
            {
                "text": "3Q",
                "question_type": "choice",
                "options": [
                    {
                        "text": "3A",
                        "value": 5,
                        "hasValue": True
                    },
                ],
                "category": "2"
            },
            {"text": "Is the sky blue?", "question_type": "boolean", "options": "", "category": "1"},
            {"text": "What is 2 + 2?", "question_type": "boolean", "options": "", "category": "1"},
        ]
        self.question_ids = []
        for question in self.questions_data:
            response = self.client.post(f'/api/tests/{self.test_id}/questions/', question, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(response.data['text'], question['text'])
            self.question_ids.append(response.data['id'])
        
        answers = [
            {'question_id': self.question_ids[0], 'answer': {'text': '1A', 'value': 5, 'hasValue': True}},
            {'question_id': self.question_ids[1], 'answer': {'text': '2A', 'value': 5, 'hasValue': True}},
            {'question_id': self.question_ids[2], 'answer': {'text': '3A', 'value': 5, 'hasValue': True}},
            {'question_id': self.question_ids[3], 'answer': {'text': 'Yes'}},
            {'question_id': self.question_ids[4], 'answer': {'text': 'No'}},

        ]
        self.scales_data = [
            {"min_points": 0, "max_points": 5, "response": "Low", "category": "1"},
            {"min_points": 0, "max_points": 15, "response": "Medium", "category": "2"},
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
        self.assertEqual(evaluation_data["total_score"], [{'category': '1', 'total_points': 5, 'response': 'Low'}, {'category': '2', 'total_points': 10, 'response': 'Medium'}]) 

class LogoutViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_logout_success(self):
        self.client.cookies['jwt'] = 'test_token'

        response = self.client.post('/api/logout/')  

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'message': 'success'})
        # self.assertNotIn('jwt', response.cookies)  

class UploadImageViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_upload_valid_image(self):
        image_content = b"iVBORw0KGgoAAANSUhEUgAAAAUA"   
        image_file = SimpleUploadedFile(
            name=f"image_{uuid.uuid4().hex}.png",
            content=image_content,
            content_type='image/png'
        )
        response = self.client.post('/api/upload-image/', {'image': image_file}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('image_url', response.data)  

    def test_upload_no_image(self):
        response = self.client.post('/api/upload-image/', {}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {"error": "No image uploaded"})

class SpecialTestsForCreatingTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(email="g@g.com", name="g")
        self.user.set_password("h")
        self.user.save()
        self.token = jwt.encode(
            {'id': self.user.id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)},
            'secret', algorithm='HS256'
        )
        self.test1 = Test.objects.create(name="Test 1", created_by=self.user)
        self.test2 = Test.objects.create(name="Test 2", created_by=self.user)

    def test_create_test_with_valid_token(self):
        self.client.cookies['jwt'] = self.token
        response = self.client.post('/api/tests/', {'name': 'Test 1'})

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertIn('name', response.data)
        self.assertEqual(response.data['name'], 'Test 1')

        test = Test.objects.get(id=response.data['id'])
        self.assertEqual(test.name, 'Test 1')

    def test_create_test_missing_token(self):
        response = self.client.post('/api/tests/', {'name': 'Test 2'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'Unauthenticated!')

    def test_create_test_expired_token(self):
        expired_token = jwt.encode(
            {'id': self.user.id, 'exp': datetime.datetime.utcnow() - datetime.timedelta(hours=1)},
            'secret', algorithm='HS256'
        )

        self.client.cookies['jwt'] = expired_token

        response = self.client.post('/api/tests/', {'name': 'Test 3'})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'Token has expired!')

    def test_create_test_user_not_found(self):
        invalid_user_token = jwt.encode(
            {'id': 99999, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)},
            'secret', algorithm='HS256'
        )
        self.client.cookies['jwt'] = invalid_user_token
        response = self.client.post('/api/tests/', {'name': 'Test 4'})

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], 'User not found!')
    
class TestListViewGetTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create(email="test@example.com", password="test123")
        self.test1 = Test.objects.create(name="Test 1", created_by=self.user)
        self.test2 = Test.objects.create(name="Test 2", created_by=self.user)

        payload = {
            'id': self.user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }
        self.token = jwt.encode(payload, 'secret', algorithm='HS256')
        self.client.cookies['jwt'] = self.token

    def test_get_tests_success(self):
        response = self.client.get('/api/tests/')  # uprav URL podľa tvojho routing
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['name'], "Test 1")
        self.assertEqual(response.data[1]['name'], "Test 2")

    def test_get_tests_unauthenticated(self):
        self.client.cookies.pop('jwt', None)
        response = self.client.get('/api/tests/')
        self.assertEqual(response.status_code, 403)
        self.assertIn("Unauthenticated", str(response.data))

    def test_get_tests_expired_token(self):
        expired_payload = {
            'id': self.user.id,
            'exp': datetime.datetime.utcnow() - datetime.timedelta(hours=1)
        }
        expired_token = jwt.encode(expired_payload, 'secret', algorithm='HS256')
        self.client.cookies['jwt'] = expired_token
        response = self.client.get('/api/tests/')
        self.assertEqual(response.status_code, 403)
        self.assertIn("Token has expired", str(response.data))

    def test_get_tests_user_not_found(self):
        self.user.delete()
        response = self.client.get('/api/tests/')
        self.assertEqual(response.status_code, 403)
        self.assertIn("User not found", str(response.data))

class UpdateTestNameTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(email='g@g.com', password='h')
        self.test = Test.objects.create(name='test', created_by=self.user)

        self.token = jwt.encode({
            'id': self.user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)
        }, 'secret', algorithm='HS256')

        self.client.cookies['jwt'] = self.token
        self.update_data = {'name': 'Updated Test Name'}

    def test_update_test_successfully(self):
        url = f'/api/tests/{self.test.id}/'
        response = self.client.put(url, data=self.update_data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], self.update_data['name'])

    def test_update_test_unauthenticated(self):
        self.client.cookies.pop('jwt')
        url = f'/api/tests/{self.test.id}/'
        response = self.client.put(url, data=self.update_data, format='json')
        self.assertEqual(response.status_code, 403)
        self.assertIn('Unauthenticated', str(response.data))

    def test_update_test_expired_token(self):
        expired_token = jwt.encode({
            'id': self.user.id,
            'exp': datetime.datetime.utcnow() - datetime.timedelta(hours=1)
        }, 'secret', algorithm='HS256')
        self.client.cookies['jwt'] = expired_token
        url = f'/api/tests/{self.test.id}/'
        response = self.client.put(url, data=self.update_data, format='json')
        self.assertEqual(response.status_code, 403)
        self.assertIn('Token has expired', str(response.data))

    def test_update_test_not_found(self):
        url = f'/api/tests/9999/'
        response = self.client.put(url, data=self.update_data, format='json')
        self.assertEqual(response.status_code, 404)
        self.assertIn('Test not found', str(response.data))

class TestResponsesViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(email="g@g.com", name="g")
        self.user.set_password("h")
        self.user.save()
        self.client.post('/api/login/', {'email': 'g@g.com', 'password': 'h'}, format='json')
        self.test_data = {"name": "g"}
        test_response = self.client.post('/api/tests/', self.test_data, format='json')
        self.test_id = test_response.data['id']
        print('ID', self.test_id)
        test_detailed = self.client.get(f'http://localhost:8000/api/tests/{self.test_id}/')
        self.assertEqual(test_detailed.status_code, status.HTTP_200_OK)  
        self.test_code = test_detailed.data.get('test_code')  

        self.questions_data = {"text": "Question 1","question_type": "text","options":"","category": "1"}

        response = self.client.post(f'/api/tests/{self.test_id}/questions/', self.questions_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        answers = [
            {'question_id': response.data['id'], 'answer': {'text': 'Yes'}},
        ]
        response = self.client.post(
            f'/api/tests/{self.test_id}/submit/',
            {
                'test_code': self.test_code,
                'answers': answers
            },
            format='json'
        )

    def test_get_test_responses_success(self):
        response = self.client.get(f'/api/tests/{self.test_id}/responses/' )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)   
        self.assertEqual(len(response.data[0]['answers']), 1)  

        answer_data = response.data[0]['answers']
        self.assertEqual(answer_data[0]['question'], 'Question 1')
        # self.assertEqual(answer_data[0]['answer']['text'], 'Yes')
       

    def test_get_test_responses_test_not_found(self):
        url = f'/api/tests/9999/responses/'  
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

class TestListAdminViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.admin = User.objects.create(email='admin@admin.com', name='Admin', is_admin=True)
        self.user = User.objects.create(email='user@user.com', name='User', is_admin=False)

        self.test_admin = Test.objects.create(name='Admins Test', created_by=self.admin)
        self.test_user = Test.objects.create(name='Users Test', created_by=self.user)


    def test_unauthenticated_user_sees_only_admin_tests(self):
        response = self.client.get('/api/tests/default/')
        self.assertEqual(response.status_code, 200)
        test_names = [t['name'] for t in response.data['tests']]
        self.assertIn('Admins Test', test_names)
        self.assertNotIn('Users Test', test_names)


# class UploadDrawingViewTestCase(TestCase):
#     def setUp(self):
#         self.client = APIClient()
#         self.user = User.objects.create(email='test@example.com', password='password')
#         self.test_obj = Test.objects.create(name='Test 1', created_by=self.user)
#         self.question = Question.objects.create(test=self.test_obj, text='Question 2', question_type='text')
#         self.post_url = '/api/save_drawing/'
#         self.get_url = f'/api/save_drawing/{self.question.id}/'
#         self.fake_base64_image = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUA'

#     def test_post_valid_drawing(self):
#         data = {
#             'question_id': self.question.id,
#             'image': self.fake_base64_image
#         }
#         response = self.client.post(self.post_url, data, format='json')
#         print(response)
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(Drawing.objects.count(), 1)

#     def test_post_missing_data(self):
#         response = self.client.post(self.post_url, {}, format='json')
#         self.assertEqual(response.status_code, 400)

#     def test_post_nonexistent_question(self):
#         data = {
#             'question_id': 9999,
#             'image': self.fake_base64_image
#         }
#         response = self.client.post(self.post_url, data, format='json')
#         self.assertEqual(response.status_code, 404)

#     def test_get_existing_drawing(self):
#         data = {
#             'question_id': self.question.id,
#             'image': self.fake_base64_image
#         }
#         self.client.post(self.post_url, data, format='json')
#         response = self.client.get(self.get_url)
#         self.assertEqual(response.status_code, 200)
#         self.assertIn('drawing', response.json())
#         self.assertEqual(response.json()['drawing'], self.fake_base64_image)

#     def test_get_no_drawing(self):
#         response = self.client.get(self.get_url)
#         self.assertEqual(response.status_code, 404)


class SaveVideoViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(email='g@g.com')
        self.user.set_password('pass')
        self.user.save()

        self.test_obj = Test.objects.create(name='Test1', created_by=self.user)
        self.question = Question.objects.create(test=self.test_obj,text='q',question_type='text')

        self.video_file = SimpleUploadedFile("test_video.webm",b'video content',content_type="video/webm")

    def test_save_video(self):
        data = {
            'question_id': str(self.question.id),  
            'video': self.video_file,
        }
        response = self.client.post('/api/save_video/', data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('id', response.json())
        self.assertTrue(RecordedVideo.objects.filter(question_id=self.question.id).exists())

    def test_save_video_missing_data(self):
        response = self.client.post('/api/save_video/', format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['error'], 'Invalid data')

    def test_get_saved_url(self):
        recorded = RecordedVideo.objects.create(
            question_id=self.question.id,
            video_file=self.video_file
        )

        get_url = f'/api/save_video/{self.question.id}/'  
        response = self.client.get(get_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('video_url', response.json())
