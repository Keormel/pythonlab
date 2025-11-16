import math

# === ЭКРАН ===
SCREEN_W, SCREEN_H = 480, 720
FPS = 60
BG_COLOR = (10, 12, 20)

# === ЦВЕТА ===
PLAYER_COLOR = (80, 200, 255)
ENEMY_COLOR = (240, 70, 70)
BULLET_COLOR = (255, 245, 120)
POWERUP_COLOR = (100, 255, 150)
UI_COLOR = (220, 220, 230)

# === ИГРОВЫЕ ПАРАМЕТРЫ ===
SPAWN_MS = 700
SPAWN_MS_MIN = 350
SPAWN_MS_DECREASE = 50
SPAWN_EVENT_ID = 1

# === ФИЗИКА ===
TAU = 2 * math.pi
PLAYER_SPEED = 5
PLAYER_SHOOT_DELAY = 220
BULLET_SPEED = 12
ENEMY_SPEED_MIN, ENEMY_SPEED_MAX = 2.0, 4.5
PLAYER_HP = 3

# === БОНЫ ===
POWERUP_SPAWN_CHANCE = 0.08
POWERUP_TYPES = ["rapidfire", "shield", "speed", "dual_shot", "health"]
