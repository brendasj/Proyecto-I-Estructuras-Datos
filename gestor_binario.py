import pickle
import os

class Gestor_Binarios:
    def __init__(self, nombre_archivo = "slot1.dat"):
        self.nombre_archivo = nombre_archivo
    
    def guardar_partida(self, trabajador, clima, pedidos):
        center_x = trabajador.trabajadorRect.centerx
        center_y = trabajador.trabajadorRect.centery

        columna = center_x // trabajador.cell_size 
        fila = center_y // trabajador.cell_size
        estado_juego = {
            'pos_x': fila, 
            'pos_y': columna,
            'center_x': center_x,
            'center_y': center_y,
            'cell_size': trabajador.cell_size,
            'resistencia': trabajador.estado.resistencia,
            'reputacion': trabajador.estado.reputacion,
            'clima_actual': clima.estado_actual if hasattr(clima, 'estado_actual') else None,
            'pedidos_activos': pedidos.pedidos_activos if hasattr(pedidos, 'pedidos_activos') else [],
            'ingresos': trabajador.estado.ingresos, 
        }
        
        with open(self.nombre_archivo, 'wb') as f:
            pickle.dump(estado_juego, f)
            return True
        return False
        
    def cargar_partida(self):
        if not os.path.exists(self.nombre_archivo):
            return None 
        with open(self.nombre_archivo, 'rb') as f:
                estado = pickle.load(f)
        if estado:
            return estado
        return None
