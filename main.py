import sys

from PyQt5 import QtWidgets

from optics.init_window import init

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    init()
    sys.exit(app.exec_())