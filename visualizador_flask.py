# visualizador_flask.py
import socket
import json
import time
import threading
import os
import config
from flask import Flask, jsonify, render_template

# --- Configuración de red: igual que antes ---
HOST_VIZ = os.getenv("VIZ_HOST", config.HOST)
PORT_VIZ = int(os.getenv("VIZ_PORT", config.PORT))
DESTINO = (HOST_VIZ, PORT_VIZ)

sock_viz = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_viz.settimeout(0.2)

# 👇 Flask sirve /assets/... como estático
app = Flask(__name__, static_folder='assets', static_url_path='/assets')

# --- ESTADO COMPARTIDO ENTRE HILO Y FLASK ---
estado_compartido = {
    "vehiculos": [],
    "semaforos": {}
}
lock_estado = threading.Lock()


def pedir_estado_controlador():
    """Envía SOLICITUD_VISUALIZADOR al controlador y devuelve el estado (o vacío si falla)."""
    solicitud = {"tipo_mensaje": "SOLICITUD_VISUALIZADOR"}
    try:
        sock_viz.sendto(json.dumps(solicitud).encode("utf-8"), DESTINO)
        datos_bytes, _ = sock_viz.recvfrom(40960)
        estado = json.loads(datos_bytes.decode("utf-8"))
    except Exception as e:
        print(f"[ERROR VIZ UDP] {e}")
        estado = {"vehiculos": [], "semaforos": {}}
    return estado


def loop_polling(intervalo=0.1):
    """
    Hilo de fondo:
    - Cada 'intervalo' segundos pregunta al controlador
    - Actualiza estado_compartido con lock
    """
    global estado_compartido
    print("[POLLING] Hilo de polling iniciado.")
    while True:
        nuevo_estado = pedir_estado_controlador()
        with lock_estado:
            estado_compartido = nuevo_estado
        time.sleep(intervalo)


@app.route("/")
def index():
    return render_template("index.html", ancho=config.ANCHO, alto=config.ALTO)


@app.route("/estado")
def estado():
    # Aquí NO hablamos por UDP, solo devolvemos el último estado cacheado
    with lock_estado:
        return jsonify(estado_compartido)


if __name__ == "__main__":
    # Lanzar hilo de polling ANTES de arrancar Flask
    hilo = threading.Thread(target=loop_polling, daemon=True)
    hilo.start()

    # Servidor web
    app.run(debug=True)


