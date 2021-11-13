import sys
import math

from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5 import QtGui, QtCore

moved_checker = None
this_turn_of = "white"
board_size = 800
checker_size = int(board_size / 8)


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

class AvailablePosition(QLabel):
    def __init__(self, color, row, col, board):
        super(AvailablePosition, self).__init__(board)
        self.setPixmap(QPixmap(f"./graphic/available.png"))
        self.posx = col * checker_size
        self.posy = row * checker_size
        self.resize(checker_size, checker_size)
        self.move(self.posx, self.posy)
        self.show()


class Checker(QLabel):
    def __init__(self, color, row, col, field):
        super(Checker, self).__init__(field)
        self.color = color
        self.setPixmap(QPixmap(f"./graphic/{color}_checker.png"))
        self.field = field
        self.captured = False
        self.row = row
        self.col = col
        self.square = field.squares[row][col]
        self.posx = col * checker_size
        self.posy = row * checker_size
        self.resize(checker_size, checker_size)
        self.move(self.posx, self.posy, square=field.squares[row][col])

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.LeftButton:
            self.drag_start_position = event.pos()
            global moved_checker
            moved_checker = self

    def move(self, x=None, y=None, point=None, square=None):
        if point is not None:
            x = int(point.x())
            y = int(point.y())
        super().move(x, y)
        self.square.checker = None
        self.square = square
        self.square.checker = self
        self.row = square.row
        self.col = square.col

    def set_captured(self):
        self.captured = True
        self.hide()
        self.square.checker = None
        if self.color == "white":
            self.field.white_checkers.remove(self)
        elif self.color == "black":
            self.field.black_checkers.remove(self)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        if not (event.buttons() & QtCore.Qt.LeftButton):
            return
        if (event.pos() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return
        drag = QtGui.QDrag(self)
        mimedata = QtCore.QMimeData()
        mimedata.setData('Checker', bytearray('Checker', 'utf8'))
        mimedata.setProperty('offset', QPoint(event.x(), event.y()))
        drag.setMimeData(mimedata)
        drag.setDragCursor(QPixmap('./assets/emptyCursor.png'), QtCore.Qt.MoveAction)
        drag.setPixmap(self.pixmap())
        drag.setHotSpot(event.pos())
        self.hide()
        drag.exec_(Qt.CopyAction | Qt.MoveAction)


class Board(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setAcceptDrops(True)
        self.set_board()
        self.set_positions()
        self.set_checkers()
        self.available = []

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
                    self.black_checkers += [Checker('black', row, col, field=self)]
        for row in range(5, 8):
            for col in range(8):
                if self.squares[row][col].is_playable():
                    self.white_checkers += [Checker('white', row, col, field=self)]

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
            available_squares = self.get_available_squares(moved_checker.square)
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
            for square in self.get_available_squares(moved_checker.square):
                self.available += [AvailablePosition(moved_checker.color, square.row, square.col, self)]
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasFormat('Checker'):
            global this_turn_of
            mime = event.mimeData()
            checker_center_pos = event.pos() - mime.property('offset') + QPoint(50, 50)
            square = self.get_position(point=checker_center_pos)
            if this_turn_of == moved_checker.color and self.square_is_available(square):
                row, col = moved_checker.square.row, moved_checker.square.col
                moved_checker.move(point=event.pos() - mime.property('offset'), square=square)
                distance_y, distance_x = moved_checker.square.row - row, moved_checker.square.col - col
                if abs(distance_x) == 2 and abs(distance_y) == 2:
                    self.squares[row + distance_y // 2][col + distance_x // 2].checker.set_captured()
                this_turn_of = 'black' if this_turn_of == 'white' else 'white'
            moved_checker.show()
            event.setDropAction(QtCore.Qt.MoveAction)
            event.accept()
            if isinstance(self.available, list):
                for square in self.available:
                    square.hide()
            self.available = []
        else:
            event.ignore()


app = QApplication(sys.argv)
app.setApplicationName('PyQt Warcaby')
window = Board()
window.show()
sys.exit(app.exec_())
