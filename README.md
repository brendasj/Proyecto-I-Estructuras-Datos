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
| **S** | **Guardar Partida**  | Guarda el estado actual de la partida (ingresos, bonos, penalizaciones, estado de finalización) en el historial de puntajes. |
| **L** | **Cargar Partida**   | Muestra un listado de partidas guardadas que **no han finalizado** para que el usuario pueda reanudar una.                   |


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

### 5. Algoritmos de Ordenación

| Clase | Uso | Detalle de Implementación | Complejidad de Operaciones |
| :--- | :--- | :--- | :--- |
| **`Inventario`** | Visualización ordenada de pedidos para el panel lateral. | Utiliza la función `sorted()` de Python con una función `lambda`. | `visualizar_por_prioridad()` / `visualizar_por_entrega()`: $O(n \log n)$ (debido al uso de `sorted()`). |

