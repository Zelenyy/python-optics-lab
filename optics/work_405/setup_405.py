from dataclasses import dataclass

import numpy as np
from diffractio import mm, nm, um, degrees
from diffractio.scalar_masks_XY import Scalar_mask_XY
from diffractio.scalar_sources_XY import Scalar_source_XY

from optics.load_setup import Setup


@dataclass
class Setup405(Setup):
    length = 2000 * mm  # mm
    lambda_light: float = 632 * nm  # micrometer

    focal1 = 100 * mm
    focal2 = 25 * mm
    grids = [(100 * um, 0.6),
             (70 * um, 0.5),
             (50 * um, 0.4),
             (20 * um, 0.3)]

    def generate(self):
        return Setup405()

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