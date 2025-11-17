"""Entrada principal del juego: inicialización y bucle principal.

Este módulo contiene la función `main()` que carga recursos, crea el mapa,
inicializa el visualizador y gestiona el bucle del juego.
"""

import copy
from collections import deque
from datetime import datetime
import time
import tkinter as tk
from tkinter import messagebox, simpledialog

import pygame

from api_client import ApiClient
from gestor_binario import Gestor_Binarios
from mapa import Mapa
from pedidos import Pedidos
from puntaje import Puntaje
from puntajes import Puntajes
from trabajador import Trabajador
from visualizador import Visualizador
from datos_clima import ClimaMarkov


def mostrar_error() -> None:
    """Muestra un cuadro de diálogo indicando que la opción no es válida."""
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

def definir_dificultad():
    def set_dificultad(valor):
        nonlocal seleccion
        seleccion = valor
        ventana.destroy()
    
    ventana = tk.Tk()
    ventana.title("Seleccionar dificultad")
    ventana.geometry("300x220")
    ventana.configure(bg="#f0f0f0")

    tk.Label(
        ventana,
        text="Elige la dificultad:",
        font=("Arial", 14, "bold"),
        bg="#f0f0f0"
    ).pack(pady=15)

    seleccion = None

    btn_facil = tk.Button(
        ventana, text="Fácil", font=("Arial", 12),
        width=12, bg="#b3ffb3",
        command=lambda: set_dificultad("facil")
    )
    btn_facil.pack(pady=5)

    btn_medio = tk.Button(
        ventana, text="Medio", font=("Arial", 12),
        width=12, bg="#ffff99",
        command=lambda: set_dificultad("medio")
    )
    btn_medio.pack(pady=5)

    btn_dificil = tk.Button(
        ventana, text="Difícil", font=("Arial", 12),
        width=12, bg="#ff9999",
        command=lambda: set_dificultad("dificil")
    )
    btn_dificil.pack(pady=5)

    ventana.mainloop()
    return seleccion

