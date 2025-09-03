class Mapa:
    def __init__(self, datos):
        # Validar que los datos existan y tengan las claves necesarias
        if not datos:
            raise ValueError("No se recibieron datos para el mapa.")

        self.width = datos.get("width")
        self.height = datos.get("height")
        self.name = datos.get("name")
        self.goal = datos.get("goal")
        self.kills = datos.get("kills", [])
        self.grid = datos.get("map")

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