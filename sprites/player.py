import pygame
import math
import config
from .bullet import Bullet

try:
    BaseSprite = pygame.sprite.Sprite
except:
    BaseSprite = object

def clamp(val, lo, hi):
    return max(lo, min(hi, val))

class Player(BaseSprite):
    def __init__(self, x, y):
        super().__init__()
        self.base_images = self._create_player_models()
        self.current_hp_visual = config.PLAYER_HP
        self.image = self.base_images[config.PLAYER_HP - 1]
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = config.PLAYER_SPEED
        self.shoot_delay = config.PLAYER_SHOOT_DELAY
        self.last_shot = 0
        self.hp = config.PLAYER_HP
        self.max_hp = config.PLAYER_HP
        self.inv_until = 0
        
        # Бонусы
        self.has_shield = False
        self.shield_until = 0
        self.rapidfire_until = 0
        self.dual_shot_until = 0
        self.speed_boost_until = 0
        self.boost_speed = config.PLAYER_SPEED
        self.animation_time = 0
        self.damage_flash = 0

    def _create_player_models(self):
        """Создаёт модели корабля для разных уровней здоровья"""
        models = []
        
        # Модель с 3 HP (целый корабль)
        surf_3 = pygame.Surface((40, 50), pygame.SRCALPHA)
        pygame.draw.polygon(surf_3, config.PLAYER_COLOR, [(20, 0), (15, 20), (25, 20)])
        pygame.draw.rect(surf_3, config.PLAYER_COLOR, (12, 18, 16, 22), border_radius=4)
        pygame.draw.polygon(surf_3, (100, 180, 255), [(10, 22), (5, 28), (12, 25)])
        pygame.draw.polygon(surf_3, (100, 180, 255), [(30, 22), (35, 28), (28, 25)])
        pygame.draw.polygon(surf_3, (120, 200, 255), [(16, 38), (14, 50), (18, 45)])
        pygame.draw.polygon(surf_3, (120, 200, 255), [(24, 38), (26, 50), (22, 45)])
        pygame.draw.circle(surf_3, (150, 200, 255), (20, 10), 2)
        pygame.draw.rect(surf_3, (200, 100, 50), (18, 40, 4, 8))
        models.append(surf_3)
        
        # Модель с 2 HP (повреждена одна сторона)
        surf_2 = pygame.Surface((40, 50), pygame.SRCALPHA)
        pygame.draw.polygon(surf_2, config.PLAYER_COLOR, [(20, 0), (15, 20), (25, 20)])
        pygame.draw.rect(surf_2, config.PLAYER_COLOR, (12, 18, 16, 22), border_radius=4)
        pygame.draw.polygon(surf_2, (100, 180, 255), [(30, 22), (35, 28), (28, 25)])  # Только правое крыло
        pygame.draw.polygon(surf_2, (120, 200, 255), [(24, 38), (26, 50), (22, 45)])  # Только правый стабилизатор
        pygame.draw.circle(surf_2, (150, 200, 255), (20, 10), 2)
        pygame.draw.rect(surf_2, (200, 100, 50), (18, 40, 4, 8))
        pygame.draw.rect(surf_2, (255, 100, 100), (8, 22, 4, 8))  # Обломок
        models.append(surf_2)
        
        # Модель с 1 HP (серьёзно повреждена)
        surf_1 = pygame.Surface((40, 50), pygame.SRCALPHA)
        pygame.draw.polygon(surf_1, config.PLAYER_COLOR, [(20, 0), (15, 20), (25, 20)])
        pygame.draw.rect(surf_1, (200, 100, 100), (12, 18, 16, 22), border_radius=4)  # Повреждённый цвет
        pygame.draw.circle(surf_1, (150, 100, 100), (20, 10), 2)  # Потемневшее окно
        pygame.draw.rect(surf_1, (150, 50, 50), (18, 40, 4, 8))  # Тусклый выхлоп
        pygame.draw.rect(surf_1, (255, 150, 150), (5, 25, 30, 4))  # Трещины
        pygame.draw.rect(surf_1, (255, 100, 100), (8, 22, 4, 8))
        pygame.draw.rect(surf_1, (255, 100, 100), (28, 22, 4, 8))
        models.append(surf_1)
        
        return models

    def update(self, keys, now):
        self.animation_time += 1
        self.damage_flash -= 1
        
        # Гладкое переключение между моделями
        if self.current_hp_visual != self.hp:
            self.current_hp_visual = self.hp
        
        dx = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a])
        dy = (keys[pygame.K_DOWN] or keys[pygame.K_s]) - (keys[pygame.K_UP] or keys[pygame.K_w])
        
        # Применяем ускорение
        current_speed = self.boost_speed if now < self.speed_boost_until else self.speed
        self.rect.x += int(dx) * current_speed
        self.rect.y += int(dy) * current_speed
        self.rect.left = clamp(self.rect.left, 0, config.SCREEN_W - self.rect.width)
        self.rect.top = clamp(self.rect.top, 0, config.SCREEN_H - self.rect.height)

        # Выбираем модель в зависимости от здоровья
        hp_index = max(0, min(self.hp - 1, 2))
        base_img = self.base_images[hp_index]
        
        # Визуальный эффект неуязвимости
        if now < self.inv_until and (now // 100) % 2 == 0:
            self.image = pygame.Surface((40, 50), pygame.SRCALPHA)
            pygame.draw.polygon(self.image, (255, 255, 255), [(20, 0), (15, 20), (25, 20)])
        elif self.damage_flash > 0:
            # Вспышка при получении урона
            self.image = pygame.Surface((40, 50), pygame.SRCALPHA)
            self.image.fill((255, 100, 100, 180))
        else:
            self.image = base_img.copy()
            
            # Щит с анимацией
            if now < self.shield_until:
                radius = 30 + int(3 * math.sin(self.animation_time * 0.1))
                pygame.draw.circle(self.image, config.POWERUP_COLOR, (20, 25), radius, 2)
                pygame.draw.circle(self.image, config.POWERUP_COLOR, (20, 25), radius - 2, 1)
            
            # Эффект ускорения
            if now < self.speed_boost_until:
                offset = int(3 * math.sin(self.animation_time * 0.15))
                pygame.draw.polygon(self.image, (255, 150, 50), [(16, 40 + offset), (14, 48), (18, 42)])
                pygame.draw.polygon(self.image, (255, 150, 50), [(24, 40 + offset), (26, 48), (22, 42)])

    def try_shoot(self, now, bullets_group, all_group):
        shoot_delay = self.shoot_delay
        if now < self.rapidfire_until:
            shoot_delay = int(self.shoot_delay * 0.4)
        elif now < self.speed_boost_until:
            shoot_delay = int(self.shoot_delay * 0.7)
            
        if now - self.last_shot >= shoot_delay:
            self.last_shot = now
            
            # Одиночный выстрел
            if now >= self.dual_shot_until:
                bullet = Bullet(self.rect.midtop[0], self.rect.top)
                bullets_group.add(bullet)
                all_group.add(bullet)
            else:
                # Двойной выстрел
                bullet1 = Bullet(self.rect.left + 8, self.rect.top + 10)
                bullet2 = Bullet(self.rect.right - 8, self.rect.top + 10)
                bullets_group.add(bullet1)
                bullets_group.add(bullet2)
                all_group.add(bullet1)
                all_group.add(bullet2)

    def damage(self, now, amount=1):
        if now >= self.inv_until:
            if now < self.shield_until:
                self.shield_until = 0
            else:
                self.hp -= amount
                self.damage_flash = 15
            self.inv_until = now + 1200

    def heal(self, amount=1):
        """Лечит корабль при подборе аптечки"""
        old_hp = self.hp
        self.hp = min(self.hp + amount, self.max_hp)
        return self.hp > old_hp

    def apply_powerup(self, ptype, now):
        if ptype == "shield":
            self.shield_until = now + 8000
        elif ptype == "rapidfire":
            self.rapidfire_until = now + 6000
        elif ptype == "speed":
            self.speed_boost_until = now + 5000
            self.boost_speed = int(self.speed * 1.5)
        elif ptype == "dual_shot":
            self.dual_shot_until = now + 7000
