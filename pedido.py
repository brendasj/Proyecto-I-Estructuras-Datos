from datetime import datetime, timezone

class Pedido:
    def __init__(self, id, payout, priority, pickup, dropoff, weight, deadline, release_time):
        self.id = id
        self.payout = payout
        self.priority = priority
        self.pickup = pickup
        self.dropoff = dropoff
        self.weight = weight

        try:
            if isinstance(deadline, str) and isinstance(release_time, (int, float)):
                deadline = deadline.strip().replace("Z", "+00:00")
                deadline_dt = datetime.fromisoformat(deadline)
                release_dt = datetime.fromtimestamp(release_time, tz=timezone.utc)
                self.deadline = (deadline_dt - release_dt).total_seconds()
                self.release_time = float(release_time)

            elif isinstance(deadline, (int, float)) and isinstance(release_time, (int, float)):
                self.deadline = float(deadline)
                self.release_time = float(release_time)

            elif isinstance(deadline, str) and isinstance(release_time, str):
                deadline = deadline.strip().replace("Z", "+00:00")
                release_time = release_time.strip().replace("Z", "+00:00")
                deadline_dt = datetime.fromisoformat(deadline)
                release_dt = datetime.fromisoformat(release_time)
                self.deadline = (deadline_dt - release_dt).total_seconds()
                self.release_time = 0

            else:
                raise ValueError("Formato de fecha no reconocido")

        except Exception as e:
            print(f"Error al convertir fechas: {e}")
            self.deadline = 300

        self.deadline_str = deadline[11:16] if isinstance(deadline, str) else "?"
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

    def verificar_interaccion(self, trabajador_rect, cell_size, inventario, estado, tiempo_juego):
        if not self.recogido and self.esta_cerca(trabajador_rect, self.pickup, cell_size):
            self.recogido = True
            print(f"Pedido {self.id} recogido")

        elif self.recogido and not self.entregado and self.esta_cerca(trabajador_rect, self.dropoff, cell_size):
            self.entregado = True
            print(f"Pedido {self.id} entregado")
            inventario.marcar_entregado(self)

            # Evaluar puntualidad con tiempo simulado
            if tiempo_juego <= self.deadline:
                estado.modificar_reputacion(10)
            else:
                estado.modificar_reputacion(-5)

            # Aplicar pago con bonus si corresponde
            pago_final = self.payout
            if estado.reputacion >= 90:
                pago_final *= 1.05
                print(f"Bonus aplicado: +5% → ${pago_final:.2f}")
            estado.recibir_pago(pago_final)