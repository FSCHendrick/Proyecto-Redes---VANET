# visualizador_flask.py
import socket
import json
import config
from flask import Flask, jsonify, render_template

DESTINO = (config.HOST, config.PORT)

sock_viz = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_viz.settimeout(0.2)

# 👇 NUEVO: usar carpeta "assets" como estática
app = Flask(__name__, static_folder='assets', static_url_path='/assets')
# (así podrás usar /assets/auto.png y /assets/ambula.png en el HTML)

def pedir_estado_controlador():
    solicitud = {"tipo_mensaje": "SOLICITUD_VISUALIZADOR"}
    try:
        sock_viz.sendto(json.dumps(solicitud).encode("utf-8"), DESTINO)
        datos_bytes, _ = sock_viz.recvfrom(40960)
        estado = json.loads(datos_bytes.decode("utf-8"))
    except Exception as e:
        print(f"[ERROR VIZ] {e}")
        estado = {"vehiculos": [], "semaforos": {}}
    return estado

@app.route("/")
def index():
    return render_template("index.html", ancho=config.ANCHO, alto=config.ALTO)

@app.route("/estado")
def estado():
    return jsonify(pedir_estado_controlador())

if __name__ == "__main__":
    app.run(debug=True)

