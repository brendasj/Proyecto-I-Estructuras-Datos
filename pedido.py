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

        # Sistema de tiempo relativo: cada pedido tiene 90 segundos (1.5 minutos)
        # para ser entregado desde su release_time
        try:
            # Convertir release_time a float
            self.release_time = (
                float(release_time)
                if isinstance(release_time, (int, float))
                else 0.0
            )
            
            # Tiempo de entrega: 90 segundos desde release_time
            TIEMPO_ENTREGA_ESTANDAR = 90.0
            self.deadline = self.release_time + TIEMPO_ENTREGA_ESTANDAR
            
        except Exception as e:
            print(f"Error al procesar tiempos del pedido {id}: {e}")
            # valores por defecto
            self.release_time = 0.0
            self.deadline = 90.0

        # Cadena para mostrar el tiempo límite en formato MM:SS
        try:
            tiempo_limite_minutos = int(self.deadline // 60)
            tiempo_limite_segundos = int(self.deadline % 60)
            self.deadline_str = f"{tiempo_limite_minutos:02d}:{tiempo_limite_segundos:02d}"
        except Exception:
            self.deadline_str = "01:30"

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
                # Entrega puntual: aumenta reputación
                estado.modificar_reputacion(5)
                tiempo_restante = self.deadline - tiempo_juego
                print(f"¡Entrega puntual! +5 reputación (sobró {tiempo_restante:.1f}s) → {estado.reputacion}/100")
            else:
                # Entrega tardía: reduce reputación
                estado.modificar_reputacion(-10)
                tiempo_excedido = tiempo_juego - self.deadline
                print(f"Entrega tardía -10 reputación (tardó {tiempo_excedido:.1f}s extra) → {estado.reputacion}/100")

            # Aplicar pago con bonus si corresponde
            pago_final = self.payout
            if estado.reputacion >= 90:
                pago_final *= 1.05
                print(f"Bonus aplicado: +5% → ${pago_final:.2f}")
            estado.recibir_pago(pago_final)