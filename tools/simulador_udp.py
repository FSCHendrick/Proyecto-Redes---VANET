import socket, json, time

SERVER_IP = "127.0.0.1"   # tu misma PC
SERVER_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

autos = [
    {"id": 1, "tipo": "normal",     "posx": -20, "posy": 270, "dir": "E", "linea": "H", "vel": 2},
    {"id": 2, "tipo": "emergencia", "posx": 340, "posy": -20, "dir": "S", "linea": "V", "vel": 3},
]

while True:
    for v in autos:
        if v["dir"] == "E": v["posx"] += v["vel"]
        if v["dir"] == "W": v["posx"] -= v["vel"]
        if v["dir"] == "S": v["posy"] += v["vel"]
        if v["dir"] == "N": v["posy"] -= v["vel"]

        data = json.dumps(v).encode()
        sock.sendto(data, (SERVER_IP, SERVER_PORT))
        time.sleep(0.03)
