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
estado_global_vehiculos = {}
estado_global_semaforos = {
    "H": "verde",
    "V": "rojo"
}
last_print_time = 0

# Variable para controlar el tiempo del semáforo
tiempo_ultimo_cambio = time.time() 

# --- Funciones del Algoritmo (R4 y R5) ---
def ejecutar_algoritmo_smart(vehiculos, semaforos):
    global tiempo_ultimo_cambio # Necesario para modificar la variable de tiempo
    
    # 1. R5: Prioridad de Emergencia
    emergencia_detectada_H = False
    emergencia_detectada_V = False

    for vid, datos_v in vehiculos.items():
        if datos_v["tipo"] == "emergencia":
            linea = datos_v.get("linea")
            # print(f"[DEBUG] Ambulancia detectada. ID: {vid}, Linea recibida: {linea}")
            if linea == "H":
                emergencia_detectada_H = True
            elif linea == "V":
                emergencia_detectada_V = True

    # Si hay emergencia, FORZAMOS el cambio y reiniciamos el temporizador
    if emergencia_detectada_H:
        semaforos["H"] = "verde"
        semaforos["V"] = "rojo"
        tiempo_ultimo_cambio = time.time() # Resetear timer para que no cambie de golpe al irse la ambulancia
        return 
    elif emergencia_detectada_V:
        semaforos["H"] = "rojo"
        semaforos["V"] = "verde"
        tiempo_ultimo_cambio = time.time()
        return 

    # 2. R4: Lógica Normal (Ciclo de Tiempo) --- ¡AQUÍ ESTABA EL PROBLEMA! ---
    # Si NO hay emergencias, alternamos las luces por tiempo.
    
    ahora = time.time()
    if ahora - tiempo_ultimo_cambio > config.DURACION_LUZ_VERDE:
        # ¡Ha pasado el tiempo! Toca cambio de luces.
        if semaforos["H"] == "verde":
            semaforos["H"] = "rojo"
            semaforos["V"] = "verde"
        else:
            semaforos["H"] = "verde"
            semaforos["V"] = "rojo"
        
        # Guardamos el tiempo de este cambio
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

    server_socket.setblocking(False)
    print("Socket en modo NO-BLOQUEANTE.")

    while True:
        # --- PASO A: Recibir y Procesar Paquetes ---
        time_now = time.time()
        
        while True:
            try:
                datos_bytes, direccion_cliente = server_socket.recvfrom(4096)
                
                try:
                    datos_string = datos_bytes.decode('utf-8')
                    mensaje = json.loads(datos_string)
                    
                    # Lógica de Mensajes
                    tipo = mensaje.get("tipo_mensaje")

                    if tipo == "SOLICITUD_VISUALIZADOR":
                        # Respuesta completa para el visualizador
                        respuesta = {
                            "semaforos": estado_global_semaforos,
                            "vehiculos": list(estado_global_vehiculos.values())
                        }
                        bytes_respuesta = json.dumps(respuesta).encode('utf-8')
                        server_socket.sendto(bytes_respuesta, direccion_cliente)
                    
                    elif tipo == "SOLICITUD_LUCES":
                        # Respuesta ligera para el simulador
                        respuesta = {"semaforos": estado_global_semaforos}
                        bytes_respuesta = json.dumps(respuesta).encode('utf-8')
                        server_socket.sendto(bytes_respuesta, direccion_cliente)

                    else:
                        # Mensaje de un vehículo
                        vid = mensaje.get("id")
                        if vid:
                            mensaje["timestamp_recibido"] = time_now
                            estado_global_vehiculos[vid] = mensaje
                        
                except (UnicodeDecodeError, json.JSONDecodeError):
                    pass 

            except BlockingIOError:
                break 
            except socket.error as e:
                print(f"[ERROR SOCKET] {e}")
                break

        # --- PASO B: Limpieza de Fantasmas ---
        ids_a_borrar = []
        for vid, datos_v in estado_global_vehiculos.items():
            tiempo_sin_actualizar = time_now - datos_v.get("timestamp_recibido", 0)
            if tiempo_sin_actualizar > config.SEGUNDOS_TIMEOUT_VEHICULO:
                ids_a_borrar.append(vid)
        
        for vid in ids_a_borrar:
            del estado_global_vehiculos[vid]

        # --- PASO C: Algoritmo ---
        ejecutar_algoritmo_smart(estado_global_vehiculos, estado_global_semaforos)

        # --- PASO D: Imprimir Resumen ---
        if (time_now - last_print_time) > 2.0: 
            print(f"--- Estado: {estado_global_semaforos} | Autos Activos: {len(estado_global_vehiculos)} ---")
            last_print_time = time_now

        time.sleep(0.05) 

if __name__ == "__main__":
    main()