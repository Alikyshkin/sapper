import random
import os
import math


def cls():
    os.system('cls' if os.name == 'nt' else 'clear')


def create_data(zero_amount, one_amount):
    data = [0] * zero_amount + [1] * one_amount
    random.shuffle(data)
    return data


def create_board(size):
    game_data = "*" * size
    return game_data


def get_amount_of_items(zero_amount, one_amount):
    return zero_amount + one_amount


def print_data(data):
    i = 0
    print("\n   ", end="")

    while i < 8:
        print(i, end="  ")
        i += 1

    i = 0
    counter = 0

    while i < len(data):
        if i % 8 == 0:
            print("\n")
            print(counter, end="  ")
            counter += 1
            print(data[i], end="  ")
        else:
            print(data[i], end="  ")
        i += 1


def get_x_y(amount_in_row):
    x = int(input("\nType x:\n"))
    y = int(input("\nType y:\n"))
    index = int(x + (math.sqrt(amount_of_items) * y))

    return index


def open_bomb(data, game_data, index):
    counter = 0
    checked = 0
    amount_in_row = int(math.sqrt(len(data)))

    # левый верх
    if index == 0:
        checked = 1
        if data[index + 1] == 1:
            counter += 1
        if data[index + amount_in_row] == 1:
            counter += 1
        if data[index + amount_in_row + 1] == 1:
            counter += 1

    # правый верх
    if index == amount_in_row:
        checked = 1
        if data[index - 1] == 1:
            counter += 1
        if data[index + amount_in_row] == 1:
            counter += 1
        if data[index + amount_in_row - 1] == 1:
            counter += 1

    # правый низ
    if index == amount_in_row * amount_in_row:
        checked = 1
        if data[index - 1] == 1:
            counter += 1
        if data[index - amount_in_row] == 1:
            counter += 1
        if data[index - amount_in_row - 1] == 1:
            counter += 1

    # левый низ
    if index == amount_in_row * amount_in_row - amount_in_row + 1:
        checked = 1
        if data[index + 1] == 1:
            counter += 1
        if data[index - amount_in_row] == 1:
            counter += 1
        if data[index - amount_in_row + 1] == 1:
            counter += 1

    # верх
    if 0 < index < amount_in_row:
        checked = 1
        if data[index - 1] == 1:
            counter += 1
        if data[index + 1] == 1:
            counter += 1
        if data[index + amount_in_row] == 1:
            counter += 1
        if data[index + amount_in_row + 1] == 1:
            counter += 1
        if data[index + amount_in_row - 1] == 1:
            counter += 1

    # низ
    if amount_in_row * amount_in_row - amount_in_row + 1 < index < amount_in_row * amount_in_row:
        checked = 1
        if data[index - 1] == 1:
            counter += 1
        if data[index + 1] == 1:
            counter += 1
        if data[index - amount_in_row] == 1:
            counter += 1
        if data[index - amount_in_row + 1] == 1:
            counter += 1
        if data[index - amount_in_row - 1] == 1:
            counter += 1

    # право
    if index % amount_in_row - 1 == 0 and index != amount_in_row * amount_in_row and index != amount_in_row:
        checked = 1
        if data[index - 1] == 1:
            counter += 1
        if data[index - amount_in_row] == 1:
            counter += 1
        if data[index + amount_in_row] == 1:
            counter += 1
        if data[index - amount_in_row - 1] == 1:
            counter += 1
        if data[index + amount_in_row - 1] == 1:
            counter += 1

    # лево
    if index % amount_in_row == 0 and index != amount_in_row * amount_in_row - amount_in_row + 1 and index != 0:
        checked = 1
        if data[index + 1] == 1:
            counter += 1
        if data[index - amount_in_row] == 1:
            counter += 1
        if data[index + amount_in_row] == 1:
            counter += 1
        if data[index - amount_in_row + 1] == 1:
            counter += 1
        if data[index + amount_in_row + 1] == 1:
            counter += 1

    # остальное
    if checked == 0:
        if data[index + 1] == 1:
            counter += 1
        if data[index - 1] == 1:
            counter += 1
        if data[index - amount_in_row] == 1:
            counter += 1
        if data[index - amount_in_row - 1] == 1:
            counter += 1
        if data[index - amount_in_row + 1] == 1:
            counter += 1
        if data[index + amount_in_row] == 1:
            counter += 1
        if data[index + amount_in_row - 1] == 1:
            counter += 1
        if data[index + amount_in_row + 1] == 1:
            counter += 1

    game_data = game_data[:index] + str(counter) + game_data[index + 1:]
    print("COUNTER = ", counter)
    return game_data


zero_amount = 55
one_amount = 9

amount_of_items = get_amount_of_items(zero_amount, one_amount)
amount_of_items_in_row = (int(math.sqrt(amount_of_items)))

data = create_data(zero_amount, one_amount)
game_data = create_board(amount_of_items)

print_data(game_data)
index = get_x_y(amount_of_items_in_row)

if data[index] != 1:
    cls()
    game_data = open_bomb(data, game_data, index)

while data[index] != 1:
    cls()
    print_data(game_data)
    index = get_x_y(amount_of_items_in_row)
    if data[index] == 1:
        break

    game_data = open_bomb(data, game_data, index)
    print_data(game_data)

print("\n\n")
cls()
print_data(data)
print("\nGame Over")
