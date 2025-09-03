class Clima:
    def __init__(self, datos):
        self.city = datos.get("city")
        self.temperature = datos.get("temperature")
        self.humidity = datos.get("humidity")
        self.description = datos.get("description", "Sin descripción")

    def mostrar(self):
        print(f"Clima en {self.city}: {self.temperature}°C, {self.humidity}% humedad, {self.description}")

    def mostrar(self):
        if self.city and self.temperature is not None:
         print(f"Clima en {self.city}: {self.temperature}°C, {self.humidity}% humedad, {self.description}")
        else:
         print("Datos de clima incompletos o inválidos.")