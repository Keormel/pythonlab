import pygame
import random
import math
import config

def add_explosion(explosions, x, y, color_base, intensity=1.0):
    count = int(random.randint(8, 14) * intensity)
    for _ in range(count):
        ang = random.uniform(0, config.TAU)
        spd = random.uniform(1.5, 4.0)
        dx, dy = math.cos(ang) * spd, math.sin(ang) * spd
        life = random.randint(18, 28)
        color = (
            min(255, color_base[0] + random.randint(-20, 20)),
            min(255, color_base[1] + random.randint(-20, 20)),
            min(255, color_base[2] + random.randint(-20, 20)),
        )
        explosions.append({"x": x, "y": y, "dx": dx, "dy": dy, "life": life, "color": color})

def update_draw_explosions(screen, explosions):
    for p in explosions[:]:
        p["x"] += p["dx"]
        p["y"] += p["dy"]
        p["dy"] *= 0.98
        p["dx"] *= 0.98
        p["life"] -= 1
        alpha = max(30, int(255 * (p["life"] / 28)))
        col = (min(255, p["color"][0]), min(255, p["color"][1]), min(255, p["color"][2]))
        surf = pygame.Surface((4, 4), pygame.SRCALPHA)
        pygame.draw.rect(surf, (*col, alpha), (0, 0, 4, 4))
        screen.blit(surf, (int(p["x"]), int(p["y"])))
        if p["life"] <= 0:
            explosions.remove(p)
