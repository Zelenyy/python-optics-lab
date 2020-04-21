from dataclasses import dataclass

import numpy as np
from diffractio import mm, nm, um, degrees
from diffractio.scalar_masks_XY import Scalar_mask_XY
from diffractio.scalar_sources_XY import Scalar_source_XY

from optics.load_setup import Setup


@dataclass
class Setup405(Setup):
    length : float = 2000 * mm  # mm
    lambda_light: float = 632 * nm  # micrometer

    focal1 : float = 100 * mm
    focal2 : float = 25 * mm
    grids : list = ((100 * um, 0.6),
             (70 * um, 0.5),
             (50 * um, 0.4),
             (20 * um, 0.3))

    @classmethod
    def generate(cls):

        setup = cls()
        setup.lambda_light = (np.random.random_sample()*300 + 400) * nm
        setup.length = (np.random.random_sample()*50 +  1750) * mm

        setup.focal1 =  (np.random.random_sample()*40 +  80) * mm
        setup.focal2 =  (np.random.random_sample()*10 +  20) * mm

        setup.grids = [(np.random.random_sample()*10 + 20*i, np.random.random_sample()) for i in range(6) ]

        return setup

    def source(self):
        length = 10 * mm
        num_data = 1024
        wavelength = self.lambda_light
        x0 = np.linspace(-length / 2, length / 2, num_data)
        y0 = np.linspace(-length / 2, length / 2, num_data)
        source = Scalar_source_XY(x=x0, y=y0, wavelength=wavelength)
        # source.plane_wave(phi=0 * degrees, theta=0 * degrees)

        source.gauss_beam(
            A=1,
            r0=(0 * um, 0 * um),
            z0=0,
            w0=(5 * mm, 5 * mm),
            phi=0 * degrees,
            theta=0 * degrees)

        return source

    def mask(self):
        length = 10 * mm
        num_data = 1024
        wavelength = self.lambda_light
        x0 = np.linspace(-length / 2, length / 2, num_data)
        y0 = np.linspace(-length / 2, length / 2, num_data)
        mask = Scalar_mask_XY(x=x0, y=y0, wavelength=wavelength)
        return mask