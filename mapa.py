import numpy as np

class Mapa:
    def __init__(self, datos):
        # Validar que los datos existan y tengan las claves necesarias
        if not datos or not isinstance(datos, dict) or 'data' not in datos:
            raise ValueError("No se recibieron datos válidos para el mapa.")

        data = datos['data']
      
        self.width = data.get('width')
        self.height = data.get('height')
        self.name = data.get('city_name', 'Ciudad')
        self.goal = data.get('goal')
        self.kills = data.get('kills', [])
        self.grid = data.get('tiles')
        self.legend = data.get('legend', {})

        # Validaciones adicionales
        if self.width is None or self.height is None:
            raise ValueError("El mapa no tiene dimensiones válidas (width/height).")

        if not isinstance(self.grid, list) or len(self.grid) != self.height:
            raise ValueError("La estructura del mapa no coincide con las dimensiones.")

        print(f"Mapa cargado: {self.name} ({self.width}x{self.height}) con objetivo {self.goal}")

    def obtener_celda(self, x, y):
        if 0 <= y < self.height and 0 <= x < self.width:
            return self.grid[y][x]
        else:
            return None

    def mostrar_resumen(self):
        print(f"Mapa: {self.name}")
        print(f"Dimensiones: {self.width}x{self.height}")
        print(f"Objetivo: {self.goal}")
        print(f"Enemigos: {', '.join(self.kills)}")

    def obtener_matriz(self):
        grid = self.grid
        width = self.width
        height = self.height

        # Aplanar la lista de listas de strings a una lista simple de strings
        if isinstance(grid, list) and all(isinstance(sublist, list) for sublist in grid):
            grid_flat = [item for sublist in grid for item in sublist]
        else:
            grid_flat = grid
            
        # Convertir a matriz
        if isinstance(grid_flat, list):
            # Buscar el tamaño correcto
            if len(grid_flat) == width * height:
                matriz = np.array(grid_flat).reshape(height, width)
            else:
                #Si no, hay que ajustar
                if len(grid_flat) >= width * height:
                    matriz = np.array(grid_flat[:width*height]).reshape(height, width)
                else:
                    grid_completo = grid_flat + [' '] * (width * height - len(grid_flat))
                    matriz = np.array(grid_completo).reshape(height, width)
        
        # Ahora la cadena string la hace lista de caracteres
        elif isinstance(grid_flat, str):
            if len(grid_flat) == width * height:
                matriz = np.array(list(grid_flat)).reshape(height, width)
            else:
                if len(grid_flat) >= width * height:
                    grid_cortados = grid_flat[:width*height]
                    matriz = np.array(list(grid_cortados)).reshape(height, width)
                else:
                    grid_completo = grid_flat + ' ' * (width * height - len(grid_flat))
                    matriz = np.array(list(grid_completo)).reshape(height, width)

        return matriz

