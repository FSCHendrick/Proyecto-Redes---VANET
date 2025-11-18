import socket
import json
import time

# --- Configuración del Servidor ---
HOST = '127.0.0.1'
PORT = 9999
SERVER_ADDRESS = (HOST, PORT)

# --- Constantes del Algoritmo ---
# Si no recibimos un paquete de un auto en 3 segundos,
# lo consideramos "desconectado" o "fantasma" y lo borramos.
SEGUNDOS_TIMEOUT_VEHICULO = 3.0 

# --- ESTADO GLOBAL (El "Cerebro" del Controlador) ---
estado_global_vehiculos = {}
estado_global_semaforos = {
    "H": "verde",
    "V": "rojo"
}
last_print_time = 0

# --- Funciones del Algoritmo (Aquí implementas R4 y R5) ---

def ejecutar_algoritmo_smart(vehiculos, semaforos):
    """
    Ejecuta la lógica de decisión.
    'vehiculos' ahora SÓLO contiene vehículos ACTIVOS.
    """
    
    # --- PASO 1: Implementar R5 (Prioridad de Emergencia) ---
    emergencia_detectada_H = False
    emergencia_detectada_V = False

    # Revisamos TODOS los vehículos ACTIVOS
    for vid, datos_v in vehiculos.items():
        if datos_v["tipo"] == "emergencia":
            if datos_v["linea"] == "H":
                emergencia_detectada_H = True
            elif datos_v["linea"] == "V":
                emergencia_detectada_V = True

    # Lógica de decisión de emergencia (R5)
    if emergencia_detectada_H:
        semaforos["H"] = "verde"
        semaforos["V"] = "rojo"
        return # Prioridad, no ejecutar lógica normal
    elif emergencia_detectada_V:
        semaforos["H"] = "rojo"
        semaforos["V"] = "verde"
        return # Prioridad, no ejecutar lógica normal

    # --- PASO 2: Implementar R4 (Lógica Dinámica "Smart") ---
    # Si no hubo emergencias, ejecutamos la lógica normal.
    
    # ... (Aquí irá tu futuro código R4 para contar autos) ...
    
    # ¡POR AHORA, si no hay emergencias, volvemos al estado normal!
    # (Esto es importante para que la luz no se quede pegada)
    # (En el futuro, esto será un ciclo de tiempo inteligente)
    if semaforos["H"] == "rojo" and semaforos["V"] == "verde":
        # (Lógica futura para cambiar de V -> H)
        pass
    else:
        # (Lógica futura para cambiar de H -> V)
        pass


def main():
    global last_print_time
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        server_socket.bind(SERVER_ADDRESS)
        print(f"Servidor escuchando en {HOST}:{PORT}")
    except socket.error as err:
        print(f"Error al enlazar (bind): {err}")
        return

    server_socket.setblocking(False)
    print("Socket configurado en modo NO-BLOQUEANTE.")

    # ------------------------- BUCLE PRINCIPAL (Tiempo Real) -------------------------
    while True:
        
        # --- PASO A: DRENAR EL BUFFER DE RED (Recibir datos) ---
        time_now = time.time()
        
        while True:
            try:
                datos_bytes, _ = server_socket.recvfrom(1024)
                
                try:
                    datos_string = datos_bytes.decode('utf-8')
                    mensaje_vehiculo = json.loads(datos_string)
                    
                    vid = mensaje_vehiculo.get("id")
                    if vid:
                        # --- ¡MEJORA 1! ---
                        # Añadimos el timestamp de cuándo lo recibimos
                        mensaje_vehiculo["timestamp_recibido"] = time_now
                        estado_global_vehiculos[vid] = mensaje_vehiculo
                        
                except (UnicodeDecodeError, json.JSONDecodeError):
                    print("[ADVERTENCIA] Paquete corrupto recibido.")

            except BlockingIOError:
                # No hay más paquetes por ahora. Salir del bucle de recepción.
                break
            except socket.error as e:
                print(f"[ERROR DE SOCKET] {e}")
                break

        # --- ¡PASO B: LIMPIEZA DE "FANTASMAS"! (NUEVO) ---
        # Borramos vehículos que no han enviado actualizaciones
        ids_a_borrar = []
        for vid, datos_v in estado_global_vehiculos.items():
            # .get() es seguro, si "timestamp_recibido" no existe, usa 0
            tiempo_sin_actualizar = time_now - datos_v.get("timestamp_recibido", 0)
            
            if tiempo_sin_actualizar > SEGUNDOS_TIMEOUT_VEHICULO:
                ids_a_borrar.append(vid)

        # Borramos fuera del bucle principal para no modificar
        # el diccionario mientras lo estamos iterando
        for vid in ids_a_borrar:
            del estado_global_vehiculos[vid]


        # --- PASO C: EJECUTAR EL ALGORITMO "SMART" ---
        # Ahora el algoritmo solo corre sobre la lista "limpia"
        ejecutar_algoritmo_smart(estado_global_vehiculos, estado_global_semaforos)

        
        # --- PASO D: IMPRIMIR UN RESUMEN ---
        if (time_now - last_print_time) > 1.0: # Imprimir solo 1 vez por segundo
            print("--- RESUMEN DEL TICK ---")
            print(f"Estado de Semáforos: {estado_global_semaforos}")
            print(f"Vehículos ACTIVOS detectados: {len(estado_global_vehiculos)}")
            
            last_print_time = time_now

        # --- PASO E: DORMIR ---
        try:
            time.sleep(0.1) # 10 Hz "Tick rate" del controlador
        except KeyboardInterrupt:
            # Capturar Ctrl+C aquí para salir limpiamente
            print("\nCerrando servidor...")
            break # Salir del bucle principal

    # Cerrar el socket al final
    server_socket.close()
    print("Servidor detenido.")

if __name__ == "__main__":
    main()