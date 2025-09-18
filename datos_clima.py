import time
import random
from api_client import ApiClient

class ClimaMarkov:
    ESTADOS = ["soleado", "lluvia", "tormenta", "viento", "calor_extremo"]
    TRANSICIONES = {
        "soleado": {"soleado": 0.5, "lluvia": 0.2, "tormenta": 0.05, "viento": 0.15, "calor_extremo": 0.1},
        "lluvia": {"soleado": 0.1, "lluvia": 0.6, "tormenta": 0.15, "viento": 0.1, "calor_extremo": 0.05},
        "tormenta": {"soleado": 0.05, "lluvia": 0.3, "tormenta": 0.5, "viento": 0.1, "calor_extremo": 0.05},
        "viento": {"soleado": 0.2, "lluvia": 0.2, "tormenta": 0.1, "viento": 0.4, "calor_extremo": 0.1},
        "calor_extremo": {"soleado": 0.2, "lluvia": 0.05, "tormenta": 0.05, "viento": 0.1, "calor_extremo": 0.6},
    }

    def __init__(self, ciudad):
        self.api = ApiClient()
        self.city = ciudad
        datos = self.api.obtener_clima(self.city)
        if datos:
            self.estado = datos.get("weather", "soleado").lower()
            self.temperature = datos.get("temperature", "")
            self.humidity = datos.get("humidity", "")
            self.description = datos.get("description", "")
        else:
            self.estado = "soleado"
            self.temperature = ""
            self.humidity = ""
            self.description = ""
        self.ultimo_cambio = time.time()
        self.intervalo = random.randint(45, 60)

    def obtener_estado_api(self):
        datos = self.api.obtener_clima(self.city)
        if datos and "weather" in datos:
            return datos["weather"].lower()
        return "soleado"

    def actualizar(self):
        ahora = time.time()
        if ahora - self.ultimo_cambio > self.intervalo:
            # Transición Markov
            self.estado = self.siguiente_estado()
            self.ultimo_cambio = ahora
            self.intervalo = random.randint(45, 60)

    def siguiente_estado(self):
        transiciones = self.TRANSICIONES.get(self.estado, self.TRANSICIONES["soleado"])
        estados = list(transiciones.keys())
        probabilidades = list(transiciones.values())
        return random.choices(estados, probabilidades)[0]

    def efecto_trabajador(self):
        if self.estado in ["lluvia", "tormenta", "viento", "calor_extremo"]:
            return {"velocidad": 0.7, "resistencia": 1.3}
        return {"velocidad": 1.0, "resistencia": 1.0}