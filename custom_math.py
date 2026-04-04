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
        if self.position.x > 0 or (self.position.x + self.size.x) > 0 or self.position.y > 0 or (self.position.y + self.size.y) > 0:
            return Vector(
                random.randrange(self.position.x, self.position.x + self.size.x),
                random.randrange(self.position.y, self.position.y + self.size.y)
                )
    
        return Vector(1, 1)

    def get_center(self) -> Vector:
        center_x = self.position.x + self.size.x / 2
        center_y = self.position.y + self.size.y / 2
        return Vector(center_x, center_y)