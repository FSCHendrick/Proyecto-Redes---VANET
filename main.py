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
    Semaforo(1, 390, 240, "verde", "H"),
    Semaforo(2, 410, 360, "verde", "H"),
    Semaforo(3, 360, 200, "rojo", "V"),
    Semaforo(4, 440, 400, "rojo", "V")
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
        linea = "H"
    elif dir == "W":
        x, y = random.randint(600, 750), 320
        linea = "H"
    elif dir == "S":
        x, y = 390, random.randint(50, 200)
        linea = "V"
    else:  # N
        x, y = 410, random.randint(400, 550)
        linea = "V"

    vehiculos.append(Vehiculo(i+1, tipo, x, y, linea, dir))



clock = pygame.time.Clock()
ejecutando = True

# Estado inicial general de los semáforos
estado_general = {
    "H": "verde",   # semáforos horizontales inician en verde
    "V": "rojo",    # semáforos verticales en rojo
    "fase": 1       # indica en qué etapa del ciclo estamos
}


last_switch = 0  # Momento del último cambio
intervalo = 6000  # Duración de cada ciclo (6 segundos aprox)


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
        s.actualizar_estado(estado_general)
        s.limpiar_datos()


    # --- Control automático del semáforo ---
    time_now = pygame.time.get_ticks()
    elapsed = time_now - last_switch

    # Fase 1 y 2: Horizontal tiene prioridad
    if estado_general["fase"] == 1:  # Horizontal verde
        if elapsed > 6000:
            estado_general["H"] = "amarillo"
            estado_general["V"] = "rojo"
            estado_general["fase"] = 2
            last_switch = time_now

    elif estado_general["fase"] == 2:  # Horizontal amarillo
        if elapsed > 3000:
            estado_general["H"] = "rojo"
            estado_general["V"] = "verde"
            estado_general["fase"] = 3
            last_switch = time_now

    # Fase 3 y 4: Vertical tiene prioridad
    elif estado_general["fase"] == 3:  # Vertical verde
        if elapsed > 6000:
            estado_general["H"] = "rojo"
            estado_general["V"] = "amarillo"
            estado_general["fase"] = 4
            last_switch = time_now

    elif estado_general["fase"] == 4:  # Vertical amarillo
        if elapsed > 3000:
            estado_general["H"] = "verde"
            estado_general["V"] = "rojo"
            estado_general["fase"] = 1
            last_switch = time_now





    # Aplicar el nuevo color a todos los semáforos
    for s in semaforos:
        s.estado = estado_general[s.linea]


    # --- Dibujar elementos ---
    dibujar_cruce(pantalla, vehiculos, semaforos)
    pygame.display.flip()

    # Controlar la velocidad de actualización (FPS)
    clock.tick(30)

# Finalizar pygame
pygame.quit()
