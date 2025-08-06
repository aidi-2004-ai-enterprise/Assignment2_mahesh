from locust import HttpUser, task, between

class MultiAppUser(HttpUser):
    # Set the host to your Cloud Run service URL
    host = "https://penguin-api-408534553654.us-central1.run.app"
    # For local testing
    host = "http://localhost:8080"
    wait_time = between(1, 5) # Wait time between tasks for each user

    @task
    def predict_cloud(self):
        # This payload matches the PenguinFeatures model in your main.py
        payload = {
            "bill_length_mm": 39.1,
            "bill_depth_mm": 18.7,
            "flipper_length_mm": 181.0,
            "body_mass_g": 3750.0,
            "sex": "male",
            "island": "Torgersen",
        }
        # Use a relative path now that the host is defined at the class level
        self.client.post("/predict", json=payload)