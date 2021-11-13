from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel, QApplication

from globals import checker_size


class Checker(QLabel):
    def __init__(self, color, row, col, board):
        super(Checker, self).__init__(board)
        self.color = color
        self.setPixmap(QPixmap(f"./graphic/{color}_checker.png"))
        self.board = board
        self.captured = False
        self.row = row
        self.col = col
        self.square = board.squares[row][col]
        self.posx = col * checker_size
        self.posy = row * checker_size
        self.resize(checker_size, checker_size)
        self.move(self.posx, self.posy, square=board.squares[row][col])

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.LeftButton:
            self.drag_start_position = event.pos()
            self.board.moved_checker = self

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
            self.board.white_checkers.remove(self)
        elif self.color == "black":
            self.board.black_checkers.remove(self)

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