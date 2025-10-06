import json 
import os

class Puntajes:
    def __init__(self, nombreArchivo = "puntajes.json"):
        self.nombreArchivo = nombreArchivo
        self.datos = self._cargar()
    
    def _cargar(self):
        if os.path.exists(self.nombreArchivo):
            with open(self.nombreArchivo, "r", encoding="utf-8") as f:
                return json.load(f)
        return []
    
    def _guardar(self): 
        with open(self.nombreArchivo, "w", encoding="utf-8") as f:
                json.dump(self.datos, f, ensure_ascii=False, indent=4)
    
    def agregar(self, nuevo_Puntaje):
        self.datos.append(nuevo_Puntaje.crear_diccionario())
        with open(self.nombreArchivo, "w", encoding="utf-8") as f:
                json.dump(self.datos, f, ensure_ascii=False, indent=4)

    def actualizar(self, indice, nuevo_Puntaje):
        if 0 <= indice < len(self.datos):
            self.datos[indice] = nuevo_Puntaje.crear_diccionario()
            self._guardar()
            return True
        return False
        
    @property
    def datos_cargados(self):
        return self.datos