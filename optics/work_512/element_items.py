from dataclasses import dataclass
from multiprocessing import Pool

from PyQt5 import QtGui
from diffractio import um, degrees, mm
from diffractio.scalar_masks_XY import Scalar_mask_XY
from diffractio.scalar_sources_XY import Scalar_source_XY
import numpy as np
from optics.work_512.setup_512 import Setup512


@dataclass()
class Element:
    position: float
    element: Scalar_mask_XY

import abc

class ObservableState:
    state = False
    listeners = None

    def add_listener(self, listener):
        if self.listeners is None: self.listeners = []
        # print("Add listener {} to {}".format(listener.item.name, self.name))
        self.listeners.append(listener)
        # print(len(self.listeners))

    def change_state(self, state):
        self.state = state
        for it in self.listeners:
            it.enable(state)


class ItemElement(abc.ABC, ObservableState):
    element: Element = None

    def __init__(self, name):
        self.name = name
        self.item = QtGui.QStandardItem(self.name)
        self.item.setData(self, role=50)
        self.item.setEditable(False)
        self.x = 0

    @abc.abstractmethod
    def update_mask(self):
        pass

    def update_z(self, z):
        self.element.position = z*mm

    def update_x(self, x):
        self.x = x*mm

    def get_position(self):
        return self.element.position


class Diaphragm(ItemElement):
    def __init__(self, name, mask, width=300 * um):
        super().__init__(name)
        self.width = width
        self.mask = mask
        self.update_mask()
        self.element = Element(0.0, self.mask)

    def update_width(self, width):
        self.width = width

    def update_mask(self):
        self.mask.square(r0=(self.x, 0 * um), size=(self.width, 10 * mm), angle=0 * degrees)


class Lens(ItemElement):
    def __init__(self, name, mask, focal=100 * mm):
        super().__init__(name)
        self.focal = focal
        self.mask = mask
        self.element: Element = Element(101 * mm, mask)

    def update_mask(self):
        self.mask.lens(
            r0=(self.x, 0 * um),
            radius=(10 * mm, 10 * mm),
            focal=(self.focal, self.focal),
            angle=0 * degrees)

class ScreenElement:
    def __init__(self, position):
        self.position = position

    @abc.abstractmethod
    def get_field(self, field):
        pass

class Screen(abc.ABC, ObservableState):

    def __init__(self, name, element):
        self.name = name
        self.element = element

    def get_position(self):
        return self.element.position

    def update_z(self, z):
        self.element.position = z*mm


class ScreenPlane(ScreenElement):
    def get_field(self, field):
        return field

class Telescope(ScreenElement):
    def __init__(self, position, setup: Setup512):
        super().__init__(position)
        self.length = 1000*mm
        self.focal1 = 1700*mm
        self.focal2 = -700*mm
        self.objective = setup.mask()
        self.objective.lens(
            r0 = (0,0),
            focal = (self.focal1, self.focal1),
            radius= 5*mm
        )

        self.eyepiece =  setup.mask()
        self.eyepiece.lens(
            r0=(0, 0),
            focal=(self.focal2, self.focal2),
            radius=5 * mm
        )

    def get_field(self, field):
        # temp = field * self.objective
        # temp.RS(z=self.length, new_field=False)
        # temp = temp*self.eyepiece
        # return temp.RS(z = 500*mm, new_field=True)
        return field.fft(new_field=True, shift=True)


class DiffractioCalculator:

    def __init__(self, setup: Setup512):
        self.setup = setup
        self.source1, self.source2  = self.setup.source()
        self.elements = []
        self.screen1 : Screen = None
        self.screen2 : Screen = None

    def calculate(self):
        if len(self.elements) == 0:
            field1 = self.empty(self.source1, self.screen1)
            field2 = self.empty(self.source2, self.screen2)
            return field1, field2
        elements = []
        for it in self.elements:
            limit = 0
            if self.screen1 is None:
                limit = np.inf
            else:
                limit = self.screen1.element.position
            if it.element.position <= limit:
                it.update_mask()
                elements.append(it.element)
        elements.sort(key=lambda x: x.position)

        if len(elements) == 0:
            field1 = self.empty(self.source1, self.screen1)
            field2 = self.empty(self.source2, self.screen2)
            return field1, field2

        with Pool() as p:
            result = tuple(p.map(_calculate, [(self.source1, self.screen1.element, elements), (self.source2, self.screen2.element, elements)]))
        return result

    def empty(self, source, screen: Screen):
        if screen is None:
            return source
        z = screen.element.position
        if z == 0:
            return screen.element.get_field(source)
        temp = source.RS(z=z, new_field=True)
        return screen.element.get_field(temp)

def _calculate(parametrs):
    source, screen, elements = parametrs
    first: Element = elements[0]
    if first.position != 0:
        temp = source.RS(z=first.position, new_field=True)
        temp = temp * first.element
    else:
        temp = source * first.element

    z_current = first.position
    for element in elements[1:]:
        diff = element.position - z_current
        if (diff > 0):
            temp.RS(z=element.position - z_current, new_field=False)
        temp = temp * element.element
        z_current = element.position
    if screen is None:
        return temp
    z = screen.position
    delta = z - z_current
    if abs(delta) > 0:
        temp.RS(z=delta, new_field=True)
    return screen.get_field(temp)