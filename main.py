import sys

from PyQt5.QtWidgets import QApplication

from board import Board

app = QApplication(sys.argv)
app.setApplicationName('PyQt Warcaby')
window = Board()
window.show()
sys.exit(app.exec_())
