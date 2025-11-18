# simulador.py (emula al ESP32)
import socket, json, time

SERVER_IP = "127.0.0.1"
SERVER_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

vehiculos_fake = [
    {"id":1,"tipo":"normal","posx":0,"posy":270,"dir":"E","vel":2,"linea":"H"},
    {"id":2,"tipo":"emergencia","posx":350,"posy":0,"dir":"S","vel":3,"linea":"V"}
]

while True:
    for v in vehiculos_fake:
        # mover
        if v["dir"]=="E": v["posx"]+=v["vel"]
        if v["dir"]=="W": v["posx"]-=v["vel"]
        if v["dir"]=="S": v["posy"]+=v["vel"]
        if v["dir"]=="N": v["posy"]-=v["vel"]

        datos = json.dumps(v).encode()
        sock.sendto(datos, (SERVER_IP, SERVER_PORT))

        time.sleep(0.05)