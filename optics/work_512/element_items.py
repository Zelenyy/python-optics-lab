from dataclasses import dataclass

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
    element: Element

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
        self.element.position = z

    def update_x(self, x):
        self.x = x

class Grating(ItemElement):


    def __init__(self, name, mask, period=100 * um, fill_factor=0.333):
        super().__init__(name)
        self.period = period
        self.fill_factor = fill_factor
        mask.ronchi_grating(
            period=period, x0=0 * um,
            angle=0 * degrees, fill_factor=fill_factor)
        self.element = Element(100*mm, mask)


class Diaphragm(ItemElement):
    element: Element

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
    element: Element

    def __init__(self, name, mask, focal=100 * mm):
        super().__init__(name)
        self.focal = focal
        self.mask = mask
        self.element = Element(101 * mm, mask)

    def update_mask(self):
        self.mask.lens(
            r0=(self.x, 0 * um),
            radius=(10 * mm, 10 * mm),
            focal=(self.focal, self.focal),
            angle=0 * degrees)


class Screen(abc.ABC):
    def __init__(self, position):
        self.position = position

    def update_z(self, z):
        self.position = z

    @abc.abstractmethod
    def get_field(self, field):
        pass

class ScreenPlane(Screen):
    def get_field(self, field):
        return field

class DiffractioCalculator:

    def __init__(self, setup: Setup512):
        self.setup = setup
        self.source1, self.source2  = self.setup.source()
        self.elements = []
        self.length = 2000*mm
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
                limit = self.screen1.position
            if it.element.position <= limit:
                it.update_mask()
                elements.append(it.element)
        elements.sort(key=lambda x: x.position)
        field1  = self._calculate(self.source1, self.screen1, elements)
        field2 = self._calculate(self.source2, self.screen2, elements)
        return field1, field2

    def empty(self, source, screen: Screen):
        if screen is None:
            return source
        z = screen.position
        if z == 0:
            return screen.get_field(source)
        temp = source.RS(z=z, new_field=True)
        return screen.get_field(temp)

    def _calculate(self, source, screen: Screen, elements):
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