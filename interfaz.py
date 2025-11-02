import pygame

ANCHO, ALTO = 800, 600

def dibujar_cruce(pantalla, vehiculos, semaforos):
    pantalla.fill((30, 30, 30))  # Fondo gris oscuro

    # Dibujar calles
    pygame.draw.rect(pantalla, (50, 50, 50), (300, 0, 200, 600))  # vertical
    pygame.draw.rect(pantalla, (50, 50, 50), (0, 250, 800, 100))  # horizontal

    # Dibujar semáforos
    for s in semaforos:
        if s.estado == "verde":
            color = (0, 255, 0)
        elif s.estado in ["amarillo1", "amarillo2"]:
            color = (255, 255, 0)
        else:
            color = (255, 0, 0)
        pygame.draw.circle(pantalla, color, (s.x, s.y), 15)

    # Dibujar vehículos
    for v in vehiculos:
        # Color: azul normal, amarillo emergencia
        color = (0, 0, 255) if v.tipo == "normal" else (255, 255, 0)

        # Si la velocidad es baja (amarillo1), hacerlo más tenue
        if v.velocidad < v.velocidad_normal:
            color = tuple(min(255, int(c * 0.5)) for c in color)  # más oscuro
        # Dibujar el rectángulo del vehículo
        pygame.draw.rect(pantalla, color, (v.x, v.y, 20, 10))

        # mostrar el ID del vehículo sobre él
        font = pygame.font.Font(None, 18)
        text = font.render(str(v.id), True, (255, 255, 255))
        pantalla.blit(text, (v.x, v.y - 12))  # ID encima del vehículo

    # mostrar leyenda de colores en la esquina
    font = pygame.font.Font(None, 22)
    pantalla.blit(font.render("Leyenda:", True, (255, 255, 255)), (10, 10))
    pantalla.blit(font.render("Azul = Auto normal", True, (0, 0, 255)), (10, 35))
    pantalla.blit(font.render("Amarillo = Emergencia", True, (255, 255, 0)), (10, 60))
    pantalla.blit(font.render("Verde = Avanza", True, (0, 255, 0)), (10, 85))
    pantalla.blit(font.render("Rojo = Detenerse", True, (255, 0, 0)), (10, 110))
    pantalla.blit(font.render("Amarillo = Precaución", True, (255, 255, 0)), (10, 135))


