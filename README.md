# Courier Quest, Repartidor en TigerCity
Este proyecto simula la vida de un repartidor en una ciudad. El objetivo principal es alcanzar la meta de ingresos por medio de los pedidos y la recompensas. Debe de recoger y entregar el pedido en diferentes locaciones mientras algunos factores como el peso y el clima influyen su resistencia y reputación. 

# Factores de derrota 
Se pierde la partida si:
1. La reputación es menor a 20
2. Cuando todos los pedidos hayan sido gestionados pero no se ha alcanzado la meta de ingresos indicada. 

# Factores del juego
**Resistencia:** Disminuye al moverse y se ve más afectada cuando hay peso o un clima díficil. Cuando esta llega a 0 debe de descansar para recuperarse.
**Reputación:** Aumenta al entregar pedidos a tiempo (+10) y disminuye si se entregan tarde (-5) o si se rechaza un pedido (-3). Una reputación alta (>= 90) otorga un bonus del 5% al pago de los pedidos
**Inventario:** El inventario tiene un peso máximo, no se pueden agregar más pedidos al inventario si se sobrepasa ese peso. 
**Clima:** El clima cambia periódicamente (cada 45-60 segundos) y afecta la velocidad y resistencia del trabajador.

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



**Estructuras de Datos que se utilizaron**

**Complejidad Algorítmica**
