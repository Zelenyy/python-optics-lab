import numpy as np
import matplotlib.pyplot as plt
from optics.work_405_window import Work405Window
from optics.optics_item import Diaphragm


def init():
    window = Work405Window()
    window.show()


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