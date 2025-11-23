import socket
import json
import time

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

ANCHO = 800
ALTO = 600
VELOCIDAD = 2


def posicion_inicial(linea: str, direccion: str):
    if linea == "H":
        if direccion == "E":
            return -20, 270
        elif direccion == "W":
            return ANCHO + 20, 330
        else:
            raise ValueError("Para LINEA='H' la DIRECCION debe ser 'E' o 'W'")

    elif linea == "V":
        if direccion == "S":
            return 340, -20
        elif direccion == "N":
            return 450, ALTO + 20
        else:
            raise ValueError("Para LINEA='V' la DIRECCION debe ser 'N' o 'S'")

    else:
        raise ValueError("LINEA debe ser 'H' o 'V'")


def enviar_estado(sock, x, y, imprimir=False):
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

    if imprimir:
        print(f"Vehículo enviado una sola vez: {mensaje}")


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Obtener posición inicial
    x, y = posicion_inicial(LINEA, DIRECCION)

    print(f"Iniciando VANET client hacia {SERVER_IP}:{SERVER_PORT}")
    print(f"Vehículo {VEHICLE_ID} creado | Línea={LINEA} | Dirección={DIRECCION} | Tipo={TIPO}")
    print(f"Posición inicial: ({x}, {y})\n")

    # ⭐ Primer envío: se imprime SOLO una vez
    enviar_estado(sock, x, y, imprimir=True)

    try:
        while True:
            enviar_estado(sock, x, y)
            if DIRECCION == "E":
                x += VELOCIDAD
            elif DIRECCION == "W":
                x -= VELOCIDAD
            elif DIRECCION == "S":
                y += VELOCIDAD
            elif DIRECCION == "N":
                y -= VELOCIDAD
            if x < -60 or x > 860 or y < -60 or y > 660:
                print("Vehículo salió de la simulación. Cliente finalizado.")
                break

            time.sleep(1 / 30)

    except KeyboardInterrupt:
        print("\nCliente detenido por el usuario.")

    finally:
        sock.close()


if __name__ == "__main__":
    main()
