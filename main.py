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
        inventario_modo = 'P'

        running = True
        while running:
            dt = clock.tick(60) / 1000.0
            tiempo_juego += dt

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                # Lógica para aceptar/rechazar pedidos
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        pedido_a_aceptar = pedidos.obtener_siguiente_pedido()
                        if pedido_a_aceptar:
                            if trabajador.inventario.agregar_pedido(pedido_a_aceptar):
                                pedidos.aceptar_pedido()
                                incluido = True
                            else:
                                incluido = False

                    if event.key == pygame.K_r:
                        if pedidos.pedidos:
                            pedidos.rechazar_pedido()

                    if event.key == pygame.K_o:
                        inventario_modo = 'O'

                    if event.key == pygame.K_p:
                        inventario_modo = 'P'

            keys = pygame.key.get_pressed()
            clima.actualizar()
            velocidad_actual = trabajador.obtener_velocidad(clima, mapa)
            trabajador.mover(keys, clima, dt, velocidad_actual, mapa)
            # Verificar recogida y entrega por proximidad
            for pedido in trabajador.inventario.todos_los_pedidos():
                pedido.verificar_interaccion(trabajador.trabajadorRect, cell_size, trabajador.inventario)

            # Limpiar y dibujar
            visualizador.screen.fill((255, 255, 255))
            visualizador.dibujar()
            trabajador.dibujar(visualizador.screen)

            # Mostrar panel lateral
            visualizador.dibujar_panel_lateral(
                clima,
                pedidos.obtener_todos_los_pedidos(),
                trabajador.inventario.todos_los_pedidos(),
                peso=trabajador.inventario.peso_actual,
                incluido=incluido,
                velocidad=velocidad_actual,
                resistencia=int(trabajador.estado.resistencia),
                reputacion=int(trabajador.estado.reputacion),
                entregados=trabajador.inventario.entregados
            )

            # Resaltar pickups y dropoffs
            for pedido in trabajador.inventario.todos_los_pedidos():
                if not pedido.recogido:
                    visualizador.resaltar_celda(pedido.pickup[0], pedido.pickup[1], (255, 185, 50, 100), "↑")
                elif not pedido.entregado:
                    visualizador.resaltar_celda(pedido.dropoff[0], pedido.dropoff[1], (255, 255, 0, 100), "↓")

            pygame.display.flip()
    else:
        print("No se pudo cargar el mapa. Saliendo del programa.")

if __name__ == "__main__":
    main()
    pygame.quit()