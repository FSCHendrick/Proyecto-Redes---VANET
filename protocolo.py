class ProtocoloVANET:
    @staticmethod
    def enviar(mensaje, semaforo):
        semaforo.recibir_datos(mensaje)
