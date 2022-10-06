import traceback
from contextlib import contextmanager
from typing import Optional

import pyperclip
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QTableWidgetItem,
    QTableWidget,
    QDialog,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QMessageBox,
    QWidget,
)


class TableItem(QTableWidgetItem):
    def __init__(self, item, flag: Optional[Qt.ItemFlag] = None):
        super().__init__(item)
        if flag is not None:
            self.setFlags(flag)


def cell_double_click_for_copy(table: QTableWidget, row: int, column: int) -> None:
    dialog = QDialog()
    dialog.setWindowTitle(' ')
    layout = QVBoxLayout()
    item = table.item(row, column)
    if item is None:
        return
    text = item.text()
    if text == '':
        return
    label = QLabel(text)
    label.setTextInteractionFlags(
        Qt.TextInteractionFlag.TextSelectableByMouse | Qt.TextInteractionFlag.TextSelectableByKeyboard)
    layout.addWidget(label)
    copy_label = QLabel('复制成功')
    btn = QPushButton('复制')

    def click():
        pyperclip.copy(text)
        layout.addWidget(copy_label)

    btn.clicked.connect(click)
    layout.addWidget(btn)
    dialog.setLayout(layout)
    dialog.exec()


@contextmanager
def wrap_exception(widget: QWidget):
    try:
        yield
    except Exception as e:
        traceback.print_exc()
        QMessageBox.critical(widget, '错误', traceback.format_exc())
        _ = e
