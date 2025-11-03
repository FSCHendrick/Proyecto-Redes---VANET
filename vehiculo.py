import math
from semaforo import Semaforo

#comentario
class Vehiculo:
    def __init__(self, id, tipo, x, y, linea, direccion):
        self.id = id
        self.tipo = tipo  # "normal" o "emergencia"
        self.x = x
        self.y = y
        self.linea = linea
        self.direccion = direccion   # corregido
        self.velocidad_normal = 2 if tipo == "normal" else 4
        self.velocidad = self.velocidad_normal
        self.velocidad_actual = 0  # velocidad real usada (para suavizar)
        self.moviendo = True
        self.activo = True  # inicializar activo

        # Referencias útiles
        self.semaforo_cercano = None
        self.distancia_semaforo = None

    def mover(self, vehiculos):
        velocidad = 2 if self.tipo == "normal" else 3  # autos de emergencia más rápidos

        # Si hay semáforo rojo cercano, el auto se detiene antes de cruzar
        if self.semaforo_cercano and self.semaforo_cercano.estado in ["rojo", "amarillo1", "amarillo2"]:
            if self.linea == "H" and abs(self.x - self.semaforo_cercano.x) < 50:
                return
            if self.linea == "V" and abs(self.y - self.semaforo_cercano.y) < 50:
                return

        # Evitar choques con otros vehículos cercanos en la misma línea y dirección
        for otro in vehiculos:
            if otro is not self and otro.linea == self.linea and otro.direccion == self.direccion:
                if self.linea == "H" and abs(self.y - otro.y) < 10:
                    if self.direccion == "E" and 0 < otro.x - self.x < 40:
                        return
                    if self.direccion == "W" and 0 < self.x - otro.x < 40:
                        return
                elif self.linea == "V" and abs(self.x - otro.x) < 10:
                    if self.direccion == "S" and 0 < otro.y - self.y < 40:
                        return
                    if self.direccion == "N" and 0 < self.y - otro.y < 40:
                        return

        # Mover según la dirección
        if self.direccion == "E":
            self.x += velocidad
        elif self.direccion == "W":
            self.x -= velocidad
        elif self.direccion == "S":
            self.y += velocidad
        elif self.direccion == "N":
            self.y -= velocidad

        # Marcar vehículos que salen completamente del área visible
        if self.x < -60 or self.x > 860 or self.y < -60 or self.y > 660:
            self.activo = False

    def detectar_semaforo(self, semaforos):
    # Evalúa si debe detenerse o desacelerar según la distancia al semáforo.
        UMBRAL_DETECCION = 120
        DISTANCIA_DETENCION = 60
        MARGEN_CRUCE = 25
        FACTOR_AMARILLO = 0.4

        if self.tipo == "emergencia":
            self.moviendo = True
            self.velocidad = self.velocidad_normal
            return

        # Solo semáforos de la misma línea
        semaforos_linea = [s for s in semaforos if s.linea == self.linea]

        # Filtrar semáforos que ya quedaron atrás
        semaforos_delante = []
        for s in semaforos_linea:
            if self.linea == "H":
                if (self.direccion == "E" and s.x > self.x) or (self.direccion == "W" and s.x < self.x):
                    semaforos_delante.append(s)
            else:  # "V"
                if (self.direccion == "S" and s.y > self.y) or (self.direccion == "N" and s.y < self.y):
                    semaforos_delante.append(s)

        if not semaforos_delante:
            self.semaforo_cercano = None
            self.moviendo = True
            self.velocidad = self.velocidad_normal
            return

        # Semáforo más cercano por delante
        closest = min(semaforos_delante, key=lambda s: math.hypot(self.x - s.x, self.y - s.y))
        distancia = math.hypot(self.x - closest.x, self.y - closest.y)
        self.semaforo_cercano = closest
        self.distancia_semaforo = distancia

        if distancia > UMBRAL_DETECCION:
            self.moviendo = True
            self.velocidad = self.velocidad_normal
            return

        # Lógica según color del semáforo
        if closest.estado == "verde":
            self.moviendo = True
            self.velocidad = self.velocidad_normal
        elif closest.estado in ["amarillo1", "amarillo2"]:
            if distancia > DISTANCIA_DETENCION:
                self.moviendo = True
                self.velocidad = self.velocidad_normal * FACTOR_AMARILLO
            else:
                self.moviendo = True
                self.velocidad = self.velocidad_normal
        elif closest.estado == "rojo":
            if distancia <= MARGEN_CRUCE:
                self.moviendo = True
                self.velocidad = self.velocidad_normal
            elif distancia <= DISTANCIA_DETENCION:
                self.moviendo = False
                self.velocidad = 0
            else:
                self.moviendo = True
                self.velocidad = self.velocidad_normal


    def generar_mensaje(self):
        return {
            "id": self.id,
            "tipo": self.tipo,
            "posicion": (self.x, self.y),
            "direccion": self.direccion  # corregido
        }
