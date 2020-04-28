import sys
import numpy as np
from PyQt5.QtCore import QModelIndex
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import QLabel, QFormLayout, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, \
    QApplication, QListView, QGroupBox, QMainWindow, QRadioButton

from diffractio import mm, nm
from diffractio.utils_optics import field_parameters

from matplotlib.backends.qt_compat import is_pyqt5
from matplotlib.figure import Figure

from optics.work_512.color import wav2RGB, create_cmap
from optics.work_512.element_items import Diaphragm, Lens, DiffractioCalculator, ScreenPlane, Screen, Telescope
from optics.work_512.item_widget import ItemWidget, add_dia_width
from optics.work_512.setup_512 import Setup512

if is_pyqt5():
    from matplotlib.backends.backend_qt5agg import (
        FigureCanvas)

else:
    from matplotlib.backends.backend_qt4agg import (
        FigureCanvas)


class Work512Window(QWidget):

    def init_setup(self, layout):
        text = [
            # "Длинна волны: {:.2f} нм".format(self.setup.lambda_light/nm),
            "Растояние от источника до экрана: {:d} см".format(int(self.setup.length/mm/10)),
        ]
        layout.addWidget(QLabel("\n".join(text)))


    def __init__(self, parent=None):
        super().__init__()
        self.hbox = QHBoxLayout()
        self.vbox = QVBoxLayout()
        self.setLayout(self.hbox)
        self.setup = Setup512()
        # self.setup = load_setup(Setup512)
        # print(self.setup)
        self.color()
        self.init_setup(self.vbox)
        self.image_calculator = DiffractioCalculator(self.setup)
        self.init_mpl_widget(self.hbox)
        self.hbox.addLayout(self.vbox)
        self.elements_store(self.vbox)
        self.calc_button(self.vbox)

    def color(self):
        self.color1 =create_cmap(wav2RGB(self.setup.lambda_light_1 / nm))
        self.color2 =create_cmap(wav2RGB(self.setup.lambda_light_2 / nm))
        return 0

    def screen_button(self, layout, form):
        group = QGroupBox("Выбрать способ наблюдения")
        layout.addWidget(group)
        vbox = QVBoxLayout()
        group.setLayout(vbox)
        qb1 = QRadioButton("Экран")
        qb2 = QRadioButton("Зрительная труба")
        qb3 = QRadioButton("Микроскоп")
        vbox.addWidget(qb1)
        vbox.addWidget(qb2)
        vbox.addWidget(qb3)

        simple_screen = Screen("Экран",ScreenPlane(200*mm))
        ItemWidget(form, simple_screen, x=False)
        telescope = Screen("Зрительная труба", Telescope(1000*mm, self.setup))
        # ItemWidget(form, telescope, x=False)
        # ItemWidget(form, simple_screen, x=False)

        def action_1(state):
            if qb1.isChecked():
                self.image_calculator.screen1 = simple_screen
                self.image_calculator.screen2 = simple_screen
                telescope.change_state(False)
                simple_screen.change_state(True)
                qb2.setChecked(False)
                qb3.setChecked(False)

        def action_2(state):
            if qb2.isChecked():
                self.image_calculator.screen1 = telescope
                self.image_calculator.screen2 = telescope
                telescope.change_state(True)
                simple_screen.change_state(False)
                qb1.setChecked(False)
                qb3.setChecked(False)

        def action_3(state):
            if qb3.isChecked():
                self.image_calculator.screen1 = simple_screen
                self.image_calculator.screen2 = simple_screen
                simple_screen.change_state(True)
                qb2.setChecked(False)
                qb1.setChecked(False)

        qb1.toggled.connect(action_1)
        qb2.toggled.connect(action_2)
        qb3.toggled.connect(action_3)
        qb1.setChecked(True)




    def fill_store(self, store_list, form):
        dia = Diaphragm("Щель 1", self.setup.mask())
        item1 = dia.item
        store_list.appendRow(item1)
        widget = ItemWidget(form, dia)
        add_dia_width(widget)

        dia = Diaphragm("Щель 2", self.setup.mask())
        item1 = dia.item
        store_list.appendRow(item1)
        widget = ItemWidget(form, dia)
        add_dia_width(widget)

        focal = self.setup.focal1
        lens = Lens("Линза 1 (F = {:.2f} см)".format(focal / mm / 10), self.setup.mask(), focal)
        item1 = lens.item
        store_list.appendRow(item1)
        widget = ItemWidget(form, lens)

        focal = self.setup.focal2
        lens = Lens("Линза 2 (F = {:.2f} см)".format(focal / mm / 10), self.setup.mask(), focal)
        item1 = lens.item
        store_list.appendRow(item1)
        widget = ItemWidget(form, lens)

        # for indx, grating in enumerate(self.setup.grids):
        #     period, fill = grating
        #     g = Grating("Решетка {}".format(indx),
        #                 self.setup.mask(),
        #                 period, fill)
        #     item1 = g.item
        #     item2 = QStandardItem(str(g.element.position/mm))
        #     item2.setEditable(True)
        #     store_list.appendRow([item1, item2])

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

        hbox = QHBoxLayout()
        layout.addLayout(hbox)
        gr_vbox = QVBoxLayout()
        hbox.addLayout(gr_vbox)
        form = QFormLayout()
        hbox.addLayout(form)
        gr_box = QGroupBox("Доступные элементы")
        gr_vbox.addWidget(gr_box)

        self.store_list = QStandardItemModel(parent=self)
        self.fill_store(self.store_list, form)
        self.screen_button(gr_vbox, form)

        vbox = QVBoxLayout()
        self.store = QListView()

        self.store.setModel(self.store_list)
        vbox.addWidget(self.store)
        gr_box.setLayout(vbox)


        gr_box = QGroupBox("Оптическая скамья")
        vbox = QVBoxLayout()
        self.bench = QListView()
        self.bench.setModel(self.store_list)
        for indx in range(0, self.store_list.rowCount()):
            self.bench.setRowHidden(indx, True)

        vbox.addWidget(self.bench)
        gr_box.setLayout(vbox)
        gr_vbox.addWidget(gr_box)


        def action_store(indx: QModelIndex):
            # item = self.store_list[indx]
            self.store.setRowHidden(indx.row(), True)
            self.bench.setRowHidden(indx.row(), False)
            data = self.store_list.item(indx.row(), 0).data(role=50)
            self.image_calculator.elements.append(data)
            data.change_state(True)


        self.store.doubleClicked.connect(action_store)

        def action_bench(indx: QModelIndex):
            self.store.setRowHidden(indx.row(), False)
            self.bench.setRowHidden(indx.row(), True)
            data = self.store_list.item(indx.row(), 0).data(role=50)
            self.image_calculator.elements.remove(data)
            data.change_state(False)

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
        field1, field2 = self.image_calculator.calculate()
        self.ax.clear()
        intensity1 = 255*self._get_intensity(field1, logarithm=True)
        intensity2 = 255*self._get_intensity(field2, logarithm=True)
        x = field1.x
        y = field1.y
        # print(field1.x.min(), field1.x.max())
        # print(field2.x.min(), field2.x.max())
        # print(intensity)
        extension = (x[0] / mm, x[-1] / mm, y[0] / mm, y[-1] / mm)

        im1 = self.ax.imshow(intensity1,
                       interpolation='bilinear',
                       origin="lower",
                       extent=extension,
                       cmap=self.color1)
        # self.ax.figure.colorbar(im1)
        im2 = self.ax.imshow(intensity2,
                       interpolation='bilinear',
                       origin="lower",
                       extent=extension,
                       cmap=self.color2,
                             alpha=0.5)
        # # # from matplotlib.image import composite_images
        # im, _, _ = composite_images([im1,im2],renderer=self.canvas.render)
        # self.ax.imshow(im)
        # self.ax.imshow(intensity1,
        #                interpolation='bilinear',
        #                origin="lower",
        #                extent=extension,
        #                cmap=self.color1)
        xlabel = "x (mm)"
        ylabel = "y (mm)"
        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)
        self.ax.figure.canvas.draw()

class Lab405Window(QMainWindow):

    def __init__(self, name):
        super().__init__()
        self.central = Work512Window()
        self.setCentralWidget(self.central)
        self.setWindowTitle(name)

def main():
    app = QApplication(sys.argv)
    window = Work512Window()
    window.show()
    sys.exit(app.exec_())
    # setup = Setup405()
    # calculate(setup)


if __name__ == '__main__':
    main()
