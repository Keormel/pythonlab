import pygame
import random
import math
import config

try:
    BaseSprite = pygame.sprite.Sprite
except:
    BaseSprite = object

def clamp(val, lo, hi):
    return max(lo, min(hi, val))

class Enemy(BaseSprite):
    def __init__(self, difficulty=1.0):
        super().__init__()
        w, h = 45, 32
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        self._draw_enemy_model(self.image, w, h)
        self.rect = self.image.get_rect()
        self.rect.centerx = random.randint(30, config.SCREEN_W - 30)
        self.rect.y = -h - 10
        self.vy = random.uniform(config.ENEMY_SPEED_MIN, config.ENEMY_SPEED_MAX) * difficulty
        self.vx = random.uniform(-1.5, 1.5) * difficulty
        self.amp = random.uniform(0.2, 0.5) * difficulty
        self.freq = random.uniform(0.005, 0.015)
        self.phase = random.uniform(0, config.TAU)
        self.t = 0
        self.hp = max(1, int(difficulty * 1.2))
        self.max_hp = self.hp
        self.wall_bounce_cooldown = 0
        self.target_vx = self.vx
        self.direction = random.choice([-1, 1])
        self.animation_pulse = 0

    def _draw_enemy_model(self, surf, w, h):
        # Основной корпус с градиентом
        pygame.draw.rect(surf, config.ENEMY_COLOR, (5, 10, w - 10, h - 16), border_radius=7)
        pygame.draw.rect(surf, (255, 100, 100), (7, 8, w - 14, 8), border_radius=4)
        
        # Левое крыло
        pygame.draw.polygon(surf, (200, 50, 50), [(3, 15), (1, 12), (3, 20), (8, 18)])
        # Правое крыло
        pygame.draw.polygon(surf, (200, 50, 50), [(w - 3, 15), (w - 1, 12), (w - 3, 20), (w - 8, 18)])
        
        # Передние окна (кабина)
        pygame.draw.circle(surf, (100, 180, 255), (w // 3, 10), 2)
        pygame.draw.circle(surf, (100, 180, 255), (2 * w // 3, 10), 2)
        
        # Центральный окно
        pygame.draw.rect(surf, (120, 200, 255), (w // 2 - 2, 12, 4, 4), border_radius=1)
        
        # Боковые панели
        pygame.draw.line(surf, (150, 150, 200), (2, 15), (2, 28), 1)
        pygame.draw.line(surf, (150, 150, 200), (w - 2, 15), (w - 2, 28), 1)
        
        # Выхлопные трубы
        pygame.draw.rect(surf, (100, 100, 120), (8, h - 3, 4, 3))
        pygame.draw.rect(surf, (100, 100, 120), (w - 12, h - 3, 4, 3))

    def update(self):
        self.t += 1
        self.animation_pulse += 1
        self.rect.y += self.vy
        
        # Улучшенное волнообразное движение
        wave_offset = int(self.amp * 50 * math.sin(self.phase + self.t * self.freq))
        
        # Плавное изменение горизонтальной скорости
        if self.wall_bounce_cooldown > 0:
            self.wall_bounce_cooldown -= 1
        else:
            # Интеллектуальное движение - случайная смена направления
            if random.random() < 0.01:
                self.direction *= -1
            self.target_vx = 2 * self.direction
        
        self.vx = self.vx * 0.9 + self.target_vx * 0.1
        self.rect.x += int(self.vx)
        
        # Отскок от стен с визуальным эффектом
        if self.rect.left < 5:
            self.rect.left = 5
            self.direction = 1
            self.wall_bounce_cooldown = 15
        elif self.rect.right > config.SCREEN_W - 5:
            self.rect.right = config.SCREEN_W - 5
            self.direction = -1
            self.wall_bounce_cooldown = 15
        
        if self.rect.top > config.SCREEN_H + 50:
            self.kill()

    def damage(self, amount=1):
        self.hp -= amount
        if self.hp <= 0:
            self.kill()
            return True
        return False

    def draw_health_bar(self, surf, x, y):
        # Полоска здоровья врага
        if self.hp < self.max_hp:
            bar_width = 40
            bar_height = 3
            fill = (self.hp / self.max_hp) * bar_width
            pygame.draw.rect(surf, (100, 100, 100), (x - bar_width // 2, y - 10, bar_width, bar_height))
            pygame.draw.rect(surf, (255, 100, 100), (x - bar_width // 2, y - 10, int(fill), bar_height))