def main():
    dificultad = definir_dificultad()

    if not dificultad:
        print("No se seleccionó dificultad. Saliendo")
        return
    
    pygame.init()
    
    params = {
        "width": 17,
        "height": 27,
        "types": ["B", "P", "C"],
        "city_name": "TigerCity",
        "goal": 1100,
        # Límite de tiempo de la partida en segundos (ej. 120 = 2 minutos)
        "time_limit": 480,
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
        trabajador_ia = Trabajador(mapa.width, mapa.height, cell_size, ruta_imagen="assets/trabajador_ia.png")
        # Alinear la IA a la cuadrícula (usar múltiplos de cell_size). Antes se usaban 50px
        # que no es múltiplo de cell_size y producía desalineación.
        trabajador_ia.trabajadorRect.center = (
            trabajador.trabajadorRect.centerx + cell_size * 2,
            trabajador.trabajadorRect.centery,
        )
        clima = ClimaMarkov("TigerCity")

        pedidos = Pedidos(client)
        pedidos.procesar_pedidos()

        # No publicar pedidos al inicio - el jugador los publica con la tecla 'A'

        historial = Puntajes()

        guardador_binario = Gestor_Binarios()

        clock = pygame.time.Clock()
        tiempo_juego = 0
        incluido = True

        inventario_trabajador = trabajador.inventario.visualizar_por_prioridad()
        inventario_modo = 'P'

        penalizaciones = 0

        total_pedidos = pedidos.cantidad_pedidos()
        pedidos_tratados = 0
        movimientos = []
        velocidad_actual_trabajador = trabajador.obtener_velocidad(clima, mapa)
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

            # No terminar la partida inmediatamente si ya no quedan pedidos
            # pendientes en la cola: es posible que el jugador (o la IA)
            # todavía tenga pedidos en su inventario por entregar. Sólo
            # declaramos derrota aquí si NO hay pedidos pendientes y ambos
            # inventarios están vacíos y no se alcanzó la meta.
            elif (
                # Sólo terminar por falta de pedidos si no hay publicados
                # y tampoco quedan trabajos sin publicar en la fuente.
                not pedidos.pedidos
                and (not hasattr(pedidos, "fuente_jobs") or not pedidos.fuente_jobs)
                and trabajador.inventario.esta_vacia()
                # and trabajador_ia.inventario.esta_vacia()
                and trabajador.estado.ingresos < params["goal"]
            ):
                running = False
                resultado_final = "derrota"
                mostrar_estado_final(resultado_final)

            dt = clock.tick(60) / 1000.0
            tiempo_juego += dt

            # Chequear límite de tiempo (derrota si no alcanza la meta)
            if tiempo_juego >= params.get("time_limit", float("inf")):
                running = False
                if trabajador.estado.ingresos >= params["goal"]:
                    resultado_final = "victoria"
                else:
                    resultado_final = "derrota"
                mostrar_estado_final(resultado_final)

            movio_este_ciclo = False  # ← NUEVO

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        # Solo publicar un pedido en el mapa
                        pedidos.publicar_siguiente_pedido()
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
                                inventario_trabajador = trabajador.inventario.visualizar_por_entrega()
                            else:
                                inventario_trabajador = trabajador.inventario.visualizar_por_prioridad()
                            
                            pedidos_tratados -= 1 
                        else:
                            messagebox.showinfo("Retroceso de movimientos", "No hay movimientos para deshacer.")
                    


                    elif event.key in [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]:
                        movio_este_ciclo = True  # ← NUEVO
                        if dificultad == "facil":
                            trabajador_ia.nivel_facil_ia(clima, dt, mapa, pedidos)
                        trabajador.mover_una_celda(event.key, clima, dt, velocidad_actual_trabajador, mapa)
                        agregar_pasos(movimientos,pedidos.pedidos, pedidos.pedidos_aceptados, trabajador.entregados, trabajador, bono, penalizaciones)

            if not movio_este_ciclo:  # ← NUEVO
                clima.actualizar()
                trabajador.estado.recuperar_resistencia(dt)
                if dificultad == "facil":
                    trabajador_ia.estado.recuperar_resistencia(dt)
                elif dificultad == "medio":
                    trabajador_ia.estado.recuperar_resistencia(dt)
                elif dificultad == "dificil":
                    trabajador_ia.estado.recuperar_resistencia(dt)

            # En modo difícil la IA debe decidir y moverse cada ciclo
            if dificultad == "dificil":
                # llamar siempre al comportamiento difícil (moverá un paso si puede)
                try:
                    trabajador_ia.nivel_dificil_ia(clima, dt, mapa, pedidos)
                except Exception:
                    # no bloquear la partida por un fallo en la IA
                    pass
            elif dificultad == "medio":
                try:
                    trabajador_ia.nivel_medio_ia(clima, dt, mapa, pedidos)
                except Exception:
                    pass

            velocidad_actual_trabajador = trabajador.obtener_velocidad(clima, mapa)
            velocidad_actual_trabajador_ia = trabajador_ia.obtener_velocidad(clima, mapa)
            
            # Aceptar automáticamente pedidos publicados cuando el jugador
            # pasa por su pickup (recogerlos al vuelo).
            # Recorremos una copia de la lista heap para evitar modificarla mientras iteramos.
            for tup in pedidos.pedidos[:]:
                try:
                    _, _, pedido_pub = tup
                except Exception:
                    continue

                # Si el jugador está lo suficientemente cerca del pickup y
                # hay capacidad en el inventario, aceptar y agregar el pedido.
                if pedido_pub.esta_cerca(trabajador.trabajadorRect, pedido_pub.pickup, cell_size):
                    # Comprobar capacidad de peso antes de aceptar
                    if trabajador.inventario.peso_actual + pedido_pub.weight <= trabajador.inventario.peso_maximo:
                        pedido_aceptado = pedidos.aceptar_pedido_especifico(pedido_pub)
                        if pedido_aceptado:
                            agregado = trabajador.inventario.agregar_pedido(pedido_aceptado)
                            if agregado:
                                # Verificar interacción ahora que está en el inventario
                                pedido_aceptado.verificar_interaccion(
                                    trabajador.trabajadorRect,
                                    cell_size,
                                    trabajador.inventario,
                                    trabajador.estado,
                                    tiempo_juego
                                )
                                pedidos_tratados += 1
                            else:
                                # Si por alguna razón no se pudo agregar, volver a insertar
                                import heapq
                                index = len(pedidos.pedidos) + 1
                                heapq.heappush(pedidos.pedidos, (-pedido_aceptado.priority, index, pedido_aceptado))
                
                # Si la IA está lo suficientemente cerca del pickup y
                # hay capacidad en el inventario, aceptar y agregar el pedido.
                elif pedido_pub.esta_cerca(trabajador_ia.trabajadorRect, pedido_pub.pickup, cell_size):
                    # Comprobar capacidad de peso antes de aceptar
                    if trabajador_ia.inventario.peso_actual + pedido_pub.weight <= trabajador_ia.inventario.peso_maximo:
                        pedido_aceptado = pedidos.aceptar_pedido_especifico(pedido_pub)
                        if pedido_aceptado:
                            agregado = trabajador_ia.inventario.agregar_pedido(pedido_aceptado)
                            if agregado:
                                # Verificar interacción ahora que está en el inventario
                                pedido_aceptado.verificar_interaccion(
                                    trabajador_ia.trabajadorRect,
                                    cell_size,
                                    trabajador_ia.inventario,
                                    trabajador_ia.estado,
                                    tiempo_juego
                                )
                                pedidos_tratados += 1
                            else:
                                # Si por alguna razón no se pudo agregar, volver a insertar
                                import heapq
                                index = len(pedidos.pedidos) + 1
                                heapq.heappush(pedidos.pedidos, (-pedido_aceptado.priority, index, pedido_aceptado))

            for pedido in trabajador.inventario.todos_los_pedidos():
                pedido.verificar_interaccion(
                    trabajador.trabajadorRect,
                    cell_size,
                    trabajador.inventario,
                    trabajador.estado,
                    tiempo_juego
                )

            for pedido in trabajador_ia.inventario.todos_los_pedidos():
                pedido.verificar_interaccion(
                    trabajador_ia.trabajadorRect,
                    cell_size,
                    trabajador_ia.inventario,
                    trabajador_ia.estado,
                    tiempo_juego
                )

            # Limpiar y dibujar
            visualizador.screen.fill((255, 255, 255))
            visualizador.dibujar()
            trabajador.dibujar(visualizador.screen)
            trabajador_ia.dibujar(visualizador.screen)


            # Mostrar panel lateral
            visualizador.dibujar_panel_lateral(
                dificultad,
                clima,
                trabajador,
                trabajador_ia,
                pedidos.obtener_todos_los_pedidos(),
                inventario_trabajador,
                trabajador_ia.inventario.visualizar_por_prioridad(),
                incluido = incluido,
                velocidad_trabajador = velocidad_actual_trabajador,
                velocidad_ia = velocidad_actual_trabajador_ia,
                meta = trabajador.estado.meta
                ,
                tiempo_juego = tiempo_juego,
                time_limit = params.get("time_limit")
            )

            if inventario_modo == 'O':
                inventario_trabajador = trabajador.inventario.visualizar_por_entrega()
            else:
                inventario_trabajador = trabajador.inventario.visualizar_por_prioridad()

            # Resaltar pedidos disponibles (no asignados)
            for pedido_tuple in pedidos.pedidos:
                _, _, pedido = pedido_tuple
                visualizador.resaltar_celda(pedido.pickup[0], pedido.pickup[1], (50, 255, 50, 120), "↑")
            
            # Resaltar pickups y dropoffs
            for pedido in trabajador.inventario.todos_los_pedidos():
                if not pedido.recogido:
                    visualizador.resaltar_celda(pedido.pickup[0], pedido.pickup[1], (255, 185, 50, 100), "↑")
                elif not pedido.entregado:
                    visualizador.resaltar_celda(pedido.dropoff[0], pedido.dropoff[1], (255, 255, 0, 100), "↓")
            
            for pedido in trabajador_ia.inventario.todos_los_pedidos():
                if not pedido.recogido:
                    visualizador.resaltar_celda(pedido.pickup[0], pedido.pickup[1], (50, 100, 255, 100), "↑")
                elif not pedido.entregado:
                    visualizador.resaltar_celda(pedido.dropoff[0], pedido.dropoff[1], (100, 150, 255, 100), "↓")

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