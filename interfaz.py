import pygame
import config

def dibujar_cruce(pantalla, vehiculos, semaforos, imagenes_dict=None):
    # 1. FONDO (Césped)
    pantalla.fill((34, 139, 34))

    # 2. CALLES (Asfalto)
    color_asfalto = (50, 50, 50)
    # Vertical
    pygame.draw.rect(pantalla, color_asfalto, (300, 0, 200, config.ALTO))
    # Horizontal
    pygame.draw.rect(pantalla, color_asfalto, (0, 250, config.ANCHO, 100))
    
    # 3. DETALLES VIALES
    # Aceras (Bordes grises claros)
    color_acera = (169, 169, 169)
    ancho_acera = 10
    # Bordes verticales
    pygame.draw.rect(pantalla, color_acera, (290, 0, 10, config.ALTO))
    pygame.draw.rect(pantalla, color_acera, (500, 0, 10, config.ALTO))
    # Bordes horizontales
    pygame.draw.rect(pantalla, color_acera, (0, 240, config.ANCHO, 10))
    pygame.draw.rect(pantalla, color_acera, (0, 350, config.ANCHO, 10))

    # Líneas Amarillas Centrales (División de carril)
    # Vertical
    pygame.draw.line(pantalla, (255, 215, 0), (400, 0), (400, 240), 3) # Arriba
    pygame.draw.line(pantalla, (255, 215, 0), (400, 360), (400, 600), 3) # Abajo
    # Horizontal
    pygame.draw.line(pantalla, (255, 215, 0), (0, 300), (290, 300), 3)   # Izq
    pygame.draw.line(pantalla, (255, 215, 0), (510, 300), (800, 300), 3) # Der

    # Pasos de Cebra (Crosswalks)
    dibujar_paso_cebra(pantalla, 300, 250, "V_ARRIBA")
    dibujar_paso_cebra(pantalla, 300, 350, "V_ABAJO")
    dibujar_paso_cebra(pantalla, 280, 250, "H_IZQ")
    dibujar_paso_cebra(pantalla, 500, 250, "H_DER")

    # 4. SEMÁFOROS (Mejorados)
    for s in semaforos:
        dibujar_semaforo_estilizado(pantalla, s)

    # 5. VEHÍCULOS
    for v in vehiculos:
        dibujar_vehiculo_individual(pantalla, v, imagenes_dict)

    # 6. LEYENDA (Fondo semitransparente para que se lea bien)
    s = pygame.Surface((200, 160))
    s.set_alpha(180)
    s.fill((0,0,0))
    pantalla.blit(s, (5,5))
    dibujar_leyenda(pantalla)

def dibujar_paso_cebra(pantalla, x, y, tipo):
    color_blanco = (230, 230, 230)
    ancho_linea = 6
    separacion = 12
    
    if tipo == "V_ARRIBA" or tipo == "V_ABAJO":
        # Dibujamos líneas horizontales dentro del carril vertical
        # La zona es x=300 a 500. y=240 a 250 (Arriba)
        base_y = 240 if tipo == "V_ARRIBA" else 350
        alto = 10
        # Dibujamos varias franjas
        for i in range(300, 500, 20):
            pygame.draw.rect(pantalla, color_blanco, (i + 5, base_y, 10, alto))

    elif tipo == "H_IZQ" or tipo == "H_DER":
        # Dibujamos líneas verticales dentro del carril horizontal
        base_x = 290 if tipo == "H_IZQ" else 500
        ancho = 10
        for i in range(250, 350, 15):
             pygame.draw.rect(pantalla, color_blanco, (base_x, i + 3, ancho, 8))

def dibujar_semaforo_estilizado(pantalla, s):
    # Determinar color
    if s.estado == "verde":
        color_luz = (0, 255, 0)
    elif s.estado in ["amarillo1", "amarillo2"]:
        color_luz = (255, 255, 0)
    else:
        color_luz = (255, 0, 0)

    # Dibujar CAJA del semáforo (Negra rectangular)
    caja_rect = pygame.Rect(s.x - 10, s.y - 10, 20, 20)
    pygame.draw.rect(pantalla, (20, 20, 20), caja_rect, border_radius=5)
    
    # Borde de la caja
    pygame.draw.rect(pantalla, (100, 100, 100), caja_rect, 1, border_radius=5)

    # Luz Brillante
    pygame.draw.circle(pantalla, color_luz, (s.x, s.y), 7)
    
    # Resplandor (Halo)
    s_luz = pygame.Surface((40, 40), pygame.SRCALPHA)
    pygame.draw.circle(s_luz, (*color_luz, 50), (20, 20), 15)
    pantalla.blit(s_luz, (s.x - 20, s.y - 20))

def dibujar_vehiculo_individual(pantalla, v, imagenes):
    dibujado_con_imagen = False
    if imagenes:
        try:
            img = imagenes[v.tipo][v.direccion]
            rect = img.get_rect(center=(v.x, v.y))
            pantalla.blit(img, rect)
            dibujado_con_imagen = True
        except Exception:
            pass

    if not dibujado_con_imagen:
        # Fallback rectangular
        color = (0, 0, 255) if v.tipo == "normal" else (255, 255, 0)
        w, h = (20, 40) if v.direccion in ["N", "S"] else (40, 20)
        pygame.draw.rect(pantalla, color, (v.x - w/2, v.y - h/2, w, h))

    # ID siempre visible
    font = pygame.font.Font(None, 18)
    text_sombra = font.render(str(v.id)[-4:], True, (0,0,0))
    text_blanco = font.render(str(v.id)[-4:], True, (255,255,255))
    pantalla.blit(text_sombra, (v.x + 1, v.y - 30))
    pantalla.blit(text_blanco, (v.x, v.y - 31))

def dibujar_leyenda(pantalla):
    font = pygame.font.Font(None, 20)
    x, y = 15, 15
    pantalla.blit(font.render("LEYENDA:", True, (200, 200, 200)), (x, y))
    pantalla.blit(font.render("Auto Normal", True, (100, 100, 255)), (x, y + 20))
    pantalla.blit(font.render("Ambulancia (Prioridad)", True, (255, 255, 0)), (x, y + 40))
    pantalla.blit(font.render("----------------", True, (100, 100, 100)), (x, y + 55))
    pantalla.blit(font.render("LUZ VERDE: Avanzar", True, (0, 255, 0)), (x, y + 70))
    pantalla.blit(font.render("LUZ ROJA: Detener", True, (255, 50, 50)), (x, y + 90))