from optics.optics_item import load_solid_iof
import numpy as np

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
    half_lambda_voltage = 1.5

    @classmethod
    def generate(cls):

        setup = cls()
        setup.lambda_light = (np.random.random_sample()*300 + 400)/1e6
        setup.crystal_length = (np.random.random_sample()*10 + 10)
        # setup.length
        setup.polaroid_zero = int(np.random.random_sample()*360)

        names = list(setup.iof.keys())
        n = len(names)
        n = np.random.random_integers(0, n)
        setup.material = names[n]
        return setup
