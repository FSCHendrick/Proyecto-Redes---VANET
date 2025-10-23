import random

class Vehiculo:
    def __init__(self, id, tipo, x, y, direccion):
        self.id = id
        self.tipo = tipo  # "normal" o "emergencia"
        self.x = x
        self.y = y
        self.velocidad = 2 if tipo == "normal" else 4
        self.direccion = direccion  # "N", "S", "E", "O"

    def mover(self):
        if self.direccion == "E":
            self.x += self.velocidad
        elif self.direccion == "W":
            self.x -= self.velocidad
        elif self.direccion == "N":
            self.y -= self.velocidad
        elif self.direccion == "S":
            self.y += self.velocidad

    def generar_mensaje(self):
        return {
            "id": self.id,
            "tipo": self.tipo,
            "posicion": (self.x, self.y),
            "direccion": self.direccion
        }
