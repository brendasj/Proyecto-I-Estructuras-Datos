# main.py
from api_client import ApiClient
from mapa import Mapa
from visualizador import Visualizador
from datos_clima import Clima
from datos_trabajos import Trabajo

# Parámetros para la API
params = {
    "height": 50,
    "width": 50,
    "goal": 1500,
    "name": "C",
    "kills": ["C", "C"]
}

# Ejecutar
client = ApiClient()
datos = client.obtener_mapa(params)

# Obtener clima
#datos_clima = client.obtener_clima("Heredia")
#if datos_clima:
   # clima = Clima(datos_clima)
    #clima.mostrar()

# Obtener trabajos
#datos_trabajos = client.obtener_trabajos()
#if datos_trabajos:
 #   for trabajo_json in datos_trabajos.get("jobs", []):
  #      trabajo = Trabajo(trabajo_json)
   #     trabajo.mostrar()

#print(datos)  
#print("Datos del clima:", datos_clima)
#print("Datos de trabajos:", datos_trabajos)

mapa = Mapa(datos)
visual = Visualizador(mapa)
visual.dibujar()