"""Сапёр — консольная игра.

Управление:
    x y      — открыть клетку (например: 3 5)
    f x y    — поставить/снять флаг (например: f 3 5)
    q        — выйти из игры
"""

import os
import random
import sys

BOMB = -1
CELL_COLORS = {
    "#": 90,
    ".": 90,
    "F": 93,
    "!": 91,
    "*": 91,
    "X": 91,
    "1": 96,
    "2": 92,
    "3": 93,
    "4": 95,
    "5": 91,
    "6": 96,
    "7": 97,
    "8": 97,
}

DIFFICULTIES = {
    "1": ("Лёгкий", 8, 8, 9),
    "2": ("Средний", 12, 12, 22),
    "3": ("Сложный", 16, 16, 40),
}


def terminal_supports_ansi():
    return sys.stdout.isatty() and os.environ.get("TERM") not in (None, "", "dumb")


def cls():
    if terminal_supports_ansi():
        print("\033[2J\033[H", end="")
    else:
        print()


def neighbors(x, y, width, height):
    """Все существующие соседи клетки (x, y)."""
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height:
                yield nx, ny


def create_field(width, height, bombs, safe_x, safe_y):
    """Создаёт поле с бомбами и числами.

    Бомбы не ставятся в первую открытую клетку и её соседей,
    чтобы первый ход никогда не проигрывал.
    """
    safe_zone = {(safe_x, safe_y)} | set(neighbors(safe_x, safe_y, width, height))
    cells = [(x, y) for y in range(height) for x in range(width) if (x, y) not in safe_zone]
    bomb_cells = set(random.sample(cells, min(bombs, len(cells))))

    field = [[0] * width for _ in range(height)]
    for x, y in bomb_cells:
        field[y][x] = BOMB
    for y in range(height):
        for x in range(width):
            if field[y][x] != BOMB:
                field[y][x] = sum(
                    1 for nx, ny in neighbors(x, y, width, height) if field[ny][nx] == BOMB
                )
    return field


def open_cell(field, opened, flags, x, y):
    """Открывает клетку; пустые области раскрываются волной (flood fill)."""
    width, height = len(field[0]), len(field)
    stack = [(x, y)]
    while stack:
        cx, cy = stack.pop()
        if (cx, cy) in opened or (cx, cy) in flags:
            continue
        opened.add((cx, cy))
        if field[cy][cx] == 0:
            stack.extend(
                (nx, ny)
                for nx, ny in neighbors(cx, cy, width, height)
                if (nx, ny) not in opened
            )


def cell_symbol(value, opened, flagged, reveal, exploded):
    if exploded:
        return "X"
    if flagged:
        if reveal and value != BOMB:
            return "!"
        return "F"
    if not opened and not reveal:
        return "#"
    if value == BOMB:
        return "*"
    return str(value) if value else "."


def render(field, opened, flags, bombs, reveal=False, exploded=None):
    width, height = len(field[0]), len(field)
    cell_width = max(2, len(str(width - 1)))
    row_width = max(2, len(str(height - 1)))
    color = terminal_supports_ansi() and "NO_COLOR" not in os.environ
    divider = " " * (row_width + 1) + "+-" + "-" * ((cell_width + 1) * width - 1) + "-+"
    header = " " * (row_width + 3) + " ".join(f"{x:>{cell_width}}" for x in range(width))
    lines = [header, divider]
    for y, values in enumerate(field):
        row = []
        for x, value in enumerate(values):
            coordinate = (x, y)
            symbol = cell_symbol(
                value, coordinate in opened, coordinate in flags, reveal, coordinate == exploded
            )
            padded = f"{symbol:>{cell_width}}"
            row.append(f"\033[{CELL_COLORS[symbol]}m{padded}\033[0m" if color else padded)
        lines.append(f"{y:>{row_width}} | " + " ".join(row) + " |")
    lines.append(divider)
    lines.append(f"Мины: {bombs}   Флаги: {len(flags)}   Открыто: {len(opened)} из {width * height - bombs}")
    return "\n".join(lines)


