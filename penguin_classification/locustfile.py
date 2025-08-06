from locust import HttpUser, task, between

class MultiAppUser(HttpUser):
    wait_time = between(1, 5)

    @task
    def predict_local(self):
        payload = {
            "species": "Adelie",
            "island": "Torgersen",
            "bill_length_mm": 39.1,
            "bill_depth_mm": 18.7,
            "flipper_length_mm": 181.0,
            "body_mass_g": 3750.0,
            "sex": "male",
        }
        #self.client.post("http://localhost:8000/predict", json=payload)
        self.client.post("http://localhost:8080/predict", json=payload)


    @task
    def predict_cloud(self):
        payload = {
            "species": "Adelie",
            "island": "Torgersen",
            "bill_length_mm": 39.1,
            "bill_depth_mm": 18.7,
            "flipper_length_mm": 181.0,
            "body_mass_g": 3750.0,
            "sex": "male",
        }
        self.client.post("https://penguin-api-408534553654.us-central1.run.app/predict", json=payload)
