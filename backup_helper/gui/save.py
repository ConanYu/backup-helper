from typing import Optional, Callable

from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtWidgets import (
    QTableWidget,
    QLineEdit,
    QHBoxLayout,
    QHeaderView,
    QMenu,
    QDialog,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QMessageBox,
)

from backup_helper.backend.access import get_save, update_save
from backup_helper.backend.backup import load
from backup_helper.common import DELETE
from backup_helper.gui.common import TableItem, cell_double_click_for_copy, wrap_exception
from backup_helper.gui.visible import control_visible_when_mode
from backup_helper.util import sync


class SaveEditor(QHBoxLayout):
    def __init__(self):
        super().__init__()
        self.__group_name_selector = QLineEdit()
        self.__group_name_selector.setPlaceholderText('存档组名搜索')
        control_visible_when_mode(self.__group_name_selector, 'save')
        self.__save_name_selector = QLineEdit()
        self.__save_name_selector.setPlaceholderText('存档名搜索')
        control_visible_when_mode(self.__save_name_selector, 'save')
        self.addWidget(self.__group_name_selector)
        self.addWidget(self.__save_name_selector)

    @sync
    def get_group_name(self):
        self.blockSignals(True)
        try:
            return self.__group_name_selector.text() or None
        finally:
            self.blockSignals(False)

    @sync
    def get_save_name(self):
        self.blockSignals(True)
        try:
            return self.__save_name_selector.text() or None
        finally:
            self.blockSignals(False)

    def set_on_edit_callback(self, callback: Callable):
        self.__group_name_selector.textChanged.connect(callback)
        self.__save_name_selector.textChanged.connect(callback)


class SaveTable(QTableWidget):
    def __init__(self, save_editor: Optional[SaveEditor] = None):
        super().__init__()
        headers = ['ID', '存档名', '存档组ID', '存档组名', '存档位置', '创建时间', '修改时间']
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        self.horizontalHeader().setSectionsClickable(False)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.verticalHeader().setHidden(True)
        self.cellDoubleClicked['int', 'int'].connect(lambda x, y: cell_double_click_for_copy(self, x, y))
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.right_click_menu)
        self.save_editor = save_editor
        self.save_editor.set_on_edit_callback(self.refresh)
        control_visible_when_mode(self, 'save')
        self.refresh()

    @sync
    def refresh(self):
        self.blockSignals(True)  # 刷新时不触发其他事件
        try:
            save_name, group_name = None, None
            if self.save_editor is not None:
                save_name = self.save_editor.get_save_name()
                group_name = self.save_editor.get_group_name()
            saves = get_save(save_name, group_name)
            self.setRowCount(len(saves))
            for row, save in enumerate(saves):
                self.setItem(row, 0, TableItem(str(save.Save.id), Qt.ItemFlag.ItemIsEnabled))
                self.setItem(row, 1, TableItem(str(save.Save.name or ''), Qt.ItemFlag.ItemIsEnabled))
                self.setItem(row, 2, TableItem(str(save.Save.group_id), Qt.ItemFlag.ItemIsEnabled))
                self.setItem(row, 3, TableItem(str(save.Group.name or ''), Qt.ItemFlag.ItemIsEnabled))
                self.setItem(row, 4, TableItem(str(save.Group.path or ''), Qt.ItemFlag.ItemIsEnabled))
                ctime = save.Save.ctime
                if ctime is not None:
                    self.setItem(row, 5, TableItem(ctime.strftime('%Y/%m/%d %H:%M:%S'), Qt.ItemFlag.ItemIsEnabled))
                else:
                    self.setItem(row, 5, TableItem('', Qt.ItemFlag.ItemIsEnabled))
                mtime = save.Save.mtime
                if mtime is not None:
                    self.setItem(row, 6, TableItem(mtime.strftime('%Y/%m/%d %H:%M:%S'), Qt.ItemFlag.ItemIsEnabled))
                else:
                    self.setItem(row, 6, TableItem('', Qt.ItemFlag.ItemIsEnabled))
        finally:
            self.blockSignals(False)

    def setVisible(self, visible: bool) -> None:
        super().setVisible(visible)
        self.refresh()

    def right_click_menu(self, pos: QPoint):
        item = self.itemAt(pos)
        if item is None:
            return
        row, column = item.row(), item.column()
        menu = QMenu()
        update_action = menu.addAction('修改存档')
        load_action = menu.addAction('加载存档')
        del_action = menu.addAction('删除存档')
        pos.setY(pos.y() + 25)  # FIXME: 为什么这样才能对齐？
        save_id = int(self.item(row, 0).text())
        action = menu.exec(self.mapToGlobal(pos))
        with wrap_exception(self):
            if action == load_action:
                load(save_id)
                QMessageBox.about(self, ' ', '加载完成')
            elif action == update_action:
                dialog = UpdateSaveDialog(self.item(row, 1).text())
                result = dialog.exec()
                if result:
                    update_save(save_id, dialog.message)
                    self.refresh()
            elif action == del_action:
                update_save(save_id, status=DELETE)
                self.refresh()


class UpdateSaveDialog(QDialog):
    def __init__(self, name: str):
        super().__init__()
        self.message: Optional[str] = None
        self.setWindowTitle('更新存档')
        layout = QVBoxLayout()
        layout_editor = QHBoxLayout()
        label = QLabel('存档名')
        self.editor = QLineEdit()
        self.editor.setText(name)
        layout_editor.addWidget(label)
        layout_editor.addWidget(self.editor)
        layout.addLayout(layout_editor)
        btn = QPushButton('确定')
        btn.clicked.connect(self.confirm)
        layout.addWidget(btn)
        self.setLayout(layout)

    def confirm(self):
        self.message = self.editor.text()
        self.accept()
