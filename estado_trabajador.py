import sys
class EstadoTrabajador:
    def __init__(self, meta_ingresos=1100):
        self.resistencia = 100
        self.reputacion = 70
        self.ingresos = 0
        self.meta = meta_ingresos
    
    def modificar_reputacion(self,cant):
        if self.reputacion < 100:
            self.reputacion += cant

    def consumir_resistencia(self, clima, peso_actual, dt):
        base = 0.5 * dt
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

        # 🔧 Forzar consumo mínimo si total es muy bajo
        if total < 0.05:
            total = 0.05

        self.resistencia = max(0, self.resistencia - total)

    def recuperar_resistencia(self, dt):
        if self.resistencia < 100:
            pendiente = (100 - self.resistencia) / 100
            recuperacion_rate = 0.1 + 0.2 * pendiente 
            incremento = recuperacion_rate * dt

            if self.resistencia >= 99.5:
                incremento = min(incremento, 0.1)

            self.resistencia += incremento
            self.resistencia = min(100, self.resistencia)

    def sumar_ingresos(self, cantidad):
        self.ingresos += cantidad

    def recibir_pago(self, cantidad):
        self.sumar_ingresos(cantidad)
        sys.stdout.reconfigure(encoding='utf-8')
        print(f"Pago recibido: ${cantidad:.2f} → Total acumulado: ${self.ingresos:.2f}")

    def meta_alcanzada(self):
        return self.ingresos >= self.meta

    def reputacion_critica(self):
        return self.reputacion < 20

    def mostrar_estado(self):
        print(f"Resistencia: {int(self.resistencia)}/100")
        print(f"Reputación: {int(self.reputacion)}/100")
        print(f"Ingresos: ${self.ingresos:.2f} / ${self.meta}")