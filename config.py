# --- CONFIGURACIÓN DE RED ---
# "127.0.0.1" para pruebas en PC. 
HOST = "127.0.0.1" 
PORT = 9999

# --- DIMENSIONES DE LA SIMULACIÓN ---
ANCHO = 800
ALTO = 600

# --- LÓGICA DEL SEMÁFORO ---
DURACION_LUZ_VERDE = 5.0        # Tiempo del ciclo normal
SEGUNDOS_TIMEOUT_VEHICULO = 3.0 # Tiempo para borrar "fantasmas"

# --- LÓGICA DE TRÁFICO ---
MAX_VEHICULOS = 15
INTERVALO_SPAWN = 2.0           # Segundos entre cada auto nuevo

# Para correr, crear tres terminales: 1. servidor (controlador.py), 2. cliente (simulador.py), y 3. visualizador.py
# Orden de Ejecucion: 1. Servidor, 2. Visualizador, 3. Cliente (Salir: Ctrl + C)
last_vehicle_id = 0
