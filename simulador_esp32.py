# simulador_esp32.py
# Simula un ESP32 enviando datos de vehículos por UDP al controlador.

import socket
import json
import time
import random
import config

# Dirección del controlador
DESTINO = (config.HOST, config.PORT)

# Crear socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(0.1)

# Vehículo simulado (generado igual que el simulador original)
direccion = random.choice(["E","W","N","S"])
tipo = random.choice(["normal","emergencia"])

# Posición inicial según dirección
if direccion == "E":       x, y, linea = -20, 270, "H"
elif direccion == "W":     x, y, linea = config.ANCHO + 20, 330, "H"
elif direccion == "S":     x, y, linea = 340, -20, "V"
else:                      x, y, linea = 450, config.ALTO + 20, "V"

vehiculo = {
    "id": 100,               # ID fijo (como si fuera un ESP32 real)
    "tipo": tipo,           # "normal" o "emergencia"
    "posicion": [x, y],     # Coordenadas según el carril
    "linea": linea,         # H o V
    "direccion": direccion  # E, W, N, S
}

# Velocidades por dirección
vel = {
    "E": (2, 0),
    "W": (-2, 0),
    "N": (0, -2),
    "S": (0, 2)
}

print(f"[SIM ESP32] Enviando datos al controlador en {DESTINO}")
print("[Ctrl + C] para salir")

# ------------------------------
# Ajuste de carriles según dirección
# ------------------------------
def ajustar_carril(vehiculo):
    """
    Ajusta la posición del vehículo para que circule por su carril correcto
    dependiendo de la línea (H/V) y dirección.
    """
    if vehiculo["linea"] == "H":  # Horizontal
        if vehiculo["direccion"] == "E":   # Este
            vehiculo["posicion"][1] = config.CARRIL_H_E
        elif vehiculo["direccion"] == "W": # Oeste
            vehiculo["posicion"][1] = config.CARRIL_H_W

    elif vehiculo["linea"] == "V":  # Vertical
        if vehiculo["direccion"] == "N":   # Norte
            vehiculo["posicion"][0] = config.CARRIL_V_N
        elif vehiculo["direccion"] == "S": # Sur
            vehiculo["posicion"][0] = config.CARRIL_V_S


# ------------------------------
# Bucle principal
# ------------------------------
try:
    while True:

        # Colocar el vehículo en el carril correcto antes de moverlo
        ajustar_carril(vehiculo)

        # Actualizar posición (movimiento simple)
        dx, dy = vel[vehiculo["direccion"]]
        vehiculo["posicion"][0] += dx
        vehiculo["posicion"][1] += dy

        # Si sale de pantalla, reaparece por el inicio
        if vehiculo["posicion"][0] > config.ANCHO + 50:
            vehiculo["posicion"][0] = -50
        if vehiculo["posicion"][0] < -50:
            vehiculo["posicion"][0] = config.ANCHO + 50
        if vehiculo["posicion"][1] > config.ALTO + 50:
            vehiculo["posicion"][1] = -50
        if vehiculo["posicion"][1] < -50:
            vehiculo["posicion"][1] = config.ALTO + 50

        # Mensaje JSON compatible con controlador.py
        msg = {
            "tipo_mensaje": "VEHICULO",
            "id": vehiculo["id"],
            "tipo": vehiculo["tipo"],
            "posicion": vehiculo["posicion"],
            "linea": vehiculo["linea"],
            "direccion": vehiculo["direccion"]
        }

        # Enviar por UDP
        sock.sendto(json.dumps(msg).encode("utf-8"), DESTINO)

        # Rate de envío (10 Hz)
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n[SIM ESP32] Finalizado.")

finally:
    sock.close()
