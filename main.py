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
from gestor_binario import Gestor_Binarios

from collections import deque
from tkinter import messagebox
import tkinter as tk
from tkinter import simpledialog
import time

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

def dehacer_pasos(mov):
    if len(mov) > 0:
        movimiento_saliente = mov.pop()
        pedidos = movimiento_saliente[0]
        aceptados = movimiento_saliente[1]
        entregados = movimiento_saliente[2]
        trabajador = movimiento_saliente[3]
        bonos = movimiento_saliente[4]
        penalizaciones = movimiento_saliente[5]
        return pedidos, aceptados, entregados, trabajador, bonos, penalizaciones
    return None, None, None, None, None, None

def agregar_pasos(mov, pedidos, aceptados, entregados, trabajador, bonos, penalizaciones):
    nuevo = [
            copy.deepcopy(pedidos),  # Deep copy de la lista de pedidos
            copy.deepcopy(aceptados),  # Deep copy de pedidos aceptados
            copy.deepcopy(entregados),  # Deep copy de entregados
            trabajador.obtener_estado(),  # Ya retorna un dict con la info
            bonos,
            penalizaciones
        ]
    mov.append(nuevo)

def mostrar_estado_final(resultado):
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
    
    root.update()
    time.sleep(0.5)
    root.destroy()

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
        resultado_final = None
        mapa = Mapa(datos)
        visualizador = Visualizador(mapa, cell_size)
        trabajador = Trabajador(mapa.width, mapa.height, cell_size)
        clima = ClimaMarkov("TigerCity")

        pedidos = Pedidos(client)
        pedidos.procesar_pedidos()

        historial = Puntajes()

        guardador_binario = Gestor_Binarios()

        clock = pygame.time.Clock()
        tiempo_juego = 0
        incluido = True

        inventario = trabajador.inventario.visualizar_por_prioridad()
        inventario_modo = 'P'

        penalizaciones = 0

        total_pedidos = pedidos.cantidad_pedidos()
        pedidos_tratados = 0
        movimientos = []
        velocidad_actual = trabajador.obtener_velocidad(clima, mapa)
        running = True
        while running:

            if trabajador.estado.ingresos >= params["goal"]:
                running = False
                resultado_final = "victoria"
                mostrar_estado_final(resultado_final)
                
            elif trabajador.estado.reputacion < 20:
                running = False
                resultado_final = "derrota"
                mostrar_estado_final(resultado_final)

            elif not pedidos.pedidos and trabajador.inventario.esta_vacia() and trabajador.estado.ingresos < params["goal"]:
                running = False
                resultado_final = "derrota"
                mostrar_estado_final(resultado_final)

            dt = clock.tick(60) / 1000.0
            tiempo_juego += dt

            movio_este_ciclo = False  # ← NUEVO

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
                        agregar_pasos(movimientos,pedidos.pedidos, pedidos.pedidos_aceptados, trabajador.entregados, trabajador, bono, penalizaciones)

                    elif event.key == pygame.K_r:
                        if pedidos.pedidos:
                            pedido_rechazado = pedidos.rechazar_pedido()
                            if pedido_rechazado:
                                trabajador.estado.modificar_reputacion(-3)
                                penalizaciones += 3 
                                pedidos_tratados += 1
                        agregar_pasos(movimientos,pedidos.pedidos, pedidos.pedidos_aceptados, trabajador.entregados, trabajador, bono, penalizaciones)

                    elif event.key == pygame.K_o:
                        if trabajador.inventario:
                            inventario_modo = 'O'

                    elif event.key == pygame.K_p:
                        if trabajador.inventario:
                            inventario_modo = 'P'

                    elif event.key == pygame.K_s:
                        guardador_binario.guardar_partida(
                            trabajador, clima, pedidos, pedidos_tratados, bono, penalizaciones
                        )

                    elif event.key == pygame.K_l:
                        estado_cargado = guardador_binario.cargar_partida()

                        if estado_cargado:
                            trabajador.trabajadorRect.centerx = estado_cargado['center_x']
                            trabajador.trabajadorRect.centery = estado_cargado['center_y']

                            trabajador.estado.resistencia = estado_cargado['resistencia']
                            trabajador.estado.reputacion = estado_cargado['reputacion']

                            trabajador.estado.ingresos = estado_cargado['ingresos']

                            clima.estado = estado_cargado['clima_actual']
                            
                            pedidos.pedidos = estado_cargado['pedidos_pendientes']
                            trabajador.inventario = estado_cargado['inventario_completo']
                            list(trabajador.inventario.todos_los_pedidos())
                            pedidos_tratados = estado_cargado['pedidos_tratados_cuenta']
                            bono = estado_cargado['bono_acumulado']
                            penalizaciones = estado_cargado['penalizaciones_acumuladas']

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
                        elif sel != -1:                         
                            mostrar_error()


                    elif event.key == pygame.K_u:
                        if len(movimientos) > 0:
                            ultimo_estado = movimientos.pop()
                            
                            nuevos_pedidos = ultimo_estado[0]
                            nuevo_aceptado = ultimo_estado[1]
                            nuevo_entregado = ultimo_estado[2]
                            nuevo_trabajador = ultimo_estado[3]
                            nuevo_bono = ultimo_estado[4]
                            nueva_penalizacion = ultimo_estado[5]
                            
                            pedidos.pedidos = copy.deepcopy(nuevos_pedidos)
                            pedidos.pedidos_aceptados = copy.deepcopy(nuevo_aceptado)
                            bono = nuevo_bono
                            penalizaciones = nueva_penalizacion
                            
                            trabajador.restaurar_estado(nuevo_trabajador, nuevo_entregado)
                            
                            if inventario_modo == 'O':
                                inventario = trabajador.inventario.visualizar_por_entrega()
                            else:
                                inventario = trabajador.inventario.visualizar_por_prioridad()
                            
                            pedidos_tratados -= 1 
                        else:
                            messagebox.showinfo("Retroceso de movimientos", "No hay movimientos para deshacer.")
                    


                    elif event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                        movio_este_ciclo = True  # ← NUEVO
                        trabajador.mover_una_celda(event.key, clima, dt, velocidad_actual, mapa)
                        agregar_pasos(movimientos,pedidos.pedidos, pedidos.pedidos_aceptados, trabajador.entregados, trabajador, bono, penalizaciones)

            if not movio_este_ciclo:  # ← NUEVO
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
        )

        historial.agregar(puntaje_final)
    else:
        print("No se pudo cargar el mapa. Saliendo del programa.")

if __name__ == "__main__":
    main()
    time.sleep(1) 
    pygame.quit()