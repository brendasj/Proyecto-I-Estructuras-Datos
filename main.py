import pygame
from api_client import ApiClient
from mapa import Mapa
from visualizador import Visualizador
from trabajador import Trabajador
from datos_clima import Clima
from datos_trabajos import Trabajo

def main():
    pygame.init()
    
    params = {
        "width": 30,
        "height": 30,
        "types": ["B", "P", "C"],
        "city_name": "TigerCity",
        "goal": 1500
    }
    cell_size = 32

    client = ApiClient()
    datos = client.obtener_mapa(params)

    # datos_clima = client.obtener_clima("Heredia")
    # if datos_clima:
    #     clima = Clima(datos_clima)
    #     clima.mostrar()

    # datos_trabajos = client.obtener_trabajos()
    # if datos_trabajos:
    #     for trabajo_json in datos_trabajos.get("jobs", []):
    #         trabajo = Trabajo(trabajo_json)
    #         trabajo.mostrar()

    if datos:
        mapa = Mapa(datos)
        visualizador = Visualizador(mapa, cell_size)
        trabajador = Trabajador(mapa.width, mapa.height, cell_size)

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            keys = pygame.key.get_pressed()
            trabajador.mover(keys)
            
            # Limpiar y dibujar
            visualizador.screen.fill((255, 255, 255))
            visualizador.dibujar()
            trabajador.dibujar(visualizador.screen)
            
            pygame.display.flip()
    else:
        print("No se pudo cargar el mapa. Saliendo del programa.")

if __name__ == "__main__":
    main()
    pygame.quit()