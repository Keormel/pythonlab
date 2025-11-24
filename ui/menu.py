import pygame
import math
import config
from .settings import Settings

class Menu:
    def __init__(self, screen, font, big_font):
        self.screen = screen
        self.font = font
        self.big_font = big_font
        self.settings = Settings()
        self.state = "main"
        self.selected = 0
        self.difficulties = list(Settings.DIFFICULTIES.keys())
        self.animation_counter = 0
        self.start_game_triggered = False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state != "main":
                        self.state = "main"
                        self.selected = 0
                    else:
                        return "quit"
                elif event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % self._get_menu_items()
                elif event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % self._get_menu_items()
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    return self._handle_selection()
        return None

    def _get_menu_items(self):
        if self.state == "main":
            return 3
        elif self.state == "difficulty":
            return len(self.difficulties)
        elif self.state == "settings":
            return 4
        return 0

    def _handle_selection(self):
        if self.state == "main":
            if self.selected == 0:
                self.state = "difficulty"
                self.selected = self.difficulties.index(self.settings.difficulty)
                return None
            elif self.selected == 1:
                self.state = "settings"
                self.selected = 0
                return None
            elif self.selected == 2:
                return "quit"
        elif self.state == "difficulty":
            self.settings.difficulty = self.difficulties[self.selected]
            self.start_game_triggered = True
            return "start"
        elif self.state == "settings":
            if self.selected == 0:
                self.settings.sfx_enabled = not self.settings.sfx_enabled
            elif self.selected == 1:
                self.settings.show_fps = not self.settings.show_fps
            elif self.selected == 2:
                self.state = "main"
                self.selected = 1
            elif self.selected == 3:
                self.start_game_triggered = True
                return "start"
        return None

    def update(self):
        self.animation_counter = (self.animation_counter + 1) % 360

    def draw(self):
        self.screen.fill(config.BG_COLOR)
        self._draw_animated_bg()
        
        if self.state == "main":
            self._draw_main_menu()
        elif self.state == "difficulty":
            self._draw_difficulty_menu()
        elif self.state == "settings":
            self._draw_settings_menu()
        
        pygame.display.flip()

    def _draw_animated_bg(self):
        for i in range(80):
            x = (i * 59) % config.SCREEN_W
            y = (i * 73 + self.animation_counter // 2) % config.SCREEN_H
            size = 1 + (i % 2)
            shade = 60 + int(40 * math.sin(self.animation_counter * 0.01 + i))
            pygame.draw.circle(self.screen, (shade, shade, 200), (x, y), size)

    def _draw_main_menu(self):
        pulse = 1.0 + 0.15 * math.sin(self.animation_counter * 0.02)
        title_size = int(72 * pulse)
        title_font = pygame.font.SysFont("arial", title_size, bold=True)
        title = title_font.render("ARCADE", True, config.PLAYER_COLOR)
        title_rect = title.get_rect(center=(config.SCREEN_W // 2, 60))
        
        shadow = title_font.render("ARCADE", True, (20, 20, 50))
        self.screen.blit(shadow, (title_rect.x + 3, title_rect.y + 3))
        self.screen.blit(title, title_rect)
        
        subtitle = pygame.font.SysFont("arial", 32, bold=True).render("TOP-DOWN SHOOTER", True, (100, 200, 255))
        self.screen.blit(subtitle, subtitle.get_rect(center=(config.SCREEN_W // 2, 125)))
        
        menu_items = [
            ("PLAY", (100, 200, 255)),
            ("SETTINGS", (100, 255, 200)),
            ("EXIT", (255, 150, 150)),
        ]
        
        y_start = 240
        item_height = 75
        
        for i, (text, color) in enumerate(menu_items):
            is_selected = i == self.selected
            y_pos = y_start + i * item_height
            
            if is_selected:
                scale = 1.0 + 0.1 * math.sin(self.animation_counter * 0.1)
                pygame.draw.rect(self.screen, color, (50, y_pos - 20, 380, 55), border_radius=10)
                pygame.draw.rect(self.screen, (255, 255, 255), (50, y_pos - 20, 380, 55), 3, border_radius=10)
                text_color = (10, 10, 20)
                font_size = int(36 * scale)
            else:
                pygame.draw.rect(self.screen, color, (50, y_pos - 20, 380, 55), 2, border_radius=10)
                text_color = color
                font_size = 32
            
            txt_font = pygame.font.SysFont("arial", font_size, bold=True)
            txt = txt_font.render(text, True, text_color)
            self.screen.blit(txt, txt.get_rect(center=(config.SCREEN_W // 2, y_pos)))

    def _draw_difficulty_menu(self):
        pulse = 0.7 #1.0 + 0.08 * math.sin(self.animation_counter * 0.02)
        title_size = int(60 * pulse)
        title_font = pygame.font.SysFont("arial", title_size, bold=True)
        
        # Main title with enhanced styling
        title = title_font.render("SELECT DIFFICULTY", True, config.ENEMY_COLOR)
        title_rect = title.get_rect(center=(config.SCREEN_W // 2, 60))
        
        # Shadow effect
        shadow = title_font.render("SELECT DIFFICULTY", True, (20, 20, 50))
        self.screen.blit(shadow, (title_rect.x + 3, title_rect.y + 3))
        self.screen.blit(title, title_rect)
        
        # Subtitle with glow effect
        subtitle_font = pygame.font.SysFont("arial", 28, bold=True)
        subtitle = subtitle_font.render("Choose Your Challenge", True, (150, 150, 200))
        self.screen.blit(subtitle, subtitle.get_rect(center=(config.SCREEN_W // 2, 120)))
        
        # Decorative line
        pygame.draw.line(self.screen, (100, 150, 200), (80, 155), (config.SCREEN_W - 80, 155), 2)
        pygame.draw.line(self.screen, (150, 200, 255), (80, 157), (config.SCREEN_W - 80, 157), 1)
        
        descriptions = {
            "Easy": "Perfect for beginners",
            "Normal": "Well balanced gameplay",
            "Hard": "For experienced players",
            "Nightmare": "Ultimate challenge",
        }
        
        colors_difficulty = {
            "Easy": (100, 255, 150),
            "Normal": (100, 200, 255),
            "Hard": (255, 180, 80),
            "Nightmare": (255, 100, 100),
        }
        
        y_start = 220
        item_height = 75
        
        for i, difficulty in enumerate(self.difficulties):
            is_selected = i == self.selected
            y_pos = y_start + i * item_height
            color = colors_difficulty[difficulty]
            
            if is_selected:
                scale = 1.0 + 0.1 * math.sin(self.animation_counter * 0.1)
                
                # Glow effect for selected item
                glow_color = tuple(min(255, c + 50) for c in color)
                pygame.draw.rect(self.screen, glow_color, (40, y_pos - 25, 400, 65), border_radius=12)
                pygame.draw.rect(self.screen, color, (45, y_pos - 22, 390, 59), border_radius=10)
                pygame.draw.rect(self.screen, (255, 255, 255), (45, y_pos - 22, 390, 59), 3, border_radius=10)
                
                text_color = (10, 10, 20)
                font_size = int(36 * scale)
            else:
                pygame.draw.rect(self.screen, color, (50, y_pos - 20, 380, 55), 2, border_radius=10)
                text_color = color
                font_size = 32
            
            txt_font = pygame.font.SysFont("arial", font_size, bold=True)
            txt = txt_font.render(difficulty.upper(), True, text_color)
            self.screen.blit(txt, txt.get_rect(center=(config.SCREEN_W // 2, y_pos - 5)))
            
            desc_font = pygame.font.SysFont("arial", 18)
            desc = desc_font.render(descriptions[difficulty], True, (180, 180, 200))
            self.screen.blit(desc, desc.get_rect(center=(config.SCREEN_W // 2, y_pos + 18)))

    def _draw_settings_menu(self):
        pulse = 1.0 + 0.15 * math.sin(self.animation_counter * 0.02)
        title_size = int(72 * pulse)
        title_font = pygame.font.SysFont("arial", title_size, bold=True)
        title = title_font.render("SETTINGS", True, config.POWERUP_COLOR)
        title_rect = title.get_rect(center=(config.SCREEN_W // 2, 60))
        
        shadow = title_font.render("SETTINGS", True, (20, 20, 50))
        self.screen.blit(shadow, (title_rect.x + 3, title_rect.y + 3))
        self.screen.blit(title, title_rect)
        
        settings_items = [
            (f"SOUND: {'ON' if self.settings.sfx_enabled else 'OFF'}", (100, 255, 200)),
            (f"FPS COUNTER: {'ON' if self.settings.show_fps else 'OFF'}", (100, 200, 255)),
            (f"DIFFICULTY: {self.settings.difficulty.upper()}", (255, 200, 100)),
            ("START GAME", (100, 255, 150)),
        ]
        
        y_start = 240
        item_height = 75
        
        for i, (text, color) in enumerate(settings_items):
            is_selected = i == self.selected
            y_pos = y_start + i * item_height
            
            if is_selected:
                scale = 1.0 + 0.1 * math.sin(self.animation_counter * 0.1)
                pygame.draw.rect(self.screen, color, (50, y_pos - 20, 380, 55), border_radius=10)
                pygame.draw.rect(self.screen, (255, 255, 255), (50, y_pos - 20, 380, 55), 3, border_radius=10)
                text_color = (10, 10, 20)
                font_size = int(36 * scale)
            else:
                pygame.draw.rect(self.screen, color, (50, y_pos - 20, 380, 55), 2, border_radius=10)
                text_color = color
                font_size = 32
            
            txt_font = pygame.font.SysFont("arial", font_size, bold=True)
            txt = txt_font.render(text, True, text_color)
            self.screen.blit(txt, txt.get_rect(center=(config.SCREEN_W // 2, y_pos)))
