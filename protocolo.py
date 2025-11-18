import socket
import json

# --- Socket del Cliente (Global) ---
# Creamos un único socket para que todos los vehículos lo usen.
# No es necesario crear uno nuevo por cada mensaje.
try:
    # 1. Crear el Socket UDP (igual que en el servidor)
    cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print("Socket de cliente (protocolo) creado.")
except socket.error as err:
    print(f"Error al crear el socket de cliente: {err}")
    # Si no podemos crear el socket, creamos un objeto 'None'
    # para que el programa no se caiga al intentar usarlo.
    cliente_socket = None

class ProtocoloVANET:

    # --- Configuración del Cliente ---
    # El destino debe ser EXACTAMENTE la misma dirección y puerto
    # que el servidor (controlador.py) está escuchando.
    HOST_SERVIDOR = '127.0.0.1'
    PORT_SERVIDOR = 9999
    DESTINO = (HOST_SERVIDOR, PORT_SERVIDOR)
    
    @staticmethod
    def enviar(mensaje):
        """
        Envía un mensaje (un diccionario de Python) al controlador 
        del semáforo a través de la red UDP.
        """
        # Asegurarnos de que el socket se creó correctamente
        if not cliente_socket:
            print("[ERROR] El socket de cliente no está inicializado.")
            return

        # El mensaje debe ser un diccionario válido para enviar
        if not mensaje:
            return

        try:
            # 1. Convertir el diccionario de Python -> string JSON
            mensaje_string = json.dumps(mensaje)
            
            # 2. Convertir el string -> bytes (usando UTF-8)
            mensaje_bytes = mensaje_string.encode('utf-8')
            
            # 3. Enviar los bytes por la red al DESTINO
            #    UDP es "fire and forget" (dispara y olvida).
            #    Simplemente enviamos el paquete.
            cliente_socket.sendto(mensaje_bytes, ProtocoloVANET.DESTINO)
            
            # (Para depuración, puedes activar esta línea:)
            # print(f"-> Enviando: {mensaje_string}")

        except socket.error as err:
            # Esto podría pasar si hay un problema de red
            print(f"[ERROR de Red al enviar] -> {err}")
        except TypeError as err:
            # Esto pasa si 'mensaje' no se puede convertir a JSON
            print(f"[ERROR de JSON] -> {err}")
        except Exception as e:
            print(f"[ERROR INESPERADO en enviar] -> {e}")

    @staticmethod
    def cerrar_socket():
        """
        Cierra el socket al final del programa.
        """
        if cliente_socket:
            print("Cerrando el socket del cliente.")
            cliente_socket.close()