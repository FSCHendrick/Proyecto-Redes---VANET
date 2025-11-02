import pygame, random, time
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
    Semaforo(1, 390, 240, "verde", "H"),
    Semaforo(2, 410, 360, "verde", "H"),
    Semaforo(3, 360, 200, "rojo", "V"),
    Semaforo(4, 440, 400, "rojo", "V")
]

# Crear vehículos (id, tipo, posición x, posición y, dirección)
vehiculos = []
direcciones = ["E", "W", "N", "S"]
tipos = ["normal", "normal", "emergencia"]  # más probabilidad de autos normales

for i in range(15):  # crea 15 vehículos
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

    # Para cada vehículo: detectar semáforo, mover y enviar mensaje (una sola vez)
    for v in vehiculos:
        v.detectar_semaforo(semaforos)
        v.mover()
        for s in semaforos:
            ProtocoloVANET.enviar(v.generar_mensaje(), s)
    



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
