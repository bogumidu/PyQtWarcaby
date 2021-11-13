from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel

from globals import checker_size


class AvailablePosition(QLabel):
    def __init__(self, color, row, col, board):
        super(AvailablePosition, self).__init__(board)
        self.setPixmap(QPixmap(f"./graphic/available.png"))
        self.posx = col * checker_size
        self.posy = row * checker_size
        self.resize(checker_size, checker_size)
        self.move(self.posx, self.posy)
        self.show()