import math
from semaforo import Semaforo

class Vehiculo:
    def __init__(self, id, tipo, x, y, linea, direccion):
        self.id = id
        self.tipo = tipo  # "normal" o "emergencia"
        self.x = x
        self.y = y
        self.linea = linea # "H" = Horizontal, "V" = Vertical
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
            self.linea = "H"
        elif self.direccion == "W":
            self.x -= self.velocidad
            self.linea = "H"
        elif self.direccion == "N":
            self.y -= self.velocidad
            self.linea = "V"
        elif self.direccion == "S":
            self.y += self.velocidad
            self.linea = "V"

    def detectar_semaforo(self, semaforos):
    
    #Controla el comportamiento del vehículo frente al semáforo más cercano.

    #Reglas:
    #- Verde: velocidad normal.
    #- Amarillo: reduce velocidad (solo si está a distancia media).
    #- Rojo: se detiene antes del cruce.
    #- Vehículos de emergencia: siempre avanzan a velocidad normal.

    #También evita que los autos se detengan justo en la intersección.
    

    # --- Parámetros ajustables ---
        UMBRAL_DETECCION = 120     # distancia máxima para "ver" el semáforo
        FACTOR_AMARILLO = 0.4      # porcentaje de reducción de velocidad
        DISTANCIA_DETENCION = 60   # punto donde el vehículo debe detenerse antes del cruce
        MARGEN_CRUCE = 25          # permite pasar si ya está muy cerca del cruce

        # --- Regla especial: vehículos de emergencia ---
        if self.tipo == "emergencia":
            self.moviendo = True
            self.velocidad = self.velocidad_normal
            return

        # --- Si no hay semáforos, avanzar normalmente ---
        if not semaforos:
            self.moviendo = True
            self.velocidad = self.velocidad_normal
            return

        # --- Buscar el semáforo más cercano ---
        closest_s = min(semaforos, key=lambda s: math.hypot(self.x - s.x, self.y - s.y))
        distancia = math.hypot(self.x - closest_s.x, self.y - closest_s.y)

        # Si está fuera del rango de detección, avanzar sin cambios
        if distancia > UMBRAL_DETECCION:
            self.moviendo = True
            self.velocidad = self.velocidad_normal
            return

        # --- Lógica según el color del semáforo ---
        if closest_s.estado == "verde":
            self.moviendo = True
            self.velocidad = self.velocidad_normal

        elif closest_s.estado in ["amarillo1", "amarillo2"]:
            # Reducir velocidad si está a distancia media
            if distancia > DISTANCIA_DETENCION:
                self.moviendo = True
                self.velocidad = self.velocidad_normal * FACTOR_AMARILLO
            else:
                self.moviendo = True
                self.velocidad = self.velocidad_normal  # si ya está cerca, puede pasar

        elif closest_s.estado == "rojo":
            # Determinar si el semáforo afecta al carril del vehículo
            afecta = (
                (self.linea == "H" and closest_s.linea == "H") or
            (self.linea == "V" and closest_s.linea == "V")
            )

            if afecta:
                # Evaluar distancia al cruce según dirección
                if self.direccion in ["E", "W"] and abs(self.x - closest_s.x) < DISTANCIA_DETENCION:
                    self.moviendo = False
                    self.velocidad = 0
                elif self.direccion in ["N", "S"] and abs(self.y - closest_s.y) < DISTANCIA_DETENCION:
                    self.moviendo = False
                    self.velocidad = 0
                elif distancia <= MARGEN_CRUCE:
                    # Si ya está muy cerca, dejarlo pasar
                    self.moviendo = True
                    self.velocidad = self.velocidad_normal
                else:
                    self.moviendo = True
                    self.velocidad = self.velocidad_normal
            else:
                # Si el semáforo no corresponde a su carril, sigue normal
                self.moviendo = True
                self.velocidad = self.velocidad_normal



    def generar_mensaje(self):
        return {
            "id": self.id,
            "tipo": self.tipo,
            "posicion": (self.x, self.y),
            "direccion": self.direccion
        }
