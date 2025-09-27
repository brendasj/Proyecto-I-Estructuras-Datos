class PedidoNodo:
    def __init__(self, pedido):
        self.pedido = pedido
        self.prev = None
        self.next = None
        
class Inventario:
    def __init__(self, peso_maximo=10):
        self.head = None
        self.tail = None
        self.actual = None
        self.peso_maximo = peso_maximo
        self.peso_actual = 0
        self.entregados = []

    def agregar_pedido(self, pedido):
        if self.peso_actual + pedido.weight > self.peso_maximo:
            return False  # No se puede agregar, excede el peso
        nuevo = PedidoNodo(pedido)
        if not self.head:
            self.head = self.tail = self.actual = nuevo
        else:
            self.tail.next = nuevo
            nuevo.prev = self.tail
            self.tail = nuevo
        self.peso_actual += pedido.weight
        return True

    def quitar_pedido(self, pedido_id):
        nodo = self.head
        while nodo:
            if nodo.pedido.id == pedido_id:
                if nodo.prev:
                    nodo.prev.next = nodo.next
                else:
                    self.head = nodo.next
                if nodo.next:
                    nodo.next.prev = nodo.prev
                else:
                    self.tail = nodo.prev
                if self.actual == nodo:
                    self.actual = nodo.next or nodo.prev
                self.peso_actual -= nodo.pedido.weight
                return True
            nodo = nodo.next
        return False
    
    def marcar_entregado(self, pedido_entregado):
        nodo = self.head
        while nodo:
            if nodo.pedido.id == pedido_entregado.id:
                self.entregados.append(nodo.pedido)
                self.peso_actual -= nodo.pedido.weight

                # Remover de la lista doblemente enlazada
                if nodo.prev:
                    nodo.prev.next = nodo.next
                else:
                    self.head = nodo.next
                if nodo.next:
                    nodo.next.prev = nodo.prev
                else:
                    self.tail = nodo.prev
                if self.actual == nodo:
                    self.actual = nodo.next or nodo.prev
                return True
            nodo = nodo.next
        return False


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

    def mostrar_inventario(self):
        print(f"Inventario ({self.peso_actual}/{self.peso_maximo} kg):")
        for pedido in self.todos_los_pedidos():
            pedido.mostrar()