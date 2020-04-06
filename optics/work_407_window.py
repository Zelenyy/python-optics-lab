import math

from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLayout, QGroupBox, QCheckBox, QSpinBox, \
    QFormLayout, QPushButton, QDialog, QLabel
import numpy as np
from scipy.stats import multivariate_normal
from matplotlib.figure import Figure
from matplotlib.backends.qt_compat import is_pyqt5

from optics.optics_item import fresnel_coefficients_s_r, fresnel_coefficients_p_r

if is_pyqt5():
    from matplotlib.backends.backend_qt5agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
else:
    from matplotlib.backends.backend_qt4agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)

from optics.base_window import WithImage, ImageCalculator
import matplotlib.pyplot as plt


class Setup407:

    length = 200 # mm
    lambda_light: float = 0.4 #micrometer
    crystal_length = 20 # mm
    n_air = 1
    n_ordinary = 1.5
    n_extra = 1.3
    laser_angle = 0 # degree
    polaroid_zero = 0

class Polaroid:
    def __init__(self, zero = 0):
        self.position = 0
        self.zero = zero

    def angle(self):
        return self.zero - self.position

class Scatter:

    def distribution(self, phi, theta):
        # return np.ones(theta.shape, "d")
        return np.cos(theta)**2


class PokkelsIC(ImageCalculator):

    scatter : Scatter = None
    polaroid: Polaroid = None

    def __init__(self, setup: Setup407):
        self.setup = setup
        # self.theta = np.linspace(0, 30, 300)
        # self.theta = np.deg2rad(self.theta)
        # self.phi = np.deg2rad(np.linspace(0, 90, 300))
        self.x = np.arange(0.5, 200, 0.5)
        # self.size = sefl.x.size
        self.X, self.Y = np.meshgrid(self.x, self.x)
        self.phi = np.arctan(self.X/self.Y)
        r = np.sqrt(self.X**2 + self.Y**2)
        alpha = self.setup.n_ordinary/self.setup.n_air
        self.theta = r/(alpha*self.setup.length+self.setup.crystal_length)
        self.theta_out = np.arcsin(alpha*np.sin(self.theta))
        # self.theta_out = np.arctan(r/self.setup.length)
        # self.theta = np.arcsin((self.setup.n_ordinary/self.setup.n_air)*np.sin(self.theta_out))
        self.k = 2*np.pi/self.setup.lambda_light
        self.phases_ordinary = self.k*((self.setup.crystal_length/np.cos(self.theta)) + (self.setup.length/np.cos(self.theta_out)))

        self.multynorm = multivariate_normal([0,0], [20,20])

    def phases_ordinary(self, theta, theta_out):
        return self.k*((self.setup.crystal_length/np.cos(theta)) + (self.setup.length/np.cos(theta_out)))

    def phases_extraordinary(self, theta, theta_out):
        pass

    def calculate(self) -> np.ndarray:
        if self.scatter is not None:
            scatter_ampl = self.scatter.distribution(self.phi, self.theta)
            diff_phases = self.k*self.setup.crystal_length*(self.setup.n_ordinary - self.setup.n_extra)*(self.theta**2)
            ampl = (scatter_ampl**2)*(1-np.cos(diff_phases))
            return self.repeat4(ampl)
        else:
            pos = np.empty(self.X.shape + (2,))
            pos[:, :, 0] = self.X
            pos[:, :, 1] = self.Y
            ampl = self.multynorm.pdf(pos)
            ampl /= ampl.max()
            if self.polaroid is not None:
                angle = self.setup.laser_angle - self.polaroid.angle()
                ampl *= (math.cos(math.radians(angle))**2)
            return self.repeat4(ampl)

    def caclualte_ordinary(self, phi, theta):
        phases = None

    def repeat4(self, ampl):
        ampl = np.vstack((ampl[::-1], ampl))
        ampl = np.hstack((ampl[:,::-1], ampl))
        return ampl


class AnalyzerZero(QDialog):
    def __init__(self, setup):
        super().__init__()
        self.setup = setup
        self.setWindowTitle("Поиск нуля анализатора")
        self.polaroid_angle = 0
        self.angle = 45

        hbox = QHBoxLayout()
        self.initMPLWidget(hbox)

        input = QSpinBox()
        input.setRange(0, 360)
        input.setValue(self.polaroid_angle)
        form = QFormLayout()
        form.addRow(QLabel("Материал отражающей поверхности: "))
        form.addRow("Угол анализатора, градусы: ", input)

        def change_polaroid_angle(angle):
            self.polaroid_angle = angle
            self.updateCanvas()
        input.valueChanged.connect(change_polaroid_angle)

        input = QSpinBox()
        input.setRange(0, 360)
        input.setValue(self.angle)

        def change_angle(angle):
            self.angle = angle
            self.updateCanvas()
        input.valueChanged.connect(change_angle)

        form.addRow("Угол отраженного света, градусы: ", input)
        hbox.addLayout(form)
        self.setLayout(hbox)
        self.updateCanvas()

    def calculate(self, angle, polaroid_angle):
        n12 = self.setup.n_air
        beta = math.asin(n12*math.sin(angle))
        Rs = fresnel_coefficients_s_r(angle, beta)
        Rp = fresnel_coefficients_p_r(angle, beta)
        permitted_direction = self.setup.polaroid_zero - polaroid_angle
        coeff = Rs*(math.cos(permitted_direction)**2) + Rp*(math.sin(permitted_direction)**2)
        return np.ones((10,10), "d")*coeff

    def initMPLWidget(self, layout):
        self.canvas = FigureCanvas(Figure(figsize=(5, 5)))
        layout.addWidget(self.canvas)
        self.ax = self.canvas.figure.subplots()

    def updateCanvas(self):
        self.ax.clear()
        ampl = self.calculate(self.angle, self.polaroid_angle)
        img = self.ax.matshow(ampl, cmap="Greys_r", vmin=0, vmax=1)
        # self.canvas.figure.colorbar(img)
        self.ax.set_axis_off()
        self.ax.figure.canvas.draw()


class Lab407Widget(QWidget):

    analyzer_zero = None

    def __init__(self):
        super().__init__()
        self.hbox = QHBoxLayout()
        self.vbox = QVBoxLayout()
        self.hbox.addLayout(self.vbox)
        self.setLayout(self.hbox)
        self.setup = Setup407()
        self.image_calculator = PokkelsIC(self.setup)
        self.initMPLWidget(self.hbox)
        self.initScatter(self.vbox)
        self.initPolaroid(self.vbox)
        self.updateCanvas()

    def initScatter(self, layout: QLayout):
        scatter = Scatter()

        ch_box = QCheckBox("Установить рассеивающую пластинку")


        def change_state(state: bool):
            if state:
                self.image_calculator.scatter = scatter
            else:
                self.image_calculator.scatter = None
            self.updateCanvas()
        ch_box.stateChanged.connect(change_state)
        layout.addWidget(ch_box)

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
        input.setRange(0,360)
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
        self.canvas = FigureCanvas(Figure(figsize=(10, 10)))
        layout.addWidget(self.canvas)
        self.ax = self.canvas.figure.subplots()

    def updateCanvas(self):
        self.ax.clear()
        ampl = self.image_calculator.calculate()
        img = self.ax.matshow(ampl, cmap="Greys_r", vmin=0, vmax=1)
        # self.canvas.figure.colorbar(img)
        self.ax.set_axis_off()
        self.ax.figure.canvas.draw()

class Lab407Window(QMainWindow):

    def __init__(self, name):
        super().__init__()
        self.central = Lab407Widget()
        self.setCentralWidget(self.central)
        self.setWindowTitle(name)



