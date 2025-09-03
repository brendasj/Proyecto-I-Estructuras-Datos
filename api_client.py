import requests

class ApiClient:
    def __init__(self):
        self.base_url = "https://tigerds-api.kindflower-ccaf48b6.eastus.azurecontainerapps.io"

    def obtener_mapa(self, params):
        try:
            response = requests.get(f"{self.base_url}/city/map", params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print("Error al obtener el mapa:", e)
            return None
        
    def obtener_clima(self, ciudad):
        try:
           response = requests.get(f"{self.base_url}/city/weather", params={"city": ciudad})
           response.raise_for_status()
           return response.json()
        except requests.exceptions.RequestException as e:
           print("Error al obtener el clima:", e)
           return None

    def obtener_trabajos(self):
        try:
           response = requests.get(f"{self.base_url}/city/jobs")
           response.raise_for_status()
           return response.json()
        except requests.exceptions.RequestException as e:
           print("Error al obtener los trabajos:", e)
           return None