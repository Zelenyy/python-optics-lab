import math

import numpy as np
from scipy.stats import multivariate_normal

from optics.base_window import ImageCalculator
from optics.work_407.electric_field import ElectricField
from optics.work_407.work_407_setup import Setup407
from optics.optics_item import Scatter, Polaroid


class PokkelsIC(ImageCalculator):
    scatter: Scatter = None
    polaroid: Polaroid = None
    crystal = None
    diod = None
    field : ElectricField = None


    def __init__(self, setup: Setup407):
        self.setup = setup
        self.init_grid()
        self.full_size = 400 # mm
        self.k = 2 * np.pi / self.setup.lambda_light

        self.diff_phases_no_field = self.k * self.setup.crystal_length * (
                self.setup.n_ordinary - self.setup.n_extra) * (self.theta ** 2)

    def init_grid(self):

        self.x = np.arange(0.5, 200, 0.5)
        self.X, self.Y = np.meshgrid(self.x, self.x)
        self.phi = np.arctan(self.X / self.Y)
        r = np.sqrt(self.X ** 2 + self.Y ** 2)
        alpha = self.setup.n_ordinary / self.setup.n_air
        self.theta = r / (alpha * self.setup.length + self.setup.crystal_length)
        self.theta_out = np.arcsin(alpha * np.sin(self.theta))

        self.theta_ordinary = np.arcsin(r / (alpha * self.setup.length + self.setup.crystal_length))
        self.theta_ordinary_out = np.arcsin(alpha * np.sin(self.theta_ordinary))

        # self.theta_extra = self.find_extra_theta()


    def find_extra_theta(self):
        r = (2 ** 0.5) * self.x ** 2
        theta = np.zeros(r.size, "d")
        ratio = self.setup.n_ordinary / self.setup.n_extra
        const = self.setup.length * np.sqrt(ratio) / self.setup.n_air

        from scipy.optimize import root
        for indx, it in enumerate(r):
            def equation(x):
                a1 = self.setup.length * np.sin(x)
                a2 = const / np.sqrt(1 + ratio * (np.tan(x) ** 2))
                return (it - a1 - a2)

            theta[indx] = root(equation, np.arctan(it / self.setup.length)).x[0]
        return theta

    def wave_ordinary(self, ampl, theta, theta_out, phi):
        nc = self.setup.n_ordinary
        n_air = self.setup.n_air
        phases = self.k * (
                (self.setup.crystal_length * nc / np.cos(theta)) + (self.setup.length * n_air / np.cos(theta_out)))
        Ex = ampl * np.cos(phi)
        Ey = ampl * np.sin(phi)
        return Ex, Ey, phases

    def wave_extraordinary(self, ampl, theta, theta_out, phi):
        n_air = self.setup.n_air
        no = self.setup.n_ordinary
        ne = self.setup.n_extra
        cos_theta = np.cos(theta)
        n = 1 / ((cos_theta / no) ** 2 + (np.sin(theta) / ne) ** 2) ** 0.5
        phases = self.k * (
                (self.setup.crystal_length * n / np.cos(theta)) + (self.setup.length * n_air / np.cos(theta_out)))

        Ex = ampl * np.cos(phi) * cos_theta
        Ey = ampl * np.sin(phi) * cos_theta
        Ez = ampl * np.sin(theta)
        return Ex, Ey, phases, Ez

    def calculate(self)-> np.ndarray:
        if self.diod is None:
            return self.calculate_view()
        else:
            return self.calculate_osc()

    def calculate_osc(self)-> np.ndarray:
        ampl = 1.0
        u = self.field.value()
        if self.polaroid is not None:
            ul2 = self.setup.half_lambda_voltage
            phases = np.pi * u / (2 * ul2)
            laser_angle = math.radians(self.setup.laser_angle)
            Ex = ampl * np.cos(laser_angle)
            Ey = ampl * np.sin(laser_angle)
            sqrt2 = 2 ** 0.5
            E1 = (-Ex + Ey) / sqrt2
            E2 = (Ex + Ey) / sqrt2

            permitted_angle = math.radians(self.polaroid.angle())
            E1x = E1 * np.cos(3 * np.pi / 4 - permitted_angle)
            E1y = E1 * np.sin(3 * np.pi / 4 - permitted_angle)
            E2x = E2 * np.cos(np.pi / 4 - permitted_angle)
            E2y = E2 * np.sin(np.pi / 4 - permitted_angle)
            Ex = E1x + E2x * np.sin(phases)
            Ey = E1y + E2y * np.sin(phases)
            ampl = Ex ** 2 + Ey ** 2
            return ampl
        else:
            return np.ones(u.size)


    def calculate_view(self) -> np.ndarray:
        ampl = self.scatter.distribution(self.phi, self.theta)
        if self.field is None:
            if self.crystal is not None:
                laser_angle = math.radians(self.setup.laser_angle)
                Ex = ampl * np.cos(laser_angle)
                Ey = ampl * np.sin(laser_angle)

                ampl_o = (Ex * np.sin(self.phi) + Ey * np.cos(self.phi)) * np.cos(self.theta)
                ampl_e = (Ex * np.cos(self.phi) + Ey * np.sin(self.phi)) * np.cos(self.theta)

                Exo, Eyo, phases_o = self.wave_ordinary(ampl_o, self.theta, self.theta_out, self.phi)
                Exe, Eye, phases_e, Eze = self.wave_extraordinary(ampl_e, self.theta, self.theta_out, self.phi)

                Ex = Exo * np.sin(phases_o) + Exe * np.sin(phases_e)
                Ey = Eyo * np.sin(phases_o) + Eye * np.sin(phases_e)
                if self.polaroid is None:
                    ampl = ampl_e ** 2 + ampl_o ** 2
                    return self.repeat4(ampl)
                permitted_angle = math.radians(self.polaroid.angle())
                Ex = Ex * np.cos(permitted_angle)
                Ey = Ey * np.sin(permitted_angle)
                ampl = Ex ** 2 + Ey ** 2
                return self.repeat4(ampl)
            else:
                if self.polaroid is not None:
                    angle = self.setup.laser_angle - self.polaroid.angle()
                    ampl *= (math.cos(math.radians(angle)) ** 2)
                return self.repeat4(ampl)
        else:
            u = self.field.value()
            ul2 = self.setup.half_lambda_voltage
            phases = np.pi*u/(2*ul2)
            laser_angle = math.radians(self.setup.laser_angle)
            Ex = ampl * np.cos(laser_angle)
            Ey = ampl * np.sin(laser_angle)
            sqrt2 = 2**0.5
            # E1 = (Ex*np.cos(self.phi-np.pi/4) + Ey*np.sin(self.phi-np.pi/4))*np.cos(self.theta)
            # E2 = (Ex*np.cos(self.phi+np.pi/4) + Ey*np.sin(self.phi+np.pi/4))*np.cos(self.theta)
            E1 = (-Ex + Ey)/sqrt2
            E2 = (Ex + Ey)/sqrt2
            if self.polaroid is not None:
                permitted_angle = math.radians(self.polaroid.angle())
                E1x = E1*np.cos(3*np.pi/4 - permitted_angle)
                E1y = E1*np.sin(3*np.pi/4 - permitted_angle)
                E2x = E2*np.cos(np.pi/4 - permitted_angle)
                E2y = E2*np.sin(np.pi/4 -permitted_angle)
                Ex = E1x + E2x*np.sin(phases)
                Ey = E1y + E2y*np.sin(phases)
                ampl = Ex**2 + Ey**2
                return self.repeat4(ampl)

            return self.repeat4(ampl)

    def repeat4(self, ampl):
        ampl = np.vstack((ampl[::-1], ampl))
        ampl = np.hstack((ampl[:, ::-1], ampl))
        return ampl