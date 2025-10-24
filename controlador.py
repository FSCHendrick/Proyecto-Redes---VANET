class ControladorCentral:
    def __init__(self, semaforos):
        self.semaforos = semaforos

    def sincronizar(self):
        # Si algún semáforo tiene emergencia, los otros se ponen en rojo
        for s in self.semaforos:
            if any(v["tipo"] == "emergencia" for v in s.vehiculos_detectados):
                for s2 in self.semaforos:
                    s2.estado = "rojo"
                s.estado = "verde"
                return
