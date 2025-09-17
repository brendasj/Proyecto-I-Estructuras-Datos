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
        self.sprites_base = {
            'C': pygame.image.load(os.path.join("Proyecto-I-Estructuras-Datos", "assets", "calle.png")),
            'B': pygame.image.load(os.path.join("Proyecto-I-Estructuras-Datos", "assets", "edificio.png")),
            'P': pygame.image.load(os.path.join("Proyecto-I-Estructuras-Datos", "assets", "parque.png"))
        }

        self.sprites_grandes = {}

    def dibujar(self):
        matriz = self.mapa.obtener_matriz()
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.screen.fill((255, 255, 255))

            # Dibujar cada celda del mapa
            for y, fila in enumerate(matriz):
                for x, celda in enumerate(fila):
                    if celda == 'C' or celda == 'P':
                        sprite = self.sprites_base.get(celda)
                        self.screen.blit(sprite, (x * self.cell_size, y * self.cell_size))
                    elif celda.startswith('B_('): # Detecta el inicio de un bloque grande
                        # Si el sprite para este bloque no ha sido creado, lo hacemos
                        if celda not in self.sprites_grandes:
                            # Extraemos el tamaño del nombre de la celda, e.g., 'B_(3x4)'
                            partes = celda.replace(')', '').split('(')[1].split('x')
                            ancho_bloque = int(partes[0])
                            alto_bloque = int(partes[1])
                            
                            # Crea un nuevo sprite escalando el original
                            base_sprite = self.sprites_base['B']
                            nuevo_tamano = (self.cell_size * ancho_bloque, self.cell_size * alto_bloque)
                            self.sprites_grandes[celda] = pygame.transform.scale(base_sprite, nuevo_tamano)
                        
                        # Dibuja el sprite grande en la posición de la celda
                        sprite_grande = self.sprites_grandes.get(celda)
                        self.screen.blit(sprite_grande, (x * self.cell_size, y * self.cell_size))
                    
                    # Si la celda es un espacio ' ', no dibujamos nada
                    elif celda == ' ':
                        continue

            pygame.display.flip()

        pygame.quit()