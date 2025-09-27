class EstadoTrabajador:
    def __init__(self, meta_ingresos=1500):
        self.resistencia = 100
        self.reputacion = 70
        self.ingresos = 0
        self.meta = meta_ingresos

    def consumir_resistencia(self, clima, peso_actual, dt):
        base = 1.5 * dt
        peso = 0.03 * dt if peso_actual > 3 else 0

        efecto_clima = {
            "lluvia": 0.05,
            "viento": 0.03,
            "tormenta": 0.08,
            "calor_extremo": 0.06,
            "soleado": 0.0
        }

        estado_clima = clima.estado.lower() if isinstance(clima.estado, str) else "desconocido"
        clima_factor = efecto_clima.get(estado_clima, 0.0) * dt

        total = base + peso + clima_factor
        self.resistencia = max(0, self.resistencia - total)

    def recuperar_resistencia(self, dt):
        recuperacion_rate = 0.5
        if self.resistencia < 100:
            self.resistencia += recuperacion_rate * dt
            self.resistencia = min(100, self.resistencia)

    def modificar_reputacion(self, cantidad):
        self.reputacion = max(0, min(100, self.reputacion + cantidad))

    def sumar_ingresos(self, cantidad):
        self.ingresos += cantidad

    def meta_alcanzada(self):
        return self.ingresos >= self.meta

    def reputacion_critica(self):
        return self.reputacion < 20

    def mostrar_estado(self):
        print(f"Resistencia: {int(self.resistencia)}/100")
        print(f"Reputación: {int(self.reputacion)}/100")
        print(f"Ingresos: ${self.ingresos:.2f} / ${self.meta}")