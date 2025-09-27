import pygame
import os

class Visualizador:
    def __init__(self, mapa, cell_size):
        pygame.init()
        self.fondo_calles = pygame.image.load(os.path.join("assets", "calle4.png"))
        self.fondo_calles = pygame.transform.scale(
            self.fondo_calles,
            (mapa.width * cell_size, mapa.height * cell_size)
        )
        self.mapa = mapa
        self.cell_size = cell_size
        self.panel_lateral = 270  # ancho del panel lateral

        # Ajustar tamaño de pantalla para incluir el panel lateral
        self.screen = pygame.display.set_mode(
            (mapa.width * cell_size + self.panel_lateral, mapa.height * cell_size)
        )
        pygame.display.set_caption(f"Mapa de {mapa.name}")

        self.sprites_base = {
            'C': pygame.image.load(os.path.join("assets", "calle4.png")),
            'B': pygame.image.load(os.path.join("assets", "edificio.png")),
            'P': pygame.image.load(os.path.join("assets", "parque.png"))
        }
        self.sprites_base['P'] = pygame.transform.scale(self.sprites_base['P'], (24, 24))

        self.sprites_grandes = {}

    def dibujar(self):
        self.screen.blit(self.fondo_calles, (0, 0))
        matriz = self.mapa.obtener_matriz()
        for y, fila in enumerate(matriz):
            for x, celda in enumerate(fila):
                if celda == 'P':
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

    def dibujar_panel_lateral(self, clima, pedidos_disponible, pedidos_inventario, peso, incluido, velocidad, resistencia=None, reputacion=None, entregados=None):
        x_panel = self.mapa.width * self.cell_size
        y_panel = 0
        alto_total = self.mapa.height * self.cell_size

        # Fondo del panel
        color_fondo = (230, 230, 230)
        pygame.draw.rect(self.screen, color_fondo, (x_panel, y_panel, self.panel_lateral, alto_total))

        # Fuentes y colores
        font_titulo = pygame.font.SysFont("Arial", 20, bold=True)
        font_contenido = pygame.font.SysFont("Arial", 16)
        font_guia = pygame.font.SysFont("Arial", 16, bold=True)
        color_texto = (30, 30, 30)
        color_titulo = (0, 0, 80)

        y_actual = 20
        margen = 10

        # Clima
        texto_clima = f"Clima: {clima.estado}"
        self.screen.blit(font_titulo.render(texto_clima, True, color_titulo), (x_panel + margen, y_actual))
        y_actual += 30

        # Resistencia
        if resistencia is not None:
            texto_res = f"Resistencia: {resistencia:.2f}/100."
            self.screen.blit(font_contenido.render(texto_res, True, color_texto), (x_panel + margen, y_actual))
            y_actual += 24

            # Barra visual
            barra_ancho = 200
            barra_alto = 12
            x_barra = x_panel + margen
            y_barra = y_actual

            porcentaje = resistencia / 100
            ancho_lleno = int(barra_ancho * porcentaje)

            if resistencia > 60:
                color_barra = (0, 200, 0)
            elif resistencia > 30:
                color_barra = (255, 200, 0)
            else:
                color_barra = (200, 0, 0)

            pygame.draw.rect(self.screen, (180, 180, 180), (x_barra, y_barra, barra_ancho, barra_alto))
            pygame.draw.rect(self.screen, color_barra, (x_barra, y_barra, ancho_lleno, barra_alto))
            y_actual += barra_alto + 10

        # Reputación
        if reputacion is not None:
            texto_rep = f"Reputación: {reputacion}/100"
            self.screen.blit(font_contenido.render(texto_rep, True, color_texto), (x_panel + margen, y_actual))
            y_actual += 24

            # Barra visual de reputación
            barra_ancho = 200
            barra_alto = 12
            x_barra = x_panel + margen
            y_barra = y_actual

            porcentaje = reputacion / 100
            ancho_lleno = int(barra_ancho * porcentaje)

            # Color dinámico: azul, celeste, gris
            if reputacion > 70:
                color_barra = (0, 120, 255)       # azul fuerte
            elif reputacion > 40:
                color_barra = (100, 180, 255)     # celeste
            else:
                color_barra = (150, 150, 150)     # gris

            pygame.draw.rect(self.screen, (180, 180, 180), (x_barra, y_barra, barra_ancho, barra_alto))
            pygame.draw.rect(self.screen, color_barra, (x_barra, y_barra, ancho_lleno, barra_alto))
            y_actual += barra_alto + 10

        # Solicitudes de pedidos
        self.screen.blit(font_titulo.render("Solicitudes de pedidos:", True, color_titulo), (x_panel + margen, y_actual))
        y_actual += 28
        for pedido in pedidos_disponible:
            texto = f"{pedido.id} | ${pedido.payout} | P:{pedido.priority}"
            self.screen.blit(font_contenido.render(texto, True, color_texto), (x_panel + margen, y_actual))
            y_actual += 22

        # Pedidos para entregar
        self.screen.blit(font_titulo.render("Pedidos para entregar:", True, color_titulo), (x_panel + margen, y_actual))
        y_actual += 28
        for pedido in pedidos_inventario:
            texto1 = f"{pedido.id} | ${pedido.payout} | P:{pedido.priority} ({pedido.pickup}) → ({pedido.dropoff})"
            texto2 = f"Hora de entrega: {pedido.deadline_str}"
            self.screen.blit(font_contenido.render(texto1, True, color_texto), (x_panel + margen, y_actual))
            y_actual += 22
            self.screen.blit(font_contenido.render(texto2, True, (80, 80, 80)), (x_panel + margen, y_actual))
            y_actual += 22

        # Pedidos entregados
        if entregados:
            self.screen.blit(font_titulo.render("Pedidos entregados:", True, color_titulo), (x_panel + margen, y_actual))
            y_actual += 28
            for pedido in entregados:
                texto = f"{pedido.id} | ${pedido.payout} | ✓"
                self.screen.blit(font_contenido.render(texto, True, (100, 100, 100)), (x_panel + margen, y_actual))
                y_actual += 22

        # Peso
        texto_peso = f"Peso: {peso}"
        self.screen.blit(font_titulo.render(texto_peso, True, color_titulo), (x_panel + margen, y_actual))
        y_actual += 28
        if incluido == False:
            texto = f"Peso máximo alcanzado"
            self.screen.blit(font_contenido.render(texto, True, (0, 0, 255)), (x_panel + margen, y_actual))
            y_actual += 22

        # Velocidad
        texto_vel = f"Velocidad: {velocidad:.2f}"
        self.screen.blit(font_titulo.render(texto_vel, True, color_titulo), (x_panel + margen, y_actual))
        y_actual += 28

        # Guía visual
        """"""""""
        self.screen.blit(font_guia.render("Pickup", True, (255,185,50)), (x_panel + margen, y_actual))
        y_actual += 22
        self.screen.blit(font_guia.render("Dropoff", True, (0, 100, 0)), (x_panel + margen, y_actual))
        y_actual += 22
"""
    def resaltar_celda(self, x, y, color, texto=None):
        font_numero = pygame.font.SysFont("Arial", 12, bold=True)

        x_pixel = x * self.cell_size
        y_pixel = y * self.cell_size

        s = pygame.Surface((self.cell_size, self.cell_size), pygame.SRCALPHA)
        s.fill(color) 
        self.screen.blit(s, (x_pixel, y_pixel))

        if texto:
            color_texto = (255, 255, 255)
            superficie_texto = font_numero.render(texto, True, color_texto)
        
            x_centrado = x_pixel + (self.cell_size - superficie_texto.get_width()) // 2
            y_centrado = y_pixel + (self.cell_size - superficie_texto.get_height()) // 2 
            self.screen.blit(superficie_texto, (x_centrado, y_centrado))