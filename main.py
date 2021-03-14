import arcade
from random import sample
import sys
sys.setrecursionlimit(10000)

SPRITE_SIZE = 50

COLUMN_COUNT = 20
ROW_COUNT = 20

BOMBS = 40

SIZE = 30

MARGIN = 3

SCREEN_WIDTH = (MARGIN + SIZE) * COLUMN_COUNT + MARGIN
SCREEN_HEIGHT = (MARGIN + SIZE) * ROW_COUNT + MARGIN

SPRITES_SCALE = SIZE / SPRITE_SIZE
TEXT_SCALE = SPRITES_SCALE * 2
TEXT_ALPHA = 180

SCREEN_TITLE = 'Сапёр'


class MyGame(arcade.Window):
    def __init__(self, width, height, title):
        # ----- Инициализация класса предка и функции вне логики: -----
        #
        self._going = True
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.DARK_GRAY)
        #
        # ----- Заполнение матрицы и списка спрайтов: -----
        #
        # -- инициализация переменных
        self.col = 0
        self.row = 0
        self.action = None
        self.gird_sprite_list = arcade.SpriteList()
        self.gird_sprites = []
        #
        # -- добавление спрайтов
        for row in range(ROW_COUNT):
            self.gird_sprites.append([])
            for column in range(COLUMN_COUNT):
                x = column * (SIZE + MARGIN) + (SIZE / 2 + MARGIN)
                y = row * (SIZE + MARGIN) + (SIZE / 2 + MARGIN)
                sprite = arcade.Sprite("sprites/void.png", SPRITES_SCALE)
                sprite.center_x = x
                sprite.center_y = y
                self.gird_sprite_list.append(sprite)
                self.gird_sprites[row].append(sprite)
        #
        # --- Заполнение поля и переменных игры:
        #
        # -- инициализация переменных
        self.field = [[0] * COLUMN_COUNT for _ in range(ROW_COUNT)]
        self.not_opened = ROW_COUNT * COLUMN_COUNT
        self.flags = []
        #
        # -- раскидка бомб
        rnd = [i for i in range(0, COLUMN_COUNT * ROW_COUNT)]
        for el in sample(rnd, BOMBS):
            self.field[el // COLUMN_COUNT][el % COLUMN_COUNT] = -1
        #
        # -- заполнение поля числами
        for row in range(ROW_COUNT):
            for col in range(COLUMN_COUNT):
                if self.field[row][col] == -1:
                    for r1 in range(max(row - 1, 0), min(row + 2, ROW_COUNT)):
                        for c1 in range(max(col - 1, 0), min(col + 2, COLUMN_COUNT)):
                            if self.field[r1][c1] != -1:
                                self.field[r1][c1] += 1
        #
        # ----- Добавления спрайтов открытых клеток: -----
        #
        for row in range(ROW_COUNT):
            for col in range(COLUMN_COUNT):
                if self.field[row][col] == -1:
                    self.gird_sprites[row][col].append_texture(arcade.load_texture("sprites/bomb1.png"))
                elif 0 <= self.field[row][col] <= 8:
                    self.gird_sprites[row][col].append_texture(
                        arcade.load_texture(f"sprites/op{self.field[row][col]}1.png"))
                self.gird_sprites[row][col].append_texture(arcade.load_texture("sprites/flag.png"))
        #
        # -- делаем поле невидимым
        #
        for row in range(ROW_COUNT):
            for col in range(COLUMN_COUNT):
                self.field[row][col] += 10

    def on_draw(self):
        """ Рендер спрайтов: """
        arcade.start_render()
        self.gird_sprite_list.draw()

    def way(self, row, col):
        """ Открытие клетки: """
        if self.field[row][col] > 8:
            self._open(row, col)
            if self.field[row][col] == -1:
                self._lose()
            else:
                if self.field[row][col] == 0:
                    self._wave(row, col)
                if self.not_opened == BOMBS:
                    self._win()

    def flag(self, row, col):
        """ Поставка влажка: """
        if self.field[row][col] > 8:
            if (row, col) in self.flags:
                self.flags.remove((row, col))
                self.gird_sprites[row][col].set_texture(0)
            elif len(self.flags) < BOMBS:
                self.flags.append((row, col))
                self.gird_sprites[row][col].set_texture(2)

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        """ Нажатие мыши (удерживание)"""
        if self._going:
            col = int(x // (SIZE + MARGIN))
            row = int(y // (SIZE + MARGIN))
            if col >= COLUMN_COUNT or row >= ROW_COUNT:
                return
            if button == arcade.MOUSE_BUTTON_LEFT:
                self.col = col
                self.row = row
                if self.field[self.row][self.col] > 8:
                    if (self.row, self.col) not in self.flags:
                        self.gird_sprites[self.row][self.col].alpha = 100
                        self.action = self.way
            elif button == arcade.MOUSE_BUTTON_RIGHT:
                if self.action == self.way:
                    self.action = None
                    self.gird_sprites[self.row][self.col].alpha = 255
                else:
                    self.flag(row, col)

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
        """ Нажатие мыши (действие) """
        if self.action:
            if self.action == self.way:
                self.gird_sprites[self.row][self.col].alpha = 255
            self.action(self.row, self.col)
            self.action = None

    def _open(self, row, col):
        """ Открытие клетки по координатам: """
        self.field[row][col] -= 10
        self.gird_sprites[row][col].set_texture(1)
        self.not_opened -= 1

    def _wave(self, row, col):
        """ Волновой алгоритм закрашивания: """
        if self.field[row][col] == 0:
            for r1 in range(max(row - 1, 0), min(row + 2, ROW_COUNT)):
                for c1 in range(max(col - 1, 0), min(col + 2, COLUMN_COUNT)):
                    if self.field[r1][c1] > 8:
                        self._open(r1, c1)
                        self._wave(r1, c1)

    def _win(self):
        """ Победа """
        self._going = False
        for row in range(ROW_COUNT):
            for col in range(COLUMN_COUNT):
                if self.field[row][col] == 9:
                    self.gird_sprites[row][col].set_texture(2)
        text = arcade.Sprite('sprites/win.png', TEXT_SCALE, center_x=SCREEN_WIDTH / 2,
                             center_y=SCREEN_HEIGHT / 2)
        text.alpha = TEXT_ALPHA
        self.gird_sprite_list.append(text)

    def _lose(self):
        """ Проигрыш """
        self._going = False
        for row in range(ROW_COUNT):
            for col in range(COLUMN_COUNT):
                self.gird_sprites[row][col].set_texture(1)
        text = arcade.Sprite('sprites/lose.png', TEXT_SCALE, center_x=SCREEN_WIDTH / 2,
                             center_y=SCREEN_HEIGHT / 2)
        text.alpha = TEXT_ALPHA
        self.gird_sprite_list.append(text)


def main():
    MyGame(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    arcade.run()


if __name__ == '__main__':
    main()
