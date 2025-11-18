import random
import time  # Usaremos 'time' en lugar de 'pygame.time'
from vehiculo import Vehiculo
from semaforo import Semaforo  # Aún lo necesitamos para que 'Vehiculo' funcione
from protocolo import ProtocoloVANET

# --- Configuración de la Simulación ---
ANCHO, ALTO = 800, 600  # Aún útil para los límites de "spawn"

# Crear semáforos (TEMPORAL)
# NOTA: Esto es solo para que v.detectar_semaforo() no falle.
# En una versión futura, el 'controlador' nos dirá los estados.
semaforos = [
    Semaforo(1, 300, 300, "verde", "H"),
    Semaforo(2, 500, 300, "verde", "H"),
    Semaforo(3, 400, 240, "rojo", "V"),
    Semaforo(4, 400, 360, "rojo", "V")
]

# Lista para guardar nuestros vehículos simulados
vehiculos = []
direcciones = ["E", "W", "N", "S"]
tipos = ["normal", "normal", "normal", "normal", "emergencia"] # 1 de 5 es emergencia

# --- Configuración para aparición gradual de vehículos ---
ultimo_spawn = 0        # tiempo del último vehículo creado (en segundos)
intervalo_spawn = 2.0   # cada 2 segundos aparece uno nuevo
max_vehiculos = 15      # límite total de autos en la simulación

print("Iniciando simulador de vehículos...")
print(f"Enviando datos a {ProtocoloVANET.DESTINO}")

# ------------------------- BUCLE PRINCIPAL (Headless) -------------------------
try:
    while True:
        # Usamos time.time() que da los segundos actuales
        time_now = time.time()

        # --- Crear vehículos gradualmente en los extremos (flujo continuo) ---
        if len(vehiculos) < max_vehiculos and (time_now - ultimo_spawn) > intervalo_spawn:
            tipo = random.choice(tipos)
            dir = random.choice(direcciones)

            if dir == "E":   # izquierda → derecha
                x, y, linea = -20, 270, "H"
            elif dir == "W": # derecha → izquierda
                x, y, linea = ANCHO + 20, 330, "H"
            elif dir == "S": # arriba → abajo
                x, y, linea = 340, -20, "V"
            else:            # N → abajo → arriba
                x, y, linea = 450, ALTO + 20, "V"

            # Evita superposición en el punto de aparición
            if not any(abs(v.x - x) < 30 and abs(v.y - y) < 30 for v in vehiculos):
                nuevo_id = int(time_now * 100) + random.randint(1, 100) # ID único
                nuevo = Vehiculo(nuevo_id, tipo, x, y, linea, dir)
                vehiculos.append(nuevo)
                ultimo_spawn = time_now
                print(f"[SPAWN] Creado vehículo {nuevo.id} (Tipo: {tipo})")

        # --- Mover y Enviar Datos de cada vehículo ---
        for v in vehiculos:
            # NOTA: 'detectar_semaforo' usa la lista 'semaforos' local y fija.
            # Los autos se detendrán en los semáforos 'rojo' iniciales.
            # ¡Esto está bien para nuestra prueba!
            v.detectar_semaforo(semaforos) 
            
            v.mover(vehiculos)
            
            # Generar el mensaje del protocolo
            mensaje = v.generar_mensaje()
            
            # Enviar el mensaje por la red
            if mensaje:
                ProtocoloVANET.enviar(mensaje)

        # Eliminar vehículos inactivos o que salieron de pantalla
        vehiculos_activos = []
        for v in vehiculos:
            if getattr(v, "activo", True):
                vehiculos_activos.append(v)
        
        if len(vehiculos) != len(vehiculos_activos):
             print(f"[CLEANUP] Vehículos activos: {len(vehiculos_activos)} / {len(vehiculos)}")
        
        vehiculos = vehiculos_activos

        # --- Controlar la velocidad de actualización ---
        # Dormimos por un corto tiempo para simular los "frames" (ej. 30 FPS)
        # Esto evita que el bucle corra al 100% de CPU y sature la red.
        time.sleep(1 / 30) # 30 "ticks" por segundo

except KeyboardInterrupt:
    # Captura si presionas Ctrl+C en la terminal
    print("\nSimulación detenida por el usuario.")

finally:
    # Esto es importante para cerrar el socket de forma limpia
    ProtocoloVANET.cerrar_socket()
    print("Simulador finalizado.")