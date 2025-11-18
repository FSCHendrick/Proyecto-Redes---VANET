import math
import time

class Semaforo:
    def __init__(self, id, x, y, estado, linea):
        self.id = id
        self.x = x
        self.y = y
        self.estado = estado
        self.linea = linea
        self.vehiculos_detectados = []
        self.ultimo_cambio = time.time()

        # Parámetros de control
        self.min_tiempo_verde = 3      # segundos
        self.max_tiempo_verde = 8
        self.min_tiempo_rojo = 3
        self.prioridad_emergencia = False

    # ------------------------------------------------------------------
    def recibir_datos(self, mensaje):
        """Recibe información de vehículos cercanos."""
        self.vehiculos_detectados.append(mensaje)

    def actualizar_estado(self, estado_general):
        """
        Actualiza el estado del semáforo:
        - Se sincroniza con el estado general de su línea.
        - Prioridad: si hay un vehículo de emergencia, se pone verde.
        """
        # Sincronizar con estado general
        self.estado = estado_general[self.linea]

        # Prioridad: emergencia
        for v in self.vehiculos_detectados:
            if v["tipo"] == "emergencia":
                self.estado = "verde"
                break

        # --- Emergencias ---
        emergencias = [v for v in self.vehiculos_detectados if v["tipo"] == "emergencia"]
        if emergencias:
            if self.estado != "verde":
                print(f"🚨 Semáforo {self.id}: prioridad a emergencia {emergencias[0]['id']}")
            self.estado = "verde"
            self.prioridad_emergencia = True
            self.ultimo_cambio = ahora
            return

        # --- Si hay emergencia reciente, mantener verde unos segundos más ---
        if self.prioridad_emergencia and tiempo_desde_ultimo < self.min_tiempo_verde:
            self.estado = "verde"
            return
        else:
            self.prioridad_emergencia = False

        # --- Análisis de tráfico general ---
        total = len(self.vehiculos_detectados)
        if total == 0:
            # Si no hay vehículos, mantener rojo si pasó el mínimo tiempo verde
            if self.estado == "verde" and tiempo_desde_ultimo > self.min_tiempo_verde:
                self.estado = "rojo"
                self.ultimo_cambio = ahora
            return

        # Contar por dirección
        por_direccion = {}
        for v in self.vehiculos_detectados:
            dir = v["direccion"]
            por_direccion[dir] = por_direccion.get(dir, 0) + 1

        # Dirección más cargada
        direccion_max = max(por_direccion, key=por_direccion.get)
        cantidad = por_direccion[direccion_max]

        # --- Decisión dinámica ---
        if cantidad >= 3:
            # Más tráfico: mantener verde más tiempo
            if self.estado != "verde":
                print(f"🟢 Semáforo {self.id}: mucho tráfico ({cantidad} vehículos) → verde")
            self.estado = "verde"
            self.ultimo_cambio = ahora
        elif cantidad == 1 or cantidad == 2:
            # Flujo moderado: alternar si pasó tiempo mínimo
            if self.estado == "verde" and tiempo_desde_ultimo > self.min_tiempo_verde:
                print(f"🔴 Semáforo {self.id}: tráfico bajo → rojo")
                self.estado = "rojo"
                self.ultimo_cambio = ahora
            elif self.estado == "rojo" and tiempo_desde_ultimo > self.min_tiempo_rojo:
                print(f"🟢 Semáforo {self.id}: detecta {cantidad} vehículos → verde")
                self.estado = "verde"
                self.ultimo_cambio = ahora
        else:
            # Sin tráfico: mantener rojo
            if self.estado != "rojo":
                self.estado = "rojo"
                self.ultimo_cambio = ahora

    # ------------------------------------------------------------------
    def limpiar_datos(self):
        """Limpia la lista de vehículos detectados para el siguiente ciclo."""
        self.vehiculos_detectados = []
