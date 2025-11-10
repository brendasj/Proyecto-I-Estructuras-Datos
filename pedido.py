from datetime import datetime, timezone


class Pedido:
    def __init__(
        self,
        id,
        payout,
        priority,
        pickup,
        dropoff,
        weight,
        deadline,
        release_time,
    ):
        self.id = id
        self.payout = payout
        self.priority = priority
        self.pickup = pickup
        self.dropoff = dropoff
        self.weight = weight

        # Normalizaremos el deadline como segundos restantes desde el inicio
        # del juego (tiempo 0). Para ello calculamos el tiempo restante en
        # segundos respecto al momento actual (UTC). Si la API ya entrega
        # un número de segundos lo consideramos como tiempo restante.
        try:
            now_utc = datetime.now(timezone.utc)

            if isinstance(deadline, str):
                # ISO string: convertir a datetime aware y calcular resto
                raw = deadline.strip().replace("Z", "+00:00")
                deadline_dt = datetime.fromisoformat(raw)
                remaining = (deadline_dt - now_utc).total_seconds()
                self.release_time = (
                    float(release_time)
                    if isinstance(release_time, (int, float))
                    else 0.0
                )

            elif isinstance(deadline, (int, float)):
                # ya es un número de segundos (tiempo restante)
                remaining = float(deadline)
                self.release_time = float(release_time) if isinstance(release_time, (int, float)) else 0.0

            else:
                raise ValueError("Formato de deadline no reconocido")

            # Nunca guardar valores negativos: si ya pasó la hora, lo marcamos 0
            self.deadline = max(0.0, remaining)

        except Exception as e:
            print(f"Error al convertir fechas del pedido {id}: {e}")
            # valor por defecto: 5 minutos
            self.deadline = 300.0
            self.release_time = 0.0

        # Cadena para mostrar (HH:MM) si se pasó un ISO original
        try:
            self.deadline_str = (
                raw[11:16] if isinstance(deadline, str) and len(raw) >= 16 else "?"
            )
        except NameError:
            self.deadline_str = "?"

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