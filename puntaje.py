class Puntaje:
    def __init__(self, ingresos, bonos, penalizaciones):
        self.ingresos = ingresos
        self.bonos = bonos
        self.penalizaciones = penalizaciones
    
    def crear_diccionario(self):
        return self.__dict__