from PyQt5.QtWidgets import QGroupBox, QFormLayout, QSpinBox
from diffractio import um, mm

from optics.work_512.element_items import ItemElement


class ItemWidget(QGroupBox):

    def __init__(self, layout, item: ItemElement, x = True):
        super().__init__(item.name)
        layout.addWidget(self)
        self.controls = []
        self.item = item
        self.form_inner = QFormLayout()
        self.setLayout(self.form_inner)
        self.position_controls(x)
        item.add_listener(self)
        self.enable(False)

    def position_controls(self, x):
        if x:
            x_input = QSpinBox()
            x_input.setRange(-10, 10)
            x_input.setSingleStep(1)
            x_input.setValue(self.item.x/mm)

            def action(x):
                self.item.update_x(x)

            x_input.valueChanged.connect(action)
            self.form_inner.addRow("Положение по x, мм:", x_input)
            self.controls.append(x_input)

        z_input = QSpinBox()
        z_input.setRange(0, 3000)
        z_input.setSingleStep(1)
        z_input.setValue(self.item.get_position()/mm)

        def action(x):
            self.item.update_z(x)

        z_input.valueChanged.connect(action)
        self.form_inner.addRow("Положение по z, мм:", z_input)
        self.controls.append(z_input)


    def enable(self, state):
        for it in self.controls:
            it.setEnabled(state)


def add_dia_width(widget: ItemWidget):
        widthInput = QSpinBox()
        widthInput.setRange(1, 400)
        widthInput.setSingleStep(1)
        widthInput.setValue(widget.item.width)
        widthInput.setDisabled(True)

        widget.form_inner.addRow("Ширина щели, мкм: ", widthInput)
        def widthChanged(width: int):
            widget.item.update_width(width*um)
        widthInput.valueChanged.connect(widthChanged)
        widget.controls.append(widthInput)