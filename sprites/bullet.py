import pygame
import config

try:
    BaseSprite = pygame.sprite.Sprite
except:
    BaseSprite = object

class Bullet(BaseSprite):
    def __init__(self, x, y, bullet_type="normal"):
        super().__init__()
        self.bullet_type = bullet_type
        self.image = pygame.Surface((6, 12), pygame.SRCALPHA)
        self._draw_bullet()
        self.rect = self.image.get_rect(center=(x, y))
        self.vy = -config.BULLET_SPEED
        self.trail_points = []

    def _draw_bullet(self):
        if self.bullet_type == "normal":
            # Основной корпус
            pygame.draw.rect(self.image, config.BULLET_COLOR, (1, 0, 4, 12), border_radius=2)
            # Острый носик
            pygame.draw.polygon(self.image, (255, 255, 200), [(2, 0), (1, 2), (5, 2)])
            # Внутреннее свечение
            pygame.draw.line(self.image, (255, 255, 150), (3, 3), (3, 10), 1)
        elif self.bullet_type == "dual":
            pygame.draw.rect(self.image, (200, 200, 255), (1, 0, 4, 12), border_radius=2)
            pygame.draw.polygon(self.image, (150, 200, 255), [(2, 0), (1, 2), (5, 2)])

    def update(self):
        self.rect.y += self.vy
        if self.rect.bottom < 0:
            self.kill()
