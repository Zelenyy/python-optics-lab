import sys

import numpy as np
from PyQt5 import QtCore
from PyQt5.QtCore import QModelIndex
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QLabel, QFormLayout, QWidget, QHBoxLayout, QVBoxLayout, QSpinBox, QPushButton, \
    QApplication, QListView, QGroupBox, QStyledItemDelegate, QTableView, QMainWindow, QCheckBox

from diffractio import mm, um, degrees, nm
from diffractio.utils_optics import field_parameters

from matplotlib.backends.qt_compat import is_pyqt5
from matplotlib.figure import Figure

from optics.load_setup import load_setup
from optics.work_405.element_items import Grating, Diaphragm, Lens, DiffractioCalculator
from optics.work_405.setup_405 import Setup405

if is_pyqt5():
    from matplotlib.backends.backend_qt5agg import (
        FigureCanvas)

else:
    from matplotlib.backends.backend_qt4agg import (
        FigureCanvas)


class SpinBoxDelegate(QStyledItemDelegate):

    def __init__(self, max_: int, my_model):
        self.max_ = max_
        super().__init__()
        self.my_model = my_model


    def createEditor(self, parent: QWidget, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> QWidget:
        editor = QSpinBox()
        editor.setFrame(False)
        editor.setRange(0, self.max_)
        editor.setSingleStep(1)
        return editor
    def setEditorData(self, editor: QWidget, index: QtCore.QModelIndex) -> None:
        value = int(float(index.model().data(index, QtCore.Qt.EditRole)))
        editor.setValue(value)

    def updateEditorGeometry(self, editor: QWidget, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> None:
        editor.setGeometry(option.rect)

    def setModelData(self, editor: QWidget, model: QtCore.QAbstractItemModel, index: QtCore.QModelIndex) -> None:
        value = int(float(editor.value()))
        model.setData(index, value, QtCore.Qt.EditRole)
        data = self.my_model.item(index.row(), 0).data( role=50)
        data.element.position = value*mm

class Work405Window(QWidget):

    def diaphragm_widget(self, form):

        widthInput = QSpinBox()
        self.widthInput = widthInput
        widthInput.setRange(10, 1000)
        widthInput.setSingleStep(10)
        widthInput.setValue(self.dia.width)
        widthInput.setDisabled(True)

        def widthChanged(width: int):
            self.dia.update_width(width*um)
            # self.updateImage()
        widthInput.valueChanged.connect(widthChanged)
        form.addRow("Ширина щели, мкм: ", widthInput)

        self.rot45 = QCheckBox("Повернуть щель на 45 градусов")
        self.rot45.setEnabled(False)

        def action(flag):
            if flag:
                self.dia.rotate(45*degrees)
            else:
                self.dia.rotate(0)
        self.rot45.stateChanged.connect(action)
        form.addRow(self.rot45)


    def initSetup(self, layout):
        text = [
            "Длинна волны: {:.2f} нм".format(self.setup.lambda_light/nm),
            "Растояние от источника до экрана: {:d} см".format(int(self.setup.length/mm/10)),
        ]
        layout.addWidget(QLabel("\n".join(text)))

    def init_description(self, form):
        btn = QPushButton(
            """
            Открыть
            Описание
            Работы
            """
        )
        btn.setStyleSheet(
            """
            QPushButton {
            font: bold 16px;
            }
            """
        )
        form.addRow(btn)
        text = [
            "Maсштаб: 1px = 1 миллиметр",
            "Длинна волны света: {} нм".format(self.setup.lambda_light * 1000)

        ]
        label = QLabel(
            "\n".join(text)
        )
        label.setStyleSheet(
            """
            QLabel {
            font: bold 16px;
            }
            """
        )
        form.addRow(label)

    def init_controls(self):
        form = QFormLayout()
        self.vbox.addLayout(form)

        # self.init_description(form)
        self.diaphragm_widget(form)
        # self.init_lens(form)

    def __init__(self, parent=None):
        super().__init__()
        self.hbox = QHBoxLayout()
        self.vbox = QVBoxLayout()
        self.setLayout(self.hbox)
        # self.setup = Setup405()
        self.setup = load_setup(Setup405)
        # print(self.setup)
        self.initSetup(self.vbox)
        self.image_calculator = DiffractioCalculator(self.setup, self.setup.source())
        self.init_mpl_widget(self.hbox)
        self.hbox.addLayout(self.vbox)
        self.elements_store(self.vbox)
        self.init_controls()
        self.calc_button(self.vbox)
        # self.update_image()


    def fill_store(self, store_list):
        self.dia = Diaphragm("Щель", self.setup.mask())
        item1 = self.dia.item
        item2 = self.dia.element.position/mm
        store_list.appendRow([item1, QStandardItem(str(item2))])

        focal = self.setup.focal1
        lens = Lens("Линза 1 (F = {:.2f} см)".format(focal / mm / 10), self.setup.mask(), focal)
        item1 = lens.item
        item2 = lens.element.position/mm
        store_list.appendRow([item1, QStandardItem(str(item2))])

        focal = self.setup.focal2
        lens = Lens("Линза 2 (F = {:.2f} см)".format(focal / mm / 10), self.setup.mask(), focal)
        item1 = lens.item
        item2 = lens.element.position/mm
        store_list.appendRow([item1, QStandardItem(str(item2))])

        for indx, grating in enumerate(self.setup.grids):
            period, fill = grating
            g = Grating("Решетка {}".format(indx),
                        self.setup.mask(),
                        period, fill)
            item1 = g.item
            item2 = QStandardItem(str(g.element.position/mm))
            item2.setEditable(True)
            store_list.appendRow([item1, item2])

    def calc_button(self, layout):
        btn = QPushButton("Рассчитать изображение")
        btn.setStyleSheet(
            """
            QPushButton {
            font: bold 16px;
            }
            """
        )

        def action(click):
            self.update_image()

        btn.clicked.connect(action)
        layout.addWidget(btn)

    def elements_store(self, layout):
        gr_box = QGroupBox("Доступные элементы")
        vbox = QVBoxLayout()
        self.store = QListView()
        self.store_list = QStandardItemModel(parent=self)
        self.fill_store(self.store_list)
        self.store.setModel(self.store_list)
        vbox.addWidget(self.store)
        gr_box.setLayout(vbox)
        layout.addWidget(gr_box)

        gr_box = QGroupBox("Оптическая скамья")
        vbox = QVBoxLayout()



        self.store_list.setHorizontalHeaderLabels(["Элемент", "Положение, мм"])
        self.bench = QTableView()
        self.bench.setModel(self.store_list)
        for indx in range(0, self.store_list.rowCount()):
            self.bench.setRowHidden(indx, True)

        self.bench.setItemDelegateForColumn(1, SpinBoxDelegate(self.setup.length, self.store_list))
        self.bench.setColumnWidth(0,150)
        self.bench.setColumnWidth(1,150)
        vbox.addWidget(self.bench)
        gr_box.setLayout(vbox)
        layout.addWidget(gr_box)



        def action_store(indx: QModelIndex):
            # item = self.store_list[indx]
            self.store.setRowHidden(indx.row(), True)
            self.bench.setRowHidden(indx.row(), False)
            data = self.store_list.item(indx.row(), 0).data(role=50)
            self.image_calculator.elements.append(data.element)
            if data is self.dia:
                self.widthInput.setEnabled(True)
                self.rot45.setEnabled(True)
            # self.update_image()

        self.store.doubleClicked.connect(action_store)

        def action_bench(indx: QModelIndex):
            if indx.column() == 0:
                self.store.setRowHidden(indx.row(), False)
                self.bench.setRowHidden(indx.row(), True)
                data = self.store_list.item(indx.row(), 0).data(role=50)
                self.image_calculator.elements.remove(data.element)
                # self.update_image()
                if data is self.dia:
                    self.widthInput.setEnabled(False)
                    self.rot45.setEnabled(False)


        self.bench.doubleClicked.connect(action_bench)

    def init_mpl_widget(self, layout):
        vbox = QVBoxLayout()
        self.canvas = FigureCanvas(Figure(figsize=(10, 10)))
        self.ax = self.canvas.figure.subplots()
        # vbox.addWidget(NavigationToolbar(self.canvas, self))
        vbox.addWidget(self.canvas)
        layout.addLayout(vbox)

    def _get_intensity(self, field, logarithm=False):
        amplitude, intensity, phase = field_parameters(
            field.u, has_amplitude_sign=True)
        intensity = np.real(intensity)
        intensity[intensity < 0] = 0
        if logarithm:
            intensity = np.log(intensity + 1)
        return intensity

    def update_image(self):
        field = self.image_calculator.calculate()
        self.ax.clear()
        intensity = self._get_intensity(field, logarithm=True)
        x = field.x
        y = field.y
        # print(intensity)
        extension = (x[0] / mm, x[-1] / mm, y[0] / mm, y[-1] / mm)
        self.ax.imshow(intensity,
                       interpolation='bilinear',
                       origin="lower",
                       extent=extension)
        xlabel = "x (mm)"
        ylabel = "y (mm)"
        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)
        self.ax.figure.canvas.draw()

class Lab405Window(QMainWindow):

    def __init__(self, name):
        super().__init__()
        self.central = Work405Window()
        self.setCentralWidget(self.central)
        self.setWindowTitle(name)

def main():
    app = QApplication(sys.argv)
    window = Work405Window()
    window.show()
    sys.exit(app.exec_())
    # setup = Setup405()
    # calculate(setup)


if __name__ == '__main__':
    main()
