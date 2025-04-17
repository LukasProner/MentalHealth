from locust import HttpUser, task, between
import random
import json
from io import BytesIO
import string
# class UserBehavior(HttpUser):
#     host = "http://localhost:8000"  
#     wait_time = between(1, 2)   

#     @task
#     def register_success(self):
#         user_data = {
#             "name": f"Test User {random.randint(1000, 9999)}",
#             "email": f"user{random.randint(1000, 9999)}@example.com",
#             "password": "securepassword123"
#         }
#         response = self.client.post("/api/register/", json=user_data, name="/api/register/")
#         assert response.status_code == 200  
#         assert "email" in response.json()  
#     @task
#     def test_valid_test_code(self):
#         response = self.client.post("/api/tests/16/public/", json={"test_code": "NqmSRtWKAj"}, name="/api/tests/16/public/")
#         assert response.status_code == 200, f"Chyba: {response.status_code}"
#         assert response.json().get("name") == "Test for Public", f"Neočakávaný výsledok: {response.json()}"

#     @task
#     def login_success(self):
#         login_data = {
#             "email": "sk@sk.sk",
#             "password": "sk"
#         }
#         response = self.client.post("/api/login/", json=login_data)

#         assert response.status_code == 200, f"Chyba: {response.status_code}"
#         assert "jwt" in response.json(), "JWT token nie je v odpovedi"

