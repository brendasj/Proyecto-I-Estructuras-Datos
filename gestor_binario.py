import pickle
import os

class Gestor_Binarios:
    def __init__(self, nombre_archivo = "slot1.dat"):
        self.nombre_archivo = nombre_archivo
    
    def guardar_partida(self, trabajador, clima, pedidos, pedidos_tratados_cuenta, bono, penalizaciones_total):
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
            'clima_actual': clima.estado if hasattr(clima, 'estado') else None,
            'pedidos_activos': pedidos.pedidos_activos if hasattr(pedidos, 'pedidos_activos') else [],
            'ingresos': trabajador.estado.ingresos, 

            'pedidos_pendientes': pedidos.pedidos,
            'inventario_completo': trabajador.inventario,
            'pedidos_tratados_cuenta': pedidos_tratados_cuenta,
            'bono_acumulado': bono,
            'penalizaciones_acumuladas': penalizaciones_total,
        }
        
        with open(self.nombre_archivo, 'wb') as f:
            pickle.dump(estado_juego, f)
            return True
        return False
        
    def cargar_partida(self):
        if not os.path.exists(self.nombre_archivo):
            return None 
        try:
            with open(self.nombre_archivo, 'rb') as f:
                    estado = pickle.load(f)
            if estado:
                return estado
        except Exception as e:
            print(f"Error al cargar la partida binaria: {e}. El archivo puede estar corrupto o no existir.")
            return None
