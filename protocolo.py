import socket
import json
import config

# --- Socket del Cliente (Global) ---
try:
    cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
except socket.error as err:
    print(f"Error al crear el socket de cliente: {err}")
    cliente_socket = None

class ProtocoloVANET:

    # Usamos la configuración centralizada
    DESTINO = (config.HOST, config.PORT)
    
    @staticmethod
    def enviar(mensaje):
        if not cliente_socket or not mensaje:
            return
        try:
            mensaje_string = json.dumps(mensaje)
            mensaje_bytes = mensaje_string.encode('utf-8')
            cliente_socket.sendto(mensaje_bytes, ProtocoloVANET.DESTINO)
        except Exception as e:
            print(f"[ERROR ENVIAR] -> {e}")

    @staticmethod
    def cerrar_socket():
        if cliente_socket:
            cliente_socket.close()