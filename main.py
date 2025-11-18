import pygame, random, time, socket, json
from vehiculo import Vehiculo
from semaforo import Semaforo
from protocolo import ProtocoloVANET
from interfaz import dibujar_cruce, ANCHO, ALTO

# Inicializar pygame y la ventana
pygame.init()
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Simulación VANET - Smart City")

# Crear semáforos (posición aproximada del cruce)
semaforos = [
    Semaforo(1, 300, 300, "verde", "H"),
    Semaforo(2, 500, 300, "verde", "H"),
    Semaforo(3, 400, 240, "rojo", "V"),
    Semaforo(4, 400, 360, "rojo", "V")
]

# Crear vehículos (id, tipo, posición x, posición y, dirección)
vehiculos = []
direcciones = ["E", "W", "N", "S"]
tipos = ["normal", "normal", "emergencia"]  # más probabilidad de autos normales

# Configuración para recibir vehículos desde servidor JSON (UDP)
USE_SERVER = True
UDP_IP = "0.0.0.0"
UDP_PORT = 5005
sock = None
if USE_SERVER:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind((UDP_IP, UDP_PORT))
        sock.setblocking(False)
    except Exception:
        sock = None

# --- Configuración para aparición gradual de vehículos (desactivada si USE_SERVER True) ---
ultimo_spawn = 0          # tiempo del último vehículo creado
intervalo_spawn = 2000    # cada 2 segundos aparece uno nuevo
max_vehiculos = 15        # límite total de autos en la simulación


clock = pygame.time.Clock()
ejecutando = True

# Estado inicial de los semáforos
estado_general = {"H": "verde", "V": "rojo"}
fase = "H_verde"
last_switch = 0
intervalo_verde = 6000
intervalo_amarillo = 3000



# ------------------------- BUCLE PRINCIPAL -------------------------
while ejecutando:
    # --- Captura de eventos (para cerrar la ventana) ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            ejecutando = False

    # --- Recibir mensajes JSON desde el servidor (si está habilitado) ---
    time_now = pygame.time.get_ticks()
    if sock:
        while True:
            try:
                data, addr = sock.recvfrom(4096)
            except BlockingIOError:
                break
            except Exception:
                break

            try:
                msg = json.loads(data.decode())
            except Exception:
                continue

            # Normalizar claves esperadas del simulador
            vid = msg.get("id")
            tipo = msg.get("tipo", "normal")
            x = msg.get("posx") if msg.get("posx") is not None else (msg.get("posicion")[0] if msg.get("posicion") else None)
            y = msg.get("posy") if msg.get("posy") is not None else (msg.get("posicion")[1] if msg.get("posicion") else None)
            direccion = msg.get("dir") or msg.get("direccion")
            linea = msg.get("linea") or ("H" if direccion in ["E", "W"] else "V")

            if vid is None or x is None or y is None or direccion is None:
                continue

            # Actualizar vehículo existente o crear nuevo
            existing = next((v for v in vehiculos if v.id == vid), None)
            if existing:
                existing.x = x
                existing.y = y
                existing.direccion = direccion
                existing.linea = linea
                existing.tipo = tipo
                existing.remote = True
                existing.activo = True
            else:
                nuevo = Vehiculo(vid, tipo, x, y, linea, direccion)
                nuevo.remote = True
                vehiculos.append(nuevo)

    # Si no usamos servidor, crear vehículos localmente (modo simulación)
    if not USE_SERVER:
        if len(vehiculos) < max_vehiculos and time_now - ultimo_spawn > intervalo_spawn:
            tipo = random.choice(tipos)
            dir = random.choice(direcciones)

            if dir == "E":   # izquierda → derecha
                x = -20
                y = 270      # carril horizontal superior
                linea = "H"
            elif dir == "W": # derecha → izquierda
                x = ANCHO + 20
                y = 330      # carril horizontal inferior
                linea = "H"
            elif dir == "S": # arriba → abajo
                x = 340      # carril vertical izquierdo
                y = -20
                linea = "V"
            else:            # N → abajo → arriba
                x = 450      # carril vertical derecho
                y = ALTO + 20
                linea = "V"

            # Evita superposición en el punto de aparición
            if not any(abs(v.x - x) < 30 and abs(v.y - y) < 30 for v in vehiculos):
                nuevo = Vehiculo(len(vehiculos) + random.randint(1, 50), tipo, x, y, linea, dir)
                vehiculos.append(nuevo)
                ultimo_spawn = time_now

    # Para cada vehículo: si es local calcular detección/movimiento; si viene del servidor, usar posición recibida
    for v in vehiculos:
        if not getattr(v, "remote", False):
            v.detectar_semaforo(semaforos)
            v.mover(vehiculos)

        # Enviar el mensaje (si deseas evitar reenviar datos de vehículos remotos, filtrar aquí)
        for s in semaforos:
            ProtocoloVANET.enviar(v.generar_mensaje(), s)

    # Eliminar vehículos inactivos o que salieron de pantalla
    vehiculos = [v for v in vehiculos if getattr(v, "activo", True)]



    # --- Control automático del semáforo ---
    time_now = pygame.time.get_ticks()

    if fase == "H_verde" and time_now - last_switch > intervalo_verde:
        estado_general["H"] = "amarillo1"
        estado_general["V"] = "rojo"
        fase = "H_amarillo"
        last_switch = time_now

    elif fase == "H_amarillo" and time_now - last_switch > intervalo_amarillo:
        estado_general["H"] = "rojo"
        estado_general["V"] = "verde"
        fase = "V_verde"
        last_switch = time_now

    elif fase == "V_verde" and time_now - last_switch > intervalo_verde:
        estado_general["V"] = "amarillo2"
        estado_general["H"] = "rojo"
        fase = "V_amarillo"
        last_switch = time_now

    elif fase == "V_amarillo" and time_now - last_switch > intervalo_amarillo:
        estado_general["V"] = "rojo"
        estado_general["H"] = "verde"
        fase = "H_verde"
        last_switch = time_now


    # --- Actualizar los semáforos ---
    for s in semaforos:
        s.actualizar_estado(estado_general)
        s.limpiar_datos()

    
    # Aplicar estado actualizado a cada semáforo
    for s in semaforos:
        s.estado = estado_general[s.linea]



    # --- Dibujar elementos ---
    dibujar_cruce(pantalla, vehiculos, semaforos)
    pygame.display.flip()

    # Controlar la velocidad de actualización (FPS)
    clock.tick(30)

# Finalizar pygame
pygame.quit()
