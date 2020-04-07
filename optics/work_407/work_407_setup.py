from optics.optics_item import load_solid_iof


class Setup407:

    def __init__(self):
        self.iof = load_solid_iof()
        self.material = list(self.iof.keys())[0]

    length = 2000  # mm
    lambda_light: float = 0.4 * 1e-3  # micrometer
    crystal_length = 20  # mm
    n_air = 1
    n_ordinary = 1.5
    n_extra = 1.3
    laser_angle = 0  # degree
    polaroid_zero = 0