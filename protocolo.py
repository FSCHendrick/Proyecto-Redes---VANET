class ProtocoloVANET:
    @staticmethod
    def enviar(mensaje, semaforo):
        print(f"Vehículo {mensaje['id']} envía datos al semáforo {semaforo.id}")
        semaforo.recibir_datos(mensaje)
