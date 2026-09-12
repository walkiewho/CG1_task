
import tkinter as tk
from dataclasses import dataclass
from typing import override

WIN_WIDTH = 500
WIN_HEIGHT = 500
GROUND_LEVEL_Y = WIN_HEIGHT * 2 // 3
CAR_SIZE = 80


@dataclass
class Point:
    x: int
    y: int

    def __setattr__(self, name, value):
        if name == "x":
            value = min(max(0, value), WIN_WIDTH)
        elif name == "y":
            value = min(max(0, value), WIN_HEIGHT)
        super().__setattr__(name, value)

    def __add__(self, other: "Point") -> "Point":
        return Point(self.x + other.x, self.y + other.y)

    def __sub__(self, other: "Point") -> "Point":
        return Point(self.x - other.x, self.y - other.y)

    def distance(self, other):
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

@dataclass
class Color:
    r: int
    g: int
    b: int

    def __setattr__(self, attr, value):
        if attr in ("r", "g", "b", "a"):
            if not 0 <= value <= 255:
                raise ValueError(f"{attr} должен быть 0-255")
        super().__setattr__(attr, value)

    def to_hex(self):
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"


class MoveableObject:
    def __init__(self, center=Point(WIN_WIDTH // 2, WIN_HEIGHT // 2)):
        self.center: Point = center
        self._moveable_parts = []


    def animate(self, d_x: int, d_y: int, v_x: int, v_y: int, delay: int = 50):
        """
        Анимация плавного перемещения объекта.

        :param d_x: Целевая координата X (Destination X)
        :param d_y: Целевая координата Y (Destination Y)
        :param v_x: Скорость перемещения по X (пикселей за кадр)
        :param v_y: Скорость перемещения по Y (пикселей за кадр)
        :param delay: Задержка между кадрами в миллисекундах (по умолчанию 50 мс)
        """
        # Примечание: Если по задумке d_x и d_y — это смещение (дельта),
        # а не абсолютные координаты цели, замените эти две строки на:
        target_x = self.center.x + d_x
        target_y = self.center.y + d_y

        def step():
            # 1. Определяем направление движения к цели (-1, 0 или 1)
            dir_x = 1 if target_x > self.center.x else -1 if target_x < self.center.x else 0
            dir_y = 1 if target_y > self.center.y else -1 if target_y < self.center.y else 0

            # 2. Вычисляем шаг так, чтобы на последнем кадре не перескочить целевую точку
            step_x = dir_x * min(abs(target_x - self.center.x), abs(v_x))
            step_y = dir_y * min(abs(target_y - self.center.y), abs(v_y))

            # 3. Обновляем логические координаты центра
            # (Point.__setattr__ автоматически ограничит их пределами окна 0..WIN_WIDTH/HEIGHT)
            self.center.x += step_x
            self.center.y += step_y

            # 4. Сдвигаем все графические примитивы объекта на холсте
            for part in self._moveable_parts:
                canvas.move(part, step_x, step_y)

            # 5. Если цель еще не достигнута, планируем следующий кадр анимации
            if self.center.x != target_x or self.center.y != target_y:
                canvas.after(delay, step)

        # Запускаем первый шаг анимации
        step()


class Car(MoveableObject):
    def __init__(self, center=Point(WIN_WIDTH // 2, WIN_HEIGHT // 2), size=100, color=Color(255, 0, 0)):
        super().__init__(center)

        self._color = color
        self.size = size // 2
        self.draw()


    def draw(self):
        self._moveable_parts.append(canvas.create_rectangle(
                                            self.center.x - self.size,
                                            self.center.y - self.size // 2,
                                            self.center.x + self.size,
                                            self.center.y + self.size // 2,
                                            outline=self._color.to_hex(), fill=self._color.to_hex(),
                                            tags='BODY_CAR'
        ))
        self._moveable_parts.append(canvas.create_rectangle(
                                            self.center.x - self.size // 1.5,
                                            self.center.y - self.size * 1.2,
                                            self.center.x + self.size // 1.5,
                                            self.center.y - self.size // 2,
                                            outline=self._color.to_hex(), fill=self._color.to_hex()
        ))
        self._moveable_parts.append(canvas.create_rectangle(
                                            self.center.x + self.size // 5,
                                            self.center.y - self.size * 1.2,
                                            self.center.x + self.size // 1.5,
                                            self.center.y - self.size // 2,
                                            outline=self._color.to_hex(), fill='lightblue'
        ))
        self._moveable_parts.append(canvas.create_oval(
                                            self.center.x + self.size * 3 // 8,
                                            self.center.y + self.size * 1 // 4,
                                            self.center.x + self.size * 7 // 8,
                                            self.center.y + self.size * 3 // 4,
                                            outline='black', fill='gray', width=5
        ))
        self._moveable_parts.append(canvas.create_oval(
                                            self.center.x - self.size * 3 // 8,
                                            self.center.y + self.size * 1 // 4,
                                            self.center.x - self.size * 7 // 8,
                                            self.center.y + self.size * 3 // 4,
                                            outline='black', fill='gray', width=5
        ))

        def ride_car(event):
            if event.x > self.center.x:
                if self.center.x < WIN_WIDTH:
                    self.animate(50, 0, 5, 0)
            else:
                if self.center.x > 0:
                    self.animate(-50, 0, -5, 0)

        canvas.tag_bind("BODY_CAR", "<Button-1>", ride_car)

if __name__ == "__main__":
    # Tkinter
    root = tk.Tk()
    canvas = tk.Canvas(root, width=WIN_WIDTH, height=WIN_HEIGHT, bg="lightblue")
    canvas.pack()
    test = canvas.create_rectangle(0, GROUND_LEVEL_Y, WIN_WIDTH + 1, WIN_HEIGHT + 1, fill="lightgreen", outline='green', width=5)
    GROUND_HEIGHT = WIN_HEIGHT - GROUND_LEVEL_Y
    ROAD_LEVEL_CENTER = GROUND_LEVEL_Y + (WIN_HEIGHT - GROUND_LEVEL_Y) // 2

    print(GROUND_LEVEL_Y + WIN_HEIGHT // 6)
    print(WIN_HEIGHT - WIN_HEIGHT // 6, WIN_HEIGHT // 6)
    canvas.create_rectangle(0, GROUND_LEVEL_Y + (WIN_HEIGHT - GROUND_LEVEL_Y) // 4, WIN_WIDTH + 1, WIN_HEIGHT - (WIN_HEIGHT - GROUND_LEVEL_Y) // 4, fill="gray", outline='black', width=5)
    canvas.create_line(0, ROAD_LEVEL_CENTER, WIN_WIDTH + 1, ROAD_LEVEL_CENTER, dash=(10, 10), width=3, fill='yellow')
    canvas.create_oval(200, 50, 300, 150, outline="yellow", fill="yellow")


    # first car to move
    test_car = Car(center=Point(50, ROAD_LEVEL_CENTER), size=CAR_SIZE, color=Color(255, 80, 60))
    #test_car.animate(WIN_WIDTH, 0, 10, 0, delay=50)

    root.mainloop()
