import pygame
import os

class Visualizador:
    def __init__(self, mapa, cell_size):
        pygame.init()
        self.mapa = mapa
        self.cell_size = cell_size
        self.panel_lateral = 250  # ancho del panel lateral

        # Ajustar tamaño de pantalla para incluir el panel lateral
        self.screen = pygame.display.set_mode(
            (mapa.width * cell_size + self.panel_lateral, mapa.height * cell_size)
        )
        pygame.display.set_caption(f"Mapa de {mapa.name}")

        self.sprites_base = {
            'C': pygame.image.load(os.path.join("assets", "calle.png")),
            'B': pygame.image.load(os.path.join("assets", "edificio.png")),
            'P': pygame.image.load(os.path.join("assets", "parque.png"))
        }
        self.sprites_base['P'] = pygame.transform.scale(self.sprites_base['P'], (24, 24))

        self.sprites_grandes = {}

    def dibujar(self):
        matriz = self.mapa.obtener_matriz()
        for y, fila in enumerate(matriz):
            for x, celda in enumerate(fila):
                if celda == 'C' or celda == 'P':
                    sprite = pygame.transform.scale(self.sprites_base.get(celda), (self.cell_size, self.cell_size))
                    self.screen.blit(sprite, (x * self.cell_size, y * self.cell_size))

                elif celda == 'B':
                    sprite = pygame.transform.scale(self.sprites_base.get(celda), (self.cell_size, self.cell_size))
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

    def dibujar_panel_lateral(self, clima, pedidos_disponible, pedidos_inventario, peso, velocidad, resistencia=None, reputacion=None):
        x_panel = self.mapa.width * self.cell_size
        y_panel = 0
        alto_total = self.mapa.height * self.cell_size

        # Fondo del panel
        color_fondo = (230, 230, 230)
        pygame.draw.rect(self.screen, color_fondo, (x_panel, y_panel, self.panel_lateral, alto_total))

        font_titulo = pygame.font.SysFont("Arial", 20)
        font_contenido = pygame.font.SysFont("Arial", 16)
        color_texto = (30, 30, 30)

        y_actual = 20
        margen = 10

        # Clima
        texto_clima = f"Clima: {clima.estado}"
        self.screen.blit(font_titulo.render(texto_clima, True, color_texto), (x_panel + margen, y_actual))
        y_actual += 30

        # Resistencia
        if resistencia is not None:
            texto_res = f"Resistencia: {resistencia:.2f}/100."
            self.screen.blit(font_contenido.render(texto_res, True, color_texto), (x_panel + margen, y_actual))
            y_actual += 24

        # Reputación
        if reputacion is not None:
            texto_rep = f"Reputación: {reputacion}/100"
            self.screen.blit(font_contenido.render(texto_rep, True, color_texto), (x_panel + margen, y_actual))
            y_actual += 24

        # Pedidos Disponibles 
        self.screen.blit(font_titulo.render("Pedidos Disponibles:", True, color_texto), (x_panel + margen, y_actual))
        y_actual += 28

        if pedidos_disponible:
            pedido = pedidos_disponible[0]
            texto = f"Aceptar (A) | Rechazar (R)"
            self.screen.blit(font_contenido.render(texto, True, (0, 0, 255)), (x_panel + margen, y_actual))
            y_actual += 22
            texto_pedido = f"{pedido.id} | ${pedido.payout} | P:{pedido.priority}"
            self.screen.blit(font_contenido.render(texto_pedido, True, (0, 0, 0)), (x_panel + margen, y_actual))
            y_actual += 28

        self.screen.blit(font_titulo.render("Pedidos en Inventario:", True, color_texto), (x_panel + margen, y_actual))
        y_actual += 28

        for pedido in pedidos_inventario:
            texto = f"{pedido.id} | ${pedido.payout}"
            self.screen.blit(font_contenido.render(texto, True, (0, 100, 0)), (x_panel + margen, y_actual))
            y_actual += 22

        # Peso
        texto_rep = f"Peso: {peso}"
        self.screen.blit(font_titulo.render(texto_rep, True, color_texto), (x_panel + margen, y_actual))
        y_actual += 28

        # Peso
        texto_rep = f"Velocidad: {velocidad:.2f}"
        self.screen.blit(font_titulo.render(texto_rep, True, color_texto), (x_panel + margen, y_actual))
        y_actual += 28

    # Estas funciones quedan opcionales si ya usás dibujar_panel_lateral
    def mostrar_info_clima(self, clima):
        pass

    def mostrar_lista_pedidos(self, pedidos):
        pass