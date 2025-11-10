"""Manejo de pedidos recibidos desde la API.

Este módulo proporciona la clase `Pedidos` que se encarga de obtener,
procesar y gestionar la cola de pedidos disponibles en el juego.
"""

import heapq
from api_client import ApiClient
from pedido import Pedido
from typing import List, Optional
from collections import deque


class Pedidos:
    """Gestor de pedidos.

    Acepta un `ApiClient` en la creación y mantiene dos estructuras:
    - `pedidos`: heap con los pedidos pendientes
    - `pedidos_aceptados`: lista con los pedidos aceptados
    """

    def __init__(self, api_client: ApiClient):
        self.api = api_client
        # `pedidos` es el heap de pedidos actualmente publicados (disponibles
        # para aceptar). No contiene todos los trabajos de la API: éstos se
        # almacenan en `fuente_jobs` y se van publicando uno a uno cuando el
        # jugador presiona la tecla correspondiente.
        self.pedidos = []
        self.pedidos_aceptados = []
        # Fuente/cola con todos los trabajos cargados desde la API; se
        # publican uno por uno.
        self.fuente_jobs: deque[Pedido] = deque()

    def procesar_pedidos(self) -> bool:
        """Carga los pedidos desde la API y los añade al heap interno.

        Devuelve True si el parseo fue correcto, False en caso contrario.
        """
        datos = self.api.obtener_trabajos()

        if isinstance(datos, dict) and "data" in datos and isinstance(datos["data"], list):
            # Vaciar estructuras previas
            self.pedidos = []
            self.pedidos_aceptados = []
            self.fuente_jobs.clear()

            # Cargar todos los trabajos en la fuente; no los publicamos todos
            # a la vez para que el jugador los vaya pidiendo.
            for pedido_data in datos["data"]:
                pedido = Pedido(
                    id=pedido_data["id"],
                    payout=pedido_data["payout"],
                    priority=pedido_data["priority"],
                    pickup=tuple(pedido_data["pickup"]),
                    dropoff=tuple(pedido_data["dropoff"]),
                    weight=pedido_data["weight"],
                    deadline=pedido_data["deadline"],
                    release_time=pedido_data["release_time"],
                )
                self.fuente_jobs.append(pedido)
            return True

        print("Error: Los datos de la API no tienen el formato esperado.")
        return False

    def obtener_siguiente_pedido(self) -> Optional[Pedido]:
        """Devuelve el siguiente pedido (sin extraerlo) o None si no hay pedidos."""
        if self.pedidos:
            _, _, pedido = self.pedidos[0]
            return pedido
        return None

    def obtener_todos_los_pedidos(self) -> List[Pedido]:
        """Devuelve una lista con todos los pedidos pendientes."""
        return [pedido for _, _, pedido in self.pedidos]

    def publicar_siguiente_pedido(self) -> Optional[Pedido]:
        """Publica (hace visible) el siguiente pedido desde la fuente.

        Devuelve el pedido publicado o None si no quedaba ninguno.
        """
        if not self.fuente_jobs:
            return None
        pedido = self.fuente_jobs.popleft()
        # Insertar en el heap con prioridad (negativa para max-heap)
        index = len(self.pedidos) + 1
        heapq.heappush(self.pedidos, (-pedido.priority, index, pedido))
        return pedido

    def cantidad_pedidos(self) -> int:
        """Devuelve el número de pedidos pendientes."""
        return len(self.pedidos)

    def aceptar_pedido(self) -> Optional[Pedido]:
        """Extrae (pop) el pedido con mayor prioridad y lo marca como aceptado."""
        if self.pedidos:
            _, _, pedido = heapq.heappop(self.pedidos)
            self.pedidos_aceptados.append(pedido)
            return pedido
        return None

    def aceptar_pedido_especifico(self, pedido_obj: Pedido) -> Optional[Pedido]:
        """Elimina un pedido específico del heap de pendientes y lo marca como
        aceptado. Esto busca por id para evitar inconsistencias cuando se
        selecciona un pedido arbitrario (por ejemplo por la IA).

        Devuelve el objeto pedido si fue encontrado y aceptado, o None si no
        se encontró.
        """
        # Buscar la tupla que contiene el pedido
        for idx, tup in enumerate(self.pedidos):
            _, _, p = tup
            if p.id == pedido_obj.id:
                # remover la tupla y reconstruir el heap
                self.pedidos.pop(idx)
                heapq.heapify(self.pedidos)
                self.pedidos_aceptados.append(p)
                return p
        return None

    def rechazar_pedido(self) -> Optional[Pedido]:
        """Rechaza (extrae) el siguiente pedido y lo devuelve."""
        if self.pedidos:
            _, _, pedido = heapq.heappop(self.pedidos)
            print(f"Pedido {pedido.id} rechazado")
            return pedido
        return None