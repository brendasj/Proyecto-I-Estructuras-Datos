import pygame
from api_client import ApiClient
from mapa import Mapa
from visualizador import Visualizador
from trabajador import Trabajador
from datos_clima import ClimaMarkov
from datos_trabajos import Pedido

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


        datos_trabajos = client.obtener_trabajos()
        pedidos = []
        if datos_trabajos:
          for datos in datos_trabajos.get("data", []):
            pedido = Pedido(datos) 
            pedidos.append(pedido)

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            keys = pygame.key.get_pressed()
            trabajador.mover(keys)
            
            clima.actualizar()  

            # Limpiar y dibujar
            visualizador.screen.fill((255, 255, 255))
            visualizador.dibujar()
            trabajador.dibujar(visualizador.screen)
            visualizador.dibujar_panel_lateral(clima, pedidos, resistencia=100, reputacion=70)
            
            pygame.display.flip()
    else:
        print("No se pudo cargar el mapa. Saliendo del programa.")

if __name__ == "__main__":
    main()
    pygame.quit()