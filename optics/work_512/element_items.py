from dataclasses import dataclass

from PyQt5 import QtGui
from diffractio import um, degrees, mm
from diffractio.scalar_masks_XY import Scalar_mask_XY
from diffractio.scalar_sources_XY import Scalar_source_XY

from optics.work_512.setup_512 import Setup512


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
        self.width = width
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

    def __init__(self, setup: Setup512):
        self.setup = setup
        self.source1, self.source2  = self.setup.source()
        self.elements = []
        self.length = 2000*mm

    def calculate(self):
        field1  = self._calculate(self.source1)
        field2 = self._calculate(self.source2)
        return field1, field2

    def _calculate(self, source):
        if len(self.elements) == 0:
            return source.RS(z=self.length, new_field=True)
        self.elements.sort(key=lambda x: x.position)
        first: Element = self.elements[0]
        if first.position != 0:
            temp = source.RS(z=first.position, new_field=True)
            temp = temp * first.element
        else:
            temp = source * first.element

        z_current = first.position
        for element in self.elements[1:]:
            diff = element.position - z_current
            if (diff > 0):
                temp.RS(z=element.position - z_current, new_field=False)
            temp = temp * element.element
            z_current = element.position
        return temp.fft(z=self.setup.length - z_current, new_field=True)