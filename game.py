import pygame
import random
import config
from sprites import Player, Enemy, Bullet, PowerUp
from effects import add_explosion, update_draw_explosions, create_stars, draw_stars
from ui import Menu

try:
    import pygame
    PYGAME_OK = True
    _PYGAME_IMPORT_ERR = None
except Exception as e:
    pygame = None
    PYGAME_OK = False
    _PYGAME_IMPORT_ERR = e

def reset_game_state(settings):
    diff_config = settings.get_difficulty_config()
    return {
        "score": 0,
        "level": 1,
        "wave": 0,
        "game_over": False,
        "explosions": [],
        "stars": create_stars(140),
        "spawn_ms": diff_config["spawn_ms"],
        "powerup_chance": diff_config["powerup_chance"],
        "spawn_decrease": diff_config["spawn_decrease"],
        "score_multiplier": diff_config["multiplier"],
    }

class Game:
    def __init__(self):
        if not PYGAME_OK:
            raise RuntimeError(f"Pygame import failed: {_PYGAME_IMPORT_ERR}")
        
        pygame.init()
        pygame.display.set_caption("Top-Down Arcade")
        self.screen = pygame.display.set_mode((config.SCREEN_W, config.SCREEN_H))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 28, bold=True)
        self.big_font = pygame.font.SysFont("arial", 60, bold=True)
        self.small_font = pygame.font.SysFont("arial", 22, bold=True)
        self.tiny_font = pygame.font.SysFont("arial", 16)
        
        self.menu = Menu(self.screen, self.font, self.big_font)
        self.in_menu = True
        self.in_game = False
        self.fps_clock = pygame.time.Clock()
        self.start_transition = 0
        self.transition_duration = 60
        
        self.running = True

    def show_menu(self):
        while self.running and self.in_menu:
            result = self.menu.handle_events()
            self.menu.update()
            
            if result == "quit":
                self.running = False
                break
            elif result == "start":
                self.in_menu = False
                self.in_game = True
                self.start_transition = self.transition_duration
                self.start_game()
            
            self.menu.draw()
            self.clock.tick(60)

    def start_game(self):
        self.state = reset_game_state(self.menu.settings)
        self.difficulty_config = self.menu.settings.get_difficulty_config()
        
        self.all_sprites = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()
        
        self.player = Player(config.SCREEN_W // 2, config.SCREEN_H - 60)
        self.all_sprites.add(self.player)
        
        self.spawn_event = pygame.USEREVENT + config.SPAWN_EVENT_ID
        pygame.time.set_timer(self.spawn_event, int(self.state["spawn_ms"]))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == self.spawn_event and not self.state["game_over"]:
                self.spawn_enemy()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.in_menu = True
                    self.in_game = False
                    pygame.time.set_timer(self.spawn_event, 0)
                    return
                if self.state["game_over"] and event.key == pygame.K_r:
                    self.start_game()

    def spawn_enemy(self):
        difficulty = 1.0 + (self.state["level"] - 1) * 0.25
        enemy = Enemy(difficulty)
        self.enemies.add(enemy)
        self.all_sprites.add(enemy)
        self.state["wave"] += 1
        
        if self.state["wave"] % 8 == 0:
            self.state["level"] += 1
            self.state["spawn_ms"] = max(
                300,
                self.state["spawn_ms"] - self.state["spawn_decrease"]
            )
            pygame.time.set_timer(self.spawn_event, int(self.state["spawn_ms"]))

    def update(self, now):
        if self.state["game_over"]:
            return
        
        keys = pygame.key.get_pressed()
        self.player.update(keys, now)
        
        if keys[pygame.K_SPACE]:
            self.player.try_shoot(now, self.bullets, self.all_sprites)
        
        self.bullets.update()
        self.enemies.update()
        self.powerups.update()
        
        # Столкновения пуль и врагов
        hits = pygame.sprite.groupcollide(self.enemies, self.bullets, False, True)
        if hits:
            for enemy, blts in hits.items():
                if enemy.damage():
                    add_explosion(self.state["explosions"], enemy.rect.centerx, enemy.rect.centery, config.ENEMY_COLOR, intensity=1.5)
                    score_gain = int(10 * self.state["level"] * self.state["score_multiplier"])
                    self.state["score"] += score_gain
                    
                    if random.random() < self.state["powerup_chance"]:
                        ptype = random.choice(config.POWERUP_TYPES)
                        powerup = PowerUp(enemy.rect.centerx, enemy.rect.centery, ptype)
                        self.powerups.add(powerup)
                        self.all_sprites.add(powerup)
                    
                    enemy.kill()
        
        # Столкновения врагов с игроком
        crush = pygame.sprite.spritecollide(self.player, self.enemies, True)
        if crush:
            add_explosion(self.state["explosions"], self.player.rect.centerx, self.player.rect.centery, config.PLAYER_COLOR, intensity=2.0)
            self.player.damage(now)
            if self.player.hp <= 0:
                self.state["game_over"] = True
        
        # Столкновения с бонусами
        pups = pygame.sprite.spritecollide(self.player, self.powerups, True)
        for pup in pups:
            if pup.ptype == "health":
                self.player.heal(1)
            else:
                self.player.apply_powerup(pup.ptype, now)

    def draw_powerup_status(self, now):
        y_offset = 50
        statuses = []
        
        if now < self.player.shield_until:
            remaining = int((self.player.shield_until - now) / 1000)
            statuses.append((f"SHIELD [{remaining}s]", (100, 200, 255)))
        if now < self.player.rapidfire_until:
            remaining = int((self.player.rapidfire_until - now) / 1000)
            statuses.append((f"RAPID [{remaining}s]", (255, 220, 100)))
        if now < self.player.speed_boost_until:
            remaining = int((self.player.speed_boost_until - now) / 1000)
            statuses.append((f"BOOST [{remaining}s]", (100, 255, 200)))
        if now < self.player.dual_shot_until:
            remaining = int((self.player.dual_shot_until - now) / 1000)
            statuses.append((f"DUAL [{remaining}s]", (220, 150, 255)))
        
        for status_text, color in statuses:
            txt = self.small_font.render(status_text, True, color)
            pygame.draw.rect(self.screen, (20, 20, 40), (5, y_offset - 5, 240, 32), border_radius=6)
            pygame.draw.rect(self.screen, color, (5, y_offset - 5, 240, 32), 2, border_radius=6)
            self.screen.blit(txt, (15, y_offset))
            y_offset += 38

    def draw(self):
        self.screen.fill(config.BG_COLOR)
        draw_stars(self.screen, self.state["stars"])
        self.all_sprites.draw(self.screen)
        update_draw_explosions(self.screen, self.state["explosions"])
        
        now = pygame.time.get_ticks()
        
        # Top HUD bar
        pygame.draw.rect(self.screen, (20, 20, 40), (0, 0, config.SCREEN_W, 45), border_radius=0)
        pygame.draw.line(self.screen, (100, 100, 150), (0, 45), (config.SCREEN_W, 45), 2)
        
        hud = self.font.render(
            f"Score: {self.state['score']}  Level: {self.state['level']}  Wave: {self.state['wave']}  HP: {max(0, self.player.hp)}/{self.player.max_hp}",
            True,
            (200, 220, 255)
        )
        self.screen.blit(hud, (12, 10))
        
        # Статус активных бонусов
        self.draw_powerup_status(now)
        
        # Полоска здоровья игрока
        self._draw_player_health_bar()
        
        # FPS счётчик
        if self.menu.settings.show_fps:
            fps = self.clock.get_fps()
            fps_txt = self.tiny_font.render(f"FPS: {int(fps)}", True, (150, 255, 100))
            fps_bg = pygame.Surface((95, 22))
            fps_bg.fill((20, 20, 40))
            pygame.draw.rect(fps_bg, (150, 255, 100), (0, 0, 95, 22), 1)
            self.screen.blit(fps_bg, (config.SCREEN_W - 105, 10))
            self.screen.blit(fps_txt, (config.SCREEN_W - 100, 12))
        
        # Сложность
        difficulty_txt = self.tiny_font.render(f"Difficulty: {self.menu.settings.difficulty}", True, (220, 160, 100))
        self.screen.blit(difficulty_txt, (12, config.SCREEN_H - 25))
        
        if self.state["game_over"]:
            self._draw_game_over()
        
        pygame.display.flip()

    def _draw_player_health_bar(self):
        bar_x = config.SCREEN_W // 2 - 80
        bar_y = config.SCREEN_H - 30
        bar_width = 160
        bar_height = 14
        
        pygame.draw.rect(self.screen, (40, 40, 60), (bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4), border_radius=3)
        pygame.draw.rect(self.screen, (30, 30, 50), (bar_x, bar_y, bar_width, bar_height), border_radius=3)
        
        fill_width = (self.player.hp / self.player.max_hp) * bar_width
        color = (100, 255, 100) if self.player.hp > 1 else (255, 100, 100)
        pygame.draw.rect(self.screen, color, (bar_x, bar_y, int(fill_width), bar_height), border_radius=3)
        pygame.draw.rect(self.screen, (200, 220, 255), (bar_x, bar_y, bar_width, bar_height), 2, border_radius=3)
        
        hp_text = self.tiny_font.render(f"HP: {max(0, self.player.hp)}", True, (200, 220, 255))
        self.screen.blit(hp_text, (bar_x - 50, bar_y - 3))

    def _draw_game_over(self):
        overlay = pygame.Surface((config.SCREEN_W, config.SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        txt1 = self.big_font.render("GAME OVER", True, (255, 100, 100))
        txt1_shadow = self.big_font.render("GAME OVER", True, (50, 20, 20))
        self.screen.blit(txt1_shadow, (txt1.get_rect(center=(config.SCREEN_W // 2 + 3, config.SCREEN_H // 2 - 60 + 3))).topleft)
        self.screen.blit(txt1, txt1.get_rect(center=(config.SCREEN_W // 2, config.SCREEN_H // 2 - 60)))
        
        txt2 = self.font.render(f"Score: {self.state['score']}  |  Level: {self.state['level']}  |  Wave: {self.state['wave']}", True, (200, 220, 255))
        self.screen.blit(txt2, txt2.get_rect(center=(config.SCREEN_W // 2, config.SCREEN_H // 2)))
        
        txt3 = self.font.render(f"Difficulty: {self.menu.settings.difficulty}", True, (220, 160, 100))
        self.screen.blit(txt3, txt3.get_rect(center=(config.SCREEN_W // 2, config.SCREEN_H // 2 + 50)))
        
        txt4 = self.font.render("Press [R] to restart  or  [ESC] for menu", True, (150, 200, 150))
        self.screen.blit(txt4, txt4.get_rect(center=(config.SCREEN_W // 2, config.SCREEN_H // 2 + 110)))

    def run(self):
        self.show_menu()
        
        while self.running and self.in_game:
            dt = self.clock.tick(config.FPS)
            now = pygame.time.get_ticks()
            
            self.handle_events()
            
            if self.in_game:
                self.update(now)
                self.draw()
            elif self.in_menu:
                self.show_menu()
        
        pygame.quit()
