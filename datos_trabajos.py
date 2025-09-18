from datetime import datetime

class Pedido:
    from datetime import datetime

class Pedido:
    def __init__(self, datos):
        self.id = datos["id"]
        self.pickup = tuple(datos["pickup"])
        self.dropoff = tuple(datos["dropoff"])
        self.payout = datos["payout"]
        self.deadline_str = datos["deadline"]
        self.deadline = datetime.strptime(self.deadline_str, "%Y-%m-%dT%H:%M")
        self.weight = datos["weight"]
        self.priority = datos["priority"]
        self.release_time = datos["release_time"]

    def tiempo_restante(self, tiempo_actual):
        delta = self.deadline - tiempo_actual
        return max(int(delta.total_seconds() // 60), 0)

    def mostrar(self):
        print(f"[{self.id}] ${self.payout} | P:{self.priority} | W:{self.weight}")
        print(f"Pickup: {self.pickup} → Dropoff: {self.dropoff}")
        print(f"Deadline: {self.deadline_str} | Release: {self.release_time}s")