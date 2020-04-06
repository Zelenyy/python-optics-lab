import math
import math as m

import numpy as np


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
    alpha = math.radians(alpha)
    beta = math.radians(beta)
    return (math.sin(alpha - beta)**2)/(math.sin(alpha + beta)**2)


def fresnel_coefficients_p_r(alpha, beta):
    alpha = math.radians(alpha)
    beta = math.radians(beta)
    return (math.tan(alpha - beta)**2)/(math.tan(alpha + beta)**2)
