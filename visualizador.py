import pygame
import os

class Visualizador:
    def __init__(self, mapa, cell_size=32):
        pygame.init()
        self.mapa = mapa
        self.cell_size = cell_size

        # Usamos los atributos correctos del mapa
        self.screen = pygame.display.set_mode((mapa.width * cell_size, mapa.height * cell_size))
        pygame.display.set_caption(f"Mapa de {mapa.name}")

        # Cargar imágenes desde la carpeta assets
        self.sprites = {
            'C': pygame.image.load(os.path.join("assets", "calle.png")),
            'B': pygame.image.load(os.path.join("assets", "edificio.png")),
            'P': pygame.image.load(os.path.join("assets", "parque.png"))
        }

    def dibujar(self):
        matriz = self.mapa.obtener_matriz()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Dibujar cada celda del mapa
            for y, fila in enumerate(matriz):
                for x, celda in enumerate(fila):
                    sprite = self.sprites.get(celda)
                    if sprite:
                        self.screen.blit(sprite, (x * self.cell_size, y * self.cell_size))

            pygame.display.flip()

        pygame.quit()