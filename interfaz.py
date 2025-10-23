import pygame

ANCHO, ALTO = 800, 600

def dibujar_cruce(pantalla, vehiculos, semaforos):
    pantalla.fill((30, 30, 30))  # Fondo gris oscuro

    # Dibujar calles
    pygame.draw.rect(pantalla, (50, 50, 50), (300, 0, 200, 600))  # vertical
    pygame.draw.rect(pantalla, (50, 50, 50), (0, 250, 800, 100))  # horizontal

    # Dibujar semáforos
    for s in semaforos:
        color = (0,255,0) if s.estado == "verde" else (255,0,0)
        pygame.draw.circle(pantalla, color, (s.x, s.y), 15)

    # Dibujar vehículos
    for v in vehiculos:
        color = (0, 0, 255) if v.tipo == "normal" else (255, 255, 0)
        pygame.draw.rect(pantalla, color, (v.x, v.y, 20, 10))
