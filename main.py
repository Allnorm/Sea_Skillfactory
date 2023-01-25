import random
import sys
import time


class SetShipException(Exception):
    pass


class PointOutException(Exception):
    pass


class PointFilledException(Exception):
    pass


class Field:
    __field = []
    __SIZE = 6

    def __init__(self):
        self.ship_sizes = [3, 2, 2, 1, 1, 1, 1]
        self.__alive_fields = sum(self.ship_sizes)
        self.clear_field()

    @property
    def alive_fields(self):
        return self.__alive_fields

    @property
    def field(self):
        return self.__field

    @property
    def size(self):
        return self.__SIZE

    def __str__(self):
        field_str = "  |" + "|".join([str(i + 1) for i in range(self.__SIZE)]) + "|"
        for i in range(self.__SIZE):
            field_str += "\n" + str(i + 1) + " |" + "|".join(self.field[i]) + "|"
        return field_str

    def get_cell_value(self, x, y):
        return self.field[x][y]

    def set_point(self, x, y):
        """ Set point if it possible """
        try:
            self.point_out(x, y)
        except PointOutException:
            raise PointOutException
        if self.field[x][y] not in ["-", "O"]:
            raise PointFilledException
        if self.field[x][y] == "O":
            self.field[x][y] = "X"
            self.__alive_fields -= 1
            return True
        else:
            self.field[x][y] = "^"
            return False

    def clear_field(self):
        self.__field = [["-" for _ in range(self.__SIZE)] for _ in range(self.__SIZE)]

    def point_out(self, x, y):
        if not (0 <= x <= self.__SIZE - 1 and 0 <= y <= self.__SIZE - 1):
            raise PointOutException

    def neighbor_chk(self, direction, x, y, first_cell):
        for i in range(x - 1, x + 2):
            for j in range(y - 1, y + 2):
                try:
                    self.point_out(i, j)
                except PointOutException:
                    continue
                if self.field[i][j] == "O":
                    if all([i == x - 1, not first_cell, direction == "right"]):
                        continue  # Костыль чтобы корабль не конфликтовал сам с собой
                    elif all([j == y - 1, not first_cell, direction == "down"]):
                        continue
                    else:
                        raise SetShipException

    def set_ship(self, ship_size, direction, x, y, first_cell=False):
        if ship_size == 0:
            return
        try:
            self.point_out(x, y)
            self.neighbor_chk(direction, x, y, first_cell)
        except (PointOutException, SetShipException):
            raise SetShipException
        if self.field[x][y] != "-":
            raise SetShipException
        self.field[x][y] = "O"
        try:
            if direction == "down":
                self.set_ship(ship_size - 1, direction, x, y + 1)
            else:
                self.set_ship(ship_size - 1, direction, x + 1, y)
        except SetShipException:
            self.field[x][y] = "-"
            raise SetShipException

    def set_ship_auto(self):
        for ship in self.ship_sizes:
            tries = 100
            installed = False
            while not installed:
                x = random.randint(0, self.__SIZE - 1)
                y = random.randint(0, self.__SIZE - 1)
                direction_list = ["down", "right"]
                random.shuffle(direction_list)
                for direction in direction_list:
                    try:
                        self.set_ship(ship, direction, x, y, first_cell=True)
                    except SetShipException:
                        tries -= 1
                        if tries <= 0:  # Регенерация поля
                            self.__field = [["-" for _ in range(self.__SIZE)] for _ in range(self.__SIZE)]
                            self.set_ship_auto()
                            return
                    else:
                        installed = True


class Player:
    _name = ""

    def __init__(self):
        self.__field = Field()

    def is_alive(self):
        if self.__field.alive_fields != 0:
            return True
        print(f"Игрок {self.name} победил! Игра окончена.")
        return False

    @property
    def name(self):
        return self._name

    @property
    def field(self):
        return self.__field


