import abc
import math
import math as m
from pathlib import Path

import numpy as np
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QDialog, QTextBrowser, QHBoxLayout, QTableView


class Lens:

    def __init__(self, focus = 100, position = 100):
        self.focus = focus # mm
        self.position = position # mm

    def focal_view(self, x: float, spectrum, lambda_light: float):
        k = 2 * m.pi / lambda_light
        theta = x/self.position
        spectrum = spectrum(theta, lambda_light)
        return spectrum/((self.focus**2)*(lambda_light**2))

    def screen_view(self, distance, focal_spectrum, x, lambda_light: float):
        k = 2 * m.pi / lambda_light
        result = np.zeros(x.size, dtype=np.complex64)
        distance2 = distance**2
        for ampl in focal_spectrum:
            phases = k*np.sqrt(x**2 + distance2)
            result += ampl*np.exp(1j*phases)
        return np.abs(result)


class Diaphragm:

    def __init__(self, width = 300):
        self.width = width

    def fourier_spectrum(self, u: float):
        temp = self.width * u / 2.0
        return self.width * np.sin(temp) / temp

    def fourier_spectrum_theta(self, theta: float, lambda_light: float):
        k = 2 * m.pi / lambda_light
        u = k * np.sin(theta)
        return self.fourier_spectrum(u)



def fresnel_coefficients_s_r(alpha, beta):
    return (math.sin(alpha - beta)**2)/(math.sin(alpha + beta)**2)


def fresnel_coefficients_p_r(alpha, beta):
    return (math.tan(alpha - beta)**2)/(math.tan(alpha + beta)**2)


def load_solid_iof():
    path = Path(__file__).parent / "data/iof.txt"
    data = {}
    with open(path) as fin:
        for line in fin.readlines():
            line = line.split()
            data[line[0]] = float(line[1])
    return data


class IOFTable(QDialog):
    def __init__(self,data: dict):
        super().__init__()
        self.table = QTableView()
        hbox = QHBoxLayout()
        self.setLayout(hbox)
        hbox.addWidget(self.table)
        sti = QStandardItemModel(parent=self)
        for key, value in data.items():
            sti.appendRow([QStandardItem(key), QStandardItem(str(value))])
        self.table.setModel(sti)
        self.setWindowTitle("Таблица показателей преломления")


class Scatter(abc.ABC):
    @abc.abstractmethod
    def distribution(self, phi, theta):
        pass


class Polaroid:
    def __init__(self, zero=0):
        self.position = 0
        self.zero = zero

    def angle(self):
        return self.zero - self.position