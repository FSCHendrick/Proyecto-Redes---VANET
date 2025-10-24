import pygame
from vehiculo import Vehiculo
from semaforo import Semaforo
from protocolo import ProtocoloVANET
from interfaz import dibujar_cruce, ANCHO, ALTO

pygame.init()
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Simulación VANET - Control Dinámico y Emergencias (CORREGIDO)")

# ------------------ CONFIGURACIÓN INICIAL ------------------

semaforos = [
    Semaforo(1, 390, 240),  # Norte
    Semaforo(2, 410, 360),  # Sur
    Semaforo(3, 300, 290),  # Oeste
    Semaforo(4, 500, 310)   # Este
]

vehiculos = [
    # E → W
    Vehiculo(1, "normal", 50, 260, "E"),
    Vehiculo(2, "normal", 100, 270, "E"),
    Vehiculo(3, "emergencia", 10, 280, "E"),

    # W → E
    Vehiculo(4, "normal", 750, 320, "W"),
    Vehiculo(5, "normal", 700, 310, "W"),

    # N → S
    Vehiculo(6, "normal", 400, 50, "S"),
    Vehiculo(7, "emergencia", 420, 30, "S"),

    # S → N
    Vehiculo(8, "normal", 410, 550, "N"),
    Vehiculo(9, "normal", 430, 560, "N"),
]

clock = pygame.time.Clock()
ejecutando = True

# ------------------ CONTROL DE SEMÁFOROS ------------------

# Iniciamos con eje N-S verde, E-O rojo
estado_NS = "verde"
estado_EO = "rojo"
last_switch = pygame.time.get_ticks()

# Duraciones en milisegundos
duracion_verde = 5000
duracion_amarillo = 2000
tiempo_cambio = duracion_verde

# Estado de emergencia
emergencia_activa_until = 0
duracion_prioridad = 5000  # ms (5 segundos de prioridad)

# -----------------------------------------------------------------
#                     BUCLE PRINCIPAL
# -----------------------------------------------------------------
while ejecutando:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            ejecutando = False

    tiempo_actual = pygame.time.get_ticks()
    emergencia_activa = tiempo_actual < emergencia_activa_until

    # -----------------------
    # CAMBIO AUTOMÁTICO DE CICLOS (solo si no hay emergencia)
    # -----------------------
    if not emergencia_activa and (tiempo_actual - last_switch > tiempo_cambio):
        if estado_NS == "verde":
            estado_NS = "amarillo"
            estado_EO = "rojo"
            tiempo_cambio = duracion_amarillo
            print("[DEBUG] Cambio → NS=amarillo, EO=rojo")
        elif estado_NS == "amarillo":
            estado_NS = "rojo"
            estado_EO = "verde"
            tiempo_cambio = duracion_verde
            print("[DEBUG] Cambio → NS=rojo, EO=verde")
        elif estado_EO == "verde":
            estado_EO = "amarillo"
            estado_NS = "rojo"
            tiempo_cambio = duracion_amarillo
            print("[DEBUG] Cambio → EO=amarillo, NS=rojo")
        elif estado_EO == "amarillo":
            estado_EO = "rojo"
            estado_NS = "verde"
            tiempo_cambio = duracion_verde
            print("[DEBUG] Cambio → EO=rojo, NS=verde")
        last_switch = tiempo_actual

    # -----------------------
    # APLICAR ESTADOS A LOS SEMÁFOROS
    # -----------------------
    for s in semaforos:
        if s.id in [1, 2]:  # Norte y Sur
            s.estado = estado_NS
        elif s.id in [3, 4]:  # Oeste y Este
            s.estado = estado_EO

    # -----------------------
    # ACTUALIZAR VEHÍCULOS Y ENVIAR MENSAJES
    # -----------------------
    for v in vehiculos:
        v.detectar_semaforo(semaforos)
        v.mover()
        for s in semaforos:
            ProtocoloVANET.enviar(v.generar_mensaje(), s)

    # -----------------------
    # DETECTAR EMERGENCIAS
    # -----------------------
    for s in semaforos:
        if any(msg["tipo"] == "emergencia" for msg in s.vehiculos_detectados):
            if not emergencia_activa:
                if s.id in [1, 2]:  # eje N-S
                    estado_NS = "verde"
                    estado_EO = "rojo"
                    print("[PRIORIDAD] Emergencia eje N-S")
                else:  # eje E-O
                    estado_EO = "verde"
                    estado_NS = "rojo"
                    print("[PRIORIDAD] Emergencia eje E-O")
                emergencia_activa_until = tiempo_actual + duracion_prioridad
                last_switch = tiempo_actual
        s.limpiar_datos()

    # -----------------------
    # DIBUJAR ESCENA
    # -----------------------
    dibujar_cruce(pantalla, vehiculos, semaforos)
    pygame.display.flip()
    clock.tick(30)

pygame.quit()
