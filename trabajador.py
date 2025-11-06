"""Definición de la clase Trabajador y su comportamiento en pantalla.

Incluye movimiento, cálculo de velocidad y gestión del inventario.
"""

import copy
import random

import pygame

from estado_trabajador import EstadoTrabajador
from inventario import Inventario
from typing import Any


class Trabajador:
    """Representa a un trabajador (jugador o IA) en el mapa.

    Proporciona métodos para movimiento, renderizado y cálculo de velocidad
    teniendo en cuenta el clima y el peso del inventario.
    """

    contador = False

    def __init__(
        self,
        mapa_width: int,
        mapa_height: int,
        cell_size: int,
        peso_maximo: int = 5,
        velocidad_estandar: int = 3,
        ruta_imagen: str = "assets/trabajador.png",
    ) -> None:
        self.mapa_width = mapa_width
        self.mapa_height = mapa_height
        self.cell_size = cell_size
        self.pedido_actual = None

        self.inventario = Inventario(peso_maximo)
        self.estado = EstadoTrabajador()
        self.entregados = []

        self.velocidad_estandar = velocidad_estandar

        self.trabajador_original = pygame.image.load(ruta_imagen)
        self.trabajador = pygame.transform.scale(self.trabajador_original, (40, 40))
        self.trabajadorRect = self.trabajador.get_rect()
        self.trabajadorRect.center = (mapa_width // 2 * cell_size, mapa_height // 2 * cell_size)

        self.movio = False

    def es_transitable(self, rect: pygame.Rect, mapa: Any) -> bool:
        """Comprueba si el rect es transitables (no está dentro de un edificio)."""
        puntos = [
            rect.topleft,
            rect.topright,
            rect.bottomleft,
            rect.bottomright,
            rect.center,
            (rect.left + rect.width // 2, rect.top),
            (rect.left + rect.width // 2, rect.bottom),
            (rect.left, rect.top + rect.height // 2),
            (rect.right, rect.top + rect.height // 2),
        ]
        for x, y in puntos:
            x_celda = int(x / self.cell_size)
            y_celda = int(y / self.cell_size)
            celda = mapa.obtener_celda(x_celda, y_celda)
            if celda in ["B", " "]:
                return False
        return True

    def obtener_estado(self) -> dict:
        """Devuelve un dict serializable con el estado actual del trabajador."""
        return {
            "pedido_actual": self.pedido_actual,
            "inventario": copy.deepcopy(self.inventario),
            "ingresos": self.estado.ingresos,
            "reputacion": self.estado.reputacion,
            "resistencia": self.estado.resistencia,
            "entregados": self.entregados.copy(),
            "trabajadorRect": self.trabajadorRect.copy(),
        }

    def restaurar_estado(self, estado_guardado: dict, entregados: list) -> None:
        """Restaura el estado del trabajador desde un dict guardado."""
        self.pedido_actual = estado_guardado["pedido_actual"]
        self.inventario = copy.deepcopy(estado_guardado["inventario"])
        self.estado.ingresos = estado_guardado["ingresos"]
        self.estado.reputacion = estado_guardado["reputacion"]
        self.estado.resistencia = estado_guardado["resistencia"]
        self.entregados = entregados
        self.trabajadorRect = estado_guardado["trabajadorRect"]

    def obtener_velocidad(self, clima: Any, mapa: Any) -> float:
        """Calcula la velocidad actual teniendo en cuenta varios modificadores."""
        efecto_clima = clima.efecto_trabajador()
        clima_velocidad = efecto_clima.get("velocidad", 1.0)
        peso_velocidad = max(0.8, 1 - 0.03 * self.inventario.peso_actual)
        reputacion_velocidad = 1.03 if self.estado.reputacion >= 90 else 1.0

        resistencia = self.estado.resistencia
        if resistencia > 30:
            resistencia_velocidad = 1.0
        elif 10 <= resistencia <= 30:
            resistencia_velocidad = 0.8
        else:
            resistencia_velocidad = 0.0

        x = int(self.trabajadorRect.centerx / self.cell_size)
        y = int(self.trabajadorRect.centery / self.cell_size)
        celda_actual = mapa.obtener_celda(x, y)
        leyenda = mapa.legend.get(celda_actual)
        surface_weight = leyenda.get("surface_weight", 1.0) if isinstance(leyenda, dict) else 1.0

        velocidad = (
            self.velocidad_estandar
            * clima_velocidad
            * peso_velocidad
            * reputacion_velocidad
            * resistencia_velocidad
            * surface_weight
        )
        return velocidad

    def dibujar(self, pantalla: pygame.Surface) -> None:
        """Dibuja el trabajador en la superficie dada."""
        pantalla.blit(self.trabajador, self.trabajadorRect)

    def mover_una_celda(self, key: int, clima: Any, dt: float, velocidad: float, mapa: Any) -> None:
        """Mueve al trabajador una celda en la dirección indicada si es posible."""
        self.movio = False

        if self.estado.resistencia == 0:
            Trabajador.contador = True
            self.estado.recuperar_resistencia(dt)
            return
        if self.estado.resistencia < 30 and Trabajador.contador:
            self.estado.recuperar_resistencia(dt)
            return

        Trabajador.contador = False
        dx, dy = 0, 0

        if key == pygame.K_UP:
            dy = -1
            self.movio = True
        elif key == pygame.K_DOWN:
            dy = 1
            self.movio = True
        elif key == pygame.K_LEFT:
            dx = -1
            self.movio = True
        elif key == pygame.K_RIGHT:
            dx = 1
            self.movio = True

        nuevo_rect = self.trabajadorRect.copy()
        nuevo_rect.move_ip(dx * self.cell_size, dy * self.cell_size)

        if self.es_transitable(nuevo_rect, mapa):
            self.trabajadorRect = nuevo_rect
            self.estado.consumir_resistencia(clima, self.inventario.peso_actual, dt)
        else:
            self.movio = False

        self.trabajadorRect.clamp_ip((0, 0, self.mapa_width * self.cell_size, self.mapa_height * self.cell_size))

        if not self.movio:
            self.estado.recuperar_resistencia(dt)

    def nivel_facil_ia(self, clima: Any, dt: float, mapa: Any, pedidos: Any) -> None:
        """Comportamiento simple de IA: movimiento aleatorio y aceptación ocasional de pedidos.

        Este método intenta moverse en una dirección transitables y, con pequeña
        probabilidad, acepta pedidos aleatorios.
        """

        if pedidos.pedidos and random.random() < 0.09:
            pedido_aleatorio = random.choice(pedidos.obtener_todos_los_pedidos())
            if self.inventario.agregar_pedido(pedido_aleatorio):
                pedidos.aceptar_pedido()

        direcciones = [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]
        random.shuffle(direcciones)

        for tecla in direcciones:
            prueba_rect = self.trabajadorRect.copy()
            dx, dy = 0, 0

            if tecla == pygame.K_UP:
                dy = -1
            elif tecla == pygame.K_DOWN:
                dy = 1
            elif tecla == pygame.K_LEFT:
                dx = -1
            elif tecla == pygame.K_RIGHT:
                dx = 1

            prueba_rect.move_ip(dx * self.cell_size, dy * self.cell_size)

            if self.es_transitable(prueba_rect, mapa):
                self.mover_una_celda(tecla, clima, dt, self.obtener_velocidad(clima, mapa), mapa)
                break

        if not self.movio:
            self.estado.recuperar_resistencia(dt)
