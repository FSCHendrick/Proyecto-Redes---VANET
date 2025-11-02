import pygame, random, time
from vehiculo import Vehiculo
from semaforo import Semaforo
from protocolo import ProtocoloVANET
from interfaz import dibujar_cruce, ANCHO, ALTO
import random

# Inicializar pygame y la ventana
pygame.init()
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Simulación VANET - Smart City")

# Crear semáforos (posición aproximada del cruce)
semaforos = [
    Semaforo(1, 390, 240),
    Semaforo(2, 410, 360)
]

# Crear vehículos (id, tipo, posición x, posición y, dirección)
vehiculos = []
direcciones = ["E", "W", "N", "S"]
tipos = ["normal", "normal", "emergencia"]  # más probabilidad de autos normales

for i in range(10):  # crea 10 vehículos
    tipo = random.choice(tipos)
    dir = random.choice(direcciones)
    if dir == "E":
        x, y = random.randint(50, 200), 260
    elif dir == "W":
        x, y = random.randint(600, 750), 320
    elif dir == "S":
        x, y = 390, random.randint(50, 200)
    else:  # N
        x, y = 410, random.randint(400, 550)
    vehiculos.append(Vehiculo(i+1, tipo, x, y, dir))


clock = pygame.time.Clock()
ejecutando = True

# Estado inicial del semáforo
traffic_light = "verde"
last_switch = 0  # último momento en que cambió el color

# ------------------------- BUCLE PRINCIPAL -------------------------
while ejecutando:
    # --- Captura de eventos (para cerrar la ventana) ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            ejecutando = False

    # Para cada vehículo: detectar semáforo, mover y enviar mensaje (una sola vez)
    for v in vehiculos:
        v.detectar_semaforo(semaforos)
        v.mover()
        for s in semaforos:
            ProtocoloVANET.enviar(v.generar_mensaje(), s)


    # --- Actualizar los semáforos ---
    for s in semaforos:
        s.actualizar_estado()
        s.limpiar_datos()

    # --- Control automático del semáforo ---
    time_now = pygame.time.get_ticks()  # tiempo actual en milisegundos

    # Ciclo de semáforo más estable (6s verde, 2s amarillo, 5s rojo)
    if traffic_light == "verde" and time_now - last_switch > 6000:
        traffic_light = "amarillo1"
        last_switch = time_now
    elif traffic_light == "amarillo1" and time_now - last_switch > 2000:
        traffic_light = "rojo"
        last_switch = time_now
    elif traffic_light == "rojo" and time_now - last_switch > 5000:
        traffic_light = "amarillo2"
        last_switch = time_now
    elif traffic_light == "amarillo2" and time_now - last_switch > 2000:
        traffic_light = "verde"
        last_switch = time_now

        # --- print("Cambio semáforo a", traffic_light, "en", time_now)

    # Aplicar el nuevo color a todos los semáforos
    for s in semaforos:
        s.estado = traffic_light

    # --- Dibujar elementos ---
    dibujar_cruce(pantalla, vehiculos, semaforos)
    pygame.display.flip()

    # Controlar la velocidad de actualización (FPS)
    clock.tick(30)

# Finalizar pygame
pygame.quit()
