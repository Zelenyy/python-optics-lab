import sys

from PyQt5 import QtWidgets

from optics.init_window import LabsWindow

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = LabsWindow(sys.argv)
    window.show()
    sys.exit(app.exec_())