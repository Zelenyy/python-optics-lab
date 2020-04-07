import math

import numpy as np
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QSpinBox, QFormLayout, QLabel, QPushButton
from matplotlib.figure import Figure
from scipy.stats import multivariate_normal

from optics.optics_item import IOFTable, fresnel_coefficients_s_r, fresnel_coefficients_p_r

from matplotlib.backends.qt_compat import is_pyqt5
if is_pyqt5():
    from matplotlib.backends.backend_qt5agg import (
        FigureCanvas)

else:
    from matplotlib.backends.backend_qt4agg import (
        FigureCanvas)

class AnalyzerZero(QDialog):
    def __init__(self, setup):
        super().__init__()
        self.setup = setup
        self.setWindowTitle("Поиск нуля анализатора")
        self.polaroid_angle = 0
        self.angle = 30
        self.n2 = self.setup.iof[self.setup.material]
        hbox = QHBoxLayout()
        self.max_int = 1
        self.initMPLWidget(hbox)

        input = QSpinBox()
        input.setRange(0, 360)
        input.setValue(self.polaroid_angle)
        form = QFormLayout()
        form.addRow(QLabel("Материал отражающей поверхности: {}".format(self.setup.material)))
        form.addRow("Угол анализатора, градусы: ", input)

        def change_polaroid_angle(angle):
            self.polaroid_angle = angle
            self.updateCanvas()

        input.valueChanged.connect(change_polaroid_angle)

        input = QSpinBox()
        input.setRange(10, 80)
        input.setValue(self.angle)

        def change_angle(angle):
            self.angle = angle
            self.updateCanvas()

        input.valueChanged.connect(change_angle)

        form.addRow("Угол отраженного света, градусы: ", input)

        btn = QPushButton("Открыть таблицу показателей преломления")
        self.table = None

        def open_table(push):
            if self.table is None:
                self.table = IOFTable(self.setup.iof)
            self.table.show()

        btn.clicked.connect(open_table)
        form.addRow(btn)
        hbox.addLayout(form)

        self.n12 = self.setup.n_air / self.n2
        self.calibrate()
        self.multynorm = multivariate_normal([0, 0], [20, 20])
        self.setLayout(hbox)
        self.updateCanvas()

    def calibrate(self):
        angle = np.deg2rad(np.arange(10.0, 81.0))
        beta = np.arcsin(self.n12 * np.sin(angle))
        Rs = np.vectorize(fresnel_coefficients_s_r)(angle, beta)
        Rp = np.vectorize(fresnel_coefficients_p_r)(angle, beta)
        Rs = Rs.max()
        Rp = Rp.max()
        self.max_int = math.log(1 + max([Rs, Rp]))

    def calculate(self, angle, polaroid_angle):
        angle_r = math.radians(angle)
        beta = math.asin(self.n12 * math.sin(angle_r))
        Rs = fresnel_coefficients_s_r(angle_r, beta)
        Rp = fresnel_coefficients_p_r(angle_r, beta)
        permitted_direction = self.setup.polaroid_zero - polaroid_angle
        permitted_direction = math.radians(permitted_direction)
        coeff = Rp * (math.cos(permitted_direction) ** 2) + Rs * (math.sin(permitted_direction) ** 2)
        # x = np.linspace(0,100, 300)
        # X, Y = np.meshgrid(x,x)
        # ampl = self.multynorm.pdf([X, Y])
        # ampl /= ampl.max()
        ampl = np.zeros((10, 10), "d")
        ampl[3:7, 3:7] = 1.0
        return np.log(1 + ampl * coeff)

    def initMPLWidget(self, layout):
        self.canvas = FigureCanvas(Figure(figsize=(5, 5)))
        layout.addWidget(self.canvas)
        self.ax = self.canvas.figure.subplots()

    def updateCanvas(self):
        self.ax.clear()
        ampl = self.calculate(self.angle, self.polaroid_angle)
        img = self.ax.matshow(ampl,
                              cmap="Greys_r",
                              vmin=0, vmax=self.max_int)
        # self.canvas.figure.colorbar(img)
        self.ax.set_axis_off()
        self.ax.figure.canvas.draw()