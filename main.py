import tkinter as tk
from dataclasses import dataclass
import random

WIN_WIDTH = 900
WIN_HEIGHT = 900
GROUND_LEVEL_Y = WIN_HEIGHT * 2 // 3
ROAD_LEVEL_CENTER = GROUND_LEVEL_Y + (WIN_HEIGHT - GROUND_LEVEL_Y) // 2
CAR_SIZE = 80
canvas: tk.Canvas


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
        if attr in ("r", "g", "b"):
            if not 0 <= value <= 255:
                raise ValueError(f"{attr} должен быть 0-255")
        super().__setattr__(attr, value)

    def to_hex(self):
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"


class MoveableObject:
    def __init__(self, center=Point(WIN_WIDTH // 2, WIN_HEIGHT // 2)):
        self.center: Point = center
        self._moveable_parts = []
        self.is_moving = False

    def move(self, d_x: int, d_y: int, v_x: int, v_y: int, delay: int = 50, on_complete=None):
        self.is_moving = True
        target_x = self.center.x + d_x
        target_y = self.center.y + d_y

        def step():
            dir_x = 1 if target_x > self.center.x else -1 if target_x < self.center.x else 0
            dir_y = 1 if target_y > self.center.y else -1 if target_y < self.center.y else 0

            step_x = dir_x * min(abs(d_x), abs(v_x))
            step_y = dir_y * min(abs(d_y), abs(v_y))

            self.center.x += step_x
            self.center.y += step_y

            for part in self._moveable_parts:
                canvas.move(part, step_x, step_y)

            if self.center.x != target_x or self.center.y != target_y:
                canvas.after(delay, step)
            else:
                self.is_moving = False
                if on_complete:
                    on_complete()

        step()


class Car(MoveableObject):
    cars_count = 0

    def __init__(self, center=Point(WIN_WIDTH // 2, WIN_HEIGHT // 2), size=100, color=Color(255, 0, 0)):
        super().__init__(center)

        self._color = color
        self._size = size
        self.__car_index = Car.cars_count
        Car.cars_count += 1
        self._window = None
        self.draw()

    def draw(self):
        self._moveable_parts.append(canvas.create_rectangle(
            self.center.x - self._size,
            self.center.y - self._size // 2,
            self.center.x + self._size,
            self.center.y + self._size // 2,
            outline=self._color.to_hex(), fill=self._color.to_hex(),
            tags=f'Car-{self.__car_index}'
        ))
        self._moveable_parts.append(canvas.create_rectangle(
            self.center.x - self._size // 1.5,
            self.center.y - self._size * 1.2,
            self.center.x + self._size // 1.5,
            self.center.y - self._size // 2,
            outline=self._color.to_hex(), fill=self._color.to_hex()
        ))
        self._window = canvas.create_rectangle(
            self.center.x + self._size // 5,
            self.center.y - self._size * 1.2,
            self.center.x + self._size // 1.5,
            self.center.y - self._size // 2,
            outline=self._color.to_hex(), fill='lightblue'
        )
        self._moveable_parts.append(self._window)
        self._moveable_parts.append(canvas.create_oval(
            self.center.x + self._size * 3 // 8,
            self.center.y + self._size * 1 // 4,
            self.center.x + self._size * 7 // 8,
            self.center.y + self._size * 3 // 4,
            outline='black', fill='gray', width=5
        ))
        self._moveable_parts.append(canvas.create_oval(
            self.center.x - self._size * 3 // 8,
            self.center.y + self._size * 1 // 4,
            self.center.x - self._size * 7 // 8,
            self.center.y + self._size * 3 // 4,
            outline='black', fill='gray', width=5
        ))

        def ride_car(event):
            if self.is_moving:
                return
            if event.x > self.center.x:
                self.move_window_forward()
                if self.center.x < WIN_WIDTH:
                    self.move(50, 0, 5, 0)
            else:
                self.move_window_backward()
                if self.center.x > 0:
                    self.move(-50, 0, -5, 0)

        canvas.tag_bind(f'Car-{self.__car_index}', "<Button-1>", ride_car)

    def move_window_forward(self):
        canvas.coords(self._window,
                      self.center.x + self._size // 5,
                      self.center.y - self._size * 1.2,
                      self.center.x + self._size // 1.5,
                      self.center.y - self._size // 2)

    def move_window_backward(self):
        canvas.coords(self._window,
                      self.center.x - self._size // 5,
                      self.center.y - self._size * 1.2,
                      self.center.x - self._size // 1.5,
                      self.center.y - self._size // 2)


class Rocket(MoveableObject):
    rocket_count = 0

    def __init__(self, center=Point(WIN_WIDTH // 2, WIN_HEIGHT // 2), size=100, color=Color(255, 0, 0), long_nose=False, epileptic=False):
        super().__init__(center)
        self._start_height = center.y
        self._height = None
        self._size = size
        self._color = color
        self.__rocket_index = Rocket.rocket_count
        Rocket.rocket_count += 1
        self.__long_nose = long_nose
        self._body = None
        self.draw()
        self.is_flight = False
        self._falling = False
        self._vy = 0
        self._gravity = 1
        self._fall_delay = 30
        if epileptic:
            self.change_color(1000)

    def draw(self):
        self._body = canvas.create_rectangle(
            self.center.x - self._size // 4,
            self.center.y - self._size,
            self.center.x + self._size // 4,
            self.center.y + self._size,
            outline='black', fill=self._color.to_hex(),
            tags=f'Rocket-{self.__rocket_index}'
        )
        self._moveable_parts.append(self._body)
        self._moveable_parts.append(canvas.create_polygon(
            self.center.x - self._size // 4,
            self.center.y + self._size,
            self.center.x - self._size // 4,
            self.center.y + self._size // 2,
            self.center.x - self._size // 4 - self._size // 2,
            self.center.y + self._size,
            outline='black', fill='gray'
        ))

        self._moveable_parts.append(canvas.create_polygon(
            self.center.x + self._size // 4,
            self.center.y + self._size,
            self.center.x + self._size // 4,
            self.center.y + self._size // 2,
            self.center.x + self._size // 4 + self._size // 2,
            self.center.y + self._size,
            outline='black', fill='gray'
        ))

        self._moveable_parts.append(canvas.create_polygon(
            self.center.x - self._size // 4,
            self.center.y - self._size,
            self.center.x + self._size // 4,
            self.center.y - self._size,
            self.center.x,
            self.center.y - self._size - int(3 ** 0.5 * self._size / (0.07 if self.__long_nose else 3)),
            outline='black', fill='gray'
        ))

        def flight(event):
            if self.is_moving:
                return

            # если ракета уже падала — остановим старый цикл падения
            self._falling = False
            self._vy = 0

            # после подъёма начнётся падение
            self.move(0, -50, 0, 5, on_complete=self.start_fall)

        canvas.tag_bind(f'Rocket-{self.__rocket_index}', "<Button-1>", flight)

    def start_fall(self):
        if self.is_moving or self._falling:
            return
        self._falling = True
        self._fall_step()

    def _fall_step(self):
        if not self._falling:
            return

        if self.is_moving:
            canvas.after(self._fall_delay, self._fall_step)
            return

        self._vy += self._gravity
        dy = self._vy

        floor_y = GROUND_LEVEL_Y - self._size

        if self.center.y + dy >= floor_y:
            dy = floor_y - self.center.y
            self.center.y = floor_y

            for part in self._moveable_parts:
                canvas.move(part, 0, dy)

            self._vy = 0
            self._falling = False
            return

        self.center.y += dy
        for part in self._moveable_parts:
            canvas.move(part, 0, dy)

        canvas.after(self._fall_delay, self._fall_step)

    def change_color(self, delay):

        def inner_timer():
            new_color = Color(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

            canvas.itemconfig(self._body, fill=new_color.to_hex())

            canvas.after(delay + 271 * self.__rocket_index, inner_timer)
        inner_timer()

    @property
    def height(self):
        return self.center.y - self._size




def main():
    global canvas
    # Tkinter
    root = tk.Tk()
    canvas = tk.Canvas(root, width=WIN_WIDTH, height=WIN_HEIGHT, bg="lightblue")
    canvas.pack()

    # ground
    canvas.create_rectangle(0, GROUND_LEVEL_Y, WIN_WIDTH + 1, WIN_HEIGHT + 1, fill="lightgreen", outline='green',
                            width=5)

    # road
    canvas.create_rectangle(0, GROUND_LEVEL_Y + (WIN_HEIGHT - GROUND_LEVEL_Y) // 4, WIN_WIDTH + 1,
                            WIN_HEIGHT - (WIN_HEIGHT - GROUND_LEVEL_Y) // 4, fill="gray", outline='black', width=5)
    canvas.create_line(0, ROAD_LEVEL_CENTER, WIN_WIDTH + 1, ROAD_LEVEL_CENTER, dash=(10, 10), width=3, fill='yellow')

    # sun
    canvas.create_oval(200, 50, 300, 150, outline="yellow", fill="yellow")

    # first car
    Car(center=Point(CAR_SIZE, ROAD_LEVEL_CENTER), size=CAR_SIZE, color=Color(255, 80, 60))

    # second car
    Car(center=Point(WIN_WIDTH - CAR_SIZE, ROAD_LEVEL_CENTER), size=CAR_SIZE // 2, color=Color(0, 0, 255))

    # first rocket
    Rocket(center=Point(WIN_WIDTH // 3 * 2, GROUND_LEVEL_Y - CAR_SIZE), size=CAR_SIZE)

    Rocket(center=Point(WIN_WIDTH // 3, GROUND_LEVEL_Y - CAR_SIZE // 2), size=CAR_SIZE // 2, color=Color(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), long_nose=False, epileptic=True)

    root.mainloop()


if __name__ == "__main__":
    main()
