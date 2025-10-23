class Semaforo:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.estado = "verde"
        self.vehiculos_detectados = []

    def recibir_datos(self, mensaje):
        self.vehiculos_detectados.append(mensaje)

    def actualizar_estado(self):
        # (Puedes dejar esto si luego quieres volver a usarlo)
        for v in self.vehiculos_detectados:
            if v["tipo"] == "emergencia":
                self.estado = "verde"
                return
        if len(self.vehiculos_detectados) > 3:
            self.estado = "verde"
        else:
            self.estado = "rojo"

    def limpiar_datos(self):
        self.vehiculos_detectados = []
