class Puntaje:
    def __init__(self, ingresos, bonos, penalizaciones, finalizado):
        self.ingresos = ingresos
        self.bonos = bonos
        self.penalizaciones = penalizaciones
        self.finalizado=finalizado
    
    def crear_diccionario(self):
        return self.__dict__