import random

class ProtocoloVANET:
    @staticmethod
    def enviar(mensaje, semaforo):
        # Simulación de retardo o pérdida de mensaje
        if random.random() < 0.05:  # 5% de pérdida
            return  # mensaje no llega
        semaforo.recibir_datos(mensaje)

