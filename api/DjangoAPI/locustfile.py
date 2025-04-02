from locust import HttpUser, task, between
import random

class UserBehavior(HttpUser):
    host = "http://localhost:8000"  
    wait_time = between(1, 2)   

    @task
    def register_success(self):
        user_data = {
            "name": f"Test User {random.randint(1000, 9999)}",
            "email": f"user{random.randint(1000, 9999)}@example.com",
            "password": "securepassword123"
        }
        response = self.client.post("/api/register/", json=user_data, name="/api/register/")
        assert response.status_code == 200  
        assert "email" in response.json()  
    @task
    def test_valid_test_code(self):
        response = self.client.post("/api/tests/16/public/", json={"test_code": "NqmSRtWKAj"}, name="/api/tests/16/public/")
        assert response.status_code == 200, f"Chyba: {response.status_code}"
        assert response.json().get("name") == "Test for Public", f"Neočakávaný výsledok: {response.json()}"

    @task
    def login_success(self):
        login_data = {
            "email": "sk@sk.sk",
            "password": "sk"
        }
        response = self.client.post("/api/login/", json=login_data)

        assert response.status_code == 200, f"Chyba: {response.status_code}"
        assert "jwt" in response.json(), "JWT token nie je v odpovedi"

class AlreadyLogged(HttpUser):
    host = "http://localhost:8000"
    wait_time = between(1, 2)

    def on_start(self):
        user_data = {
            'email': 'sk@sk.sk',
            'password': 'sk'
        }
        # Prihlásenie používateľa
        response = self.client.post('/api/login/', json=user_data, name='/api/login/')
        if response.status_code == 200:
            self.token = response.json().get('jwt')  # Uloženie JWT tokenu na ďalšie požiadavky
        else:
            self.token = None
            print("Login failed")

    @task
    def create_test_success(self):
        if self.token:
            headers = {
                'Authorization': f'Bearer {self.token}'  # Nastavenie Authorization header pre autentifikáciu
            }
            test_data = {
                "name": f"Test názov {random.randint(1000, 5000)}",
            }
            response = self.client.post('/api/tests/', json=test_data, headers=headers, name='/api/tests/')
            assert response.status_code == 201, f"Failed to create test: {response.status_code}"
            assert response.json().get('name') == test_data['name'], f"Unexpected test name: {response.json().get('name')}"
        else:
            print("Skipping test creation due to failed login")