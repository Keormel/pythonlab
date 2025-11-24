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
        """Создаёт детализированные модели корабля для разных уровней здоровья"""
        models = []
        
        # Модель с 3 HP (целый корабль)
        surf_3 = pygame.Surface((50, 60), pygame.SRCALPHA)
        
        # Основной корпус
        pygame.draw.polygon(surf_3, (100, 150, 255), [(25, 5), (15, 25), (35, 25)])
        pygame.draw.polygon(surf_3, config.PLAYER_COLOR, [(25, 5), (12, 28), (38, 28)])
        pygame.draw.rect(surf_3, config.PLAYER_COLOR, (14, 26, 22, 24), border_radius=5)
        
        # Кабина (окно)
        pygame.draw.circle(surf_3, (150, 200, 255), (25, 12), 4)
        pygame.draw.circle(surf_3, (200, 230, 255), (25, 12), 2)
        
        # Левое крыло
        pygame.draw.polygon(surf_3, (80, 140, 255), [(12, 28), (4, 35), (14, 32)])
        pygame.draw.polygon(surf_3, (100, 160, 255), [(12, 28), (8, 32), (14, 30)])
        
        # Правое крыло
        pygame.draw.polygon(surf_3, (80, 140, 255), [(38, 28), (46, 35), (36, 32)])
        pygame.draw.polygon(surf_3, (100, 160, 255), [(38, 28), (42, 32), (36, 30)])
        
        # Левый стабилизатор
        pygame.draw.polygon(surf_3, (120, 180, 255), [(16, 42), (10, 52), (16, 48)])
        pygame.draw.polygon(surf_3, (150, 200, 255), [(16, 42), (12, 48), (16, 46)])
        
        # Правый стабилизатор
        pygame.draw.polygon(surf_3, (120, 180, 255), [(34, 42), (40, 52), (34, 48)])
        pygame.draw.polygon(surf_3, (150, 200, 255), [(34, 42), (38, 48), (34, 46)])
        
        # Двигатели (основной)
        pygame.draw.rect(surf_3, (200, 100, 50), (22, 48, 6, 10), border_radius=2)
        pygame.draw.rect(surf_3, (255, 150, 80), (22, 48, 6, 4))
        
        # Боковые двигатели
        pygame.draw.rect(surf_3, (180, 80, 40), (12, 50, 4, 8), border_radius=1)
        pygame.draw.rect(surf_3, (180, 80, 40), (34, 50, 4, 8), border_radius=1)
        
        # Полоски на корпусе
        pygame.draw.line(surf_3, (120, 170, 255), (20, 32), (20, 38), 1)
        pygame.draw.line(surf_3, (120, 170, 255), (30, 32), (30, 38), 1)
        
        models.append(surf_3)
        
        # Модель с 2 HP (повреждена левая сторона)
        surf_2 = pygame.Surface((50, 60), pygame.SRCALPHA)
        
        # Основной корпус
        pygame.draw.polygon(surf_2, (100, 150, 255), [(25, 5), (15, 25), (35, 25)])
        pygame.draw.polygon(surf_2, config.PLAYER_COLOR, [(25, 5), (12, 28), (38, 28)])
        pygame.draw.rect(surf_2, config.PLAYER_COLOR, (14, 26, 22, 24), border_radius=5)
        
        # Кабина
        pygame.draw.circle(surf_2, (150, 200, 255), (25, 12), 4)
        pygame.draw.circle(surf_2, (200, 230, 255), (25, 12), 2)
        
        # Только правое крыло (левое повреждено)
        pygame.draw.polygon(surf_2, (80, 140, 255), [(38, 28), (46, 35), (36, 32)])
        pygame.draw.polygon(surf_2, (100, 160, 255), [(38, 28), (42, 32), (36, 30)])
        pygame.draw.polygon(surf_2, (255, 100, 100), [(12, 28), (8, 35), (14, 32)])  # Обломок левого крыла
        
        # Только правый стабилизатор
        pygame.draw.polygon(surf_2, (120, 180, 255), [(34, 42), (40, 52), (34, 48)])
        pygame.draw.polygon(surf_2, (150, 200, 255), [(34, 42), (38, 48), (34, 46)])
        pygame.draw.polygon(surf_2, (255, 100, 100), [(16, 42), (10, 52), (16, 48)])  # Обломок левого стабилизатора
        
        # Двигатели
        pygame.draw.rect(surf_2, (200, 100, 50), (22, 48, 6, 10), border_radius=2)
        pygame.draw.rect(surf_2, (255, 150, 80), (22, 48, 6, 4))
        pygame.draw.rect(surf_2, (180, 80, 40), (34, 50, 4, 8), border_radius=1)
        
        # Повреждённые полоски
        pygame.draw.line(surf_2, (200, 100, 100), (20, 32), (20, 38), 1)
        pygame.draw.line(surf_2, (120, 170, 255), (30, 32), (30, 38), 1)
        pygame.draw.rect(surf_2, (255, 100, 100), (10, 28, 3, 12))  # Трещина
        
        models.append(surf_2)
        
        # Модель с 1 HP (серьёзно повреждена)
        surf_1 = pygame.Surface((50, 60), pygame.SRCALPHA)
        
        # Повреждённый корпус
        pygame.draw.polygon(surf_1, (150, 100, 100), [(25, 5), (15, 25), (35, 25)])
        pygame.draw.polygon(surf_1, (200, 100, 100), [(25, 5), (12, 28), (38, 28)])
        pygame.draw.rect(surf_1, (180, 80, 80), (14, 26, 22, 24), border_radius=5)
        
        # Повреждённая кабина
        pygame.draw.circle(surf_1, (150, 100, 100), (25, 12), 4)
        pygame.draw.circle(surf_1, (200, 120, 120), (25, 12), 2)
        
        # Обломки крыльев
        pygame.draw.polygon(surf_1, (255, 100, 100), [(12, 28), (8, 35), (14, 32)])
        pygame.draw.polygon(surf_1, (255, 100, 100), [(38, 28), (46, 35), (36, 32)])
        
        # Обломки стабилизаторов
        pygame.draw.polygon(surf_1, (255, 100, 100), [(16, 42), (10, 52), (16, 48)])
        pygame.draw.polygon(surf_1, (255, 100, 100), [(34, 42), (40, 52), (34, 48)])
        
        # Слабый двигатель
        pygame.draw.rect(surf_1, (150, 50, 50), (22, 48, 6, 10), border_radius=2)
        pygame.draw.rect(surf_1, (200, 80, 80), (22, 48, 6, 4))
        
        # Большие трещины
        pygame.draw.line(surf_1, (255, 100, 100), (15, 30), (35, 35), 2)
        pygame.draw.line(surf_1, (255, 80, 80), (20, 28), (30, 42), 1)
        pygame.draw.rect(surf_1, (255, 100, 100), (10, 28, 30, 2))
        
        models.append(surf_1)
        
        return models

    def update(self, keys, now):
        """Обновляет состояние игрока"""
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
            self.image = pygame.Surface((50, 60), pygame.SRCALPHA)
            pygame.draw.polygon(self.image, (255, 255, 255), [(25, 5), (15, 25), (35, 25)])
        elif self.damage_flash > 0:
            # Вспышка при получении урона - показываем повреждённый корабль
            self.image = pygame.Surface((50, 60), pygame.SRCALPHA)
            
            # Повреждённый корпус (серый цвет)
            pygame.draw.polygon(self.image, (120, 120, 140), [(25, 5), (15, 25), (35, 25)])
            pygame.draw.polygon(self.image, (100, 100, 120), [(25, 5), (12, 28), (38, 28)])
            pygame.draw.rect(self.image, (100, 100, 120), (14, 26, 22, 24), border_radius=5)
            
            # Повреждённая кабина
            pygame.draw.circle(self.image, (80, 80, 100), (25, 12), 4)
            pygame.draw.circle(self.image, (120, 120, 140), (25, 12), 2)
            
            # Сломанные крылья (показываем только части)
            if self.damage_flash % 3 != 0:  # Мигание сломанных частей
                pygame.draw.polygon(self.image, (150, 80, 80), [(12, 28), (8, 32), (14, 30)])
                pygame.draw.polygon(self.image, (150, 80, 80), [(38, 28), (42, 32), (36, 30)])
            
            # Сломанные стабилизаторы
            if self.damage_flash % 4 != 0:
                pygame.draw.polygon(self.image, (150, 80, 80), [(16, 42), (12, 48), (16, 46)])
                pygame.draw.polygon(self.image, (150, 80, 80), [(34, 42), (38, 48), (34, 46)])
            
            # Повреждённый двигатель
            pygame.draw.rect(self.image, (140, 80, 80), (22, 48, 6, 10), border_radius=2)
            pygame.draw.rect(self.image, (180, 100, 100), (22, 48, 6, 2))
            
            # Трещины и искры
            pygame.draw.line(self.image, (200, 100, 100), (15, 30), (35, 35), 1)
            pygame.draw.line(self.image, (200, 120, 120), (20, 28), (30, 42), 1)
        else:
            self.image = base_img.copy()
            
            # Щит с анимацией
            if now < self.shield_until:
                radius = 30 + int(3 * math.sin(self.animation_time * 0.1))
                pygame.draw.circle(self.image, config.POWERUP_COLOR, (25, 30), radius, 2)
                pygame.draw.circle(self.image, config.POWERUP_COLOR, (25, 30), radius - 2, 1)
            
            # Эффект ускорения
            if now < self.speed_boost_until:
                offset = int(3 * math.sin(self.animation_time * 0.15))
                pygame.draw.polygon(self.image, (255, 150, 50), [(18, 48 + offset), (16, 56), (20, 50)])
                pygame.draw.polygon(self.image, (255, 150, 50), [(32, 48 + offset), (34, 56), (30, 50)])

    def shoot(self, now):
        """Стреляет с учётом задержки"""
        if now - self.last_shot >= self.shoot_delay:
            self.last_shot = now
            
            # Одиночная пуля
            bullet = Bullet(self.rect.centerx, self.rect.top, -math.pi / 2)
            bullet.speed *= 1.5  # Увеличиваем скорость пули
            return [bullet]
        
    def damage(self, now, amount=1):
        """Получает урон"""
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
        """Применяет бонус"""
        if ptype == "shield":
            self.shield_until = now + 8000
        elif ptype == "rapidfire":
            self.rapidfire_until = now + 6000
        elif ptype == "speed":
            self.speed_boost_until = now + 5000
            self.boost_speed = int(self.speed * 1.5)
        elif ptype == "dual_shot":
            self.dual_shot_until = now + 7000