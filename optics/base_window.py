from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QLabel


class ImageCalculator:

    def calculate(self) -> QImage:
        pass

class WithImage:
    image : QImage = None
    image_label : QLabel = None
    image_calculator : ImageCalculator = None

    def initImage(self, layout):
        self.image_label = QLabel()
        layout.addWidget(self.image_label)


    def updateImage(self):
        self.image = self.image_calculator.calculate()
        self.image_label.setPixmap(QPixmap.fromImage(self.image))