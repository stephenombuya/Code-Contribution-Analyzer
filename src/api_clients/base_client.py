import requests

class BaseClient:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.token = token
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Accept': 'application/json'
        }

    def get(self, endpoint):
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def post(self, endpoint, data):
        url = f"{self.base_url}/{endpoint}"
        response = requests.post(url, json=data, headers=self.headers)
        response.raise_for_status()
        return response.json()

