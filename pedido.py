from datetime import datetime

class Pedido:
    def __init__(self, id, payout, priority, pickup, dropoff, weight, deadline, release_time):
        self.id = id
        self.payout = payout
        self.priority = priority
        self.pickup = pickup
        self.dropoff = dropoff
        self.weight = weight

        # Convertir fechas ISO a segundos relativos desde el release_time
        formato = "%Y-%m-%dT%H:%M"
        try:
            release_dt = datetime.strptime(release_time, formato)
            deadline_dt = datetime.strptime(deadline, formato)
            self.release_time = 0
            self.deadline = (deadline_dt - release_dt).total_seconds()
        except Exception as e:
            print(f"Error al convertir fechas: {e}")
            self.release_time = 0
            self.deadline = 300  # valor por defecto: 5 minutos

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
                estado.modificar_reputacion(+10)
            else:
                estado.modificar_reputacion(-5)

            # Aplicar pago con bonus si corresponde
            pago_final = self.payout
            if estado.reputacion >= 90:
                pago_final *= 1.05
                print(f"Bonus aplicado: +5% → ${pago_final:.2f}")
            estado.recibir_pago(pago_final)