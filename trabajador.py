import pygame
import os
from inventario import Inventario
from estado_trabajador import EstadoTrabajador

class Trabajador:
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

    def es_transitable(self, rect, mapa):
      puntos = [
        rect.topleft,
        rect.topright,
        rect.bottomleft,
        rect.bottomright,
        rect.center,
        (rect.left + rect.width // 2, rect.top),      # borde superior
        (rect.left + rect.width // 2, rect.bottom),   # borde inferior
        (rect.left, rect.top + rect.height // 2),     # borde izquierdo
        (rect.right, rect.top + rect.height // 2),    # borde derecho
    ]
      for x, y in puntos:
            x_celda = int(x / self.cell_size)
            y_celda = int(y / self.cell_size)
            celda = mapa.obtener_celda(x_celda, y_celda)
            if celda in ['B', ' '] :  # edificio
               return False    
      return True


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

    def mover(self, keys, clima, dt, velocidad, mapa):
        movimiento = False
        movimiento_pixeles = velocidad * self.cell_size * dt
        nuevo_rect = self.trabajadorRect.copy()

        if self.estado.resistencia > 1:
            if keys == pygame.QUIT:
                return
            else:
                if keys==pygame.K_UP:
                    nuevo_rect.move_ip(0, -movimiento_pixeles)
                    if self.es_transitable(nuevo_rect, mapa):
                        self.trabajadorRect = nuevo_rect.copy()
                        movimiento = True

                if keys==pygame.K_DOWN:
                    nuevo_rect = self.trabajadorRect.copy()
                    nuevo_rect.move_ip(0, movimiento_pixeles)
                    if self.es_transitable(nuevo_rect, mapa):
                        self.trabajadorRect = nuevo_rect.copy()
                        movimiento = True

                if keys==pygame.K_LEFT:
                    nuevo_rect = self.trabajadorRect.copy()
                    nuevo_rect.move_ip(-movimiento_pixeles, 0)
                    if self.es_transitable(nuevo_rect, mapa):
                        self.trabajadorRect = nuevo_rect.copy()
                        movimiento = True

                if keys==pygame.K_RIGHT:
                    nuevo_rect = self.trabajadorRect.copy()
                    nuevo_rect.move_ip(movimiento_pixeles, 0)
                    if self.es_transitable(nuevo_rect, mapa):
                        self.trabajadorRect = nuevo_rect.copy()
                        movimiento = True

                if movimiento:
                    self.estado.consumir_resistencia(clima, self.inventario.peso_actual, dt)

        if not movimiento:
            self.estado.recuperar_resistencia(dt)

        self.trabajadorRect.clamp_ip((0, 0, self.mapa_width * self.cell_size, self.mapa_height * self.cell_size))

    def dibujar(self, pantalla):
        pantalla.blit(self.trabajador, self.trabajadorRect)