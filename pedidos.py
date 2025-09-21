from api_client import ApiClient
from pedido import Pedido

class Pedidos:
    def __init__(self, api_client: ApiClient):
        self.api = api_client
        self.pedidos_dict = {}
    
    def procesar_pedidos(self):
        datos = self.api.obtener_trabajos()

        if isinstance(datos, dict) and "data" in datos and isinstance(datos["data"], list):
            self.pedidos_dict = {}
            for pedido_data in datos["data"]:
                pedido = Pedido(pedido_data)
                self.pedidos_dict[pedido.id] = pedido
            return True
        else:
            print("Error: Los datos de la API no tienen el formato esperado.")
            return False
    
    def obtener_pedido_por_id(self, pedido_id: str) -> Pedido:
        return self.pedidos_dict.get(pedido_id)

    def obtener_todos_los_pedidos(self) -> list[Pedido]:
        return list(self.pedidos_dict.values())