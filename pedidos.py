"""Manejo de pedidos recibidos desde la API.

Este módulo proporciona la clase `Pedidos` que se encarga de obtener,
procesar y gestionar la cola de pedidos disponibles en el juego.
"""

import heapq
from api_client import ApiClient
from pedido import Pedido
from typing import List, Optional


class Pedidos:
    """Gestor de pedidos.

    Acepta un `ApiClient` en la creación y mantiene dos estructuras:
    - `pedidos`: heap con los pedidos pendientes
    - `pedidos_aceptados`: lista con los pedidos aceptados
    """

    def __init__(self, api_client: ApiClient):
        self.api = api_client
        self.pedidos = []
        self.pedidos_aceptados = []

    def procesar_pedidos(self) -> bool:
        """Carga los pedidos desde la API y los añade al heap interno.

        Devuelve True si el parseo fue correcto, False en caso contrario.
        """
        datos = self.api.obtener_trabajos()

        if isinstance(datos, dict) and "data" in datos and isinstance(datos["data"], list):
            self.pedidos = []
            for i, pedido_data in enumerate(datos["data"]):
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
                heapq.heappush(self.pedidos, (-pedido.priority, i, pedido))
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

    def rechazar_pedido(self) -> Optional[Pedido]:
        """Rechaza (extrae) el siguiente pedido y lo devuelve."""
        if self.pedidos:
            _, _, pedido = heapq.heappop(self.pedidos)
            print(f"Pedido {pedido.id} rechazado")
            return pedido
        return None