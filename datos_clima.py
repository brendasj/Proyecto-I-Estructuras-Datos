"""Módulo que gestiona el clima usando una cadena de Markov.

El clima inicial se obtiene del endpoint `/city/weather` de la API y las
transiciones se extraen del campo `data.transition` si está presente.
"""

import time
import random
from typing import Dict, List

from api_client import ApiClient


class ClimaMarkov:
    """Controla el estado del clima y sus transiciones.

    Atributos principales:
    - city: nombre de la ciudad consultada en la API
    - estado: condición actual (p. ej. 'clear', 'rain')
    - intensidad: intensidad asociada al estado
    - transition: diccionario con la matriz de transición
    """

    def __init__(self, city: str):
        self.api = ApiClient()
        self.city = city
        datos = self.api.obtener_clima(self.city)
        if datos and "data" in datos:
            data = datos["data"]
            self.estado = data["initial"]["condition"]
            self.intensidad = data["initial"].get("intensity", 0)
            self.conditions: List[str] = data.get("conditions", [])
            self.transition: Dict[str, Dict[str, float]] = data.get("transition", {})
        else:
            self.estado = "clear"
            self.intensidad = 0
            self.conditions = []
            self.transition = {}

        # La API del profesor no devuelve temperatura/humedad; se dejan vacíos
        self.temperature = ""
        self.humidity = ""
        self.description = self.estado

        self.ultimo_cambio = time.time()
        self.intervalo = random.randint(45, 60)

    def actualizar(self) -> None:
        """Actualiza el estado del clima si ha pasado el intervalo aleatorio.

        El nuevo estado se selecciona según la matriz de transición recibida
        en la respuesta del API.
        """
        ahora = time.time()
        if ahora - self.ultimo_cambio > self.intervalo:
            self.estado = self.siguiente_estado()
            self.ultimo_cambio = ahora
            self.intervalo = random.randint(45, 60)
            self.description = self.estado

    def siguiente_estado(self) -> str:
        """Calcula el siguiente estado usando la distribución de transición."""
        transiciones = self.transition.get(self.estado, {})
        if not transiciones:
            return self.estado
        estados = list(transiciones.keys())
        probabilidades = list(transiciones.values())
        return random.choices(estados, probabilidades)[0]

    def efecto_trabajador(self) -> Dict[str, float]:
        """Devuelve modificadores para el trabajador según el clima actual.

        Retorna dict con claves 'velocidad' y 'resistencia'.
        """
        adversos = {"rain", "rain_light", "storm", "wind", "heat", "cold", "fog"}
        if self.estado in adversos:
            return {"velocidad": 0.7, "resistencia": 1.3}
        return {"velocidad": 1.0, "resistencia": 1.0}