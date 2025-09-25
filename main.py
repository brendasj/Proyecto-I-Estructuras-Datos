import pygame
from api_client import ApiClient
from mapa import Mapa
from visualizador import Visualizador
from trabajador import Trabajador
from datos_clima import ClimaMarkov
from pedidos import Pedidos

def main():
    pygame.init()
    
    params = {
        "width": 17,
        "height": 27,
        "types": ["B", "P", "C"],
        "city_name": "TigerCity",
        "goal": 1500
    }
    cell_size = 24

    client = ApiClient()
    datos = client.obtener_mapa(params)

    if datos:
        mapa = Mapa(datos)
        visualizador = Visualizador(mapa, cell_size)
        trabajador = Trabajador(mapa.width, mapa.height, cell_size)
        clima = ClimaMarkov("TigerCity")

        pedidos = Pedidos(client)
        pedidos.procesar_pedidos()

        clock = pygame.time.Clock()

        tiempo_juego = 0
        incluido = True

        running = True
        while running:
            dt = clock.tick(60) / 1000.0
            tiempo_juego += dt

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                # Lógica para aceptar/rechazar pedidos
                if event.type == pygame.KEYDOWN:
                    # Aceptar pedido
                    if event.key == pygame.K_a:
                        pedido_a_aceptar = pedidos.obtener_siguiente_pedido()
                        if pedido_a_aceptar:
                            if trabajador.inventario.agregar_pedido(pedido_a_aceptar):
                                pedidos.aceptar_pedido()
                                incluido = True
                            else:
                                incluido = False

                    # Rechazar pedido
                    if event.key == pygame.K_r:
                        if pedidos.pedidos:
                            pedidos.rechazar_pedido()

            keys = pygame.key.get_pressed()
            clima.actualizar() 

            velocidad_actual = trabajador.obtener_velocidad(clima, mapa)

            trabajador.mover(keys, clima, dt, velocidad_actual)

            # Limpiar y dibujar
            visualizador.screen.fill((255, 255, 255))
            visualizador.dibujar()
            trabajador.dibujar(visualizador.screen)
            visualizador.dibujar_panel_lateral(clima, pedidos.obtener_todos_los_pedidos(), trabajador.inventario.forward(), trabajador.inventario.peso_actual, incluido, velocidad_actual, resistencia=trabajador.resistencia, reputacion = trabajador.reputacion)
            
            pygame.display.flip()
    else:
        print("No se pudo cargar el mapa. Saliendo del programa.")

if __name__ == "__main__":
    main()
    pygame.quit()