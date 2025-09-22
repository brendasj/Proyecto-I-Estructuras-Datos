import pygame
import os
from inventario import Inventario

class Trabajador:
    def __init__(self, mapa_width, mapa_height, cell_size=32, peso_maximo = 10, velocidad_estandar = 3):
        self.mapa_width = mapa_width
        self.mapa_height = mapa_height
        self.cell_size = cell_size

        self.resistencia = 100
        self.reputacion = 70
        self.inventario = Inventario(peso_maximo)

        self.velocidad_estandar = velocidad_estandar

        self.trabajador_original = pygame.image.load(os.path.join("assets", "trabajador.png"))
        self.trabajador = pygame.transform.scale(self.trabajador_original, (80, 80))
        self.trabajadorRect = self.trabajador.get_rect()

        # Poner al trabajador en una posición inicial
        self.trabajadorRect.center = (mapa_width // 2 * cell_size, mapa_height // 2 * cell_size)

    def esta_en_parque(self, mapa):
        esquinas = [
            (self.trabajadorRect.topleft[0], self.trabajadorRect.topleft[1]),
            (self.trabajadorRect.topright[0], self.trabajadorRect.topright[1]),
            (self.trabajadorRect.bottomleft[0], self.trabajadorRect.bottomleft[1]),
            (self.trabajadorRect.bottomright[0], self.trabajadorRect.bottomright[1]),
        ]

        for x, y in esquinas:
            x_celda = int(x / self.cell_size)
            y_celda = int(y / self.cell_size)
        
            celda_actual = mapa.obtener_celda(x_celda, y_celda)

            if celda_actual == 'P':
                return True
        return False

    def obtener_velocidad(self, clima, mapa):
        efecto_clima = clima.efecto_trabajador()
        clima_velocidad = efecto_clima.get("velocidad", 1.0)

        peso_velocidad = max(0.8, 1-0.03 * self.inventario.peso_actual)

        reputacion_velocidad = 1.03 if self.reputacion >= 90 else 1.0

        if self.resistencia > 30:
            resistencia_velocidad = 1.0
        elif 10 <= self.resistencia <= 30:
            resistencia_velocidad = 0.8
        else:
            resistencia_velocidad = 0

        if self.esta_en_parque(mapa):
            surface_weight = 0.95
        else:
            x = int(self.trabajadorRect.centerx / self.cell_size)
            y = int(self.trabajadorRect.centery / self.cell_size)
            celda_actual = mapa.obtener_celda(x, y)

            leyenda_celda = mapa.legend.get(celda_actual)

            if leyenda_celda and isinstance(leyenda_celda, dict):
                surface_weight = leyenda_celda.get('surface_weight', 1.0)
            else:
                surface_weight = 1.0

        velocidad = self.velocidad_estandar * clima_velocidad * peso_velocidad * reputacion_velocidad * resistencia_velocidad * surface_weight
        return velocidad

    def mover(self, keys, clima, dt, velocidad):
        movimiento = False

        posicion_inicial = self.trabajadorRect.copy()

        if self.resistencia > 0:
            movimiento_pixeles = velocidad * self.cell_size * dt

            # Movimiento vertical
            if keys[pygame.K_UP]:
                self.trabajadorRect.move_ip(0, -movimiento_pixeles)
                movimiento = True
            if keys[pygame.K_DOWN]:
                self.trabajadorRect.move_ip(0, movimiento_pixeles)
                movimiento = True
            
            # Movimiento horizontal
            if keys[pygame.K_LEFT]:
                self.trabajadorRect.move_ip(-movimiento_pixeles, 0)
                movimiento = True
            if keys[pygame.K_RIGHT]:
                self.trabajadorRect.move_ip(movimiento_pixeles, 0)
                movimiento = True
        
            if posicion_inicial != self.trabajadorRect:
                movimiento = True
                self.calculo_resistencia(clima, dt)
        
        if not movimiento:
            self.recuperar_resistencia(dt)

        # Limitar al trabajador a los bordes del mapa
        self.trabajadorRect.clamp_ip(
            (0, 0, self.mapa_width * self.cell_size, self.mapa_height * self.cell_size)
        )
        
    
    def calculo_resistencia(self, clima, dt):
        base = 0.5 * dt

        peso = 0
        if self.inventario.peso_actual > 3:
            peso = 0.2 * dt
        
        efecto_clima = {
            "lluvia" : 0.1,
            "viento" : 0.1,
            "tormenta" : 0.3,
            "calor_extremo" : 0.2,
            "soleado" : 0
        }
            
        clima = efecto_clima.get(clima.estado.lower, 0.0) * dt
        self.resistencia -= (base + peso + clima)

        if self.resistencia < 0:
            self.resistencia = 0
        
    def recuperar_resistencia(self, tiempo):
        recuperacion_rate = 5
        self.resistencia += recuperacion_rate * tiempo

        if self.resistencia > 100:
            self.resistencia = 100

    def dibujar(self, pantalla):
        # Dibuja el trabajador en la pantalla
        pantalla.blit(self.trabajador, self.trabajadorRect)