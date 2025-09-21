from datetime import datetime

class Pedido:
    def __init__(self, datos):
        self.id = datos.get("id")
        self.pickup = tuple(datos.get("pickup", ()))
        self.dropoff = tuple(datos.get("dropoff", ()))
        self.payout = datos.get("payout", 0)
        self.deadline_str = datos.get("deadline", "")
        self.weight = datos.get("weight", 0)
        self.priority = datos.get("priority", 0)
        self.release_time = datos.get("release_time", 0)

        try:
            self.deadline = datetime.strptime(self.deadline_str, "%Y-%m-%dT%H:%M")
        except (ValueError, TypeError):
            self.deadline = None
    
    def tiempo_restante(self, tiempo_actual):
        delta = self.deadline - tiempo_actual
        return max(int(delta.total_seconds() // 60), 0)

    def mostrar(self):
        print(f"[{self.id}] ${self.payout} | P:{self.priority} | W:{self.weight}")
        print(f"Pickup: {self.pickup} → Dropoff: {self.dropoff}")
        print(f"Deadline: {self.deadline_str} | Release: {self.release_time}s")