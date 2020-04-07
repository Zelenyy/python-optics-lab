from enum import Enum, auto
import numpy as np


class EFState(Enum):
    DC = auto()
    AC = auto()


class ElectricField:
    def __init__(self, U, state: EFState):
        self.state = state
        self.U = U
        self.time = np.linspace(0, 0.02, 300)

    def value(self):
        if self.state == EFState.DC:
            return self.U
        else:
            return self.U*np.sin(2*np.pi*50*self.time)