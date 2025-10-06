import pygame
import copy
from datetime import datetime
from api_client import ApiClient
from mapa import Mapa
from visualizador import Visualizador
from trabajador import Trabajador
from datos_clima import ClimaMarkov
from pedidos import Pedidos
from puntaje import Puntaje
from puntajes import Puntajes

from collections import deque
from tkinter import messagebox
import tkinter as tk
from tkinter import simpledialog

def dehacer_pasos(mov):
    if len(mov) > 0:
        movimiento_saliente = mov.pop()
        pedidos = movimiento_saliente[0]
        trabajador = movimiento_saliente[1]
        bonos = movimiento_saliente[2]
        penalizaciones = movimiento_saliente[3]
        return pedidos, trabajador, bonos, penalizaciones
    return None, None, None, None


def agregar_pasos(mov, pedidos, trabajador, bonos, penalizaciones):
    nuevo = [
        copy.deepcopy(pedidos),
        trabajador.obtener_estado(),  
        bonos,
        penalizaciones
    ]
    mov.append(nuevo)


def mostrar_estado_final(resultado):
    movimientos=None
    root = tk.Tk()
    root.withdraw()

    if resultado == "victoria":
        titulo = "VICTORIA"
        mensaje = f"¡Felicidades! Has alcanzado la meta"
        
        messagebox.showinfo(titulo, mensaje)
    elif resultado == "derrota":
        titulo = "DERROTA"
        mensaje = f"Perdiste, no alcanzaste los objetivos"
        messagebox.showinfo(titulo, mensaje)

    root.destroy()

def mostrar_error():
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("Error", "Opción no válida")

    root.destroy()

def mostrar_opciones(op):
    titulo = "Partidas disponibles"
    mensaje ="Seleccione una opción de partida"
    impresion = ""
    contador = 1
    for i in op:
        dato1 = "Ingresos: " + str(i["ingresos"])
        dato2 = " Bonos: " + str(i["bonos"])
        dato3 = " Penalización: " + str(i["penalizaciones"])
        impresion += "Opcion " + str(contador) + "\n" + dato1 + dato2 + dato3 + "\n"
        contador += 1

    select = simpledialog.askinteger(titulo,impresion)
    if select is not None:
        return select - 1
    else:
        return -1

