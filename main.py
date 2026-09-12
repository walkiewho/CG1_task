
import tkinter as tk
from dataclasses import dataclass


root = tk.Tk()

WIN_WIDTH = 1500
WIN_HEIGHT = 1500
canvas = tk.Canvas(root, width=WIN_WIDTH, height=WIN_HEIGHT, bg="white")
canvas.pack()

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
        self.__moveable_parts: list = []
        self.vx = 5
        self.vy = 0






class Car(MoveableObject):
    def __init__(self, center=Point(WIN_WIDTH // 2, WIN_HEIGHT // 2), size=200, color=Color(255, 0, 0)):
        super().__init__(center)

        self._color = color
        self.size = size // 2
        self.draw()

        # Parts
        self.__moveable_parts = [self._body, self._top, self._window, self._backward_wheel, self._forward_wheel]
        self._body = None
        self._top = None
        self._window = None
        self._backward_wheel = None
        self._forward_wheel = None

    def draw(self):
        self._body = canvas.create_rectangle(
                                            self.center.x - self.size,
                                            self.center.y - self.size // 2,
                                            self.center.x + self.size,
                                            self.center.y + self.size // 2,
                                            outline=self._color.to_hex(), fill=self._color.to_hex()
        )
        self._top = canvas.create_rectangle(
                                            self.center.x - self.size // 1.5,
                                            self.center.y - self.size * 1.2,
                                            self.center.x + self.size // 1.5,
                                            self.center.y - self.size // 2,
                                            outline=self._color.to_hex(), fill=self._color.to_hex()
        )
        self._window = canvas.create_rectangle(
                                            self.center.x + self.size // 5,
                                            self.center.y - self.size * 1.2,
                                            self.center.x + self.size // 1.5,
                                            self.center.y - self.size // 2,
                                            outline=self._color.to_hex(), fill='lightblue'
        )
        self._forward_wheel = canvas.create_oval(
                                            self.center.x + self.size * 3 // 8,
                                            self.center.y + self.size * 1 // 4,
                                            self.center.x + self.size * 7 // 8,
                                            self.center.y + self.size * 3 // 4,
                                            outline='black', fill='gray', width=5
        )
        self._backward_wheel = canvas.create_oval(
                                            self.center.x - self.size * 3 // 8,
                                            self.center.y + self.size * 1 // 4,
                                            self.center.x - self.size * 7 // 8,
                                            self.center.y + self.size * 3 // 4,
                                            outline='black', fill='gray', width=5
        )

    def animate(self):
        self.center += Point(self.vx, self.vy)
        if self.center.x < 1500:
            for part in self.__moveable_parts:
                canvas.move(part, self.vx, self.vy)
            root.after(50, self.animate)


GROUND_LEVEL_Y = WIN_HEIGHT * 2 // 3
canvas.create_rectangle(0, GROUND_LEVEL_Y, WIN_WIDTH + 1, WIN_HEIGHT + 1, fill="lightgreen", outline='green')
canvas.create_oval(200, 50, 300, 150, outline="yellow", fill="yellow")
print(Color(255, 0, 0).to_hex())
test_car = Car()
test_car.animate()
print(1)
root.mainloop()
