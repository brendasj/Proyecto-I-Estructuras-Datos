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

        self.sprites_base = {
            'C': pygame.image.load(os.path.join("Proyecto-I-Estructuras-Datos", "assets", "calle.png")),
            'B': pygame.image.load(os.path.join("Proyecto-I-Estructuras-Datos", "assets", "edificio.png")),
            'P': pygame.image.load(os.path.join("Proyecto-I-Estructuras-Datos", "assets", "parque.png"))
        }

        self.sprites_grandes = {}

    def dibujar(self):
        matriz = self.mapa.obtener_matriz()
        
        for y, fila in enumerate(matriz):
            for x, celda in enumerate(fila):
                if celda == 'C' or celda == 'P':
                    sprite = self.sprites_base.get(celda)
                    self.screen.blit(sprite, (x * self.cell_size, y * self.cell_size))
                elif celda.startswith('B_('):
                    if celda not in self.sprites_grandes:
                        partes = celda.replace(')', '').split('(')[1].split('x')
                        ancho_bloque = int(partes[0])
                        alto_bloque = int(partes[1])
                        
                        base_sprite = self.sprites_base['B']
                        nuevo_tamano = (self.cell_size * ancho_bloque, self.cell_size * alto_bloque)
                        self.sprites_grandes[celda] = pygame.transform.scale(base_sprite, nuevo_tamano)
                    
                    sprite_grande = self.sprites_grandes.get(celda)
                    self.screen.blit(sprite_grande, (x * self.cell_size, y * self.cell_size))
                
                elif celda == ' ':
                    continue