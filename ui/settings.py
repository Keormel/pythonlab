class Settings:
    DIFFICULTIES = {
        "Easy": {
            "enemy_speed_min": 1.5,
            "enemy_speed_max": 3.0,
            "spawn_ms": 900,
            "spawn_decrease": 30,
            "powerup_chance": 0.12,
            "multiplier": 0.8,
        },
        "Normal": {
            "enemy_speed_min": 2.0,
            "enemy_speed_max": 4.5,
            "spawn_ms": 700,
            "spawn_decrease": 50,
            "powerup_chance": 0.08,
            "multiplier": 1.0,
        },
        "Hard": {
            "enemy_speed_min": 2.8,
            "enemy_speed_max": 5.5,
            "spawn_ms": 500,
            "spawn_decrease": 70,
            "powerup_chance": 0.05,
            "multiplier": 1.5,
        },
        "Nightmare": {
            "enemy_speed_min": 3.5,
            "enemy_speed_max": 6.5,
            "spawn_ms": 350,
            "spawn_decrease": 90,
            "powerup_chance": 0.02,
            "multiplier": 2.5,
        },
    }
    
    def __init__(self):
        self.difficulty = "Normal"
        self.sfx_enabled = True
        self.fullscreen = False
        self.show_fps = True

    def get_difficulty_config(self):
        return self.DIFFICULTIES[self.difficulty].copy()

    def to_dict(self):
        return {
            "difficulty": self.difficulty,
            "sfx_enabled": self.sfx_enabled,
            "fullscreen": self.fullscreen,
            "show_fps": self.show_fps,
        }
