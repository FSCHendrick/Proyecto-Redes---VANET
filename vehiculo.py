import math

class Vehiculo:
    def __init__(self, id, tipo, x, y, direccion):
        self.id = id
        self.tipo = tipo  # "normal" o "emergencia"
        self.x = x
        self.y = y
        # velocidad_normal es la velocidad de crucero; velocidad_actual es la que usamos para movernos
        self.velocidad_normal = 2 if tipo == "normal" else 4
        self.velocidad = self.velocidad_normal
        self.direccion = direccion  # "N", "S", "E", "O"
        self.moviendo = True  # indica si el vehiculo esta en movimiento o no

    def mover(self):
        if not self.moviendo:
            return  # Si está detenido, no se mueve
        if self.direccion == "E":
            self.x += self.velocidad
        elif self.direccion == "W":
            self.x -= self.velocidad
        elif self.direccion == "N":
            self.y -= self.velocidad
        elif self.direccion == "S":
            self.y += self.velocidad

    def detectar_semaforo(self, semaforos):
        """
        Detiene o reduce la velocidad del vehículo según el color del semáforo más cercano.
        Comportamiento:
        - verde: velocidad normal
        - amarillo1: reducción parcial
        - amarillo2: detener (como rojo)
        - rojo: detener
        - emergencias: mantienen velocidad normal
        """
        UMBRAL_DETECCION = 100
        FACTOR_AMARILLO = 0.4
        MARGEN_SEGURO = 30

        # Emergencia siempre avanza a velocidad normal
        if self.tipo == "emergencia":
            self.moviendo = True
            self.velocidad = self.velocidad_normal
            return

        # Si no hay semáforo cercano, avanzar normalmente
        if not semaforos:
            self.moviendo = True
            self.velocidad = self.velocidad_normal
            return

        # Tomar solo el semáforo más cercano
        closest_s = min(semaforos, key=lambda s: math.hypot(self.x - s.x, self.y - s.y))
        distancia = math.hypot(self.x - closest_s.x, self.y - closest_s.y)

        if closest_s.estado == "verde":
            self.moviendo = True
            self.velocidad = self.velocidad_normal
        elif closest_s.estado == "amarillo1":
            # Si está muy cerca del semáforo, se puede mantener velocidad normal
            if distancia <= MARGEN_SEGURO:
                self.moviendo = True
                self.velocidad = self.velocidad_normal
            else:
                self.moviendo = True
                self.velocidad = max(0.1, self.velocidad_normal * FACTOR_AMARILLO)
        elif closest_s.estado in ["rojo", "amarillo2"]:
            if distancia <= MARGEN_SEGURO:
                self.moviendo = True  # deja cruzar si ya está muy cerca
                self.velocidad = self.velocidad_normal
            else:
                self.moviendo = False
                self.velocidad = 0

    def generar_mensaje(self):
        return {
            "id": self.id,
            "tipo": self.tipo,
            "posicion": (self.x, self.y),
            "direccion": self.direccion
        }
