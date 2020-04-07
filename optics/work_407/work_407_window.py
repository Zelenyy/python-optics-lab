import numpy as np
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLayout, QGroupBox, QCheckBox, QSpinBox, \
    QFormLayout, QPushButton, QDoubleSpinBox, QLabel
from matplotlib.backends.qt_compat import is_pyqt5
from matplotlib.figure import Figure
from matplotlib.ticker import MultipleLocator
from scipy.stats import multivariate_normal

from optics.load_setup import load_setup
from optics.optics_item import Scatter, Polaroid
from optics.work_407.electric_field import ElectricField, EFState
from optics.work_407.work_407_physics import PokkelsIC
from optics.work_407.work_407_setup import Setup407
from optics.work_407.work_407_zero import AnalyzerZero

if is_pyqt5():
    from matplotlib.backends.backend_qt5agg import (
        FigureCanvas)

else:
    from matplotlib.backends.backend_qt4agg import (
        FigureCanvas)


class CosScatter(Scatter):

    def distribution(self, phi, theta):
        return np.cos(3*theta) ** 2


class GaussScatter(Scatter):

    def __init__(self):
        self.multynorm = multivariate_normal([0, 0], [20, 20])
        self.x = np.arange(0.5, 200, 0.5)
        self.X, self.Y = np.meshgrid(self.x, self.x)

    def distribution(self, phi, theta):
        pos = np.empty(self.X.shape + (2,))
        pos[:, :, 0] = self.X
        pos[:, :, 1] = self.Y
        ampl = self.multynorm.pdf(pos)
        ampl /= ampl.max()
        return ampl

