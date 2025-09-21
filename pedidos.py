import heapq
from api_client import ApiClient
from pedido import Pedido

class Pedidos:
    def __init__(self, api_client: ApiClient):
        self.api = api_client
        self.pedidos = []
    
    def procesar_pedidos(self):
        datos = self.api.obtener_trabajos()

        if isinstance(datos, dict) and "data" in datos and isinstance(datos["data"], list):
            self.pedidos = []
            for i, pedido_data in enumerate(datos["data"]):
                pedido = Pedido(pedido_data)
                heapq.heappush(self.pedidos, (-pedido.priority, i, pedido))
            return True
        else:
            print("Error: Los datos de la API no tienen el formato esperado.")
            return False
    
    def obtener_siguiente_pedido(self) -> Pedido:
        if self.pedidos:
            prioridad, pedido = heapq.heappop(self.pedidos)
            return pedido
        return None

    def obtener_todos_los_pedidos(self) -> list[Pedido]:
        return [pedido for prioridad, indice, pedido in self.pedidos]