class AI(Player):
    _name = "AllnormZero"
    delay = 0

    def __init__(self):
        super().__init__()
        answer = ""
        while answer == "":
            try:
                answer = input("Укажите задержку вывода для AllnormZero (число от 0 до 10, по умолчанию 2): ")
                if answer == "":
                    answer = 2
                answer = int(answer)
                if not 0 <= answer <= 10:
                    raise ValueError
            except (TypeError, ValueError):
                answer = ""
                print("Неверное значение (должно быть числом от 0 до 10)")
        self.delay = answer
        self.field.set_ship_auto()
        print("Вот ваше поле:")
        print(self.field)

    def step(self):
        hit = True
        while hit:
            try:
                hit = self.field.set_point(random.randint(0, self.field.size - 1),
                                           random.randint(0, self.field.size - 1))
            except(PointOutException, PointFilledException):
                continue
            if hit:
                print("AllnormZero: ДОКЛАДЫВАЮ ОБ УСПЕШНОМ ПОПАДАНИИ! СМЕРТЬ ЧЕЛОВЕКАМ!")
                print(self.field)
                if self.field.alive_fields <= 0:
                    return
                time.sleep(self.delay)
        print("AllnormZero: ДОКЛАДЫВАЮ О НЕУДАЧНОМ ПОПАДАНИИ")
        print(self.field)
        time.sleep(self.delay)


class Human(Player):
    _name = "Человек"

    def __init__(self):
        super().__init__()
        answer = ""
        while answer == "":
            answer = input("Введите Ваше имя: ")
        self._name = answer
        print("Вашим противником будет наш Великий Интеллект по имени AllnormZero")
        self._name = answer
        self.__field = Field()
        self.field.set_ship_auto()
        print(f"AllnormZero: Я СГЕНЕРИРОВАЛ СВОЁ ПОЛЕ.")
        print('Краткий инструктаж молодого бойца:\n'
              '"-" - пустая клетка\n"X" - подбитая клетка\n"O" - корабль\n"^" - промах"')

    @staticmethod
    def hidden(field_str):
        return str(field_str).replace("O", "-")

    def step(self):
        print("Вот поле вашего врага:")
        hit = True
        while hit:
            print(self.hidden(self.field))
            print("  |" + "|".join(["^^" for _ in range(self.field.size)]) + "|")
            buffer_list = []
            for i in range(self.field.size):
                buffer_str = str(i + 1) + " |"
                for j in range(self.field.size):
                    cell_value = self.field.get_cell_value(i, j)
                    if cell_value in ["-", "O"]:
                        buffer_list.append((i, j))
                        buffer_str = buffer_str + f"{len(buffer_list):02}" + "|"
                    elif cell_value in ["^", "X"]:
                        buffer_str = buffer_str + self.field.field[i][j] * 2 + "|"
                print(buffer_str)
            num_choice = -1
            while not (len(buffer_list) > num_choice >= 0):
                num_choice = input("Выберите, куда нанести удар: ")
                try:
                    num_choice = int(num_choice) - 1
                except ValueError:
                    num_choice = -1
            try:
                hit = self.field.set_point(buffer_list[num_choice][0], buffer_list[num_choice][1])
            except(PointOutException, PointFilledException):  # Оно НИКОГДА не должно появиться
                print("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
                continue
            if hit:
                print("Вы попали!")
            if self.field.alive_fields <= 0:
                return
        print("Вы промахнулись...")


def game():
    human = Human()
    ai = AI()
    player_list = [human, ai]
    random.shuffle(player_list)
    play = True
    while play:
        for player in player_list:
            player.step()
            if not player.is_alive():
                play = False
                break
    print(f"Итоговое поле игрока {human.name}:\n{ai.field}")
    print(f"Итоговое поле AllnormZero:\n{human.field}")


def start():
    print("Приветствую на эпической битве!\nНа полях морских волн сойдутся Человек и Компьютер!")
    while True:
        game()
        if input("Ещё разок?)))) (Д/н): ").upper() in ["Н", "N"]:
            sys.exit()


if __name__ == "__main__":
    start()
