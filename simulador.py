import random
import time
import socket
import json
import config
from vehiculo import Vehiculo
from semaforo import Semaforo
from protocolo import ProtocoloVANET

# --- Configuración ---
config.ANCHO, config.ALTO = 800, 600

# Crear semáforos locales (Estos se actualizarán con datos de la red)
semaforos = [
    Semaforo(1, 300, 300, "verde", "H"),
    Semaforo(2, 500, 300, "verde", "H"),
    Semaforo(3, 400, 240, "rojo", "V"),
    Semaforo(4, 400, 360, "rojo", "V")
]

vehiculos = []
direcciones = ["E", "W", "N", "S"]
tipos = ["normal", "normal", "normal", "normal", "normal", "normal", "normal", "normal", "normal", "emergencia"]

ultimo_spawn = 0
config.intervalo_spawn = 2.0
config.max_vehiculos = 15

# Configurar socket para RECIBIR respuesta del controlador
sock_sim = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_sim.settimeout(0.05)

print("Iniciando simulador de vehículos...")
print(f"Enviando datos a {ProtocoloVANET.DESTINO}")

try:
    while True:
        time_now = time.time()

        # --- 1. SINCRONIZAR SEMÁFOROS CON EL CONTROLADOR (NUEVO) ---
        try:
            # A. Preguntar al controlador
            solicitud = {"tipo_mensaje": "SOLICITUD_LUCES"}
            sock_sim.sendto(json.dumps(solicitud).encode('utf-8'), ProtocoloVANET.DESTINO)
            
            # B. Esperar respuesta
            datos_bytes, _ = sock_sim.recvfrom(1024)
            datos_str = datos_bytes.decode('utf-8')
            respuesta = json.loads(datos_str)
            
            estado_luces = respuesta.get("semaforos", {})
            
            # C. Actualizar nuestros objetos Semaforo locales
            # Si el controlador dice H='rojo', todos los H en rojo.
            for s in semaforos:
                if s.linea in estado_luces:
                    s.estado = estado_luces[s.linea]
                    
        except socket.timeout:
            pass
        except Exception as e:
            print(f"Error al sincronizar luces: {e}")


        # --- 2. LOGICA DE VEHÍCULOS ---
        if len(vehiculos) < config.max_vehiculos and (time_now - ultimo_spawn) > config.intervalo_spawn:
            tipo = random.choice(tipos)
            dir = random.choice(direcciones)

            if dir == "E":   x, y, linea = -20, 270, "H"
            elif dir == "W": x, y, linea = config.ANCHO + 20, 330, "H"
            elif dir == "S": x, y, linea = 340, -20, "V"
            else:            x, y, linea = 450, config.ALTO + 20, "V"

            if not any(abs(v.x - x) < 30 and abs(v.y - y) < 30 for v in vehiculos):
                config.last_vehicle_id += 1
                nuevo_id = config.last_vehicle_id
                nuevo = Vehiculo(nuevo_id, tipo, x, y, linea, dir)
                vehiculos.append(nuevo)
                ultimo_spawn = time_now
                print(f"[SPAWN] {nuevo.id} ({tipo}) en {linea}")

        # Mover y Enviar
        for v in vehiculos:
            v.detectar_semaforo(semaforos) 
            v.mover(vehiculos)
            
            mensaje = v.generar_mensaje()
            if mensaje:
                ProtocoloVANET.enviar(mensaje)

        # Cleanup
        vehiculos_activos = [v for v in vehiculos if getattr(v, "activo", True)]
        vehiculos = vehiculos_activos

        time.sleep(1 / 30)

except KeyboardInterrupt:
    print("\nSimulación detenida.")
finally:
    ProtocoloVANET.cerrar_socket()
    sock_sim.close()