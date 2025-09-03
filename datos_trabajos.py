class Trabajo:
    def __init__(self, datos):
        self.nombre = datos.get("name")
        self.descripcion = datos.get("description")
        self.recompensa = datos.get("reward")

    def mostrar(self):
        print(f"Trabajo: {self.nombre} - {self.descripcion} (${self.recompensa})")

    def mostrar(self):
        if self.nombre:
         print(f"Trabajo: {self.nombre} - {self.descripcion} (${self.recompensa})")
        else:
         print("Trabajo inválido o sin nombre.")