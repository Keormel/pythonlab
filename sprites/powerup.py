import pygame
import random
import math
import config

try:
    BaseSprite = pygame.sprite.Sprite
except:
    BaseSprite = object

class PowerUp(BaseSprite):
    POWERUP_MODELS = {
        "shield": (config.POWERUP_COLOR, "shield"),
        "rapidfire": ((255, 200, 50), "fire"),
        "speed": ((100, 255, 200), "speed"),
        "dual_shot": ((200, 100, 255), "dual"),
        "health": ((100, 255, 100), "health")
    }

    def __init__(self, x, y, ptype):
        super().__init__()
        self.ptype = ptype
        self.image = pygame.Surface((48, 48), pygame.SRCALPHA)
        color, model_type = self.POWERUP_MODELS.get(ptype, (config.POWERUP_COLOR, "shield"))
        self._draw_powerup_model(self.image, color, model_type)
        self.rect = self.image.get_rect(center=(x, y))
        self.vy = 1.5
        self.life = 300
        self.rotation = 0
        self.bob_offset = 0
        self.base_y = y

    def _draw_powerup_model(self, surf, color, model_type):
        center = 24
        
        if model_type == "shield":
            # Щит - большой круг с радиусом
            pygame.draw.circle(surf, color, (center, center), 20, 3)
            pygame.draw.circle(surf, color, (center, center), 16, 2)
            pygame.draw.circle(surf, color, (center, center), 10)
            pygame.draw.polygon(surf, color, [(center, 10), (center - 8, center), (center, 30), (center + 8, center)])
            
        elif model_type == "fire":
            # Скорострельность - языки пламени
            pygame.draw.polygon(surf, (255, 100, 0), [(center, 8), (center - 6, 20), (center + 6, 18)])
            pygame.draw.polygon(surf, (255, 200, 0), [(center, 12), (center - 4, 20), (center + 4, 18)])
            pygame.draw.rect(surf, color, (center - 8, 22, 16, 14), border_radius=5)
            pygame.draw.circle(surf, (255, 150, 0), (center - 4, 32), 3)
            pygame.draw.circle(surf, (255, 150, 0), (center + 4, 32), 3)
            
        elif model_type == "speed":
            # Скорость - стрелка/ветер
            pygame.draw.polygon(surf, color, [(center - 12, center), (center + 12, center - 6), (center + 8, center), (center + 12, center + 6)])
            pygame.draw.polygon(surf, color, [(center - 8, center), (center + 6, center - 4), (center + 4, center), (center + 6, center + 4)])
            pygame.draw.line(surf, color, (center - 14, center), (center + 14, center), 2)
            
        elif model_type == "dual":
            # Двойной выстрел - две пули
            pygame.draw.circle(surf, color, (center - 8, center - 4), 5)
            pygame.draw.circle(surf, color, (center + 8, center - 4), 5)
            pygame.draw.line(surf, color, (center - 8, center - 4), (center + 8, center - 4), 3)
            pygame.draw.rect(surf, color, (center - 10, center + 6, 20, 10), border_radius=3)
            pygame.draw.circle(surf, (200, 200, 255), (center - 4, center + 14), 2)
            pygame.draw.circle(surf, (200, 200, 255), (center + 4, center + 14), 2)
        
        elif model_type == "health":
            # Аптечка - красный крест
            pygame.draw.rect(surf, color, (center - 12, center - 3, 24, 6))  # Горизонтальная линия
            pygame.draw.rect(surf, color, (center - 3, center - 12, 6, 24))  # Вертикальная линия
            pygame.draw.circle(surf, color, (center, center), 18, 2)  # Обод

    def update(self):
        self.rect.y += self.vy
        self.life -= 1
        self.rotation = (self.rotation + 5) % 360
        
        # Волнообразное движение вверх-вниз
        self.bob_offset = int(3 * math.sin(self.life * 0.1))
        self.rect.y += self.bob_offset
        
        if self.life <= 0 or self.rect.top > config.SCREEN_H + 50:
            self.kill()
        
        # Пульсирующий эффект при скором исчезновении
        if self.life < 60:
            if (self.life // 10) % 2 == 0:
                self.image.set_alpha(180)
            else:
                self.image.set_alpha(255)
        else:
            self.image.set_alpha(255)
