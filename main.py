from game import Game

if __name__ == "__main__":
    try:
        game = Game()
        game.run()
    except RuntimeError as e:
        print(f"Ошибка: {e}")
        print("Установите pygame: pip install pygame")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
