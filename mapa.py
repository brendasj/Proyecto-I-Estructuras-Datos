"""Representación y utilidades del mapa del juego."""

import numpy as np
from typing import Any, List


class Mapa:
    """Clase que encapsula los datos y operaciones sobre el mapa.

    Recibe el JSON devuelto por la API y expone métodos para obtener
    celdas y matrices listas para dibujar.
    """

    def __init__(self, datos: dict) -> None:
        # Validar que los datos existan y tengan las claves necesarias
        if not datos or not isinstance(datos, dict) or "data" not in datos:
            raise ValueError("No se recibieron datos válidos para el mapa.")

        data = datos["data"]

        self.width = data.get("width")
        self.height = data.get("height")
        self.name = data.get("city_name", "Ciudad")
        self.goal = data.get("goal")
        self.kills = data.get("kills", [])
        self.grid = data.get("tiles")
        self.legend = data.get("legend", {})

        self.grid = self.procesar_cuadricula()

        # Validaciones adicionales
        if self.width is None or self.height is None:
            raise ValueError("El mapa no tiene dimensiones válidas (width/height).")

        if not isinstance(self.grid, list) or len(self.grid) != self.height:
            raise ValueError("La estructura del mapa no coincide con las dimensiones.")

        print(f"Mapa cargado: {self.name} ({self.width}x{self.height}) con objetivo {self.goal}")

    def obtener_celda(self, x: int, y: int) -> Any:
        """Devuelve el contenido de la celda en coordenadas (x, y) o None si está fuera."""
        if 0 <= y < self.height and 0 <= x < self.width:
            return self.grid[y][x]
        return None

    def mostrar_resumen(self) -> None:
        """Imprime un resumen informativo del mapa en la salida estándar."""
        print(f"Mapa: {self.name}")
        print(f"Dimensiones: {self.width}x{self.height}")
        print(f"Objetivo: {self.goal}")
        print(f"Enemigos: {', '.join(self.kills)}")

    def obtener_matriz(self) -> np.ndarray:
        """Normaliza `self.grid` y devuelve una matriz numpy de dimensiones (height, width)."""
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
                # Si no, hay que ajustar
                if len(grid_flat) >= width * height:
                    matriz = np.array(grid_flat[: width * height]).reshape(height, width)
                else:
                    grid_completo = grid_flat + [" "] * (width * height - len(grid_flat))
                    matriz = np.array(grid_completo).reshape(height, width)

        # Ahora la cadena string la hace lista de caracteres
        elif isinstance(grid_flat, str):
            if len(grid_flat) == width * height:
                matriz = np.array(list(grid_flat)).reshape(height, width)
            else:
                if len(grid_flat) >= width * height:
                    grid_cortados = grid_flat[: width * height]
                    matriz = np.array(list(grid_cortados)).reshape(height, width)
                else:
                    grid_completo = grid_flat + " " * (width * height - len(grid_flat))
                    matriz = np.array(list(grid_completo)).reshape(height, width)

        return matriz

    def procesar_cuadricula(self) -> List[List[str]]:
        """Detecta bloques de edificios rectangulares y los marca como `B_(wxh)`.

        Devuelve la nueva cuadrícula procesada.
        """
        nueva_cuadricula = [fila[:] for fila in self.grid]
        visitado = [[False for _ in range(self.width)] for _ in range(self.height)]

        for y in range(self.height):
            for x in range(self.width):
                if nueva_cuadricula[y][x] == "B" and not visitado[y][x]:
                    # Encontramos la esquina superior izquierda de un bloque de edificios

                    # Encontrar el ancho del bloque
                    ancho_bloque = 0
                    while (
                        x + ancho_bloque < self.width
                        and nueva_cuadricula[y][x + ancho_bloque] == "B"
                        and not visitado[y][x + ancho_bloque]
                    ):
                        ancho_bloque += 1

                    # Encontrar el alto del bloque
                    alto_bloque = 0
                    while (
                        y + alto_bloque < self.height
                        and nueva_cuadricula[y + alto_bloque][x] == "B"
                        and not visitado[y + alto_bloque][x]
                    ):
                        alto_bloque += 1

                    # Verificar si es un bloque rectangular válido
                    es_rectangulo = True
                    for i in range(alto_bloque):
                        for j in range(ancho_bloque):
                            if (
                                nueva_cuadricula[y + i][x + j] != "B"
                                or visitado[y + i][x + j]
                            ):
                                es_rectangulo = False
                                break
                        if not es_rectangulo:
                            break

                    if es_rectangulo:
                        # Marcar el bloque
                        nueva_cuadricula[y][x] = f"B_({ancho_bloque}x{alto_bloque})"
                        for i in range(alto_bloque):
                            for j in range(ancho_bloque):
                                visitado[y + i][x + j] = True
                                if i != 0 or j != 0:
                                    nueva_cuadricula[y + i][x + j] = " "
        return nueva_cuadricula
