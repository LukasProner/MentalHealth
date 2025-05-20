from locust import HttpUser, task, between
import random
import json
from io import BytesIO
import string

logged_in_users = set()

class AlreadyLogged(HttpUser):
    host = "http://localhost:8000"
    wait_time = between(1, 2)

    @task
    def create_test_success(self):
        name=f"Test User {random.randint(1000, 9000)}"
        email=f"user{random.randint(1000, 9000)}@example.com"
        password=f"securepassword{random.randint(1000, 9000)}"

        if email in logged_in_users:
            return
        
        user_data={
            "name":name,
            "email":email,
            "password":password
        }
        response_register=self.client.post("/api/register/",json=user_data)

        login_data={"email":email,"password":password}
        response_login=self.client.post('/api/login/',json=login_data,name='/api/login/')

        if response_login.status_code==200:
            self.token = response_login.json().get('jwt')
            logged_in_users.add(email)  
        else:
            self.token = None
            return

        if self.token:
            headers={'Authorization':f'Bearer{self.token}'}
            test_data ={"name":f"Test názov {random.randint(1000, 5000)}"}

            response=self.client.post('/api/tests/',json=test_data,headers=headers)
            assert response.status_code == 201, f"chyba pri vytvarani testu {response.status_code}"
            test_id = response.json().get("id")
            for_code = self.client.get(f'/api/tests/{test_id}/', headers=headers)
            if for_code.status_code == 200:
                try:
                    self.testCode = for_code.json().get("test_code")
                    print("Test code: ", self.testCode)
                except ValueError:
                    print("chyba")
            else:
                print(f"nepodarilo sa získať test {for_code.status_code}")

            self.questions_data=[
                {"text":"Is it smt?","question_type":"text","options":"","category":"Nezaradená"}
            ]
            for question in self.questions_data:
                question_data={
                    "text":question["text"],
                    "question_type":question["question_type"],
                    "options":question["options"],
                    "category":question["category"]
                }
                responsequestion=self.client.post(f'/api/tests/{test_id}/questions/',json=question_data,headers=headers)
                assert responsequestion.status_code==201,f"chyba vytvorenie testu {responsequestion.status_code}"
                assert responsequestion.json().get('text') == question['text'], "iny text otazku / nezhoda"
                question_id=responsequestion.json().get('id')

                updated_data={
                    "text":"is grass green?",   
                    "question_type":"text",
                    "options":"",
                    "category":"Nezaradená"
                }

                update_url=f'/api/questions/{question_id}/'
                update_response=self.client.put(update_url, json=updated_data, headers=headers)
                assert update_response.status_code ==200,f"chzba -update question, id={question_id}), {update_response.status_code}"
                updated_question= update_response.json()
                assert updated_question.get('text')== updated_data['text'], "ERROR1"

            self.scales_data=[
                {"min_points":0,"max_points": 10,"response":"Low","category":"Nezaradená"},
                {"min_points":11,"max_points":20,"response":"Medium","category": "Nezaradená"},
                {"min_points": 21, "max_points": 30, "response": "High","category": "Nezaradená"},
            ]
            scale_response=self.client.post(f'/api/tests/{test_id}/scales/',json=self.scales_data,headers=headers)
            assert scale_response.status_code==201,f"Scale response:{scale_response.status_code}"

            get_scales_response = self.client.get(f'/api/tests/{test_id}/scales/', headers=headers)
            assert get_scales_response.status_code==200,f"Scale response: {scale_response.status_code}"

            test_with_questions=self.client.get(f'/api/tests/{test_id}/',headers=headers)
            assert test_with_questions.status_code==200, f"chyba 96 gettest{test_with_questions.status_code}"
            assert len(test_with_questions.json().get('questions', [])) == len(self.questions_data), \
                f"ERROR2: {len(self.questions_data)},{len(test_with_questions.json().get('questions', []))}"
            
            if(test_with_questions.status_code==200):
                response_public = self.client.post(f'/api/tests/{test_id}/public/',{'test_code':self.testCode})
                assert response_public.status_code==200,f"102 delete test {self.testCode}) {response_public.status_code}"

                answers=[
                    {'question_id': question_id, 'answer':{'text':'super', 'value':5, 'hasValue':True}},
                ]
                response_submit = self.client.post(f'/api/tests/{test_id}/submit/',
                    json={'test_code':self.testCode,'answers':answers}
                )
                assert response_submit.status_code == 201, f"110 submit - {response_submit.status_code}"

                response_eval = self.client.post(f'/api/tests/{test_id}/evaluate/',json={"test_code": self.testCode,"answers": answers,},
                )
                assert response_eval.status_code==200,f"114 eval-{response_eval.status_code}"

                response_responses=self.client.get(f'/api/tests/{test_id}/responses/') 
                assert response_responses.status_code==200
                response_list_of_admins_tests=self.client.get('/api/tests/default/')
                assert response_list_of_admins_tests.status_code==200

                files={
                    "question_id": (None, str(question_id)),
                    "video": ("test_video.webm", BytesIO(b"video content"),"video/webm")
                }
                response_video=self.client.post("/api/save_video/",files=files)
                delete_response=self.client.delete(f"/api/tests/{test_id}/", headers=headers)
                assert delete_response.status_code == 204,f"127 delete,{delete_response.status_code}"
            

            response_logout=self.client.post('/api/logout/',headers=headers)
            assert "success" in response_logout.text
            

            logged_in_users.remove(email)  
        else:
            print("failed smth")
