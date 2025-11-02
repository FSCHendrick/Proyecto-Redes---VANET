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
    "H": "verde",   # Los semáforos horizontales comienzan en verde
    "V": "rojo"     # Los verticales comienzan en rojo
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

    # Cambiar el estado cada cierto tiempo
    if time_now - last_switch > intervalo:
        # Intercambiar los colores
        if estado_general["H"] == "verde":
            estado_general["H"] = "rojo"
            estado_general["V"] = "verde"
        else:
            estado_general["H"] = "verde"
            estado_general["V"] = "rojo"

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
