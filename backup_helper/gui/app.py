import sys

from PyQt6.QtWidgets import QApplication

from backup_helper.gui.widget import Widget


def application():
    app = QApplication(sys.argv)
    w = Widget()
    w.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    application()
