import random

class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Rect:
    def __init__(self, position = Vector(0, 0), size = Vector(0, 0)):
        self.position = position
        self.size = size

    def get_random_point(self) -> Vector:
        return Vector(
            random.randrange(self.position.x, self.position.x + self.size.x),
            random.randrange(self.position.y, self.position.y + self.size.y)
            )