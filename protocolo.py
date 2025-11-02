class ProtocoloVANET:
    @staticmethod
    def enviar(mensaje, semaforo):
        """
        Envía un mensaje desde un vehículo hacia un semáforo.
        """
        if mensaje and semaforo:
            # Enviar información del vehículo al semáforo
            semaforo.recibir_datos(mensaje)
            # Para depuración, puedes activar esta línea:
            # print(f"Vehículo {mensaje['id']} envía datos al semáforo {semaforo.id}")
