import sys
from PyQt5 import QtWidgets, QtGui

from drop_analysis.gui import MainWindow


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('data/icon.ico'))
    main = MainWindow()

    main.show()
    sys.exit(app.exec_())