class AlreadyLogged(HttpUser):
    host = "http://localhost:8000"
    wait_time = between(1, 2)
    @task
    def create_test_success(self):
        user_data = {
            "name": f"Test User {random.randint(1000, 9999)}",
            "email": f"user{random.randint(1000, 9999)}@example.com",
            "password": f"securepassword{random.randint(1000, 9999)}"
        }
        response_register = self.client.post("/api/register/", json=user_data)

        user_data = {'email':user_data["email"], 'password': user_data["password"]}
        response_login = self.client.post('/api/login/', json=user_data, name='/api/login/')

        if response_login.status_code == 200:
            self.token = response_login.json().get('jwt')
        else:
            self.token = None
            print("Login failed")
        if self.token:
            headers = {'Authorization': f'Bearer {self.token}'}
            test_data = {"name": f"Test názov {random.randint(1000, 5000)}"}

            # Vytváranie testu
            response = self.client.post('/api/tests/', json=test_data, headers=headers)
            assert response.status_code == 201, f"Failed to create test: {response.status_code}"
            test_id = response.json().get("id")
            for_code = self.client.get(f'/api/tests/{test_id}/', headers=headers)
            self.testCode = for_code.json().get("test_code")
            print("Test code: ", self.testCode)
            assert test_id, "Test ID not found in the response"

            # # Pridávanie otázok k testu
            # self.questions_data = [
            #     {"text": "Is the sky blue?", "question_type": "text", "options": "", "category": "Nezaradená"}
            # ]
            # for question in self.questions_data:
            #     question_data = {
            #         "text": question["text"],
            #         "question_type": question["question_type"],
            #         "options": question["options"],
            #         "category": question["category"]
            #     }
            #     responsequestion = self.client.post(f'/api/tests/{test_id}/questions/', json=question_data, headers=headers)
            #     assert responsequestion.status_code == 201, f"Failed to create question: {responsequestion.status_code}"
            #     assert responsequestion.json().get('text') == question['text'], "Question text mismatch"
            #     question_id = responsequestion.json().get('id')

            #     # Test na update otázky
            #     updated_data = {
            #         "text": "Is the sky green?",  # Aktualizovaný text
            #         "question_type": "text",
            #         "options": "",
            #         "category": "Nezaradená"
            #     }

            #     # Aktualizácia otázky
            #     update_url = f'/api/questions/{question_id}/'
            #     update_response = self.client.put(update_url, json=updated_data, headers=headers)
            #     assert update_response.status_code == 200, f"Failed to update question (id={question_id}): {update_response.status_code}"
            #     updated_question = update_response.json()
            #     assert updated_question.get('text') == updated_data['text'], "Updated question text mismatch"




            #     delete_question_response = self.client.delete(f'/api/questions/{question_id}/', headers=headers)
            #     assert delete_question_response.status_code == 204, f"Failed to delete question (id={question_id}): {delete_question_response.status_code}"

            # # pridavam skaly
            # self.scales_data = [
            #     {"min_points": 0, "max_points": 10, "response": "Low", "category": "Nezaradená"},
            #     {"min_points": 11, "max_points": 20, "response": "Medium", "category": "Nezaradená"},
            #     {"min_points": 21, "max_points": 30, "response": "High", "category": "Nezaradená"},
            # ]
            # scale_response = self.client.post(f'/api/tests/{test_id}/scales/',json=self.scales_data,headers=headers)
            # assert scale_response.status_code == 201,f"Scale response status code: {scale_response.status_code}"

            # get_scales_response = self.client.get(f'/api/tests/{test_id}/scales/', headers=headers)
            # assert get_scales_response.status_code == 200,f"Scale response status code: {scale_response.status_code}"

            # # Overenie, že otázky sú pridané k testu
            # test_with_questions = self.client.get(f'/api/tests/{test_id}/', headers=headers)
            # assert test_with_questions.status_code == 200, f"Failed to get test with questions: {test_with_questions.status_code}"
            # assert len(test_with_questions.json().get('questions', [])) == len(self.questions_data), \
            #     f"Mismatch in number of questions. Expected: {len(self.questions_data)}, Got: {len(test_with_questions.json().get('questions', []))}"
            
            # #ak su tak otvorim odovdzdavaciu obrzovku
            # if(test_with_questions.status_code == 200):
            #     print("Test created successfully with questions.")
            #     response_public = self.client.post(f'/api/tests/{test_id}/public/', {'test_code': self.testCode})
            #     assert response_public.status_code == 200,f"Failed to delete test (code={self.testCode}): {response_public.status_code}"

            #     answers = [
            #         {'question_id': question_id, 'answer': {'text': 'super', 'value': 5, 'hasValue': True}},
            #     ]
            #     response_submit = self.client.post(
            #         f'/api/tests/{test_id}/submit/',
            #         json={
            #             'test_code': self.testCode,
            #             'answers': answers
            #         }
            #     )
            #     assert response_submit.status_code == 201, f"Failed to submit test: {response_submit.status_code}"

            #     response_eval = self.client.post(
            #         f'/api/tests/{test_id}/evaluate/',
            #         json={
            #             "test_code": self.testCode,  
            #             "answers": answers,
            #         },
            #     )
            #     assert response_eval.status_code == 200, f"Failed to eval test: {response_eval.status_code}"

            #     response_responses = self.client.get(f'/api/tests/{test_id}/responses/') 
            #     assert response_responses.status_code == 200
            #     response_list_of_admins_tests = self.client.get('/api/tests/default/')
            #     assert response_list_of_admins_tests.status_code == 200

            #     # #test ukladania obrazku
            #     # data = {
            #     #     'question_id': question_id,
            #     #     'image': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUA'
            #     # }
            #     # response_drawing = self.client.post('/api/save_drawing/', json=data)
            #     # assert response_drawing.status_code == 200


            #     #ulozenie videa
            #     files = {
            #         "question_id": (None, str(question_id)),
            #         "video": ("test_video.webm", BytesIO(b"this is test video content"), "video/webm")
            #     }
            #     response_video = self.client.post("/api/save_video/", files=files)
            #     delete_response = self.client.delete(f"/api/tests/{test_id}/", headers=headers)
            #     assert delete_response.status_code == 204, f"Failed to delete test (id={test_id}): {delete_response.status_code}"
            # # Mazanie testu po vytvorení a overení
            

            response_logout = self.client.post('/api/logout/')  

            assert response_logout.status_code == 200, f"Failed to lohout"
        else:
            print("Skipping test creation due to failed login")


