# vanet_client.py
import socket
import json
import time

# ==========================
# CONFIGURACIÓN DEL SERVIDOR
# ==========================
SERVER_IP = "44.214.110.153"   # IP pública de tu EC2
SERVER_PORT = 9999             # Mismo puerto que usa controlador.py
DESTINO = (SERVER_IP, SERVER_PORT)

# ==========================
# CONFIG DEL "VEHÍCULO"
# ==========================
VEHICLE_ID = "gurt"     # ID único para este vehículo
TIPO = "normal"        # "normal" o "emergencia"
LINEA = "V"            # "H" o "V"
DIRECCION = "S"        # Para H: "E", "W". Para V: "N", "S"

# Dimensiones de la simulación (como en config.py)
ANCHO = 800
ALTO = 600

# Velocidad del vehículo (pixeles por paso)
VELOCIDAD = 2


def posicion_inicial(linea: str, direccion: str):
    """
    Devuelve (x, y) de inicio según la línea y dirección,
    usando las mismas posiciones que tu simulador.py.
    """
    if linea == "H":
        if direccion == "E":
            # De izquierda a derecha
            return -20, 270
        elif direccion == "W":
            # De derecha a izquierda
            return ANCHO + 20, 330
        else:
            raise ValueError("Para LINEA='H' la DIRECCION debe ser 'E' o 'W'")
    elif linea == "V":
        if direccion == "S":
            # De arriba hacia abajo
            return 340, -20
        elif direccion == "N":
            # De abajo hacia arriba
            return 450, ALTO + 20
        else:
            raise ValueError("Para LINEA='V' la DIRECCION debe ser 'N' o 'S'")
    else:
        raise ValueError("LINEA debe ser 'H' o 'V'")


def enviar_estado(sock, x, y):
    """Construye y envía el mensaje del vehículo al controlador."""
    mensaje = {
        "tipo_mensaje": "VEHICULO",
        "id": VEHICLE_ID,
        "tipo": TIPO,
        "linea": LINEA,
        "direccion": DIRECCION,
        "posicion": [x, y],
    }
    datos = json.dumps(mensaje).encode("utf-8")
    sock.sendto(datos, DESTINO)
    print(f"Enviado: {mensaje}")


def main():
    # Crear socket UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print(f"Iniciando VANET client hacia {SERVER_IP}:{SERVER_PORT} con ID={VEHICLE_ID}")
    print(f"LINEA={LINEA}, DIRECCION={DIRECCION}, TIPO={TIPO}")

    # Posición inicial según línea/dirección
    x, y = posicion_inicial(LINEA, DIRECCION)

    try:
        while True:
            # Enviar estado actual
            enviar_estado(sock, x, y)

            # Actualizar posición según la dirección
            if DIRECCION == "E":
                x += VELOCIDAD
            elif DIRECCION == "W":
                x -= VELOCIDAD
            elif DIRECCION == "S":
                y += VELOCIDAD
            elif DIRECCION == "N":
                y -= VELOCIDAD

            # Si se sale de la zona visible, terminamos
            if x < -60 or x > 860 or y < -60 or y > 660:
                print("Vehículo salió del área de simulación. Fin del cliente.")
                break

            # ~30 FPS
            time.sleep(1 / 30)

    except KeyboardInterrupt:
        print("\nCliente detenido por el usuario.")
    finally:
        sock.close()


if __name__ == "__main__":
    main()
