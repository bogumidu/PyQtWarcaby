import math

from globals import checker_size


class Field:
    def __init__(self, row=None, col=None, point=None):
        if point is not None:
            self.row = math.ceil(point.y() / checker_size)
            self.col = math.ceil(point.x() / checker_size)
            self.x = point.x()
            self.y = point.y()
        else:
            self.x = row * checker_size
            self.y = col * checker_size
        self.row = row
        self.col = col
        self.checker = None

    def get_pos(self):
        return self.x, self.y

    def is_playable(self):
        return (self.row + self.col) % 2 != 0  # zwraca tylko wspolrzedne zielonych pol