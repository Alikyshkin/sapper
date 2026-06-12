"""Сапёр — консольная игра.

Управление:
    x y      — открыть клетку (например: 3 5)
    f x y    — поставить/снять флаг (например: f 3 5)
    q        — выйти из игры
"""

import random
import sys

BOMB = -1

DIFFICULTIES = {
    "1": ("Лёгкий", 8, 8, 9),
    "2": ("Средний", 12, 12, 22),
    "3": ("Сложный", 16, 16, 40),
}


def cls():
    # ANSI: очистить экран и поставить курсор в начало
    print("\033[2J\033[H", end="")


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


def render(field, opened, flags, bombs, reveal=False):
    width, height = len(field[0]), len(field)
    lines = []
    header = "    " + " ".join(f"{x:>2}" for x in range(width))
    lines.append(header)
    lines.append("    " + "---" * width)
    for y in range(height):
        row = []
        for x in range(width):
            if (x, y) in flags and not reveal:
                cell = "F"
            elif (x, y) in opened or reveal:
                value = field[y][x]
                if value == BOMB:
                    cell = "*"
                elif value == 0:
                    cell = "."
                else:
                    cell = str(value)
            else:
                cell = "#"
            row.append(f"{cell:>2}")
        lines.append(f"{y:>2} | " + " ".join(row))
    lines.append(f"\nБомб: {bombs}   Флагов: {len(flags)}")
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
    if len(parts) != 2 or not all(p.lstrip("-").isdigit() for p in parts):
        return None
    x, y = int(parts[0]), int(parts[1])
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
    message = "Ход: 'x y' — открыть, 'f x y' — флаг, 'q' — выход."

    while True:
        cls()
        if field is None:
            # До первого хода показываем пустое поле
            empty = [[0] * width for _ in range(height)]
            print(render(empty, set(), flags, bombs))
        else:
            print(render(field, opened, flags, bombs))
        print("\n" + message)

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
            print(render(field, opened, flags, bombs, reveal=True))
            print(f"\n💥 БУМ! Бомба на ({x}, {y}). Игра окончена.")
            return True

        open_cell(field, opened, flags, x, y)
        message = f"Открыто клеток: {len(opened)} из {total_safe}."

        if len(opened) >= total_safe:
            cls()
            print(render(field, opened, flags, bombs, reveal=True))
            print("\n🎉 Победа! Все безопасные клетки открыты.")
            return True


def main():
    cls()
    print("=== САПЁР ===\n")
    width, height, bombs = choose_difficulty()
    while True:
        finished = play(width, height, bombs)
        if not finished:
            break
        again = input("\nСыграть ещё раз? [y/n]: ").strip().lower()
        if again not in ("y", "yes", "д", "да", ""):
            print("Пока!")
            break


if __name__ == "__main__":
    try:
        main()
    except (EOFError, KeyboardInterrupt):
        print("\nПока!")
        sys.exit(0)
