from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel


class Lab407Widget(QWidget):
    def __init__(self):
        self.image_label = QLabel()
        self.hbox = QHBoxLayout()
        self.hbox.addWidget(self.image_label)
        self.vbox = QVBoxLayout()
        self.hbox.addLayout(self.vbox)
        self.setLayout(self.hbox)

class Lab407Window(QMainWindow):

    def __init__(self):
        self.central = Lab407Widget()
        self.setCentralWidget(self.central)