def parse_move(raw, width, height):
    """Разбирает ввод игрока. Возвращает ('open'|'flag'|'quit', x, y) или None."""
    parts = raw.strip().lower().replace(",", " ").split()
    if not parts:
        return None
    if parts[0] in ("q", "quit", "exit", "выход"):
        return ("quit", 0, 0)

    action = "open"
    if parts[0] in ("f", "flag", "ф"):
        action = "flag"
        parts = parts[1:]
    if len(parts) != 2:
        return None
    if not all((part[1:] if part.startswith("-") else part).isdecimal() for part in parts):
        return None
    try:
        x, y = map(int, parts)
    except ValueError:
        return None
    if not (0 <= x < width and 0 <= y < height):
        return None
    return (action, x, y)


def choose_difficulty():
    print("Выбери сложность:")
    for key, (name, w, h, b) in DIFFICULTIES.items():
        print(f"  {key} — {name}: {w}x{h}, {b} бомб")
    while True:
        choice = input("Сложность [1]: ").strip() or "1"
        if choice in DIFFICULTIES:
            _, w, h, b = DIFFICULTIES[choice]
            return w, h, b
        print("Введи 1, 2 или 3.")


def play(width, height, bombs):
    field = None
    opened = set()
    flags = set()
    total_safe = width * height - bombs
    empty_field = [[0] * width for _ in range(height)]
    message = ""

    while True:
        cls()
        print(f"САПЁР  ·  {width} × {height}\n")
        print(render(field if field is not None else empty_field, opened, flags, bombs))
        print("\nОткрыть: x y   Флаг: f x y   Выход: q")
        if message:
            print(message)

        try:
            raw = input("> ")
        except (EOFError, KeyboardInterrupt):
            print("\nПока!")
            return False

        move = parse_move(raw, width, height)
        if move is None:
            message = f"Не понял. Введи координаты 0..{width - 1} 0..{height - 1}, 'f x y' или 'q'."
            continue
        action, x, y = move

        if action == "quit":
            print("Пока!")
            return False

        if action == "flag":
            if (x, y) in opened:
                message = "Эта клетка уже открыта."
            elif (x, y) in flags:
                flags.discard((x, y))
                message = f"Флаг снят с ({x}, {y})."
            else:
                flags.add((x, y))
                message = f"Флаг поставлен на ({x}, {y})."
            continue

        # action == "open"
        if (x, y) in flags:
            message = "Клетка под флагом. Сначала сними флаг: f x y."
            continue
        if (x, y) in opened:
            message = "Эта клетка уже открыта."
            continue

        if field is None:
            field = create_field(width, height, bombs, x, y)

        if field[y][x] == BOMB:
            cls()
            print(render(field, opened, flags, bombs, reveal=True, exploded=(x, y)))
            print(f"\nНа клетке ({x}, {y}) была мина. Игра окончена.")
            if flags:
                print("F — верный флаг, ! — ошибочный.")
            return True

        open_cell(field, opened, flags, x, y)
        message = ""

        if len(opened) >= total_safe:
            cls()
            print(render(field, opened, flags, bombs, reveal=True))
            print("\nПобеда! Все безопасные клетки открыты.")
            return True


def main():
    cls()
    print("=== САПЁР ===\n")
    width, height, bombs = choose_difficulty()
    while True:
        finished = play(width, height, bombs)
        if not finished:
            break
        while True:
            again = input("\nСыграть ещё раз? [д/н]: ").strip().lower()
            if again in ("y", "yes", "д", "да", ""):
                break
            if again in ("n", "no", "н", "нет", "q", "quit", "exit", "выход"):
                print("Пока!")
                return
            print("Введите «д» или «н».")



if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\nПока!")
        sys.exit(0)
