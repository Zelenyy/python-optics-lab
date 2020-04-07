from dataclasses import dataclass
from typing import Type

import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton
from PyQt5 import QtWidgets
from optics.optics_item import Diaphragm
from optics.work_407.work_407_window import Lab407Window


@dataclass
class Launcher:
    btn_name : str
    window_factory: Type
    window : QWidget = None


    def launch(self, push):
        if self.window is None:
            self.window = self.window_factory(self.btn_name)
        self.window.show()

class LabsWigget(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        vbox = QVBoxLayout()

        label = QLabel("Выберите лабораторную работу")

        labs = [
            Launcher("407: Эффект Поккельса", Lab407Window)
        ]

        vbox.addWidget(label)



        for lab in labs:
            btn = QPushButton(lab.btn_name)
            # btn.clicked.connect(lab.launch)
            btn.clicked.connect(lambda x: lab.launch(x))
            vbox.addWidget(btn)
        self.setLayout(vbox)
        vbox.addStretch()

class LabsWindow(QMainWindow):
    def __init__(self, args):
        super().__init__()
        self.central = LabsWigget()
        self.setCentralWidget(self.central)
        self.setMinimumSize(640, 480)




def main():
    theta = np.linspace(0.001, 20, 10000)
    theta =np.deg2rad(theta)
    dia = Diaphragm(300)
    ampl = np.abs(dia.fourier_spectrum_theta(theta, 0.4))
    inv = np.fft.ifft(ampl)
    # lens = Lens()
    # x = np.linspace(0,300, 300)
    # ampl = lens.fourier_view(x, 1900, dia.fourier_spectrum_theta, 0.4)
    # ampl = (lambda x: np.sin(x)/x )(theta)
    plt.subplots(1,2)
    plt.subplot(121)
    plt.plot(theta, ampl)
    plt.subplot(122)
    plt.plot(theta, np.abs(inv))
    # inv_m  =  np.abs(inv)
    # inv_m = np.abs(inv_m - inv_m.max())
    # plt.plot(theta,inv_m)
    # plt.plot(x, ampl)
    plt.show()
    plt.show()


