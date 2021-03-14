from random import sample
from sys import setrecursionlimit
setrecursionlimit(10000)

def create_field(n, m, k):
    field = [[0] * m for _ in range(n)]
    rnd = [i for i in range(0, n * m)]\

    for el in sample(rnd, k):
        field[el // m][el % m] = -1

    for x in range(n):
        for y in range(m):
            if field[x][y] == -1:
                for x1 in range(max(x - 1, 0), min(x + 2, n)):
                    for y1 in range(max(y - 1, 0), min(y + 2, m)):
                        if field[x1][y1] != -1:
                            field[x1][y1] += 1

    for x in range(n):
        for y in range(m):
            field[x][y] += 10

    return field


def print_field(field, n, m):
    for i in range(m):
        print('{:^3}'.format(i), end='')
    print()
    for x in range(n):
        for y in range(m):
            el = field[x][y]
            if el == -1:
                print('\033[41m\033[30m\033[1m # \033[0m', end='')
            elif el == 0:
                print(f'\033[47m   \033[0m', end='')
            elif el > 8:
                if (x, y) in marked:
                    print(f'\033[40m\033[31m # \033[0m', end='')
                else:
                    print(f'\033[40m\033[37m # \033[0m', end='')
            else:
                print('\033[44m\033[30m\033[1m{:^3}\033[0m'.format(el), end='')

        print('{:^3}'.format(x))


def wave(field, n, m, x, y):
    global not_opened
    if field[x][y] == 0:
        for x1 in range(max(x - 1, 0), min(x + 2, n)):
            for y1 in range(max(y - 1, 0), min(y + 2, m)):
                if field[x1][y1] > 8:
                    not_opened -= 1
                    field[x1][y1] -= 10
                    wave(field, n, m, x1, y1)


def way(field, n, m, x, y):
    global not_opened
    if field[x][y] > 8:
        field[x][y] -= 10
        not_opened -= 1
        if field[x][y] == 0:
            wave(field, n, m, x, y)
        elif field[x][y] == -1:
            return 0
    return 1


def mark(x, y):
    marked.append((x, y))


width = 50
height = 50
not_opened = width * height
bombs = 100
marked = []
fld = create_field(height, width, bombs)
print_field(fld, height, width)

while not_opened != bombs:
    c, tx, ty = input('Enter command: ').split()
    c = c.lower()
    tx, ty = int(ty), int(tx)
    if c in ['mark', 'm', 'mrk']:
        mark(tx, ty)
    elif c in ['way', 'go', 'w', 'g']:
        if not way(fld, height, width, tx, ty):
            print_field(fld, height, width)
            print('\033[31m\033[1m~~You lose!~~\033[0m')
            break
    print_field(fld, height, width)
else:
    print('\033[32m\033[1m~~You win!~~\033[0m')
