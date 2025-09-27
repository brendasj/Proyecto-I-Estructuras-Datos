class Pedido:
    def __init__(self, id, payout, priority, pickup, dropoff, weight, deadline, release_time):
        self.id = id
        self.payout = payout
        self.priority = priority
        self.pickup = pickup
        self.dropoff = dropoff
        self.weight = weight
        self.deadline = deadline  # formato ISO: "2025-09-01T12:10"
        self.release_time = release_time

        # Derivado para mostrar solo la hora
        self.deadline_str = deadline[11:] if isinstance(deadline, str) else "?"

        self.recogido = False
        self.entregado = False

    def esta_cerca(self, trabajador_rect, celda, cell_size, tolerancia=60):
        centro_trabajador = trabajador_rect.center
        centro_celda = (
            celda[0] * cell_size + cell_size // 2,
            celda[1] * cell_size + cell_size // 2
        )
        distancia = ((centro_trabajador[0] - centro_celda[0]) ** 2 +
                     (centro_trabajador[1] - centro_celda[1]) ** 2) ** 0.5
        return distancia <= tolerancia

    def verificar_interaccion(self, trabajador_rect, cell_size, inventario):
        if not self.recogido and self.esta_cerca(trabajador_rect, self.pickup, cell_size):
            self.recogido = True
            print(f"Pedido {self.id} recogido")

        elif self.recogido and not self.entregado and self.esta_cerca(trabajador_rect, self.dropoff, cell_size):
            self.entregado = True
            print(f"Pedido {self.id} entregado")
            inventario.marcar_entregado(self)