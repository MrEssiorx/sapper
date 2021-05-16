import arcade
from random import sample

# --- Setting global values (optional) ---

COLUMN_COUNT = 20  # The width of field (tiles number)
ROW_COUNT = 20  # The height of field (tiles number)

BOMBS = 40  # The number of bombs

SIZE = 30  # The size of one tile

MARGIN = 3  # The distance between tiles on field

SCREEN_TITLE = 'Sapper'  # The title of screen
TEXT_ALPHA = 180  # The transparency of win/lose message

SPRITE_SIZE = 50  # The size of sprites (png image)

# --- Setting non-optional global variables ---

SCREEN_WIDTH = (MARGIN + SIZE) * COLUMN_COUNT + MARGIN  # Width of game screen (in pixels)
SCREEN_HEIGHT = (MARGIN + SIZE) * ROW_COUNT + MARGIN  # Height of game screen (in pixels)

SPRITES_SCALE = SIZE / SPRITE_SIZE  # The scale of drawing tiles
TEXT_SCALE = SPRITES_SCALE * 2  # The scale of drawing lose/win messages


# ----- The main game class (see arcade documentation) ------
class MyGame(arcade.Window):
    def __init__(self, width, height, title):

        # ----- Initialing parent class and setting out-game properties: -----
        super().__init__(width, height, title)
        arcade.set_background_color(arcade.color.DARK_GRAY)

        # ----- Creating Sprite-objects and filling  -----
        #       grind list and list containing all sprites
        self.gird_sprite_list = arcade.SpriteList()
        self.gird_sprites = []
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

        # ----- Initialing game logic variables: -----
        self.col = 0
        self.row = 0
        self.action = None
        self._going = True
        self.field = [[0] * COLUMN_COUNT for _ in range(ROW_COUNT)]
        self.not_opened = ROW_COUNT * COLUMN_COUNT
        self.flags = []

        # -- placing mines on field
        rnd = [i for i in range(0, COLUMN_COUNT * ROW_COUNT)]
        for el in sample(rnd, BOMBS):
            self.field[el // COLUMN_COUNT][el % COLUMN_COUNT] = -1

        # -- filling field with numbers according to rules
        for row in range(ROW_COUNT):
            for col in range(COLUMN_COUNT):
                if self.field[row][col] == -1:
                    for r1 in range(max(row - 1, 0), min(row + 2, ROW_COUNT)):
                        for c1 in range(max(col - 1, 0), min(col + 2, COLUMN_COUNT)):
                            if self.field[r1][c1] != -1:
                                self.field[r1][c1] += 1

        # ----- **adding open-tile sprites: -----
        for row in range(ROW_COUNT):
            for col in range(COLUMN_COUNT):
                if self.field[row][col] == -1:
                    self.gird_sprites[row][col].append_texture(arcade.load_texture("sprites/bomb1.png"))
                elif 0 <= self.field[row][col] <= 8:
                    self.gird_sprites[row][col].append_texture(
                        arcade.load_texture(f"sprites/op{self.field[row][col]}1.png"))
                self.gird_sprites[row][col].append_texture(arcade.load_texture("sprites/flag.png"))

        # -- making tiles closed
        for row in range(ROW_COUNT):
            for col in range(COLUMN_COUNT):
                self.field[row][col] += 10

    def on_draw(self):
        """ Sprites rendering: """
        arcade.start_render()
        self.gird_sprite_list.draw()

    def way(self, row, col):
        """ Player opens closed tile: """
        if self.field[row][col] > 8 and (row, col) not in self.flags:
            self._open(row, col)
            if self.field[row][col] == -1:
                self._lose()
            else:
                if self.field[row][col] == 0:
                    self._wave(row, col)
                if self.not_opened == BOMBS:
                    self._win()

    def number(self, row, col):
        """ Player opens closed tiles around number: """
        for r in range(row - 1, row + 2):
            for c in range(col - 1, col + 2):
                if 0 <= r < ROW_COUNT and 0 <= c < COLUMN_COUNT:
                    self.way(r, c)

    def flag(self, row, col):
        """ Player placing flag on closed tile: """
        if self.field[row][col] > 8:
            if (row, col) in self.flags:
                self.flags.remove((row, col))
                self.gird_sprites[row][col].set_texture(0)
            elif len(self.flags) < BOMBS:
                self.flags.append((row, col))
                self.gird_sprites[row][col].set_texture(2)

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        """ Pressing mouse (acting flag placing, but not opening tile or pressing number)"""
        if self._going:
            col = int(x // (SIZE + MARGIN))
            row = int(y // (SIZE + MARGIN))
            if col >= COLUMN_COUNT or row >= ROW_COUNT:
                return

            # holding not opened tile or number
            if button == arcade.MOUSE_BUTTON_LEFT:
                self.col = col
                self.row = row

                # holding not opened tile
                if self.field[self.row][self.col] > 8:
                    if (self.row, self.col) not in self.flags:
                        self.gird_sprites[self.row][self.col].alpha = 100
                        self.action = self.way

                # holding number
                elif 1 <= self.field[self.row][self.col] <= 8:
                    flags_count = 0
                    for r in range(self.row - 1, self.row + 2):
                        for c in range(self.col - 1, self.col + 2):
                            if 0 <= r < ROW_COUNT and 0 <= c < COLUMN_COUNT:
                                if (r, c) in self.flags:
                                    flags_count += 1
                    if flags_count == self.field[self.row][self.col]:
                        for r in range(self.row - 1, self.row + 2):
                            for c in range(self.col - 1, self.col + 2):
                                if 0 <= r < ROW_COUNT and 0 <= c < COLUMN_COUNT and \
                                        not (r == self.row and c == self.col) and \
                                        self.field[r][c] > 8 and (r, c) not in self.flags:
                                    self.gird_sprites[r][c].alpha = 100
                        self.action = self.number

            # canceling action or placing flag
            elif button == arcade.MOUSE_BUTTON_RIGHT:
                # canceling action
                if self.action == self.way:
                    self.action = None
                    self.gird_sprites[self.row][self.col].alpha = 255
                elif self.action == self.number:
                    self.action = None
                    for r in range(self.row - 1, self.row + 2):
                        for c in range(self.col - 1, self.col + 2):
                            if 0 <= r < ROW_COUNT and 0 <= c < COLUMN_COUNT and \
                                    not (r == self.row and c == self.col):
                                self.gird_sprites[r][c].alpha = 255
                # actual, placing flag
                else:
                    self.flag(row, col)

    def on_mouse_release(self, x: float, y: float, button: int, modifiers: int):
        """ Releasing mouse (opening tile or acting pressing number if action wasn't canceled) """
        if self.action:
            if self.action == self.way:
                self.gird_sprites[self.row][self.col].alpha = 255
            elif self.action == self.number:
                for r in range(self.row - 1, self.row + 2):
                    for c in range(self.col - 1, self.col + 2):
                        if 0 <= r < ROW_COUNT and 0 <= c < COLUMN_COUNT and \
                                not (r == self.row and c == self.col):
                            self.gird_sprites[r][c].alpha = 255
            self.action(self.row, self.col)
            self.action = None

    def _open(self, row, col):
        """ Changing tile to opened: """
        self.field[row][col] -= 10
        self.gird_sprites[row][col].set_texture(1)
        self.not_opened -= 1

    def _wave(self, row, col):
        """ Wave algorithm of filling void: """
        if self.field[row][col] == 0:
            for r1 in range(max(row - 1, 0), min(row + 2, ROW_COUNT)):
                for c1 in range(max(col - 1, 0), min(col + 2, COLUMN_COUNT)):
                    if self.field[r1][c1] > 8:
                        self._open(r1, c1)
                        self._wave(r1, c1)

    def _win(self):
        """ Player won """
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
        """ Player bombed """
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
