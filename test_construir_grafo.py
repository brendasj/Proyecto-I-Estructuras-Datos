#!/usr/bin/env python3
"""
Prueba de `construir_grafo` en `mapa.py`.

Uso:
    python .\test_construir_grafo.py

Este script crea un `Mapa` pequeño de ejemplo y un clima "dummy",
llama a `construir_grafo(mapa, clima)` y muestra/comprueba el resultado.
"""

from pprint import pprint

# intentamos importar la función de ambas maneras (módulo o método de clase)
from mapa import Mapa

class DummyClima:
    def __init__(self, estado='clear'):
        self.estado = estado


def main():
    datos = {
        "data": {
            "width": 5,
            "height": 5,
            "city_name": "TestCity",
            "goal": None,
            "kills": [],
            "tiles": [
                ["C", "C", "C", "C", "C"],
                ["C", "B", "B", "B", "C"],
                ["C", "C", "C", "B", "C"],
                ["C", "P", "C", "C", "C"],
                ["C", "C", "C", "C", "C"],
            ],
            "legend": {
                "C": {"surface_weight": 1.0},
                "P": {"surface_weight": 1.5},
                "B": {"surface_weight": float('inf')},
                " ": {"surface_weight": float('inf')},
            },
        }
    }

    mapa = Mapa(datos)
    clima = DummyClima('clear')

    # Importar el módulo y buscar la función al nivel de módulo
    import mapa as mapa_mod

    if hasattr(mapa_mod, "construir_grafo"):
        print("Invocando construir_grafo(mapa, clima) desde el módulo...")
        grafo = mapa_mod.construir_grafo(mapa, clima)
    else:
        print("La función 'construir_grafo' no está definida en el módulo 'mapa'.")
        print("Contenido disponible en el módulo:", sorted([n for n in dir(mapa_mod) if not n.startswith('_')]))
        raise AttributeError("'construir_grafo' no encontrada en el módulo 'mapa'")

    print("\nNodos en grafo:", len(grafo))

    # Mostrar las primeras entradas del grafo
    print("\nPrimeras 12 entradas del grafo (nodo -> vecinos):")
    for i, (n, vecinos) in enumerate(grafo.items()):
        if i >= 12:
            break
        print(n, "->", vecinos)

    # Comprobación simple: celdas 'B' (edificio) no deben aparecer como nodos
    matriz = mapa.obtener_matriz()
    altura, ancho = matriz.shape
    bloques = []
    for y in range(altura):
        for x in range(ancho):
            if matriz[y][x] == 'B':
                bloques.append((x, y))

    errores = []
    for b in bloques:
        if b in grafo:
            errores.append(b)

    if errores:
        print("\nERROR: las siguientes celdas marcadas como 'B' aparecen en el grafo:")
        pprint(errores)
        raise AssertionError("Celdas 'B' encontradas en grafo")
    else:
        print("\nComprobación: celdas 'B' NO están en el grafo — OK")


if __name__ == '__main__':
    main()
