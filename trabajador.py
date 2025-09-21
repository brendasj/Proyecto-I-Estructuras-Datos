import pygame
import os

class Trabajador:
    def __init__(self, mapa_width, mapa_height, cell_size=32):
        self.mapa_width = mapa_width
        self.mapa_height = mapa_height
        self.cell_size = cell_size

        self.resistencia = 100
        self.peso_total = 0

        self.trabajador_original = pygame.image.load(os.path.join("assets", "trabajador.png"))
        self.trabajador = pygame.transform.scale(self.trabajador_original, (100, 100))
        self.trabajadorRect = self.trabajador.get_rect()

        # Poner al trabajador en una posición inicial
        self.trabajadorRect.center = (mapa_width // 2 * cell_size, mapa_height // 2 * cell_size)

    def mover(self, keys, clima, dt):
        movimiento = False

        posicion_inicial = self.trabajadorRect.copy()

        if self.resistencia > 0:
            velocidad = 5

            # Movimiento vertical
            if keys[pygame.K_UP]:
                self.trabajadorRect.move_ip(0, -velocidad)
                movimiento = True
            if keys[pygame.K_DOWN]:
                self.trabajadorRect.move_ip(0, velocidad)
                movimiento = True
            
            # Movimiento horizontal
            if keys[pygame.K_LEFT]:
                self.trabajadorRect.move_ip(-velocidad, 0)
                movimiento = True
            if keys[pygame.K_RIGHT]:
                self.trabajadorRect.move_ip(velocidad, 0)
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
        if self.peso_total > 3:
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