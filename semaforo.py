class Semaforo:
    def __init__(self, id, x, y, estado, linea):
        self.id = id
        self.x = x
        self.y = y
        self.estado = estado
        self.linea = linea
        self.vehiculos_detectados = []

    def recibir_datos(self, mensaje):
        self.vehiculos_detectados.append(mensaje)

    def actualizar_estado(self, estado_general):
        # (Puedes dejar esto si luego quieres volver a usarlo)
        for v in self.vehiculos_detectados:
            if v["tipo"] == "emergencia":
                self.estado = "verde"
                return
        if len(self.vehiculos_detectados) > 3:
            self.estado = "verde"
        else:
            self.estado = "rojo"
        # Sincroniza el semáforo según su línea
        if self.linea == "H":
            self.estado = estado_general["H"]
        else:
            self.estado = estado_general["V"]

    def limpiar_datos(self):
        self.vehiculos_detectados = []
