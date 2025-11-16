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
        self.state = "main"  # main, difficulty, settings
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
        # Анимированный фон со звёздами
        for i in range(80):
            x = (i * 59) % config.SCREEN_W
            y = (i * 73 + self.animation_counter // 2) % config.SCREEN_H
            size = 1 + (i % 2)
            shade = 60 + int(40 * math.sin(self.animation_counter * 0.01 + i))
            pygame.draw.circle(self.screen, (shade, shade, 200), (x, y), size)

    def _draw_main_menu(self):
        # Заголовок с пульсирующим эффектом
        pulse = 1.0 + 0.1 * math.sin(self.animation_counter * 0.02)
        title_size = int(54 * pulse)
        title_font = pygame.font.SysFont("arial", title_size, bold=True)
        title = title_font.render("ARCADE", True, config.PLAYER_COLOR)
        self.screen.blit(title, title.get_rect(center=(config.SCREEN_W // 2, 70)))
        
        subtitle = self.font.render("TOP-DOWN", True, (100, 200, 255))
        self.screen.blit(subtitle, subtitle.get_rect(center=(config.SCREEN_W // 2, 120)))
        
        menu_items = [
            ("PLAY", "🎮"),
            ("SETTINGS", "⚙️"),
            ("EXIT", "❌"),
        ]
        
        y_start = 220
        for i, (text, emoji) in enumerate(menu_items):
            is_selected = i == self.selected
            
            if is_selected:
                # Анимированный фон для выбранного пункта
                rect_color = (255, 200, 100, 80)
                pygame.draw.rect(self.screen, (255, 200, 100), (35, y_start + i * 80 - 18, 410, 56), border_radius=12)
                color = (255, 255, 255)
                prefix = "▶ "
                size_mult = 1.15
            else:
                color = config.UI_COLOR
                prefix = "  "
                size_mult = 1.0
            
            # Эмодзи
            emoji_font = pygame.font.SysFont("arial", int(32 * size_mult), bold=True)
            emoji_txt = emoji_font.render(emoji, True, color)
            emoji_x = config.SCREEN_W // 2 - 140
            self.screen.blit(emoji_txt, (emoji_x, y_start + i * 80 - 8))
            
            # Текст
            txt_font = pygame.font.SysFont("arial", int(32 * size_mult), bold=True)
            txt = txt_font.render(f"{prefix}{text}", True, color)
            self.screen.blit(txt, txt.get_rect(center=(config.SCREEN_W // 2 + 40, y_start + i * 80)))

    def _draw_difficulty_menu(self):
        pulse = 1.0 + 0.1 * math.sin(self.animation_counter * 0.02)
        title_size = int(48 * pulse)
        title_font = pygame.font.SysFont("arial", title_size, bold=True)
        title = title_font.render("DIFFICULTY", True, config.ENEMY_COLOR)
        self.screen.blit(title, title.get_rect(center=(config.SCREEN_W // 2, 50)))
        
        descriptions = {
            "Easy": "Relax Mode",
            "Normal": "Balanced",
            "Hard": "Challenge",
            "Nightmare": "Extreme",
        }
        
        emojis = {
            "Easy": "😊",
            "Normal": "😐",
            "Hard": "😈",
            "Nightmare": "💀",
        }
        
        colors_difficulty = {
            "Easy": (100, 255, 150),
            "Normal": (100, 200, 255),
            "Hard": (255, 200, 100),
            "Nightmare": (255, 100, 100),
        }
        
        y_start = 160
        for i, difficulty in enumerate(self.difficulties):
            is_selected = i == self.selected
            color = colors_difficulty[difficulty]
            emoji = emojis[difficulty]
            
            if is_selected:
                pygame.draw.rect(self.screen, color, (30, y_start + i * 70 - 12, 420, 48), border_radius=8)
                text_color = (10, 12, 20)
                prefix = "▶▶ "
                size_mult = 1.1
            else:
                pygame.draw.rect(self.screen, color, (30, y_start + i * 70 - 12, 420, 48), 2, border_radius=8)
                text_color = color
                prefix = "   "
                size_mult = 1.0
            
            # Эмодзи
            emoji_font = pygame.font.SysFont("arial", int(28 * size_mult), bold=True)
            emoji_txt = emoji_font.render(emoji, True, text_color)
            self.screen.blit(emoji_txt, (50, y_start + i * 70 - 6))
            
            # Название сложности
            txt_font = pygame.font.SysFont("arial", int(28 * size_mult), bold=True)
            txt = txt_font.render(f"{prefix}{difficulty}", True, text_color)
            self.screen.blit(txt, txt.get_rect(center=(config.SCREEN_W // 2 + 30, y_start + i * 70)))
            
            # Описание
            desc_font = pygame.font.SysFont("arial", 18)
            desc = desc_font.render(descriptions[difficulty], True, (180, 180, 180))
            self.screen.blit(desc, desc.get_rect(center=(config.SCREEN_W // 2 + 30, y_start + i * 70 + 22)))

    def _draw_settings_menu(self):
        pulse = 1.0 + 0.1 * math.sin(self.animation_counter * 0.02)
        title_size = int(48 * pulse)
        title_font = pygame.font.SysFont("arial", title_size, bold=True)
        title = title_font.render("SETTINGS", True, config.POWERUP_COLOR)
        self.screen.blit(title, title.get_rect(center=(config.SCREEN_W // 2, 50)))
        
        settings_items = [
            (f"SOUND: {'ON' if self.settings.sfx_enabled else 'OFF'}", "🔊" if self.settings.sfx_enabled else "🔇"),
            (f"FPS: {'ON' if self.settings.show_fps else 'OFF'}", "📊"),
            (f"DIFF: {self.settings.difficulty}", "⚔️"),
            ("START GAME", "▶️"),
        ]
        
        option_colors = [
            (100, 255, 200),
            (100, 200, 255),
            (255, 200, 100),
            (100, 255, 150),
        ]
        
        y_start = 180
        for i, (text, emoji) in enumerate(settings_items):
            is_selected = i == self.selected
            color = option_colors[i]
            
            if is_selected:
                pygame.draw.rect(self.screen, color, (30, y_start + i * 70 - 12, 420, 48), border_radius=8)
                text_color = (10, 12, 20)
                prefix = "▶▶ "
                size_mult = 1.1
            else:
                pygame.draw.rect(self.screen, color, (30, y_start + i * 70 - 12, 420, 48), 2, border_radius=8)
                text_color = color
                prefix = "   "
                size_mult = 1.0
            
            # Эмодзи
            emoji_font = pygame.font.SysFont("arial", int(28 * size_mult), bold=True)
            emoji_txt = emoji_font.render(emoji, True, text_color)
            self.screen.blit(emoji_txt, (50, y_start + i * 70 - 6))
            
            # Текст
            txt_font = pygame.font.SysFont("arial", int(26 * size_mult), bold=True)
            txt = txt_font.render(f"{prefix}{text}", True, text_color)
            self.screen.blit(txt, txt.get_rect(center=(config.SCREEN_W // 2 + 30, y_start + i * 70)))
