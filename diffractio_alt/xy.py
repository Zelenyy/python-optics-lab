
import abc
from dataclasses import dataclass
import numpy as np

@dataclass
class Field2D:
    x: np.ndarray
    y: np.ndarray
    field : np.ndarray
    wavelength : float

    @property
    def intensity(self):
        return np.abs(self.field)**2

    @property
    def phase(self):
        return np.angle(self.field)

    def get_info(self) -> str:
        I = self.intensity
        phase = self.phase



class Source2D(abc.ABC):

    @abc.abstractmethod
    def generate(self) -> Field2D:
        pass

class Mask2D(abc.ABC):
    @abc.abstractmethod
    def transform(self, field : Field2D) -> Field2D:
        pass


class Propagator2D(abc.ABC):

    def propagate(self, field: Field2D, distance : float) -> Field2D:
        pass