def main():
    pygame.init()
    
    params = {
        "width": 17,
        "height": 27,
        "types": ["B", "P", "C"],
        "city_name": "TigerCity",
        "goal": 1100
    }
    cell_size = 24

    client = ApiClient()
    datos = client.obtener_mapa(params)

    if datos:
        bono = 0
        final = False
        mapa = Mapa(datos)
        visualizador = Visualizador(mapa, cell_size)
        trabajador = Trabajador(mapa.width, mapa.height, cell_size)
        clima = ClimaMarkov("TigerCity")

        pedidos = Pedidos(client)
        pedidos.procesar_pedidos()

        historial = Puntajes()

        indice_partida_cargada = -1

        clock = pygame.time.Clock()
        tiempo_juego = 0
        incluido = True

        inventario = trabajador.inventario.visualizar_por_prioridad()
        inventario_modo = 'P'

        penalizaciones = 0

        total_pedidos = pedidos.cantidad_pedidos()
        pedidos_tratados = 0
        movimientos = []
        running = True
        while running:

            if trabajador.estado.ingresos >= params["goal"]:
                running = False
                mostrar_estado_final("victoria")
                final = True
                
            elif trabajador.estado.reputacion < 20:
                final = True
                running = False
                mostrar_estado_final("derrota")
            elif total_pedidos == pedidos_tratados and trabajador.estado.ingresos < params["goal"] and trabajador.inventario.esta_vacia():
                running = False
                mostrar_estado_final("derrota")
                final = False

            dt = clock.tick(60) / 1000.0
            tiempo_juego += dt

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        pedido_a_aceptar = pedidos.obtener_siguiente_pedido()
                        if pedido_a_aceptar:
                            if trabajador.inventario.agregar_pedido(pedido_a_aceptar):
                                pedidos.aceptar_pedido()
                                pedidos_tratados += 1
                                incluido = True
                                if inventario_modo == 'O':
                                    inventario = trabajador.inventario.visualizar_por_entrega()
                                else:
                                    inventario = trabajador.inventario.visualizar_por_prioridad() 
                            else:
                                incluido = False
                        agregar_pasos(movimientos,pedidos, trabajador, bono, penalizaciones)

                    elif event.key == pygame.K_r:
                        if pedidos.pedidos:
                            pedido_rechazado = pedidos.rechazar_pedido()
                            if pedido_rechazado:
                                trabajador.estado.modificar_reputacion(-3)
                                penalizaciones += 3 
                                pedidos_tratados += 1
                        agregar_pasos(movimientos,pedidos, trabajador, bono, penalizaciones)


                    elif event.key == pygame.K_o:
                        if trabajador.inventario:
                            inventario_modo = 'O'

                    elif event.key == pygame.K_p:
                        if trabajador.inventario:
                            inventario_modo = 'P'

                    elif event.key == pygame.K_s:
                        #guardar en json la partida
                        puntaje = Puntaje(
                            ingresos=trabajador.estado.ingresos,
                            bonos=bono, 
                            penalizaciones=penalizaciones,
                            finalizado=final
                        )
                        if indice_partida_cargada != -1:
                            historial.actualizar(indice_partida_cargada, puntaje)
                        else:
                            historial.agregar(puntaje)

                    elif event.key == pygame.K_l:#usuario escoge entre los que tienen finalizado == False
                        partidas_anteriores = historial.datos_cargados
                        opciones = []
                        indices_mapeados = []
                        
                        for idx, op in enumerate(partidas_anteriores):
                            if op["finalizado"] is False:
                                opciones.append(op)
                                indices_mapeados.append(idx)
                        #imprimir opciones 
                        sel = mostrar_opciones(opciones)

                        if sel >= 0 and sel < len(opciones):
                            trabajador.estado.ingresos = opciones[sel]["ingresos"]
                            bono = opciones[sel]["bonos"]
                            penalizaciones = opciones[sel]["penalizaciones"]

                            indice_partida_cargada = indices_mapeados[sel]
                        else:                         
                            mostrar_error()

                        #se debe cargar la partida

                    elif event.key == pygame.K_u:
                        nuevos_pedidos, nuevo_trabajador, nuevo_bono, nueva_penalizacion = dehacer_pasos(movimientos)
                        if nuevos_pedidos is not None:
                            pedidos = nuevos_pedidos
                            bono = nuevo_bono
                            penalizaciones = nueva_penalizacion
                            trabajador.restaurar_estado(nuevo_trabajador)
                        else:
                            messagebox.showinfo("Retroceso de movimientos","No hay movimientos para deshacer.")
                        


                    elif event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                        trabajador.mover_una_celda(event.key, clima, dt, velocidad_actual, mapa)
                        agregar_pasos(movimientos, pedidos, trabajador, bono, penalizaciones)

            teclas = pygame.key.get_pressed()

            if not any(teclas):
                clima.actualizar()
                trabajador.estado.recuperar_resistencia(dt)
                velocidad_actual = trabajador.obtener_velocidad(clima, mapa)
            
            for pedido in trabajador.inventario.todos_los_pedidos():
                pedido.verificar_interaccion(
                    trabajador.trabajadorRect,
                    cell_size,
                    trabajador.inventario,
                    trabajador.estado,
                    tiempo_juego
                )

            # Limpiar y dibujar
            visualizador.screen.fill((255, 255, 255))
            visualizador.dibujar()
            trabajador.dibujar(visualizador.screen)

            # Mostrar panel lateral
            visualizador.dibujar_panel_lateral(
                clima,
                pedidos.obtener_todos_los_pedidos(),
                inventario,
                peso = trabajador.inventario.peso_actual,
                incluido = incluido,
                velocidad = velocidad_actual,
                resistencia = int(trabajador.estado.resistencia),
                reputacion = int(trabajador.estado.reputacion),
                entregados = trabajador.inventario.entregados,
                ingresos = trabajador.estado.ingresos,
                meta = trabajador.estado.meta
            )

            if inventario_modo == 'O':
                inventario = trabajador.inventario.visualizar_por_entrega()
            else:
                inventario = trabajador.inventario.visualizar_por_prioridad()

            # Resaltar pickups y dropoffs
            for pedido in trabajador.inventario.todos_los_pedidos():
                if not pedido.recogido:
                    visualizador.resaltar_celda(pedido.pickup[0], pedido.pickup[1], (255, 185, 50, 100), "↑")
                elif not pedido.entregado:
                    visualizador.resaltar_celda(pedido.dropoff[0], pedido.dropoff[1], (255, 255, 0, 100), "↓")

            pygame.display.flip()
        
        if trabajador.estado.reputacion >= 90:
            bno = 0.05 * trabajador.estado.ingresos
            bono += bno
        else:
            bno = 0

        puntaje_final = Puntaje(
            ingresos = trabajador.estado.ingresos,
            bonos = bono, 
            penalizaciones = penalizaciones,
            finalizado = final
        )

        if indice_partida_cargada != 1:
            historial.actualizar(indice_partida_cargada, puntaje_final)
        else:
            historial.agregar(puntaje_final)
    else:
        print("No se pudo cargar el mapa. Saliendo del programa.")

if __name__ == "__main__":
    main()
    pygame.quit()