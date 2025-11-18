# Courier Quest, Repartidor en TigerCity
Courier Quest es un simulador donde el jugador controla a un repartidor que debe navegar por una ciudad, recoger pedidos y entregarlos a tiempo, mientras compite contra un **agente de Inteligencia Artificial (IA)**.  
El objetivo del juego es **superar a la IA** generando más ingresos dentro de un tiempo límite.


# Modo Competitivo Humano vs IA

En esta fase del proyecto, el jugador humano compite directamente contra una IA. Ambos:

- Reciben los mismos pedidos.
- Tienen resistencia, reputación e inventario independientes.
- Se mueven por el mismo mapa.
- Seleccionan, recogen y entregan pedidos bajo las mismas reglas.

El ganador final es **quien acumule más ingresos**.

# Condiciones de Victoria y Derrota

## Victoria
El jugador humano gana si:

- Al terminar el tiempo tiene **más ingresos que la IA**, o  
- Ya no quedan pedidos y **su ingreso es mayor al de la IA**.

## Derrota
El jugador humano pierde si:

- Su **reputación baja de 20** (derrota inmediata).  
- Finaliza el tiempo y la **IA tiene más ingresos**.  
- No quedan pedidos y la **IA tiene más ingresos**.

## Empate
Si ambos tienen exactamente los mismos ingresos al finalizar la partida. 

# Factores del juego
- **Resistencia:** Disminuye al moverse y se ve más afectada cuando hay peso o un clima díficil. Cuando esta llega a 0 debe de descansar para recuperarse.
- **Reputación:** Aumenta al entregar pedidos a tiempo (+10) y disminuye si se entregan tarde (-5) o si se rechaza un pedido (-3). Una reputación alta (>= 90) otorga un bonus del 5% al pago de los pedidos 
- **Inventario:** El inventario tiene un peso máximo, no se pueden agregar más pedidos al inventario si se sobrepasa ese peso. 
- **Clima:** El clima cambia periódicamente (cada 45-60 segundos) y afecta la velocidad y resistencia del trabajador.

# Controles y teclas
| Tecla | Acción               | Descripción |
| :---: | :---                 | :--- |
| **↑** | Mover arriba         | Desplaza al trabajador una celda hacia arriba.                                                                               |
| **↓** | Mover abajo          | Desplaza al trabajador una celda hacia abajo.                                                                                |
| **←** | Mover izquierda      | Desplaza al trabajador una celda a la izquierda.                                                                             |
| **→** | Mover derecha        | Desplaza al trabajador una celda a la derecha.                                                                               |
| **A** | **Aceptar Pedido**   | Intenta tomar el pedido de mayor prioridad de la lista de solicitudes. Fallará si excede el peso máximo del inventario.      |
| **R** | **Rechazar Pedido**  | Descarta el pedido de mayor prioridad. Reduce la reputación del trabajador en 3 puntos.                                      |
| **P** | **Lista Prioridad**  | Visualiza los pedidos en el inventario ordenados por **Prioridad** (la de mayor prioridad primero).                          |
| **O** | **Lista Entrega**    | Visualiza los pedidos en el inventario ordenados por **Hora de entrga** (la más cercana primero).                            |
| **S** | **Guardar Partida**  | Guarda el estado actual de la partida en un archivo. |
| **L** | **Cargar Partida**   | Carga la partida anterior y se puede seguir jugando.                   |
| **U** | **Retroceder pasos**   | Permite retroceder los pasos anteriores.                   |


# Inteligencia Artificial (IA)

La IA tiene **tres niveles de dificultad**:

## Nivel Fácil
- Movimiento aleatorio.
- Selección aleatoria de pedidos.
- Evita edificios de forma básica.

## Nivel Medio — Greedy Lookahead (DFS Limitada)

La IA evalúa movimientos futuros usando una función heurística basada en:

- distancia Manhattan  
- clima  
- recompensas esperadas

### Horizonte de anticipación (max_depth)

Aunque la guía del proyecto sugiere usar 2–3 acciones de anticipación, en el mapa real esto causaba muchos ciclos.  
Por ello, se ajustó a: `max_depth` = 7

Esto evita bucles, mantiene un comportamiento intermedio y no convierte al agente en un planificador completo.

## Nivel Difícil — Búsqueda Óptima

- Modela la ciudad como un grafo ponderado.
- Usa algoritmos como:
  - **Dijkstra**
  - **A\***
  - **BFS ponderado**
- Replanifica cuando cambia el clima o las condiciones.
- Selecciona rutas y secuencias de entregas óptimas.

# Estructuras de Datos que se utilizaron
### 1. Lista Doblemente Enlazada (Inventario)

| Clase | Uso | Detalle de Implementación | Complejidad de Operaciones |
| :--- | :--- | :--- | :--- |
| **`Inventario`** | Almacena los pedidos que el trabajador ha **aceptado** y debe entregar. | Utiliza la clase `PedidoNodo` para formar una lista doblemente enlazada, que permite la navegación bidireccional entre pedidos. | `agregar_pedido()`: $O(1)$. `quitar_pedido()` / `marcar_entregado()`: $O(n)$ (búsqueda). |

