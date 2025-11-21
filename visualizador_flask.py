# visualizador_flask.py
import socket
import json
import time
import threading
import sys

import config
from flask import Flask, jsonify, render_template

# ---------------------------
# LEER PUERTOS DESDE ARGUMENTOS
# ---------------------------
# Uso:
#   python visualizador_flask.py <PUERTO_UDP_CONTROLADOR> <PUERTO_HTTP_FLASK>
#
# Ejemplo:
#   python visualizador_flask.py 9999 5000
#   python visualizador_flask.py 10000 5001

if len(sys.argv) >= 2:
    UDP_PORT = int(sys.argv[1])
else:
    UDP_PORT = config.PORT  # por defecto lo que tengas en config

if len(sys.argv) >= 3:
    HTTP_PORT = int(sys.argv[2])
else:
    HTTP_PORT = 5000  # por defecto 5000

HOST_VIZ = config.HOST
DESTINO = (HOST_VIZ, UDP_PORT)

print(f"[VIZ] Me conectaré al controlador en {DESTINO} (UDP) y serviré Flask en puerto HTTP {HTTP_PORT}")

# Flask sirve /assets/... como estático
app = Flask(__name__, static_folder='assets', static_url_path='/assets')

# --- ESTADO COMPARTIDO ---
estado_compartido = {"vehiculos": [], "semaforos": {}}
lock_estado = threading.Lock()

def pedir_estado_controlador():
    solicitud = {"tipo_mensaje": "SOLICITUD_VISUALIZADOR"}
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(0.2)
    try:
        sock.sendto(json.dumps(solicitud).encode("utf-8"), DESTINO)
        datos_bytes, _ = sock.recvfrom(262144)  # 256 KB para muchos vehículos
        estado_raw = json.loads(datos_bytes.decode("utf-8"))

        # Normalizar para que siempre existan estos campos
        estado = {
            "vehiculos": estado_raw.get("vehiculos", []),
            "semaforos": estado_raw.get("semaforos", {})
        }

    except Exception as e:
        print(f"[ERROR VIZ UDP] {e}")
        estado = {"vehiculos": [], "semaforos": {}}
    finally:
        sock.close()
    return estado

def loop_polling(intervalo=0.1):
    global estado_compartido
    print("[POLLING] Hilo de polling iniciado.")
    while True:
        nuevo_estado = pedir_estado_controlador()
        with lock_estado:
            estado_compartido["vehiculos"] = nuevo_estado.get("vehiculos", [])
            estado_compartido["semaforos"] = nuevo_estado.get("semaforos", {})
        time.sleep(intervalo)

@app.route("/")
def index():
    return render_template("index.html", ancho=config.ANCHO, alto=config.ALTO)

@app.route("/estado")
def estado():
    with lock_estado:
        return jsonify(estado_compartido)

if __name__ == "__main__":
    hilo = threading.Thread(target=loop_polling, daemon=True)
    hilo.start()

    app.run(debug=True, port=HTTP_PORT)
