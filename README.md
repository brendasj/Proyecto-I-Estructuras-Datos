# Courier Quest, Repartidor en TigerCity
Este proyecto simula la vida de un repartidor en una ciudad. El objetivo principal es alcanzar la meta de ingresos por medio de los pedidos y la recompensas. Debe de recoger y entregar el pedido en diferentes locaciones mientras algunos factores como el peso y el clima influyen su resistencia y reputación. 

# Factores de derrota 
Se pierde la partida si:
1. La reputación es menor a 20
2. Cuando todos los pedidos hayan sido gestionados pero no se ha alcanzado la meta de ingresos indicada. 

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

## SEGUNDO PROYECTO (CONTINUACIÓN)

Descripción del Proyecto:

Esta segunda fase del proyecto Courier Quest incorpora un jugador controlado por inteligencia artificial (IA), que competirá contra el jugador humano para realizar entregas dentro de una ciudad simulada. El objetivo es diseñar e implementar tres niveles de dificultad para la IA, cada uno utilizando diferentes técnicas de búsqueda, estructuras de datos y estrategias de decisión.

Objetivos de Aprendizaje:

- Aplicar estructuras de datos lineales y no lineales como listas, colas, árboles, grafos y colas de prioridad.
- Implementar algoritmos de búsqueda y decisión adaptados al contexto del juego.
- Analizar la eficiencia de distintos enfoques de IA.
- Desarrollar un agente autónomo que se comporte de manera coherente y competitiva.
Jugabilidad
El sistema debe incluir al menos un jugador controlado por IA que:
- Reciba la misma información del mapa, clima y solicitudes de entrega que el jugador humano.
- Pueda desplazarse por la ciudad, recoger y entregar pedidos siguiendo las reglas del juego.
- Tenga su propia barra de resistencia, reputación y capacidad de carga.
- Pueda ser configurado en tres niveles de dificultad: fácil, medio y difícil.

Niveles de Dificultad de la IA:

En el nivel fácil, la IA toma decisiones aleatorias. Elige un trabajo disponible al azar y se mueve en direcciones aleatorias evitando edificios. Ocasionalmente, vuelve a lanzar el objetivo después de un tiempo límite o al completar una entrega. Este nivel utiliza lógica probabilística simple y estructuras como listas y colas.

En el nivel medio, la IA evalúa movimientos futuros en función de una puntuación heurística. Mantiene un horizonte de anticipación pequeño (2 o 3 acciones por delante) y calcula una puntuación para cada movimiento posible usando una fórmula como:
score = a * (ganancia esperada) - ß * (costo de distancia) - y * (penalización por clima)
Luego selecciona el movimiento con la puntuación más alta. Se puede implementar con algoritmos como búsqueda greedy, minimax simplificado o expectimax.

En el nivel difícil, la IA busca rutas óptimas entre entregas considerando costos y condiciones climáticas. Se representa la ciudad como un grafo ponderado, donde el peso de cada superficie se usa como costo de arista. Se pueden aplicar algoritmos como Dijkstra, A* o BFS ponderado. Además, se puede integrar replanificación dinámica si el clima empeora o si la resistencia del jugador es baja. También se debe incluir lógica para elegir la secuencia de entregas que minimice los desplazamientos y maximice las ganancias.

Requisitos Técnicos:

El código debe estar escrito en Python, cumplir con las normas PEP8 y estar debidamente documentado utilizando docstrings. La documentación debe explicar claramente el funcionamiento de cada módulo y función.




