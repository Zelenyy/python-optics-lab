from dataclasses import dataclass

import numpy as np
from diffractio import mm, nm, um, degrees
from diffractio.scalar_masks_XY import Scalar_mask_XY
from diffractio.scalar_sources_XY import Scalar_source_XY

from optics.load_setup import Setup


@dataclass
class Setup512(Setup):
    length : float = 2000 * mm  # mm
    lambda_light_1: float = 632 * nm  # micrometer
    lambda_light_2: float = 532 * nm  # micrometer

    focal1 : float = 50 * mm
    focal2 : float = 100 * mm
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

        setup.grids = [( (np.random.random_sample()*10 + 20*i)* um, np.random.random_sample()) for i in range(6) ]

        return setup

    def source(self):
        length = 10 * mm
        num_data = 1024
        x0 = np.linspace(-length / 2, length / 2, num_data)
        y0 = np.linspace(-length / 2, length / 2, num_data)

        def get_source(wavelength, shift):
            source = Scalar_source_XY(x=x0, y=y0, wavelength=wavelength)
            # source.plane_wave(phi=0 * degrees, theta=0 * degrees)

            source.plane_wave(
                A=1,
                z0=0,
                phi=0 * degrees,
                theta=0 * degrees)

            mask = Scalar_mask_XY(x=x0, y=y0, wavelength=wavelength)
            mask.square(r0=(shift, 0), size=(0.45*mm, 10*mm), angle=0)
            return source*mask

        return get_source(self.lambda_light_1, -1000*um),  get_source(self.lambda_light_1, 1000*um)

    def mask(self):
        length = 10 * mm
        num_data = 1024
        wavelength = self.lambda_light_1
        x0 = np.linspace(-length / 2, length / 2, num_data)
        y0 = np.linspace(-length / 2, length / 2, num_data)
        mask = Scalar_mask_XY(x=x0, y=y0, wavelength=wavelength)
        return mask