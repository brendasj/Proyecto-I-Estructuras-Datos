import pygame
import os

class Trabajador:
    def __init__(self, mapa_width, mapa_height, cell_size=32):
        self.mapa_width = mapa_width
        self.mapa_height = mapa_height
        self.cell_size = cell_size

        self.trabajador_original = pygame.image.load(os.path.join("Proyecto-I-Estructuras-Datos", "assets", "trabajador.png"))
        self.trabajador = pygame.transform.scale(self.trabajador_original, (100, 100))
        self.trabajadorRect = self.trabajador.get_rect()

        # Poner al trabajador en una posición inicial
        self.trabajadorRect.center = (mapa_width // 2 * cell_size, mapa_height // 2 * cell_size)

    def mover(self, keys):
        velocidad = 5

        # Movimiento vertical
        if keys[pygame.K_UP]:
            self.trabajadorRect.move_ip(0, -velocidad)
        if keys[pygame.K_DOWN]:
            self.trabajadorRect.move_ip(0, velocidad)
        
        # Movimiento horizontal
        if keys[pygame.K_LEFT]:
            self.trabajadorRect.move_ip(-velocidad, 0)
        if keys[pygame.K_RIGHT]:
            self.trabajadorRect.move_ip(velocidad, 0)

        # Limitar al trabajador a los bordes del mapa
        self.trabajadorRect.clamp_ip(
            (0, 0, self.mapa_width * self.cell_size, self.mapa_height * self.cell_size)
        )

    def dibujar(self, pantalla):
        # Dibuja el trabajador en la pantalla
        pantalla.blit(self.trabajador, self.trabajadorRect)