### 2. Cola de Prioridad (Heap - Pedidos Disponibles)

| Clase | Uso | Detalle de Implementación | Complejidad de Operaciones |
| :--- | :--- | :--- | :--- |
| **`Pedidos`** | Almacena la lista de pedidos disponibles de la API, priorizando cuáles ofrecer al jugador. | Utiliza el módulo **`heapq`** de Python. Los pedidos se insertan con una tupla de prioridad `(-priority, index, pedido)` para simular una **Max-Heap** basada en la prioridad del pedido. | `procesar_pedidos()`: $O(n \log n)$ (por los $n$ `heappush`). `obtener_siguiente_pedido()`: $O(1)$ (el elemento raíz). `aceptar_pedido()` / `rechazar_pedido()`: $O(\log n)$ (por `heappop`). |

### 3. Matriz (Mapa)

| Clase | Uso | Detalle de Implementación | Complejidad de Operaciones |
| :--- | :--- | :--- | :--- |
| **`Mapa`** | Representa la cuadrícula de la ciudad, incluyendo calles, edificios y parques. | La cuadrícula (`self.grid`) es una **lista de listas** de caracteres. El método `obtener_matriz()` utiliza **NumPy** para convertir esto en una matriz $N \times M$ para procesamiento eficiente. | `obtener_celda(x, y)`: $O(1)$ (acceso directo a la posición $[y][x]$). `procesar_cuadricula()`: $O(N \cdot M)$ (recorrido completo de la matriz para identificar y marcar bloques de edificios). |

### 4. Diccionarios (Mapas de Transición y caché)

| Clase | Uso | Detalle de Implementación | Complejidad de Operaciones |
| :--- | :--- | :--- | :--- |
| **`ClimaMarkov`** | Define la lógica para el cambio de clima. | Utiliza un diccionario anidado (`self.transition`) donde la clave es el estado actual del clima y el valor es otro diccionario con los posibles siguientes estados y sus probabilidades. | `siguiente_estado()`: $O(k)$ (donde $k$ es el número de posibles estados de transición). |
| **`ApiClient`** | Implementa un mecanismo de "modo offline". | Utiliza un directorio (`self.cache_dir`) y archivos `.json` para guardar la última respuesta de la API (mapa, trabajos) como caché. Esto se implementa con la función `json.dump()` y `json.load()`. | `guardar_en_cache()` / `cargar_desde_cache()`: $O(T)$ (donde $T$ es el tamaño de los datos en caché, generalmente rápido para archivos pequeños). |

### 5. Algoritmos de Ordenamiento

| Clase | Uso | Detalle de Implementación | Complejidad de Operaciones |
| :--- | :--- | :--- | :--- |
| **`Inventario`** | Visualización ordenada de pedidos para el panel lateral. | Utiliza la función `sorted()` de Python con una función `lambda`. | `visualizar_por_prioridad()` / `visualizar_por_entrega()`: $O(n \log n)$ (debido al uso de `sorted()`). |

# Finalización del Juego

El juego termina por:

1. **Derrota inmediata:** reputación < 20  
2. **Fin del tiempo:** gana quien tenga más ingresos  
3. **Sin pedidos disponibles:** gana quien tenga más ingresos  
4. **Empate:** ingresos iguales

# Mejoras Técnicas Implementadas
Durante esta fase del proyecto se realizaron mejoras estructurales importantes que garantizan estabilidad, consistencia del tiempo de juego y compatibilidad multiplataforma.
## 1. Manejo de Tiempo Relativo para Entregas
Originalmente, las entregas se evaluaban usando el tiempo real del sistema (time.time()), lo que producía errores como: 
- pedidos marcados como “tarde” al cargar la partida
- pedidos identificados como tardíos al iniciar el juego con retraso

*Solución Implementada*
Ahora el juego utiliza tiempo relativo interno, es decir, el tiempo empieza en 0 cuando inicia la partida, se incrementa con cada ciclo del juego (dt) y todas las comparaciones de entrega se basan en este tiempo virtual.

## 2. Crash en macOS (NSException)
En la retroalimentación del primer proyecto se brindó lo siguiente:
"Crash en medio juego: libc++abi: terminating due to uncaught exception of type NSException"

Se le preguntó a una IA a qué se debía ese error y lo que respondió es que una de las posibles causas era por cómo se manejan los hilos de Pygame y Tkinter en macOS (Se adjunta el prompt y la respuesta en el documeento de prompts).

*Solución implementada*
A pesar de que ninguna de las integrantes del grupo trabaja con macOS se implementaron medidas de seguridad para tratar de evitar el crash:
1. Verificación de existencia de ventanas con `winfo_exists()`.
2. `try/except/finally` en todas las operaciones GUI (Tkinter + diálogos).
3. Inicialización segura de Pygame (`pygame.get_init()`) en `visualizador.py`.
4. Variables de entorno SDL para evitar conflictos en macOS.
5. Limpieza controlada de ventanas evitando dobles destrucciones.
6. Manejo seguro del cierre en el bloque `__main__`.

# Notas Técnicas

- Escrito en **Python 3**.  
- Cumple con PEP8.  
- Documentado con docstrings.  
