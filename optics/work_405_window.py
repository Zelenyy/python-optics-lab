import numpy as np
from PyQt5 import QtWidgets
from PyQt5.QtGui import QImage, QPixmap

from optics.base_window import WithImage
from optics.optics_item import Lens, Diaphragm


class Setup405:
    length = 2000 # mm
    lambda_light: float = 0.4 #micrometer

class EMPoint:
    def __init__(self, ampl: float, phases: float):
        self.ampl = ampl
        self.phases = phases

    def value(self):
        return self.ampl*np.exp(1j*self.phases)

    @classmethod
    def from_value(cls, value):
        return cls(np.abs(value), np.angle(value))

    def __add__(self, other):
        v1 = self.value()
        v2 = other.value()
        return EMPoint.from_value(v1+v2)

def phases_from_point(theta, distance: float):
    return distance/np.cos(theta)


def image_from_2darray(data : np.ndarray):
    data = data.astype(np.uint8)
    width = data.shape[1]
    height = data.shape[0]
    return QImage(data.tobytes(), width, height, QImage.Format_Grayscale8)


class ImageCalculator:
    diaphragm : Diaphragm = None
    lens1 : Lens = None
    lens2 : Lens = None

    def __init__(self, setup: Setup405):
        self.setup = setup
        self.screen = np.linspace(0.1, 320, 320, endpoint=True)

    def calculate(self) -> QImage:
        if self.diaphragm is None:
            pass
        else:
            if self.lens1 is None and self.lens2 is None:
                return self._calculate_only_diaphragm()
            elif self.lens1 is not None and self.lens2 is None:
                return self._calualte_2()

    def _calculate_only_diaphragm(self):
        L = self.setup.length # mm
        theta = np.arctan(self.screen/L)
        spectrum = self.diaphragm.fourier_spectrum_theta(theta, self.setup.lambda_light)
        return self.oned_to_2d(spectrum**2)

    def oned_to_2d(self, data):
        data = np.log10(data+1)
        step = (data.max() - data.min())/(2**8)
        data /= step
        data -= 1
        data = np.hstack((data[::-1], data))
        data = np.tile(data, (480,1))
        return image_from_2darray(data)

    def _calualte_2(self):
        spectrum = self.diaphragm.fourier_spectrum_theta
        z = self.setup.length - self.lens1.position
        spectrum = self.lens1.focal_view(self.screen, spectrum, self.setup.lambda_light)
        spectrum = self.lens1.screen_view(z, spectrum, self.screen, self.setup.lambda_light)
        return self.oned_to_2d(spectrum)


class Work405Window(QtWidgets.QWidget, WithImage):

    def init_diaphragm(self, form):
        diaphragm = Diaphragm()
        dia_btn = QtWidgets.QCheckBox()
        widthInput = QtWidgets.QSpinBox()
        widthInput.setRange(10, 1000)
        widthInput.setSingleStep(10)
        widthInput.setValue(diaphragm.width)
        widthInput.setDisabled(True)

        def widthChanged(width: int):
            diaphragm.width = width
            self.updateImage()

        widthInput.valueChanged.connect(widthChanged)

        def setup_dia(state: bool):
            widthInput.setEnabled(state)
            if state:
                self.image_calculator.diaphragm = diaphragm
            else:
                self.image_calculator.diaphragm = None
            self.updateImage()

        dia_btn.stateChanged.connect(setup_dia)

        form.addRow("Поставить щель", dia_btn)
        form.addRow("Ширина щели: ", widthInput)


    def init_lens(self, form):
        lens = Lens(100)
        lens_btn = QtWidgets.QCheckBox()
        posInput = QtWidgets.QSpinBox()
        posInput.setRange(10, int(self.setup.length/10))
        posInput.setSingleStep(1)
        posInput.setValue(0)
        posInput.setDisabled(True)

        def posChanged(position: int):
            lens.position = position*10
            self.updateImage()

        posInput.valueChanged.connect(posChanged)

        def setup_lens(state: bool):
            posInput.setEnabled(state)
            if state:
                self.image_calculator.lens1 = lens
            else:
                self.image_calculator.lens1 = None
            self.updateImage()

        lens_btn.stateChanged.connect(setup_lens)

        form.addRow("Поставить линзу", lens_btn)
        form.addRow("Положение линзы, см", posInput)

    def init_description(self, form):
        btn = QtWidgets.QPushButton(
            """
            Открыть
            Описание
            Работы
            """
        )
        btn.setStyleSheet(
            """
            QPushButton {
            font: bold 16px;
            }
            """
        )
        form.addRow(btn)
        text = [
            "Maсштаб: 1px = 1 миллиметр",
            "Длинна волны света: {} нм".format(self.setup.lambda_light*1000)

        ]
        label = QtWidgets.QLabel(
            "\n".join(text)
        )
        label.setStyleSheet(
            """
            QLabel {
            font: bold 16px;
            }
            """
        )
        form.addRow(label)

    def init_controls(self):
        form = QtWidgets.QFormLayout()
        self.vbox.addLayout(form)
        self.init_description(form)
        self.init_diaphragm(form)
        self.init_lens(form)


    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setup = Setup405()
        self.image_calculator = ImageCalculator(self.setup)
        self.image_label = QtWidgets.QLabel()
        self.hbox = QtWidgets.QHBoxLayout()
        self.hbox.addWidget(self.image_label)
        self.vbox = QtWidgets.QVBoxLayout()
        self.hbox.addLayout(self.vbox)
        self.setLayout(self.hbox)
        self.init_controls()


    # def randomFill(self):
    #     rnd = np.random.randint(0,256)
    #     color = QColor(rnd)
    #     self.image.fill(color)
    #     self.updateImage()

