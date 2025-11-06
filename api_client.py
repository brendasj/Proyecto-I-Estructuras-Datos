"""Cliente HTTP simple para interactuar con el backend del juego.

Provee métodos para obtener el mapa, el clima y los trabajos (pedidos).
Implementa una caché en disco para permitir modo offline.
"""

import json
import os
from typing import Any, Dict, Optional

import requests


class ApiClient:
    """Cliente para consultar los endpoints remotos y manejar caché local."""

    def __init__(self) -> None:
        self.base_url = (
            "https://tigerds-api.kindflower-ccaf48b6.eastus.azurecontainerapps.io"
        )
        self.cache_dir = "cache"
        os.makedirs(self.cache_dir, exist_ok=True)

    def obtener_mapa(self, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Consulta `/city/map` y devuelve el JSON o la caché en caso de fallo."""
        try:
            response = requests.get(f"{self.base_url}/city/map", params=params)
            response.raise_for_status()
            datos = response.json()
            self.guardar_en_cache("mapa.json", datos)
            return datos
        except requests.exceptions.RequestException:
            print("Modo offline: cargando mapa desde caché")
            return self.cargar_desde_cache("mapa.json")

    def obtener_clima(self, ciudad: str) -> Optional[Dict[str, Any]]:
        """Consulta `/city/weather?city=<ciudad>` y devuelve el JSON.

        Devuelve None en caso de error de red.
        """
        try:
            response = requests.get(
                f"{self.base_url}/city/weather", params={"city": ciudad}
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print("Error al obtener el clima:", e)
            return None

    def obtener_trabajos(self) -> Optional[Dict[str, Any]]:
        """Consulta `/city/jobs` y devuelve los datos o la caché en caso de fallo."""
        try:
            response = requests.get(f"{self.base_url}/city/jobs")
            response.raise_for_status()
            datos = response.json()
            self.guardar_en_cache("pedidos.json", datos)
            return datos
        except requests.exceptions.RequestException:
            print("Modo offline: cargando trabajos desde caché")
            return self.cargar_desde_cache("pedidos.json")

    def guardar_en_cache(self, nombre_archivo: str, datos: Any) -> None:
        """Guarda un objeto JSON en la carpeta de caché."""
        ruta = os.path.join(self.cache_dir, nombre_archivo)
        try:
            with open(ruta, "w", encoding="utf-8") as f:
                json.dump(datos, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"No se pudo guardar {nombre_archivo} en caché:", e)

    def cargar_desde_cache(self, nombre_archivo: str) -> Optional[Dict[str, Any]]:
        """Carga y devuelve un archivo JSON desde la caché si existe."""
        ruta = os.path.join(self.cache_dir, nombre_archivo)
        if os.path.exists(ruta):
            try:
                with open(ruta, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"No se pudo cargar {nombre_archivo} desde caché:", e)
        else:
            print(f"Archivo de caché no encontrado: {nombre_archivo}")
        return None