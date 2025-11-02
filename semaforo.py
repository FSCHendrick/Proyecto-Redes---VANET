class Semaforo:
    def __init__(self, id, x, y, estado, linea):
        self.id = id
        self.x = x
        self.y = y
        self.estado = estado
        self.linea = linea
        self.vehiculos_detectados = []

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

    def limpiar_datos(self):
        """Limpia la lista de vehículos detectados para el siguiente ciclo."""
        self.vehiculos_detectados = []
