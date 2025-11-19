import math
from semaforo import Semaforo

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
        # Configuración
        UMBRAL_DETECCION = 120
        DISTANCIA_DETENCION = 60
        FACTOR_AMARILLO = 0.4
        
        # Coordenadas aproximadas del centro del cruce
        CENTRO_X = 400
        CENTRO_Y = 300

        if self.tipo == "emergencia":
            self.moviendo = True
            self.velocidad = self.velocidad_normal
            return

        semaforos_linea = [s for s in semaforos if s.linea == self.linea]
        semaforos_relevantes = []

        for s in semaforos_linea:
            
            # --- 1. FILTRO DE ZONA (¡LA SOLUCIÓN A TU PROBLEMA!) ---
            # Ignoramos los semáforos que están "al otro lado" del cruce.
            # Solo obedecemos los de entrada.
            
            if self.linea == "H":
                # Autos hacia el Este (E): Solo obedecen semáforos a la IZQUIERDA del centro
                if self.direccion == "E" and s.x > CENTRO_X:
                    continue
                # Autos hacia el Oeste (W): Solo obedecen semáforos a la DERECHA del centro
                if self.direccion == "W" and s.x < CENTRO_X:
                    continue
                    
            elif self.linea == "V":
                # Autos hacia el Sur (S): Solo obedecen semáforos ARRIBA del centro
                if self.direccion == "S" and s.y > CENTRO_Y:
                    continue
                # Autos hacia el Norte (N): Solo obedecen semáforos ABAJO del centro
                if self.direccion == "N" and s.y < CENTRO_Y:
                    continue

            # --- 2. FILTRO DE POSICIÓN (Lo que ya tenías) ---
            # Si ya pasé el semáforo, lo ignoro.
            
            if self.linea == "H":
                if self.direccion == "E":
                    if s.x < self.x: continue 
                    semaforos_relevantes.append(s)
                elif self.direccion == "W":
                    if s.x > self.x: continue
                    semaforos_relevantes.append(s)

            else: # Vertical
                if self.direccion == "S":
                    if s.y < self.y: continue
                    semaforos_relevantes.append(s)
                elif self.direccion == "N":
                    if s.y > self.y: continue
                    semaforos_relevantes.append(s)

        # Si no hay semáforos relevantes (porque ya pasé el de entrada y el de salida lo ignoro),
        # entonces ACELERO para salir del cruce.
        if not semaforos_relevantes:
            self.semaforo_cercano = None
            self.moviendo = True
            self.velocidad = self.velocidad_normal
            return

        # --- 3. CALCULO DE DISTANCIA (Igual que antes) ---
        closest = min(semaforos_relevantes, key=lambda s: math.hypot(self.x - s.x, self.y - s.y))
        distancia = math.hypot(self.x - closest.x, self.y - closest.y)
        
        self.semaforo_cercano = closest
        self.distancia_semaforo = distancia

        if distancia > UMBRAL_DETECCION:
            self.moviendo = True
            self.velocidad = self.velocidad_normal
            return

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
            if distancia <= DISTANCIA_DETENCION:
                self.moviendo = False
                self.velocidad = 0
            else:
                self.moviendo = True
                self.velocidad = self.velocidad_normal


    def generar_mensaje(self):
        return {
            "id": self.id,
            "tipo": self.tipo,
            "linea": self.linea,
            "posicion": (self.x, self.y),
            "direccion": self.direccion  # corregido
        }