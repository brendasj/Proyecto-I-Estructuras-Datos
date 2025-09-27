class PedidoNodo:
    def __init__(self, pedido):
        self.pedido = pedido
        self.prev = None
        self.next = None

class Inventario:
    def __init__(self):
        self.head = None
        self.tail = None
        self.actual = None 

    def agregar_pedido(self, pedido):
        nuevo = PedidoNodo(pedido)
        if not self.head:
            self.head = self.tail = self.actual = nuevo
        else:
            self.tail.next = nuevo
            nuevo.prev = self.tail
            self.tail = nuevo

    def siguiente(self):
        if self.actual and self.actual.next:
            self.actual = self.actual.next

    def anterior(self):
        if self.actual and self.actual.prev:
            self.actual = self.actual.prev

    def pedido_actual(self):
        return self.actual.pedido if self.actual else None

    def todos_los_pedidos(self):
        pedidos = []
        nodo = self.head
        while nodo:
            pedidos.append(nodo.pedido)
            nodo = nodo.next
        return pedidos

    def visualizar_por_prioridad(self):
        return sorted(self.todos_los_pedidos(), key=lambda p: p.priority, reverse=True)

    def visualizar_por_entrega(self):
        return sorted(self.todos_los_pedidos(), key=lambda p: p.deadline)