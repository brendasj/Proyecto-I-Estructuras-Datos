import time
import random
from api_client import ApiClient

class ClimaMarkov:
    def __init__(self, city):
        self.api = ApiClient()
        self.city = city
        datos = self.api.obtener_clima(self.city)
        if datos and "data" in datos:
            data = datos["data"]
            self.estado = data["initial"]["condition"]
            self.intensidad = data["initial"].get("intensity", 0)
            self.conditions = data.get("conditions", [])
            self.transition = data.get("transition", {})
        else:
            self.estado = "clear"
            self.intensidad = 0
            self.conditions = []
            self.transition = {}
        self.temperature = ""  # No disponible en la respuesta
        self.humidity = ""     # No disponible en la respuesta
        self.description = self.estado
        self.ultimo_cambio = time.time()
        self.intervalo = random.randint(45, 60)

    def actualizar(self):
        ahora = time.time()
        if ahora - self.ultimo_cambio > self.intervalo:
            self.estado = self.siguiente_estado()
            self.ultimo_cambio = ahora
            self.intervalo = random.randint(45, 60)
            self.description = self.estado

    def siguiente_estado(self):
        transiciones = self.transition.get(self.estado, {})
        if not transiciones:
            return self.estado
        estados = list(transiciones.keys())
        probabilidades = list(transiciones.values())
        return random.choices(estados, probabilidades)[0]

    def efecto_trabajador(self):
        # Ejemplo: reduce velocidad y aumenta resistencia en climas adversos
        if self.estado in ["rain", "rain_light", "storm", "wind", "heat", "cold", "fog"]:
            return {"velocidad": 0.7, "resistencia": 1.3}
        return {"velocidad": 1.0, "resistencia": 1.0}