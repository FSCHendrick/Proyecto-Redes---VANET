import pygame
import socket
import json
import time
import config
from interfaz import dibujar_cruce

# --- Configuración de Red ---
DESTINO = (config.HOST, config.PORT)

# Crear socket UDP para el visualizador
sock_viz = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_viz.settimeout(0.1) 

# --- Clases "Dummy" ---
class VehiculoDummy:
    def __init__(self, datos_dict):
        self.id = datos_dict.get("id")
        self.tipo = datos_dict.get("tipo")
        pos = datos_dict.get("posicion", [0,0])
        self.x = pos[0]
        self.y = pos[1]
        self.linea = datos_dict.get("linea")
        self.direccion = datos_dict.get("direccion")
        self.velocidad = 0
        self.velocidad_normal = 0

# --- CARGA DE IMÁGENES ---
IMAGENES_VEHICULOS = {}

def cargar_assets():
    """Carga las imágenes de la carpeta assets y genera las rotaciones específicas."""
    try:
        # 1. Cargar imágenes base
        img_auto = pygame.image.load("assets/auto.png")      
        img_ambula = pygame.image.load("assets/ambula.png")  

        # 2. Escalar
        TAMANO_AUTO = (50, 40)  
        TAMANO_AMBULA_BASE = (40, 60) 

        img_auto = pygame.transform.scale(img_auto, TAMANO_AUTO)
        img_ambula = pygame.transform.scale(img_ambula, TAMANO_AMBULA_BASE)

        # 3. Generar rotaciones        
        # --- AUTO ---
        IMAGENES_VEHICULOS["normal"] = {
            "S": img_auto,                                  # 0º (Base)
            "E": pygame.transform.rotate(img_auto, 90),     # Abajo -> Derecha (+90º)
            "N": pygame.transform.rotate(img_auto, 180),    # Abajo -> Arriba
            "W": pygame.transform.rotate(img_auto, 270)     # Abajo -> Izquierda
        }
        
        # --- AMBULANCIA ---
        IMAGENES_VEHICULOS["emergencia"] = {
            "W": img_ambula,                                # 0º (Base)
            "S": pygame.transform.rotate(img_ambula, 90),   # Izquierda -> Abajo (+90º)
            "E": pygame.transform.rotate(img_ambula, 180),  # Izquierda -> Derecha
            "N": pygame.transform.rotate(img_ambula, 270)   # Izquierda -> Arriba
        }
        
        print("✅ Imágenes cargadas y rotadas correctamente.")
        return True

    except Exception as e:
        print(f"⚠️ Error cargando imágenes: {e}")
        return False

def main():
    pygame.init()
    pantalla = pygame.display.set_mode((config.ANCHO, config.ALTO))
    pygame.display.set_caption("Visualizador VANET (Con Imágenes)")
    clock = pygame.time.Clock()
    
    usar_imagenes = cargar_assets()
    
    ejecutando = True
    print("Iniciando Visualizador...")

    while ejecutando:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                ejecutando = False

        # --- RED ---
        solicitud = {"tipo_mensaje": "SOLICITUD_VISUALIZADOR"}
        vehiculos_objs = []
        semaforos_objs = []

        try:
            sock_viz.sendto(json.dumps(solicitud).encode('utf-8'), DESTINO)
            datos_bytes, _ = sock_viz.recvfrom(40960)
            estado_recibido = json.loads(datos_bytes.decode('utf-8'))
            
            lista_vehiculos_raw = estado_recibido.get("vehiculos", [])
            dict_semaforos = estado_recibido.get("semaforos", {})
            
            vehiculos_objs = [VehiculoDummy(v) for v in lista_vehiculos_raw]
            
            semaforos_objs = [
                type('obj', (object,), {"x": 300, "y": 300, "estado": dict_semaforos.get("H", "rojo")}),
                type('obj', (object,), {"x": 500, "y": 300, "estado": dict_semaforos.get("H", "rojo")}),
                type('obj', (object,), {"x": 400, "y": 240, "estado": dict_semaforos.get("V", "rojo")}),
                type('obj', (object,), {"x": 400, "y": 360, "estado": dict_semaforos.get("V", "rojo")})
            ]

        except Exception:
            pass

        # --- DIBUJAR ---
        try:
            dibujar_cruce(pantalla, vehiculos_objs, semaforos_objs, IMAGENES_VEHICULOS if usar_imagenes else None)
        except Exception as e:
            print(f"Error dibujo: {e}")
        
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()

if __name__ == "__main__":
    main()