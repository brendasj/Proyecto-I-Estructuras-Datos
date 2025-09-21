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
    cell_size = 22

    client = ApiClient()
    datos = client.obtener_mapa(params)

    if datos:
        mapa = Mapa(datos)
        visualizador = Visualizador(mapa, cell_size)
        trabajador = Trabajador(mapa.width, mapa.height, cell_size)
        clima = ClimaMarkov("TigerCity")

        pedidos = Pedidos(client)
        pedidos.procesar_pedidos()

        # datos_trabajos = client.obtener_trabajos()
        # pedidos = []
        # if datos_trabajos:
          # for datos in datos_trabajos.get("data", []):
            # pedido = Pedido(datos) 
            # pedidos.append(pedido)

        clock = pygame.time.Clock()

        running = True
        while running:
            dt = clock.tick(60) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            keys = pygame.key.get_pressed()
            trabajador.mover(keys, clima, dt)
            
            clima.actualizar() 

            # Limpiar y dibujar
            visualizador.screen.fill((255, 255, 255))
            visualizador.dibujar()
            trabajador.dibujar(visualizador.screen)
            visualizador.dibujar_panel_lateral(clima, pedidos.obtener_todos_los_pedidos(), resistencia=trabajador.resistencia, reputacion=72)
            
            pygame.display.flip()
    else:
        print("No se pudo cargar el mapa. Saliendo del programa.")

if __name__ == "__main__":
    main()
    pygame.quit()