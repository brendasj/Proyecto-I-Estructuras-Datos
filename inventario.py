class Nodo:
    def __init__(self, pedido):
        self.pedido = pedido
        self.siguiente = None
        self.anterior = None
    

class Inventario:
    def __init__(self, peso_maximo):
        self.head = None
        self.tail = None
        self.peso_maximo = peso_maximo
        self.peso_actual = 0
    
    def agregar_pedido(self, pedido):
        if self.peso_actual + pedido.weight > self.peso_maximo:
            print("No se puede agregar el pedido, el peso maximo ha sido superado")
            return False
        else:
            nodo = Nodo(pedido)
            if not self.head:
                self.head = nodo
                self.tail = nodo
            else:
                self.tail.siguiente = nodo
                nodo.anterior = self.tail
                self.tail = nodo
            
            self.peso_actual += pedido.getPeso()
            return True

    def quitar_pedido(self, pedido_id):
        actual = self.head

        while actual:
            if actual.pedido.id == pedido_id:
                if actual.anterior:
                    actual.anterior.siguiente = actual.siguiente
                else:
                    self.head = actual.siguiente
                
                if actual.siguiente:
                    actual.siguiente.anterior = actual.anterior
                else:
                    self.tail = actual.anterior
                
                self.peso_actual -= actual.pedido.getPeso()
                return True
            actual = actual.siguiente
        return False
    
    def forward(self):
        pedidos = []
        actual = self.head
        while actual:
            pedidos.append(actual.pedido)
            actual = actual.siguiente
        return pedidos
    
    def backward(self):
        pedidos = []
        actual = self.tail
        while actual:
            pedidos.append(actual.pedido)
            actual = actual.anterior
        return pedidos