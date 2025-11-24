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

    def _draw_hud(self, now):
        """Draw enhanced HUD with better styling and layout"""
        # Top-left info panel
        hud_data = [
            ("SCORE", str(self.state['score']), (255, 215, 0)),
            ("LEVEL", str(self.state['level']), (100, 200, 255)),
            ("WAVE", str(self.state['wave']), (100, 255, 150)),
        ]
        
        x_offset = 15
        y_offset = 15
        label_font_size = 16
        value_font_size = 24
        row_height = 45
        
        # Create smaller font for labels
        label_font = pygame.font.SysFont("arial", label_font_size, bold=True)
        
        # Draw background panel
        panel_width = 160
        panel_height = len(hud_data) * row_height + 15
        pygame.draw.rect(self.screen, (0, 0, 0, 140), (x_offset - 8, y_offset - 8, panel_width, panel_height), border_radius=10)
        pygame.draw.rect(self.screen, (100, 150, 200), (x_offset - 8, y_offset - 8, panel_width, panel_height), 2, border_radius=10)
        
        # Draw HUD items with labels above values
        current_y = y_offset
        for label, value, color in hud_data:
            label_txt = label_font.render(label, True, (150, 150, 150))
            value_txt = self.font.render(value, True, color)
            
            self.screen.blit(label_txt, (x_offset + 10, current_y))
            self.screen.blit(value_txt, (x_offset + 10, current_y + 18))
            current_y += row_height
        
        # Top-right info panel (Difficulty only)
        right_panel_width = 220
        right_x = config.SCREEN_W - right_panel_width - 10
        right_y = 15
        
        difficulty_label = label_font.render("DIFFICULTY", True, (150, 150, 150))
        difficulty_value = self.font.render(self.menu.settings.difficulty, True, (200, 150, 100))
        
        right_panel_height = 60
        pygame.draw.rect(self.screen, (0, 0, 0, 140), (right_x - 8, right_y - 8, right_panel_width, right_panel_height), border_radius=10)
        pygame.draw.rect(self.screen, (150, 200, 100), (right_x - 8, right_y - 8, right_panel_width, right_panel_height), 2, border_radius=10)
        
        self.screen.blit(difficulty_label, (right_x + 10, right_y))
        self.screen.blit(difficulty_value, (right_x + 10, right_y + 18))
        
        # FPS counter (bottom-right)
        if self.menu.settings.show_fps:
            fps = self.clock.get_fps()
            fps_txt = self.tiny_font.render(f"FPS: {int(fps)}", True, (100, 255, 100))
            fps_bg_width = 100
            fps_bg_height = 28
            pygame.draw.rect(self.screen, (0, 0, 0, 140), (config.SCREEN_W - fps_bg_width - 10, config.SCREEN_H - 35, fps_bg_width, fps_bg_height), border_radius=8)
            pygame.draw.rect(self.screen, (100, 200, 100), (config.SCREEN_W - fps_bg_width - 10, config.SCREEN_H - 35, fps_bg_width, fps_bg_height), 2, border_radius=8)
            self.screen.blit(fps_txt, (config.SCREEN_W - fps_bg_width - 5, config.SCREEN_H - 30))

    def _draw_powerup_indicators(self, now):
        """Draw powerup indicators as enhanced icons at the right edge"""
        powerups_active = []
        
        if now < self.player.shield_until:
            remaining = int((self.player.shield_until - now) / 1000)
            powerups_active.append(("SHIELD", remaining, config.POWERUP_COLOR, "⬟"))
        if now < self.player.rapidfire_until:
            remaining = int((self.player.rapidfire_until - now) / 1000)
            powerups_active.append(("RAPID", remaining, (255, 200, 50), "⚡"))
        if now < self.player.speed_boost_until:
            remaining = int((self.player.speed_boost_until - now) / 1000)
            powerups_active.append(("BOOST", remaining, (100, 255, 200), "▶"))
        if now < self.player.dual_shot_until:
            remaining = int((self.player.dual_shot_until - now) / 1000)
            powerups_active.append(("DUAL", remaining, (200, 100, 255), "⬣"))
        
        if not powerups_active:
            return
        
        # Right edge positioning
        icon_size = 55
        spacing = 75
        padding = 15
        start_x = config.SCREEN_W - icon_size - padding
        start_y = config.SCREEN_H // 2 - (len(powerups_active) * spacing) // 2
        
        for idx, (name, remaining, color, symbol) in enumerate(powerups_active):
            x = start_x
            y = start_y + idx * spacing
            
            # Draw outer glow effect
            glow_color = tuple(min(255, c + 50) for c in color)
            pygame.draw.circle(self.screen, glow_color, (x, y), icon_size // 2 + 3, 1)
            
            # Draw main icon circle with gradient effect (multiple circles for depth)
            pygame.draw.circle(self.screen, color, (x, y), icon_size // 2)
            dark_color = tuple(max(0, c - 40) for c in color)
            pygame.draw.circle(self.screen, dark_color, (x - 5, y - 5), icon_size // 2 - 3)
            
            # Draw white border
            pygame.draw.circle(self.screen, (255, 255, 255), (x, y), icon_size // 2, 3)
            
            # Draw inner highlight
            pygame.draw.circle(self.screen, (255, 255, 255), (x - 8, y - 8), 6)
            
            # Draw powerup name
            name_font = pygame.font.SysFont("arial", 10, bold=True)
            name_txt = name_font.render(name, True, (255, 255, 255))
            name_rect = name_txt.get_rect(center=(x, y))
            self.screen.blit(name_txt, (name_rect.x, name_rect.y - 2))
            
            # Draw remaining time in a small badge below
            time_font = pygame.font.SysFont("arial", 12, bold=True)
            time_txt = time_font.render(f"{remaining}s", True, (255, 255, 255))
            
            # Draw time badge background
            badge_x = x - 18
            badge_y = y + 28
            pygame.draw.rect(self.screen, color, (badge_x - 2, badge_y - 2, 40, 18), border_radius=4)
            pygame.draw.rect(self.screen, (0, 0, 0), (badge_x - 2, badge_y - 2, 40, 18), 1, border_radius=4)
            self.screen.blit(time_txt, (badge_x + 2, badge_y - 1))

    def draw(self):
        self.screen.fill(config.BG_COLOR)
        draw_stars(self.screen, self.state["stars"])
        self.all_sprites.draw(self.screen)
        update_draw_explosions(self.screen, self.state["explosions"])
        
        now = pygame.time.get_ticks()
        
        # Draw enhanced HUD
        self._draw_hud(now)
        
        # Powerup indicators (visual icons)
        self._draw_powerup_indicators(now)
        
        # Полоска здоровья игрока
        self._draw_player_health_bar()
        
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
        txt2 = self.font.render(f"Score: {self.state['score']} | Lv: {self.state['level']} | Wave: {self.state['wave']}", True, config.UI_COLOR)
        txt3 = self.font.render(f"Difficulty: {self.menu.settings.difficulty}", True, (200, 150, 100))
        txt4 = self.font.render("R - restart   ESC - menu", True, config.UI_COLOR)
        
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
