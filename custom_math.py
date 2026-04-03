
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Rect:
    def __init__(self, position = Vector(0, 0), size = Vector(0, 0)):
        self.position = position
        self.size = size
