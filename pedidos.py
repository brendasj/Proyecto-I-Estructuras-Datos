import heapq
from api_client import ApiClient
from pedido import Pedido

class Pedidos:
    def __init__(self, api_client: ApiClient):
        self.api = api_client
        self.pedidos = []
        self.pedidos_aceptados = []
    
    def procesar_pedidos(self):
        datos = self.api.obtener_trabajos()

        if isinstance(datos, dict) and "data" in datos and isinstance(datos["data"], list):
            self.pedidos = []
            for i, pedido_data in enumerate(datos["data"]):
                pedido = Pedido(
                    id = pedido_data["id"],
                    payout = pedido_data["payout"],
                    priority = pedido_data["priority"],
                    pickup = tuple(pedido_data["pickup"]),
                    dropoff = tuple(pedido_data["dropoff"]),
                    weight = pedido_data["weight"],
                    deadline = pedido_data["deadline"],
                    release_time = pedido_data["release_time"]
                )
                heapq.heappush(self.pedidos, (-pedido.priority, i, pedido))
            return True
        else:
            print("Error: Los datos de la API no tienen el formato esperado.")
            return False
    
    def obtener_siguiente_pedido(self) -> Pedido:
        if self.pedidos:
            _, _, pedido = self.pedidos[0]
            return pedido
        return None

    def obtener_todos_los_pedidos(self) -> list[Pedido]:
        return [pedido for _, _, pedido in self.pedidos]
    
    def cantidad_pedidos(self, sum = 0):
        for i in self.pedidos:
            sum += 1
        return sum
    
    def aceptar_pedido(self) -> Pedido:
        if self.pedidos:
            _, _, pedido = heapq.heappop(self.pedidos)
            self.pedidos_aceptados.append(pedido)
            return pedido
        return None

    def rechazar_pedido(self) -> Pedido:
        if self.pedidos:
            _, _, pedido = heapq.heappop(self.pedidos)
            print(f"Pedido {pedido.id} rechazado")
            return pedido
        return None