class Lab407Widget(QWidget):
    analyzer_zero = None

    def __init__(self):
        super().__init__()
        self.hbox = QHBoxLayout()
        self.vbox = QVBoxLayout()

        self.setLayout(self.hbox)
        # self.setup = Setup407()
        self.setup = load_setup(Setup407)
        self.image_calculator = PokkelsIC(self.setup)
        self.initSetup(self.vbox)
        self.initMPLWidget(self.hbox)
        self.initCrystal(self.vbox)
        self.initScatter(self.vbox)
        self.initPolaroid(self.vbox)
        self.initField(self.vbox)
        self.initDiod(self.vbox)
        self.hbox.addLayout(self.vbox)
        self.vbox.addStretch()
        self.updateCanvas = self.updateCanvasView
        self.updateCanvas()

    def initSetup(self, layout):
        text = [
            "Длинна волны: {:.2f} нм".format(self.setup.lambda_light*1e6),
            "Длинная кристалла: {:.1f} мм".format(self.setup.crystal_length),
            "Растояние от кристала до экрана: {:d} см".format(int(self.setup.length/10)),
            "Показатель преломления обыкновенной волны: {:.5f}".format(self.setup.n_ordinary),
            "Полная длинна картины {}  мм".format(self.image_calculator.full_size)
        ]
        layout.addWidget(QLabel("\n".join(text)))

    def initField(self, layout):
        self.field =  ElectricField(9, EFState.DC)

        self.field_checkbox = QCheckBox("Включить блок питания")
        input = QDoubleSpinBox()
        input.setRange(0, self.field.U)
        input.setSingleStep(0.1)
        self.field.U = 0

        def set_field(state):
            input.setEnabled(state)
            if state:
                self.image_calculator.field = self.field
            else:
                self.image_calculator.field = None
            self.updateCanvas()

        self.field_checkbox.stateChanged.connect(set_field)

        def set_u(u:float):
            self.field.U = u
            self.updateCanvas()

        input.valueChanged.connect(set_u)
        gr_box = QGroupBox("Блок питания")
        form = QFormLayout()
        form.addRow(self.field_checkbox)
        form.addRow("Установить напряжение, В: ", input)
        gr_box.setLayout(form)
        layout.addWidget(gr_box)

    def initDiod(self, layout):
        ch_box = QCheckBox("Установить диод")

        def set_diod(state):
            self.field_checkbox.stateChanged.emit(True)
            self.field_checkbox.setDisabled(state)
            self.crys_box.setDisabled(state)
            self.sca_box.setDisabled(state)
            if state:
                # self.cha
                self.image_calculator.diod = True
                self.updateCanvas = self.updateCanvasOscilogramm
                self.field.state = EFState.AC
            else:
                self.image_calculator.diod = None
                self.updateCanvas = self.updateCanvasView
                self.field.state = EFState.DC
            self.updateCanvas()
        ch_box.stateChanged.connect(set_diod)
        layout.addWidget(ch_box)

    def initCrystal(self, layout):
        self.crys_box = QCheckBox("Установить кристал")

        def set_crystall(state):
            if state:
                self.image_calculator.crystal = True
            else:
                self.image_calculator.crystal = None
            self.updateCanvas()

        self.crys_box.stateChanged.connect(set_crystall)
        layout.addWidget(self.crys_box)

    def initScatter(self, layout: QLayout):
        cos_scatter = CosScatter()
        gauss_scatter = GaussScatter()
        self.image_calculator.scatter = gauss_scatter
        sca_box = QCheckBox("Установить рассеивающую пластинку")
        self.sca_box = sca_box
        def change_state(state: bool):
            if state:
                self.image_calculator.scatter = cos_scatter
            else:
                self.image_calculator.scatter = gauss_scatter
            self.updateCanvas()

        sca_box.stateChanged.connect(change_state)
        layout.addWidget(sca_box)

    def initPolaroid(self, layout):
        polaroid = Polaroid(self.setup.polaroid_zero)

        btn = QPushButton("Поиск нуля анализатора")

        def open_analyzer_zero(push):
            if self.analyzer_zero is None:
                self.analyzer_zero = AnalyzerZero(self.setup)
            self.analyzer_zero.show()

        btn.clicked.connect(open_analyzer_zero)

        gr_box = QGroupBox("Анализатор")
        ch_box = QCheckBox("Установить анализатор")
        input = QSpinBox()
        input.setRange(0, 360)
        input.setValue(polaroid.position)
        input.setDisabled(True)
        form = QFormLayout()
        form.addRow(btn)
        form.addRow(ch_box)
        form.addRow("Угол, градусы: ", input)
        gr_box.setLayout(form)

        def change_angle(angle: int):
            polaroid.position = angle
            self.updateCanvas()

        input.valueChanged.connect(change_angle)

        def change_state(state: bool):
            if state:
                self.image_calculator.polaroid = polaroid
            else:
                self.image_calculator.polaroid = None
            input.setEnabled(state)
            self.updateCanvas()

        ch_box.stateChanged.connect(change_state)
        layout.addWidget(gr_box)

    def initMPLWidget(self, layout):
        vbox = QVBoxLayout()
        self.canvas = FigureCanvas(Figure(figsize=(10, 10)))

        self.ax = self.canvas.figure.subplots()
        # vbox.addWidget(NavigationToolbar(self.canvas, self))
        vbox.addWidget(self.canvas)
        layout.addLayout(vbox)

    def updateCanvas(self):
        pass

    def updateCanvasView(self):
        self.ax.clear()
        ampl = self.image_calculator.calculate()
        img = self.ax.matshow(ampl, cmap="Greys_r", vmin=0, vmax=1)
        # self.canvas.figure.colorbar(img)
        self.ax.set_axis_off()
        self.ax.figure.canvas.draw()

    def updateCanvasOscilogramm(self):
        self.ax.clear()
        ampl = self.image_calculator.calculate()
        field = self.field.value()
        img = self.ax.scatter(field, 10*ampl, marker=".")
        # self.canvas.figure.colorbar(img)
        self.ax.grid(True)
        self.ax.set_xlim(0,9, auto = True)
        self.ax.set_ylim(0,10, auto = True)
        self.ax.xaxis.set_minor_locator(MultipleLocator(5))
        self.ax.yaxis.set_minor_locator(MultipleLocator(5))

        # self.ax.set_axis_off()
        self.ax.figure.canvas.draw()


class Lab407Window(QMainWindow):

    def __init__(self, name):
        super().__init__()
        self.central = Lab407Widget()
        self.setCentralWidget(self.central)
        self.setWindowTitle(name)
