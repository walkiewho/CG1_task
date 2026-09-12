import tkinter as tk
from dataclasses import dataclass

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
        self.is_moving = False

    def move(self, d_x: int, d_y: int, v_x: int, v_y: int, delay: int = 50):
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

        step()


class Car(MoveableObject):
    cars_count = 0

    def __init__(self, center=Point(WIN_WIDTH // 2, WIN_HEIGHT // 2), size=100, color=Color(255, 0, 0)):
        super().__init__(center)

        self._color = color
        self._size = size
        self.car_index = Car.cars_count
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
            tags=f'Body-{self.car_index}'
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

        canvas.tag_bind(f'Body-{self.car_index}', "<Button-1>", ride_car)

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

    root.mainloop()


if __name__ == "__main__":
    main()
