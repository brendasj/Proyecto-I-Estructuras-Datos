"""Definición de la clase Trabajador y su comportamiento en pantalla.

Incluye movimiento, cálculo de velocidad y gestión del inventario.
"""

import copy
import random
import heapq

import pygame

from estado_trabajador import EstadoTrabajador
from inventario import Inventario
from typing import Any, List, Tuple, Optional


class Trabajador:
    """Representa a un trabajador (jugador o IA) en el mapa.

    Proporciona métodos para movimiento, renderizado y cálculo de velocidad
    teniendo en cuenta el clima y el peso del inventario.
    """

    contador = False

    def __init__(
        self,
        mapa_width: int,
        mapa_height: int,
        cell_size: int,
        peso_maximo: int = 5,
        velocidad_estandar: int = 3,
        ruta_imagen: str = "assets/trabajador.png",
    ) -> None:
        self.mapa_width = mapa_width
        self.mapa_height = mapa_height
        self.cell_size = cell_size
        self.pedido_actual = None

        self.inventario = Inventario(peso_maximo)
        self.estado = EstadoTrabajador()
        self.entregados = []

        self.velocidad_estandar = velocidad_estandar

        self.trabajador_original = pygame.image.load(ruta_imagen)
        self.trabajador = pygame.transform.scale(self.trabajador_original, (40, 40))
        self.trabajadorRect = self.trabajador.get_rect()
        self.trabajadorRect.center = (mapa_width // 2 * cell_size, mapa_height // 2 * cell_size)

        self.movio = False
        # Debug: ruta planeada (lista de (x,y) en celdas) y flag de visualización
        self._debug_ruta = []
        self._debug_enabled = False

        self.plan_movimientos = []
        self.objetivo_medio = None
        self.cooldown_movimiento = 0 
        self.DELAY_MOVIMIENTO = 0.2

        self.historial_pos = []
        self.max_historial = 6

        self.contador_bloqueos = 0
        self.max_bloqueos = 3

    def es_transitable(self, rect: pygame.Rect, mapa: Any) -> bool:
        """Comprueba si el rect es transitables (no está dentro de un edificio)."""
        puntos = [
            rect.topleft,
            rect.topright,
            rect.bottomleft,
            rect.bottomright,
            rect.center,
            (rect.left + rect.width // 2, rect.top),
            (rect.left + rect.width // 2, rect.bottom),
            (rect.left, rect.top + rect.height // 2),
            (rect.right, rect.top + rect.height // 2),
        ]
        
        # Contar cuántos puntos están en terreno válido (calles C o parques P)
        puntos_validos = 0
        total_puntos = len(puntos)
        
        for x, y in puntos:
            x_celda = int(x / self.cell_size)
            y_celda = int(y / self.cell_size)
            celda = mapa.obtener_celda(x_celda, y_celda)
            
            # Si está en calle o parque, es válido
            if celda in ["C", "P"]:
                puntos_validos += 1
            # Si está en edificio o espacio, es inválido
            elif celda in ["B", " "] or (isinstance(celda, str) and celda.startswith("B_")):
                continue
            # Para otros terrenos, asumimos válido
            else:
                puntos_validos += 1
        
        # Permitir movimiento si al menos el 60% de los puntos están en terreno válido
        # Esto permite cierta tolerancia en los bordes de parques
        return puntos_validos >= (total_puntos * 0.6)

    def obtener_estado(self) -> dict:
        """Devuelve un dict serializable con el estado actual del trabajador."""
        return {
            "pedido_actual": self.pedido_actual,
            "inventario": copy.deepcopy(self.inventario),
            "ingresos": self.estado.ingresos,
            "reputacion": self.estado.reputacion,
            "resistencia": self.estado.resistencia,
            "entregados": self.entregados.copy(),
            "trabajadorRect": self.trabajadorRect.copy(),
        }

    def restaurar_estado(self, estado_guardado: dict, entregados: list) -> None:
        """Restaura el estado del trabajador desde un dict guardado."""
        self.pedido_actual = estado_guardado["pedido_actual"]
        self.inventario = copy.deepcopy(estado_guardado["inventario"])
        self.estado.ingresos = estado_guardado["ingresos"]
        self.estado.reputacion = estado_guardado["reputacion"]
        self.estado.resistencia = estado_guardado["resistencia"]
        self.entregados = entregados
        self.trabajadorRect = estado_guardado["trabajadorRect"]

    def obtener_velocidad(self, clima: Any, mapa: Any) -> float:
        """Calcula la velocidad actual teniendo en cuenta varios modificadores."""
        efecto_clima = clima.efecto_trabajador()
        clima_velocidad = efecto_clima.get("velocidad", 1.0)
        peso_velocidad = max(0.8, 1 - 0.03 * self.inventario.peso_actual)
        reputacion_velocidad = 1.03 if self.estado.reputacion >= 90 else 1.0

        resistencia = self.estado.resistencia
        if resistencia > 30:
            resistencia_velocidad = 1.0
        elif 10 <= resistencia <= 30:
            resistencia_velocidad = 0.8
        else:
            resistencia_velocidad = 0.0

        x = int(self.trabajadorRect.centerx / self.cell_size)
        y = int(self.trabajadorRect.centery / self.cell_size)
        celda_actual = mapa.obtener_celda(x, y)
        leyenda = mapa.legend.get(celda_actual)
        surface_weight = leyenda.get("surface_weight", 1.0) if isinstance(leyenda, dict) else 1.0

        velocidad = (
            self.velocidad_estandar
            * clima_velocidad
            * peso_velocidad
            * reputacion_velocidad
            * resistencia_velocidad
            * surface_weight
        )
        return velocidad

    def dibujar(self, pantalla: pygame.Surface) -> None:
        """Dibuja el trabajador en la superficie dada."""
        # Dibujar ruta de debug (si está activada) antes de dibujar al trabajador
        if self._debug_enabled and self._debug_ruta:
            # color del camino y tamaño del rect (ligera reducción para ver bordes)
            color_camino = (255, 0, 0)
            color_objetivo = (0, 255, 0)
            pad = max(1, int(self.cell_size * 0.15))
            for idx, (cx, cy) in enumerate(self._debug_ruta):
                rect = pygame.Rect(
                    cx * self.cell_size + pad,
                    cy * self.cell_size + pad,
                    self.cell_size - 2 * pad,
                    self.cell_size - 2 * pad,
                )
                # último elemento es el objetivo
                if idx == len(self._debug_ruta) - 1:
                    pygame.draw.rect(pantalla, color_objetivo, rect)
                else:
                    pygame.draw.rect(pantalla, color_camino, rect)

        pantalla.blit(self.trabajador, self.trabajadorRect)

    def set_debug_mode(self, enabled: bool) -> None:
        """Activa/desactiva el modo debug para visualizar la ruta planeada."""
        self._debug_enabled = bool(enabled)

    def _set_debug_ruta(self, ruta: List[Tuple[int, int]]) -> None:
        """Establece (internamente) la ruta que será mostrada en modo debug."""
        self._debug_ruta = ruta or []

    def mover_una_celda(self, key: int, clima: Any, dt: float, velocidad: float, mapa: Any) -> None:
        """Mueve al trabajador una celda en la dirección indicada si es posible."""
        self.movio = False

        if self.estado.resistencia == 0:
            Trabajador.contador = True
            self.estado.recuperar_resistencia(dt)
            return
        if self.estado.resistencia < 30 and Trabajador.contador:
            self.estado.recuperar_resistencia(dt)
            return

        Trabajador.contador = False
        dx, dy = 0, 0

        if key == pygame.K_UP:
            dy = -1
            self.movio = True
        elif key == pygame.K_DOWN:
            dy = 1
            self.movio = True
        elif key == pygame.K_LEFT:
            dx = -1
            self.movio = True
        elif key == pygame.K_RIGHT:
            dx = 1
            self.movio = True

        nuevo_rect = self.trabajadorRect.copy()
        nuevo_rect.move_ip(dx * self.cell_size, dy * self.cell_size)

        if self.es_transitable(nuevo_rect, mapa):
            self.trabajadorRect = nuevo_rect
            self.estado.consumir_resistencia(clima, self.inventario.peso_actual, dt)
        else:
            self.movio = False

        self.trabajadorRect.clamp_ip((0, 0, self.mapa_width * self.cell_size, self.mapa_height * self.cell_size))

        if not self.movio:
            self.estado.recuperar_resistencia(dt)


    def nivel_facil_ia(self, clima: Any, dt: float, mapa: Any, pedidos: Any) -> None:
        """IA fácil: movimiento simple + recoger/entregar cuando esté cerca."""

        x_actual = int(self.trabajadorRect.centerx / self.cell_size)
        y_actual = int(self.trabajadorRect.centery / self.cell_size)

        # 1. SI ESTÁ CERCA DE PICKUP → RECOGER 
        recogio_algo = False

        for p in pedidos.obtener_todos_los_pedidos():
            if p.esta_cerca(self.trabajadorRect, p.pickup, self.cell_size):
                if self.inventario.peso_actual + p.weight <= self.inventario.peso_maximo:
                    aceptado = pedidos.aceptar_pedido_especifico(p)
                    if aceptado:
                        if self.inventario.agregar_pedido(aceptado):
                            p.recogido = True
                            recogio_algo = True
                break  # solo revisar un pedido

        # 2. SI ESTÁ CERCA DE DROPOFF → ENTREGAR
        pedidos_inv = self.inventario.todos_los_pedidos()

        if pedidos_inv:
            pedido_actual = pedidos_inv[0]
            x_obj, y_obj = pedido_actual.dropoff

            if x_actual == x_obj and y_actual == y_obj:
                pedido_actual.verificar_interaccion(
                    self.trabajadorRect,
                    self.cell_size,
                    self.inventario,
                    self.estado,
                    0
                )
                return  

        # SI TIENE PEDIDOS → IR AL DROPOFF
        if pedidos_inv:
            pedido_actual = pedidos_inv[0]
            x_obj, y_obj = pedido_actual.dropoff

            movimientos = []

            if x_obj > x_actual: movimientos.append(pygame.K_RIGHT)
            elif x_obj < x_actual: movimientos.append(pygame.K_LEFT)

            if y_obj > y_actual: movimientos.append(pygame.K_DOWN)
            elif y_obj < y_actual: movimientos.append(pygame.K_UP)

            # Intentar movimientos hacia destino
            for tecla in movimientos:
                if self._intento_movimiento(tecla, clima, dt, mapa):
                    self.contador_bloqueos = 0  # se movió, reset
                    return
                else:
                    self.contador_bloqueos += 1

            # Si está bloqueado muchas veces, hacer escape
            if self.contador_bloqueos >= self.max_bloqueos:
                self.contador_bloqueos = 0
                ruta_escape = self._calcular_escape(x_actual, y_actual, mapa)
                if ruta_escape:
                    mov = ruta_escape[0]
                    self._intento_movimiento(mov, clima, dt, mapa)
                    return

            # Si no pudo, movimiento aleatorio
            if self._mover_aleatorio(clima, dt, mapa):
                self.contador_bloqueos = 0
            return

        # SIN PEDIDOS: MOVIMIENTO ALEATORIO SIEMPRE
        if self._mover_aleatorio(clima, dt, mapa):
            self.contador_bloqueos = 0

    def _intento_movimiento(self, tecla, clima, dt, mapa):
        dx, dy = 0, 0
        if tecla == pygame.K_UP: dy = -1
        elif tecla == pygame.K_DOWN: dy = 1
        elif tecla == pygame.K_LEFT: dx = -1
        elif tecla == pygame.K_RIGHT: dx = 1

        prueba_rect = self.trabajadorRect.copy()
        prueba_rect.move_ip(dx * self.cell_size, dy * self.cell_size)

        if self.es_transitable(prueba_rect, mapa):
            self.mover_una_celda(tecla, clima, dt, self.obtener_velocidad(clima, mapa), mapa)
            return True
        return False


    def _mover_aleatorio(self, clima, dt, mapa):
        direcciones = [pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT]
        random.shuffle(direcciones)

        for tecla in direcciones:
            if self._intento_movimiento(tecla, clima, dt, mapa):
                return True
        return False

    def _a_estrella_matriz(self, matriz, inicio: Tuple[int, int], destino: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Algoritmo A* sobre la matriz devuelta por mapa.obtener_matriz().

        Args:
            matriz: numpy ndarray con shape (height, width) y caracteres.
            inicio: tupla (x, y)
            destino: tupla (x, y)

        Retorna:
            Lista de tuplas (x, y) desde inicio hasta destino (incluidos). Si no
            hay ruta, retorna lista vacía.
        """
        # Validar
        if inicio == destino:
            return [inicio]

        ancho = matriz.shape[1]
        alto = matriz.shape[0]

        def es_valida(x, y):
            if 0 <= x < ancho and 0 <= y < alto:
                celda = matriz[y][x]
                # Aceptar calles (C), parques (P), y rechazar edificios (B, B_...) y espacios
                if celda in ("C", "P"):
                    return True
                # Bloquear edificios individuales, bloques procesados y espacios
                if celda == "B" or celda == " " or (isinstance(celda, str) and celda.startswith("B_")):
                    return False
                # Por defecto permitir (en caso de otros tipos de terreno)
                return True
            return False

        def heuristica(a: Tuple[int, int], b: Tuple[int, int]) -> int:
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        start = inicio
        goal = destino

        open_heap = []
        heapq.heappush(open_heap, (heuristica(start, goal), 0, start))

        came_from = {}
        g_score = {start: 0}

        closed = set()

        while open_heap:
            _, current_g, current = heapq.heappop(open_heap)
            if current in closed:
                continue
            if current == goal:
                # reconstruir ruta
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                path.reverse()
                return path

            closed.add(current)

            x, y = current
            for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
                nx, ny = x + dx, y + dy
                neigh = (nx, ny)
                if not es_valida(nx, ny) and neigh != goal:
                    # permitir que destino sea una celda especial si está marcada como transitable
                    continue

                tentative_g = g_score.get(current, float('inf')) + 1
                if tentative_g < g_score.get(neigh, float('inf')):
                    came_from[neigh] = current
                    g_score[neigh] = tentative_g
                    f = tentative_g + heuristica(neigh, goal)
                    heapq.heappush(open_heap, (f, tentative_g, neigh))

        return []
    
    def nivel_medio_ia(self, clima, dt, mapa, pedidos):
        """IA nivel medio:
        - Utiliza greedy lookahead con planificación limitada (DFS con max_depth=7).
        - Prioriza entregar pedidos ya recogidos.
        - Luego intenta recoger nuevos pedidos.
        - Mantiene comportamiento no óptimo pero suficientemente competente.
        """

        # Actualizar cooldown
        if self.cooldown_movimiento > 0:
            self.cooldown_movimiento -= dt
            return

        # PRIORIDAD 1: Entregar pedidos que ya hay
        for pedido in self.inventario.todos_los_pedidos():
            if pedido.recogido and not pedido.entregado:
                x0 = int(self.trabajadorRect.centerx / self.cell_size)
                y0 = int(self.trabajadorRect.centery / self.cell_size)
                objetivo = pedido.dropoff

                # --- CONTROL ANTI-BUCLE (DROP-OFF) ---
                pos_actual = (x0, y0)
                self.historial_pos.append(pos_actual)

                if len(self.historial_pos) > self.max_historial:
                    self.historial_pos.pop(0)

                # Si se cumple es que esta entrando en un bucle
                if self.historial_pos.count(pos_actual) >= 3:
                    # Forzar escape
                    self.plan_movimientos = self._calcular_escape(x0, y0, mapa)

                # Revisa si esta cerca de la entrega
                if pedido.esta_cerca(self.trabajadorRect, objetivo, self.cell_size):
                    # Entregar el pedido
                    pedido.verificar_interaccion(
                        self.trabajadorRect,
                        self.cell_size,
                        self.inventario,
                        self.estado,
                        0
                    )
                    self.objetivo_medio = None
                    self.plan_movimientos = []
                    return

                # Replanificar ruta hacia dropoff
                if self.objetivo_medio != objetivo or not self.plan_movimientos:
                    self.objetivo_medio = objetivo
                    self.plan_movimientos = self._calcular_movimientos(x0, y0, objetivo, mapa)

                # Ejecutar movimiento
                if self.plan_movimientos:
                    mov = self.plan_movimientos.pop(0)
                    self.mover_una_celda(mov, clima, dt, self.obtener_velocidad(clima, mapa), mapa)
                    self.cooldown_movimiento = self.DELAY_MOVIMIENTO
                return

        # PRIORIDAD 2: Recoger nuevos pedidos
        lista = pedidos.obtener_todos_los_pedidos()
        if not lista:
            return

        x0 = int(self.trabajadorRect.centerx / self.cell_size)
        y0 = int(self.trabajadorRect.centery / self.cell_size)

        # --- CONTROL ANTI-BUCLE ---
        pos_actual = (x0, y0)
        self.historial_pos.append(pos_actual)

        if len(self.historial_pos) > self.max_historial:
            self.historial_pos.pop(0)

        if self.historial_pos.count(pos_actual) >= 3:
            self.plan_movimientos = self._calcular_escape(x0, y0, mapa)

        # objetivo con mejor pago
        mejor_p = max(lista, key=lambda p: p.payout)
        objetivo = mejor_p.pickup

        if mejor_p.esta_cerca(self.trabajadorRect, objetivo, self.cell_size):
            if self.inventario.peso_actual + mejor_p.weight <= self.inventario.peso_maximo:
                pedido_aceptado = pedidos.aceptar_pedido_especifico(mejor_p)
                if pedido_aceptado:
                    agregado = self.inventario.agregar_pedido(pedido_aceptado)
                    if agregado:
                        pedido_aceptado.recogido = True
            self.objetivo_medio = None
            self.plan_movimientos = []
            return

        if self.objetivo_medio != objetivo or not self.plan_movimientos:
            self.objetivo_medio = objetivo
            self.plan_movimientos = self._calcular_movimientos(x0, y0, objetivo, mapa)

        if self.plan_movimientos:
            mov = self.plan_movimientos.pop(0)
            self.mover_una_celda(mov, clima, dt, self.obtener_velocidad(clima, mapa), mapa)
            self.cooldown_movimiento = self.DELAY_MOVIMIENTO
   

    def _calcular_movimientos(self, x0, y0, objetivo, mapa, max_depth=7):
        """Greedy lookahead con horizonte de 7 pasos (DFS limitada). """
        moves = [
            (pygame.K_UP,    (0, -1)),
            (pygame.K_DOWN,  (0, 1)),
            (pygame.K_LEFT,  (-1, 0)),
            (pygame.K_RIGHT, (1, 0)),
        ]

        def es_valido(nx, ny):
            rect = self.trabajadorRect.copy()
            rect.centerx = nx * self.cell_size
            rect.centery = ny * self.cell_size
            return self.es_transitable(rect, mapa)

        mejor_score = float("inf")
        mejor_secuencia = []

        def dfs(px, py, depth, secuencia):
            nonlocal mejor_score, mejor_secuencia

            # ancho de búsqueda limitado
            if depth == max_depth:
                dist = abs(px - objetivo[0]) + abs(py - objetivo[1])
                if dist < mejor_score:
                    mejor_score = dist
                    mejor_secuencia = secuencia.copy()
                return

            # expansión greedy: probar primero movimientos que acercan más
            movs_ordenados = []
            for key, (dx, dy) in moves:
                nx, ny = px + dx, py + dy
                if not es_valido(nx, ny):
                    continue
                d = abs(nx - objetivo[0]) + abs(ny - objetivo[1])
                movs_ordenados.append((d, key, nx, ny))

            movs_ordenados.sort(key=lambda t: t[0])

            # probar hasta 3 movimientos más prometedores
            for _, key, nx, ny in movs_ordenados[:3]:
                dfs(nx, ny, depth + 1, secuencia + [key])

        # lanzar DFS
        dfs(x0, y0, 0, [])

        return mejor_secuencia

    def _calcular_escape(self, x0, y0, mapa):
        """Salir de bucles moviendose a una celda valida aleatoria."""
        moves = [
            (pygame.K_UP, (0, -1)),
            (pygame.K_DOWN, (0, 1)),
            (pygame.K_LEFT, (-1, 0)),
            (pygame.K_RIGHT, (1, 0)),
        ]

        random.shuffle(moves)

        for key, (dx, dy) in moves:
            nx, ny = x0 + dx, y0 + dy
            rect = self.trabajadorRect.copy()
            rect.centerx = nx * self.cell_size
            rect.centery = ny * self.cell_size

            if self.es_transitable(rect, mapa):
                return [key]  # hace un movimiento para salir del bucle
        return []


    def nivel_dificil_ia(self, clima: Any, dt: float, mapa: Any, pedidos: Any) -> None:
        """IA difícil: selecciona el pedido más cercano y usa A* para planear.

        Comportamiento:
        - Si tiene pedidos en inventario, apunta al dropoff más cercano.
        - Si no, busca el pickup más cercano entre los pedidos publicados.
        - Calcula ruta con A* y avanza una celda por ciclo (si tiene resistencia).
        - Al llegar al pickup intenta agregarlo al inventario y marcarlo aceptado.
        - Al llegar al dropoff marca entregado.
        """
        # Controlar velocidad de movimiento - solo mover cada cierto tiempo
        if not hasattr(self, '_tiempo_ultimo_movimiento_ia'):
            self._tiempo_ultimo_movimiento_ia = 0
        
        # Intervalo de movimiento (en segundos) - ajustar para controlar velocidad
        intervalo_movimiento = 0.05  # La IA se mueve cada 0.05 segundos (más rápido que antes)
        
        self._tiempo_ultimo_movimiento_ia += dt
        if self._tiempo_ultimo_movimiento_ia < intervalo_movimiento:
            return  # No es momento de moverse
        
        # Reset del timer
        self._tiempo_ultimo_movimiento_ia = 0
        # obtener matriz y posición actual en celdas
        try:
            matriz = mapa.obtener_matriz()
        except Exception:
            return

        x = int(self.trabajadorRect.centerx / self.cell_size)
        y = int(self.trabajadorRect.centery / self.cell_size)
        inicio = (x, y)

        objetivo: Optional[Tuple[int, int]] = None
        objetivo_pedido = None

        # Si hay pedidos en inventario -> ir al dropoff más cercano
        pedidos_inventario = self.inventario.todos_los_pedidos()
        if pedidos_inventario:
            # elegir el dropoff más cercano (Manhattan)
            mejor = None
            mejor_dist = None
            for p in pedidos_inventario:
                dest = p.dropoff
                dist = abs(dest[0] - x) + abs(dest[1] - y)
                if mejor_dist is None or dist < mejor_dist:
                    mejor_dist = dist
                    mejor = (dest[0], dest[1])
                    objetivo_pedido = p
            objetivo = mejor
        else:
            # elegir pickup más cercano entre pedidos visibles (pendientes)
            pendientes = pedidos.obtener_todos_los_pedidos()
            if pendientes:
                mejor = None
                mejor_dist = None
                # pedidos.obtener_todos_los_pedidos() devuelve lista de Pedido
                for p in pendientes:
                    dest = p.pickup
                    dist = abs(dest[0] - x) + abs(dest[1] - y)
                    if mejor_dist is None or dist < mejor_dist:
                        mejor_dist = dist
                        mejor = (dest[0], dest[1])
                        objetivo_pedido = p
                objetivo = mejor

        if objetivo is None:
            # nada que hacer
            return

        # calcular ruta con A*
        try:
            ruta = self._a_estrella_matriz(matriz, inicio, objetivo)
        except Exception:
            ruta = []

        # guardar ruta para modo debug (aunque esté desactivado por defecto)
        try:
            self._set_debug_ruta(ruta)
        except Exception:
            # no crítico si falla el debug
            pass

        if not ruta or len(ruta) < 2:
            # si no hay ruta válida o estoy junto al objetivo, permitir interacción
            if objetivo_pedido is not None:
                try:
                    cerca = objetivo_pedido.esta_cerca(self.trabajadorRect, objetivo, self.cell_size)
                except Exception:
                    # fallback a comparación exacta
                    cerca = inicio == objetivo

                if cerca:
                    # interacción: pickup o dropoff
                    if not objetivo_pedido.recogido:
                        # intentar agregar al inventario
                        if self.inventario.agregar_pedido(objetivo_pedido):
                            pedidos.aceptar_pedido_especifico(objetivo_pedido)
                            objetivo_pedido.recogido = True
                    else:
                        if objetivo_pedido.recogido and not objetivo_pedido.entregado:
                            objetivo_pedido.entregado = True
                            self.inventario.marcar_entregado(objetivo_pedido)
                            self.entregados.append(objetivo_pedido.id)
                    return
            return

        # mover un paso hacia el siguiente nodo de la ruta
        siguiente = ruta[1]
        dx = siguiente[0] - x
        dy = siguiente[1] - y

        tecla = None
        if dx == 1 and dy == 0:
            tecla = pygame.K_RIGHT
        elif dx == -1 and dy == 0:
            tecla = pygame.K_LEFT
        elif dx == 0 and dy == 1:
            tecla = pygame.K_DOWN
        elif dx == 0 and dy == -1:
            tecla = pygame.K_UP

        if tecla is not None:
            # Intentar mover en la dirección prevista
            self.mover_una_celda(tecla, clima, dt, self.obtener_velocidad(clima, mapa), mapa)

            # Si no se movió (bloqueado por colisión), intentar movimientos alternativos
            if not self.movio:
                # generar alternativas ordenadas por cercanía al objetivo
                alternativas = []
                x0, y0 = x, y
                vecinos = [((1, 0), pygame.K_RIGHT), ((-1, 0), pygame.K_LEFT), ((0, 1), pygame.K_DOWN), ((0, -1), pygame.K_UP)]
                for (dx_a, dy_a), tecla_a in vecinos:
                    nx, ny = x0 + dx_a, y0 + dy_a
                    # distancia heurística al objetivo
                    dist = abs(nx - objetivo[0]) + abs(ny - objetivo[1]) if objetivo is not None else 0
                    alternativas.append((dist, tecla_a, nx, ny))
                alternativas.sort(key=lambda t: t[0])

                for _, tecla_a, nx, ny in alternativas:
                    prueba_rect = self.trabajadorRect.copy()
                    # mover el rect de prueba *sin* cambiar self.trabajadorRect
                    if tecla_a == pygame.K_UP:
                        prueba_rect.move_ip(0, -self.cell_size)
                    elif tecla_a == pygame.K_DOWN:
                        prueba_rect.move_ip(0, self.cell_size)
                    elif tecla_a == pygame.K_LEFT:
                        prueba_rect.move_ip(-self.cell_size, 0)
                    elif tecla_a == pygame.K_RIGHT:
                        prueba_rect.move_ip(self.cell_size, 0)

                    if self.es_transitable(prueba_rect, mapa):
                        self.mover_una_celda(tecla_a, clima, dt, self.obtener_velocidad(clima, mapa), mapa)
                        if self.movio:
                            break

        # La IA solo se mueve al objetivo, la lógica automática del main.py
        # se encarga de recoger/entregar pedidos cuando esté cerca
