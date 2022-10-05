from PyQt6.QtGui import QGuiApplication
from PyQt6.QtWidgets import QWidget, QHBoxLayout

from backup_helper.gui.nav import nav
from backup_helper.gui.table import table


class Widget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowTitle('存档小助手')
        rect = QGuiApplication.primaryScreen().geometry()
        self.setFixedSize(rect.width() // 2, rect.height() // 2)
        layout = QHBoxLayout()
        layout.addLayout(nav())
        layout.addLayout(table())
        self.setLayout(layout)
