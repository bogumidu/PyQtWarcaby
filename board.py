import math

from PyQt5 import QtCore
from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QLabel

from available_position import AvailablePosition
from checker import Checker
from field import Field
from globals import checker_size, board_size


class Board(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setAcceptDrops(True)
        self.set_board()
        self.set_positions()
        self.set_checkers()
        self.available = []
        self.moved_checker = None
        self.this_turn_of = "white"

    def set_board(self):
        self.fieldLabel = QLabel(self)  # definiuje widget jako label
        self.fieldLabel.setScaledContents(True)  # pozwala na skalowanie grafiki
        self.fieldLabel.setPixmap(QPixmap('./graphic/field.png'))  # ustawia label jako grafike
        self.fieldLabel.setGeometry(0, 0, board_size, board_size)  # ustawia wielkosc okna i grafiki

    def set_positions(self):
        self.squares = [[Field(row, col) for col in range(8)] for row in range(8)]

    def set_checkers(self):
        self.white_checkers = []
        self.black_checkers = []
        for row in range(0, 3):
            for col in range(8):
                if self.squares[row][col].is_playable():
                    self.black_checkers += [Checker('black', row, col, board=self)]
        for row in range(5, 8):
            for col in range(8):
                if self.squares[row][col].is_playable():
                    self.white_checkers += [Checker('white', row, col, board=self)]

    def get_position(self, row=None, col=None, point=None):
        if point is not None:
            row = int(math.ceil(point.y() / checker_size) - 1)
            col = int(math.ceil(point.x() / checker_size) - 1)
        return self.squares[row][col]

    def remove_checker(self, checker):
        pass

    def get_available_squares(self, square):
        available_squares = [square]
        row, col = square.row, square.col
        available_squares += [self.squares[row + y][col + x] for x in (2, 1, -1, -2) for y in (2, 1, -1, -2)
                              if row + y in range(8) and col + x in range(8) and ((row + y) + (col + x)) % 2 != 0]
        return available_squares

    def square_is_available(self, square):
        if (square.row + square.col) % 2 == 0:
            return False
        if square.checker is not None:
            return False
        else:
            available_squares = self.get_available_squares(self.moved_checker.square)
            if square in available_squares:
                return True
        return False

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('Checker'):
            event.setDropAction(QtCore.Qt.MoveAction)
            event.accept()
            if isinstance(self.available, list):
                for square in self.available:
                    square.hide()
            self.available = []
            for square in self.get_available_squares(self.moved_checker.square):
                self.available += [AvailablePosition(self.moved_checker.color, square.row, square.col, self)]
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasFormat('Checker'):
            mime = event.mimeData()
            checker_center_pos = event.pos() - mime.property('offset') + QPoint(50, 50)
            square = self.get_position(point=checker_center_pos)
            distance_y, distance_x = square.row - self.moved_checker.square.row, square.col - self.moved_checker.square.col
            if self.this_turn_of == self.moved_checker.color and self.square_is_available(square) and \
                    ((abs(distance_y) == 2 and abs(distance_x) == 2 and
                      self.squares[self.moved_checker.square.row + distance_y // 2][self.moved_checker.square.col + distance_x // 2].checker is not None) or
                     (abs(distance_y) == 1 and abs(distance_x) == 1)) :
                row, col = self.moved_checker.square.row, self.moved_checker.square.col
                self.moved_checker.move(point=event.pos() - mime.property('offset'), square=square)
                if abs(distance_x) == 2 and abs(distance_y) == 2:
                    self.squares[row + distance_y // 2][col + distance_x // 2].checker.set_captured()
                self.this_turn_of = 'black' if self.this_turn_of == 'white' else 'white'
            self.moved_checker.show()
            event.setDropAction(QtCore.Qt.MoveAction)
            event.accept()
            if isinstance(self.available, list):
                for square in self.available:
                    square.hide()
            self.available = []
        else:
            event.ignore()