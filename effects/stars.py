import pygame
import random
import config

def create_stars(count):
    stars = []
    for _ in range(count):
        size = random.choice([1, 1, 1, 2, 2, 3])
        speed = random.uniform(0.5, 2.0) * (1 + size * 0.2)
        x = random.randint(0, config.SCREEN_W - 1)
        y = random.randint(0, config.SCREEN_H - 1)
        shade = 120 + int(120 * (speed / 3.0))
        color = (shade, shade, 255)
        stars.append({"x": x, "y": y, "size": size, "speed": speed, "color": color})
    return stars

def draw_stars(screen, stars):
    for s in stars:
        s["y"] += s["speed"]
        if s["y"] > config.SCREEN_H:
            s["y"] = -s["size"]
            s["x"] = random.randint(0, config.SCREEN_W - 1)
            s["speed"] = random.uniform(0.5, 2.0) * (1 + s["size"] * 0.2)
        screen.fill(s["color"], (int(s["x"]), int(s["y"]), s["size"], s["size"]))
