import socket
import json
import time
import config

# --- Configuración del Servidor ---
SERVER_ADDRESS = (config.HOST, config.PORT)

# --- Constantes ---
config.SEGUNDOS_TIMEOUT_VEHICULO = 3.0 
config.DURACION_LUZ_VERDE = 5.0  # (NUEVO) Tiempo que dura el semáforo en verde normal

# --- ESTADO GLOBAL ---
# Ahora preparado para múltiples vehículos enviando paquetes simultáneamente
estado_global_vehiculos = {}  # { "esp32_1": {...}, "esp32_2": {...} }

estado_global_semaforos = {
    "H": "verde",
    "V": "rojo"
}
last_print_time = 0

# Variable para controlar el tiempo del semáforo
tiempo_ultimo_cambio = time.time() 

# --- Funciones del Algoritmo (R4 y R5) ---
def ejecutar_algoritmo_smart(vehiculos, semaforos):
    global tiempo_ultimo_cambio
    
    # 1. R5: Prioridad de Emergencia
    emergencia_detectada_H = False
    emergencia_detectada_V = False

    # Revisar TODOS los vehículos activos (multi ESP32)
    for vid, datos_v in vehiculos.items():
        if datos_v.get("tipo") == "emergencia":
            linea = datos_v.get("linea")
            if linea == "H":
                emergencia_detectada_H = True
            elif linea == "V":
                emergencia_detectada_V = True

    # Emergencia detectada → forzar estado
    if emergencia_detectada_H:
        semaforos["H"] = "verde"
        semaforos["V"] = "rojo"
        tiempo_ultimo_cambio = time.time()
        return 

    elif emergencia_detectada_V:
        semaforos["H"] = "rojo"
        semaforos["V"] = "verde"
        tiempo_ultimo_cambio = time.time()
        return 

    # 2. R4: Alternancia normal por tiempo
    ahora = time.time()
    if ahora - tiempo_ultimo_cambio > config.DURACION_LUZ_VERDE:
        if semaforos["H"] == "verde":
            semaforos["H"] = "rojo"
            semaforos["V"] = "verde"
        else:
            semaforos["H"] = "verde"
            semaforos["V"] = "rojo"
        
        tiempo_ultimo_cambio = ahora


def main():
    global last_print_time
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        server_socket.bind(SERVER_ADDRESS)
        print(f"Servidor escuchando en {config.HOST}:{config.PORT}")
    except socket.error as err:
        print(f"Error al enlazar: {err}")
        return

    # Modo no bloqueante → permite múltiples vehículos simultáneos
    server_socket.setblocking(False)
    print("Socket en modo NO-BLOQUEANTE.")

    while True:
        time_now = time.time()
        
        # --- PASO A: Recibir y Procesar Paquetes ---
        while True:
            try:
                datos_bytes, direccion_cliente = server_socket.recvfrom(4096)
                
                try:
                    datos_string = datos_bytes.decode('utf-8')
                    mensaje = json.loads(datos_string)

                    tipo = mensaje.get("tipo_mensaje")

                    if tipo == "SOLICITUD_VISUALIZADOR":
                        # Visualizador → devuelve todo el estado
                        respuesta = {
                            "semaforos": estado_global_semaforos,
                            "vehiculos": list(estado_global_vehiculos.values())
                        }
                        server_socket.sendto(json.dumps(respuesta).encode('utf-8'), direccion_cliente)
                    
                    elif tipo == "SOLICITUD_LUCES":
                        # Simulador → solo luces
                        respuesta = {"semaforos": estado_global_semaforos}
                        server_socket.sendto(json.dumps(respuesta).encode('utf-8'), direccion_cliente)

                    else:
                        # --- Mensaje de un vehículo ---
                        vid = mensaje.get("id")

                        # Ignorar paquetes sin ID
                        if not vid:
                            continue

                        # Agregar timestamp y actualizar info del vehículo
                        mensaje["timestamp_recibido"] = time_now
                        estado_global_vehiculos[vid] = mensaje

                except (UnicodeDecodeError, json.JSONDecodeError):
                    # Ignorar paquetes corruptos
                    pass 

            except BlockingIOError:
                # Ya no hay más mensajes
                break 
            except socket.error as e:
                print(f"[ERROR SOCKET] {e}")
                break

        # --- PASO B: Limpieza de Fantasmas ---
        ids_a_borrar = []
        for vid, datos_v in estado_global_vehiculos.items():
            if time_now - datos_v.get("timestamp_recibido", 0) > config.SEGUNDOS_TIMEOUT_VEHICULO:
                ids_a_borrar.append(vid)
        
        for vid in ids_a_borrar:
            del estado_global_vehiculos[vid]

        # --- PASO C: Algoritmo ---
        ejecutar_algoritmo_smart(estado_global_vehiculos, estado_global_semaforos)

        # --- PASO D: Imprimir Resumen ---
        if (time_now - last_print_time) > 2.0: 
            print(f"--- Estado: {estado_global_semaforos} | Autos Activos: {len(estado_global_vehiculos)} ---")
            last_print_time = time_now

        # Pausa ligera para evitar consumo excesivo
        time.sleep(0.05) 


if __name__ == "__main__":
    main()
