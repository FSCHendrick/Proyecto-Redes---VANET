import socket
import json

# --- Configuración del Servidor ---
HOST = '127.0.0.1'  # localhost (escuchar solo en esta máquina)
PORT = 9999          # Puerto para escuchar (puedes usar otro si este está ocupado)
SERVER_ADDRESS = (HOST, PORT)

# --- Almacenamiento de Datos (El "estado" del cruce) ---
# Esta lista guardará los datos de los vehículos que recibamos
# Se irá actualizando en cada ciclo del algoritmo (Paso futuro)
vehiculos_detectados = []

def main():
    # 1. Crear el Socket UDP
    #    socket.AF_INET = Usar IPv4
    #    socket.SOCK_DGRAM = Usar UDP (Datagramas)
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        print("Socket creado exitosamente.")
    except socket.error as err:
        print(f"Error al crear el socket: {err}")
        return # Salir si no se puede crear el socket

    # 2. Enlazar (Bind) el Socket
    #    Le dice al S.O. que este script "es dueño" de este puerto.
    try:
        server_socket.bind(SERVER_ADDRESS)
        print(f"Servidor escuchando en {HOST}:{PORT}")
    except socket.error as err:
        print(f"Error al enlazar (bind): {err}")
        print("Es posible que el puerto ya esté en uso.")
        server_socket.close()
        return # Salir si no se puede enlazar

    # 3. Bucle Principal del Servidor
    print("Esperando mensajes de los vehículos...")
    while True:
        try:
            # 4. Recibir Datos (Operación Bloqueante)
            #    El script se pausará aquí hasta que llegue un paquete.
            #    'buffer_size' (ej. 1024 bytes) es el tamaño máx. del mensaje.
            datos_bytes, direccion_cliente = server_socket.recvfrom(1024)
            
            # 5. Decodificar y Parsear
            #    Los datos llegan como bytes -> decodificar a string (UTF-8)
            datos_string = datos_bytes.decode('utf-8')
            
            #    El string es JSON -> parsear a diccionario de Python
            mensaje_vehiculo = json.loads(datos_string)
            
            # 6. Procesar el Mensaje (¡Aquí irá tu algoritmo!)
            
            # Por ahora, solo mostramos el mensaje y quién lo envió
            print(f"[RECIBIDO de {direccion_cliente}] -> {mensaje_vehiculo}")
            
            # (Futuro Paso): Añadir a la lista para el algoritmo
            # vehiculos_detectados.append(mensaje_vehiculo)
            
            # (Futuro Paso): Aquí llamarías a tu lógica:
            # actualizar_estado_semaforos(vehiculos_detectados)

        except json.JSONDecodeError:
            # El mensaje recibido no era un JSON válido
            print(f"[ERROR de {direccion_cliente}] -> Mensaje corrupto o no es JSON.")
        except Exception as e:
            # Captura cualquier otro error inesperado
            print(f"[ERROR INESPERADO] -> {e}")

    # (Este código nunca se alcanza en este bucle infinito,
    # pero es buena práctica cerrarlo si el bucle tuviera una condición de salida)
    # server_socket.close()

if __name__ == "__main__":
    # Esta línea asegura que el script solo se ejecute
    # cuando lo corres directamente (python controlador.py)
    main()