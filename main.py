import random
import math
import sys

# Safe pygame import and flags
try:
    import pygame
    PYGAME_OK = True
    _PYGAME_IMPORT_ERR = None
except Exception as e:
    pygame = None
    PYGAME_OK = False
    _PYGAME_IMPORT_ERR = e

# Добавляем безопасную базу для спрайтов
BaseSprite = pygame.sprite.Sprite if PYGAME_OK else object

# --- Константы ---
SCREEN_W, SCREEN_H = 480, 720
FPS = 60
BG_COLOR = (10, 12, 20)
PLAYER_COLOR = (80, 200, 255)
ENEMY_COLOR = (240, 70, 70)
BULLET_COLOR = (255, 245, 120)
UI_COLOR = (220, 220, 230)
TAU = 2 * math.pi

# Безопасная инициализация пользовательского события
if PYGAME_OK:
    SPAWN_EVENT = pygame.USEREVENT + 1
else:
    SPAWN_EVENT = 0
SPAWN_MS = 700

# --- Вспомогательные функции ---
def make_triangle_surface(w, h, color):
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    points = [(w // 2, 0), (0, h - 1), (w - 1, h - 1)]
    pygame.draw.polygon(surf, color, points)
    return surf

def clamp(val, lo, hi):
    return max(lo, min(hi, val))

def create_stars(count):
    stars = []
    for _ in range(count):
        size = random.choice([1, 1, 1, 2, 2, 3])
        speed = random.uniform(0.5, 2.0) * (1 + size * 0.2)
        x = random.randint(0, SCREEN_W - 1)
        y = random.randint(0, SCREEN_H - 1)
        shade = 120 + int(120 * (speed / 3.0))
        color = (shade, shade, 255)
        stars.append({"x": x, "y": y, "size": size, "speed": speed, "color": color})
    return stars

def reset_game_state():
    return {
        "score": 0,
        "game_over": False,
        "explosions": [],  # частицы взрывов: dict(x,y,dx,dy,life,color)
        "stars": create_stars(140),
    }

# --- Спрайты ---
class Player(BaseSprite):
    def __init__(self, x, y):
        super().__init__()
        self.base_image = make_triangle_surface(40, 30, PLAYER_COLOR)
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 5
        self.shoot_delay = 220
        self.last_shot = 0
        self.hp = 3
        self.inv_until = 0

    def update(self, keys, now):
        dx = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (keys[pygame.K_LEFT] or keys[pygame.K_a])
        dy = (keys[pygame.K_DOWN] or keys[pygame.K_s]) - (keys[pygame.K_UP] or keys[pygame.K_w])
        self.rect.x += int(dx) * self.speed
        self.rect.y += int(dy) * self.speed
        self.rect.left = clamp(self.rect.left, 0, SCREEN_W - self.rect.width)
        self.rect.top = clamp(self.rect.top, 0, SCREEN_H - self.rect.height)

        # Визуальный эффект неуязвимости
        if now < self.inv_until and (now // 100) % 2 == 0:
            self.image.fill((0, 0, 0, 0))
            pygame.draw.polygon(self.image, (255, 255, 255), [(20, 0), (0, 29), (39, 29)])
        else:
            self.image = self.base_image.copy()

    def try_shoot(self, now, bullets_group, all_group):
        if now - self.last_shot >= self.shoot_delay:
            self.last_shot = now
            bullet = Bullet(self.rect.midtop[0], self.rect.top)
            bullets_group.add(bullet)
            all_group.add(bullet)

    def damage(self, now, amount=1):
        if now >= self.inv_until:
            self.hp -= amount
            self.inv_until = now + 1200  # мс неуязвимости

class Bullet(BaseSprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((4, 10), pygame.SRCALPHA)
        pygame.draw.rect(self.image, BULLET_COLOR, (0, 0, 4, 10))
        self.rect = self.image.get_rect(center=(x, y))
        self.vy = -12

    def update(self):
        self.rect.y += self.vy
        if self.rect.bottom < 0:
            self.kill()

class Enemy(BaseSprite):
    def __init__(self):
        super().__init__()
        w, h = 34, 26
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(self.image, ENEMY_COLOR, (0, 6, w, h - 6), border_radius=6)
        pygame.draw.rect(self.image, (255, 150, 150), (4, 4, w - 8, 6), border_radius=3)
        self.rect = self.image.get_rect()
        self.rect.centerx = random.randint(20, SCREEN_W - 20)
        self.rect.y = -h - 10
        self.vy = random.uniform(2.0, 4.5)
        self.amp = random.uniform(0, 50)
        self.freq = random.uniform(0.005, 0.02)
        self.phase = random.uniform(0, TAU)
        self.t = 0

    def update(self):
        self.t += 1
        self.rect.y += self.vy
        self.rect.x += int(self.amp * math.sin(self.phase + self.t * self.freq))
        if self.rect.left < -40 or self.rect.right > SCREEN_W + 40:
            self.rect.x = clamp(self.rect.x, -30, SCREEN_W - self.rect.width + 30)
        if self.rect.top > SCREEN_H + 40:
            self.kill()

# --- Рендер вспомогательных элементов ---
def draw_stars(screen, stars):
    for s in stars:
        s["y"] += s["speed"]
        if s["y"] > SCREEN_H:
            s["y"] = -s["size"]
            s["x"] = random.randint(0, SCREEN_W - 1)
            s["speed"] = random.uniform(0.5, 2.0) * (1 + s["size"] * 0.2)
        screen.fill(s["color"], (int(s["x"]), int(s["y"]), s["size"], s["size"]))

def add_explosion(explosions, x, y, color_base):
    count = random.randint(8, 14)
    for _ in range(count):
        ang = random.uniform(0, TAU)
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

# --- Главный цикл ---
def main():
    if not PYGAME_OK:
        print("Не могу импортировать pygame:", _PYGAME_IMPORT_ERR)
        print("Установите pygame: py -m pip install pygame")
        return
    pygame.init()
    pygame.display.set_caption("Top-Down Arcade")
    try:
        screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    except Exception as e:
        print("Не удалось создать окно отображения:", e)
        print("Проверьте драйверы видео/окружение и попробуйте снова.")
        return
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 28)
    big_font = pygame.font.SysFont(None, 54)

    state = reset_game_state()

    all_sprites = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    enemies = pygame.sprite.Group()

    player = Player(SCREEN_W // 2, SCREEN_H - 60)
    all_sprites.add(player)

    pygame.time.set_timer(SPAWN_EVENT, SPAWN_MS)

    running = True
    while running:
        dt = clock.tick(FPS)
        now = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == SPAWN_EVENT and not state["game_over"]:
                enemy = Enemy()
                enemies.add(enemy)
                all_sprites.add(enemy)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if state["game_over"] and event.key == pygame.K_r:
                    # Рестарт
                    state = reset_game_state()
                    all_sprites.empty()
                    bullets.empty()
                    enemies.empty()
                    player = Player(SCREEN_W // 2, SCREEN_H - 60)
                    all_sprites.add(player)

        keys = pygame.key.get_pressed()

        if not state["game_over"]:
            # Ввод/обновление игрока
            player.update(keys, now)
            if keys[pygame.K_SPACE]:
                player.try_shoot(now, bullets, all_sprites)

            # Обновления спрайтов
            bullets.update()
            enemies.update()

            # Столкновения пуль и врагов
            hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
            if hits:
                for enemy, blts in hits.items():
                    add_explosion(state["explosions"], enemy.rect.centerx, enemy.rect.centery, ENEMY_COLOR)
                    state["score"] += 10

            # Столкновения врагов с игроком
            crush = pygame.sprite.spritecollide(player, enemies, True)
            if crush:
                add_explosion(state["explosions"], player.rect.centerx, player.rect.centery, PLAYER_COLOR)
                player.damage(now, amount=1)
                if player.hp <= 0:
                    state["game_over"] = True

        # Рендер
        screen.fill(BG_COLOR)
        draw_stars(screen, state["stars"])
        all_sprites.draw(screen)
        update_draw_explosions(screen, state["explosions"])

        # UI
        hud = font.render(f"Score: {state['score']}   HP: {max(0, player.hp)}", True, UI_COLOR)
        screen.blit(hud, (10, 10))

        if state["game_over"]:
            overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            screen.blit(overlay, (0, 0))
            txt1 = big_font.render("GAME OVER", True, (255, 120, 120))
            txt2 = font.render("R - рестарт   ESC - выход", True, UI_COLOR)
            screen.blit(txt1, txt1.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 - 20)))
            screen.blit(txt2, txt2.get_rect(center=(SCREEN_W // 2, SCREEN_H // 2 + 30)))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    # Подсказка: установите pygame, если необходимо: pip install pygame
    main()
