from dataclasses import dataclass

from PyQt5 import QtGui
from diffractio import um, degrees, mm
from diffractio.scalar_masks_XY import Scalar_mask_XY
from diffractio.scalar_sources_XY import Scalar_source_XY

from optics.work_405.setup_405 import Setup405


@dataclass()
class Element:
    position: float
    element: Scalar_mask_XY


class ItemElement:
    element: Element
    def __init__(self, name):
        self.name = name
        self.item = QtGui.QStandardItem(self.name)
        self.item.setData(self, role=50)
        self.item.setEditable(False)


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
        self.update_width(width)
        self.element = Element(0.0, mask)

    def update_width(self, width):
        self.mask.square(r0=(0 * um, 0 * um), size=(width, 10 * mm), angle=0 * degrees)

    def rotate(self, angle):
        self.mask.square(r0=(0 * um, 0 * um), size=(self.width, 10 * mm), angle=angle)

class Lens(ItemElement):
    element: Element

    def __init__(self, name, mask, focal=100 * mm):
        super().__init__(name)
        self.focal = focal
        mask.lens(
            r0=(0 * um, 0 * um),
            radius=(10 * mm, 10 * mm),
            focal=(focal, focal),
            angle=0 * degrees)

        self.element = Element(101 * mm, mask)


class DiffractioCalculator:

    def __init__(self, setup: Setup405, source: Scalar_source_XY):
        self.setup = setup
        self.source = source
        self.elements = []
        # self.empty_source =  self.source.fft(self.setup.length, shift=True, new_field=True)
        self.empty_source = self.source.RS(z=self.setup.length, new_field=True)

    def calculate(self):
        if len(self.elements) == 0:
            return self.empty_source
        self.elements.sort(key=lambda x: x.position)
        first: Element = self.elements[0]
        if first.position != 0:
            temp = self.source.RS(z=first.position, new_field=True)
            temp = temp * first.element
        else:
            temp = self.source * first.element

        z_current = first.position
        for element in self.elements[1:]:
            temp.RS(z=element.position - z_current, new_field=False)
            temp = temp * element.element
            z_current = element.position
        return temp.fft(z=self.setup.length - z_current, new_field=True)