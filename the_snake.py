"""Классическая игра «Змейка» на pygame."""
import sys
from random import choice, randint

import pygame as pg

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

CENTER_POSITION = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
CYAN = (93, 216, 228)

BOARD_BACKGROUND_COLOR = BLACK
BORDER_COLOR = CYAN
APPLE_COLOR = RED
SNAKE_COLOR = GREEN

SPEED = 20

screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)
pg.display.set_caption('Змейка')

clock = pg.time.Clock()


class GameObject:
    """Базовый класс игровых объектов: позиция и цвет."""

    def __init__(self, color=None, position=None) -> None:
        """Инициализирует позицию и цвет объекта."""
        self.position = position if position is not None else CENTER_POSITION
        self.body_color = color

    def draw_cell(self, position, color=None, border=True) -> None:
        """Рисует одну ячейку поля: квадрат с границей."""
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, color or self.body_color, rect)
        if border:
            pg.draw.rect(screen, BORDER_COLOR, rect, 1)

    def draw(self) -> None:
        """Заготовка отрисовки, наследники обязаны переопределить."""
        raise NotImplementedError(
            f'Метод draw не переопределён в классе {type(self).__name__}.'
        )


class Apple(GameObject):
    """Яблоко, появляющееся в свободной ячейке игрового поля."""

    def __init__(self, occupied_positions=None, color=APPLE_COLOR) -> None:
        """Задаёт цвет и случайную свободную позицию яблока."""
        super().__init__(color=color)
        self.randomize_position(occupied_positions)

    def randomize_position(self, occupied_positions=None) -> None:
        """Размещает яблоко в случайной ячейке вне занятых позиций."""
        occupied = occupied_positions or []
        while True:
            position = (
                randint(0, GRID_WIDTH - 1) * GRID_SIZE,
                randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
            )
            if position not in occupied:
                self.position = position
                return

    def draw(self) -> None:
        """Рисует яблоко на игровом поле."""
        self.draw_cell(self.position, self.body_color)


class Snake(GameObject):
    """Змейка: сегменты, движение, рост и сброс при столкновении."""

    def __init__(self, color=SNAKE_COLOR) -> None:
        """Создаёт змейку из одной головы, стартовое направление — вправо."""
        super().__init__(color=color)
        self.next_direction = None
        self.last: tuple[int, int] | None = None
        self.reset()
        self.direction = RIGHT

    def get_head_position(self) -> tuple:
        """Возвращает координаты головы змейки."""
        return self.positions[0]

    def update_direction(self) -> None:
        """Применяет направление, отложенное после нажатия клавиши."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self) -> None:
        """Сдвигает змейку на ячейку, телепортируя через края поля."""
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction
        new_head = (
            (head_x + dx * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + dy * GRID_SIZE) % SCREEN_HEIGHT,
        )
        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.last = self.positions.pop()

    def reset(self) -> None:
        """Сбрасывает атрибуты змейки в начальное состояние."""
        self.length = 1
        self.position = CENTER_POSITION
        self.positions = [self.position]
        self.direction = choice([UP, DOWN, LEFT, RIGHT])
        self.next_direction = None
        self.last = None

    def draw(self) -> None:
        """Рисует голову и затирает клетку, покинутую хвостом."""
        self.draw_cell(self.get_head_position(), self.body_color)
        if self.last:
            self.draw_cell(self.last, BOARD_BACKGROUND_COLOR, border=False)


TURNS = {
    pg.K_UP: (UP, DOWN),
    pg.K_DOWN: (DOWN, UP),
    pg.K_LEFT: (LEFT, RIGHT),
    pg.K_RIGHT: (RIGHT, LEFT),
}


def handle_keys(game_object) -> None:
    """Обрабатывает нажатия клавиш, меняя направление змейки."""
    for event in pg.event.get():
        if event.type == pg.QUIT or (
            event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE
        ):
            pg.quit()
            sys.exit()
        elif event.type == pg.KEYDOWN and event.key in TURNS:
            new_direction, opposite = TURNS[event.key]
            if game_object.direction != opposite:
                game_object.next_direction = new_direction


def main() -> None:
    """Основной игровой цикл."""
    pg.init()
    snake = Snake()
    apple = Apple(occupied_positions=snake.positions)

    screen.fill(BOARD_BACKGROUND_COLOR)

    while True:
        clock.tick(SPEED)

        handle_keys(snake)
        snake.update_direction()
        snake.move()

        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(snake.positions)
        elif snake.get_head_position() in snake.positions[4:]:
            snake.reset()
            screen.fill(BOARD_BACKGROUND_COLOR)
            apple.randomize_position(snake.positions)

        snake.draw()
        apple.draw()
        pg.display.update()


if __name__ == '__main__':
    main()
