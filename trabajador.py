import pygame
import os
from inventario import Inventario
from estado_trabajador import EstadoTrabajador
import copy
class Trabajador:
    contador = False

    def __init__(self, mapa_width, mapa_height, cell_size, peso_maximo=5, velocidad_estandar=3):
        self.mapa_width = mapa_width
        self.mapa_height = mapa_height
        self.cell_size = cell_size
        self.pedido_actual = None

        self.inventario = Inventario(peso_maximo)
        self.estado = EstadoTrabajador()
        self.entregados = []

        self.velocidad_estandar = velocidad_estandar

        self.trabajador_original = pygame.image.load(os.path.join("assets", "trabajador.png"))
        self.trabajador = pygame.transform.scale(self.trabajador_original, (30, 30))
        self.trabajadorRect = self.trabajador.get_rect()
        self.trabajadorRect.center = (mapa_width // 2 * cell_size, mapa_height // 2 * cell_size)

        self.movio = False  

    def es_transitable(self, rect, mapa):
        puntos = [
            rect.topleft, rect.topright, rect.bottomleft, rect.bottomright, rect.center,
            (rect.left + rect.width // 2, rect.top),
            (rect.left + rect.width // 2, rect.bottom),
            (rect.left, rect.top + rect.height // 2),
            (rect.right, rect.top + rect.height // 2),
        ]
        for x, y in puntos:
            x_celda = int(x / self.cell_size)
            y_celda = int(y / self.cell_size)
            celda = mapa.obtener_celda(x_celda, y_celda)
            if celda in ['B', ' '] :  # edificio
               return False    
        return True

    def obtener_estado(self):
        return {
            "pedido_actual": self.pedido_actual,
            "inventario": copy.deepcopy(self.inventario),
            "ingresos": self.estado.ingresos,
            "reputacion": self.estado.reputacion,
            "resistencia": self.estado.resistencia,
            "entregados": self.entregados.copy(),
            "trabajadorRect": self.trabajadorRect.copy()
        }

    def restaurar_estado(self, estado_guardado, entregados):
        self.pedido_actual = estado_guardado["pedido_actual"]
        self.inventario = copy.deepcopy(estado_guardado["inventario"])
        self.estado.ingresos = estado_guardado["ingresos"]
        self.estado.reputacion = estado_guardado["reputacion"]
        self.estado.resistencia = estado_guardado["resistencia"]
        self.entregados = entregados 
        self.trabajadorRect = estado_guardado["trabajadorRect"]


    def obtener_velocidad(self, clima, mapa):
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
            resistencia_velocidad = 0

        x = int(self.trabajadorRect.centerx / self.cell_size)
        y = int(self.trabajadorRect.centery / self.cell_size)
        celda_actual = mapa.obtener_celda(x, y)
        leyenda = mapa.legend.get(celda_actual)
        surface_weight = leyenda.get('surface_weight', 1.0) if isinstance(leyenda, dict) else 1.0

        velocidad = self.velocidad_estandar * clima_velocidad * peso_velocidad * reputacion_velocidad * resistencia_velocidad * surface_weight
        return velocidad

    def dibujar(self, pantalla):
        pantalla.blit(self.trabajador, self.trabajadorRect)

    def mover_una_celda(self, key, clima, dt, velocidad, mapa):
        self.movio = False 

        if self.estado.resistencia == 0:
            Trabajador.contador = True
            self.estado.recuperar_resistencia(dt)
            return
        elif self.estado.resistencia < 30 and Trabajador.contador:
            self.estado.recuperar_resistencia(dt)
            return
        else:
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