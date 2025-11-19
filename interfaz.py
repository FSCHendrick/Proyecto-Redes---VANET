import pygame
import config

def dibujar_cruce(pantalla, vehiculos, semaforos, imagenes_dict=None):
    pantalla.fill((30, 30, 30))  # Fondo gris oscuro

    # Dibujar calles (Gris más claro)
    pygame.draw.rect(pantalla, (50, 50, 50), (300, 0, 200, config.ALTO))  # Vertical
    pygame.draw.rect(pantalla, (50, 50, 50), (0, 250, config.ANCHO, 100)) # Horizontal
    
    # Líneas amarillas del centro (Decoración opcional)
    pygame.draw.line(pantalla, (200, 200, 0), (400, 0), (400, 250), 2) # V-Arriba
    pygame.draw.line(pantalla, (200, 200, 0), (400, 350), (400, 600), 2) # V-Abajo
    pygame.draw.line(pantalla, (200, 200, 0), (0, 300), (300, 300), 2)   # H-Izq
    pygame.draw.line(pantalla, (200, 200, 0), (500, 300), (800, 300), 2) # H-Der

    # Dibujar semáforos
    for s in semaforos:
        if s.estado == "verde":
            color = (0, 255, 0)
            # Efecto de brillo
            pygame.draw.circle(pantalla, (0, 100, 0), (s.x, s.y), 18, 1) 
        elif s.estado in ["amarillo1", "amarillo2"]:
            color = (255, 255, 0)
        else:
            color = (255, 0, 0)
        
        # Base del semáforo (negro)
        pygame.draw.circle(pantalla, (0, 0, 0), (s.x, s.y), 16)
        # Luz
        pygame.draw.circle(pantalla, color, (s.x, s.y), 14)

    # Dibujar vehículos
    for v in vehiculos:
        dibujado = False
        
        # 1. INTENTAR DIBUJAR IMAGEN
        if imagenes_dict:
            try:
                # Buscamos la imagen específica: Diccionario[TIPO][DIRECCION]
                # Ej: imagenes_dict['normal']['N']
                img = imagenes_dict.get(v.tipo, {}).get(v.direccion)
                
                if img:
                    # Centramos la imagen en la posición x,y del auto
                    rect = img.get_rect(center=(v.x, v.y))
                    pantalla.blit(img, rect)
                    dibujado = True
            except Exception:
                pass # Si falla, usamos el rectángulo de respaldo

        # 2. FALLBACK: DIBUJAR RECTÁNGULO (Si no hay imagen)
        if not dibujado:
            color = (0, 0, 255) if v.tipo == "normal" else (255, 255, 0)
            
            # Ajustamos la forma del rectángulo según la dirección
            if v.direccion in ["N", "S"]:
                w, h = 20, 40 # Vertical
            else:
                w, h = 40, 20 # Horizontal
                
            # Centrar el rectángulo
            pygame.draw.rect(pantalla, color, (v.x - w/2, v.y - h/2, w, h))

        # 3. DIBUJAR ID (Siempre encima)
        font = pygame.font.Font(None, 20)
        # Sombra del texto (para que se lea sobre cualquier color)
        text_sombra = font.render(str(v.id), True, (0, 0, 0))
        text_blanco = font.render(str(v.id), True, (255, 255, 255))
        
        pantalla.blit(text_sombra, (v.x + 1, v.y - 24))
        pantalla.blit(text_blanco, (v.x, v.y - 25))

    # Leyenda
    dibujar_leyenda(pantalla)

def dibujar_leyenda(pantalla):
    font = pygame.font.Font(None, 22)
    pantalla.blit(font.render("Leyenda:", True, (255, 255, 255)), (10, 10))
    pantalla.blit(font.render("Azul/Auto = Normal", True, (100, 100, 255)), (10, 35))
    pantalla.blit(font.render("Amarillo/Ambula = Emergencia", True, (255, 255, 0)), (10, 60))
    pantalla.blit(font.render("SEMÁFOROS:", True, (255, 255, 255)), (10, 90))
    pantalla.blit(font.render("Verde = Avanza", True, (0, 255, 0)), (10, 115))
    pantalla.blit(font.render("Rojo = Detenerse", True, (255, 0, 0)), (10, 140))