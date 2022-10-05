from typing import Optional

import pyperclip
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtWidgets import (
    QTableWidgetItem,
    QTableWidget,
    QHeaderView,
    QPushButton,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QFileDialog,
    QMessageBox,
    QMenu,
)

from backup_helper.backend.access import get_group, add_group, update_group, delete_group
from backup_helper.backend.backup import save
from backup_helper.common import DELETE
from backup_helper.gui.common import TableItem, cell_double_click_for_copy
from backup_helper.gui.visible import control_visible_when_mode
from backup_helper.util import sync


class GroupTable(QTableWidget):
    def __init__(self):
        super().__init__()
        headers = ['ID', '存档组名', '存档位置', '创建时间', '修改时间']
        self.setColumnCount(len(headers))
        self.setHorizontalHeaderLabels(headers)
        self.horizontalHeader().setSectionsClickable(False)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.verticalHeader().setHidden(True)
        self.refresh()
        # self.cellChanged['int', 'int'].connect(self.on_edit)
        self.cellDoubleClicked['int', 'int'].connect(lambda x, y: cell_double_click_for_copy(self, x, y))
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.right_click_menu)
        control_visible_when_mode(self, 'group')

    @sync
    def refresh(self):
        self.blockSignals(True)  # 刷新时不触发其他事件
        try:
            groups = get_group()
            self.setRowCount(len(groups))
            for row, group in enumerate(groups):
                self.setItem(row, 0, TableItem(str(group.id), Qt.ItemFlag.ItemIsEnabled))
                self.setItem(row, 1, TableItem(str(group.name), Qt.ItemFlag.ItemIsEnabled))
                self.setItem(row, 2, TableItem(str(group.path), Qt.ItemFlag.ItemIsEnabled))
                self.setItem(row, 3, TableItem(group.ctime.strftime('%Y/%m/%d %H:%M:%S'), Qt.ItemFlag.ItemIsEnabled))
                self.setItem(row, 4, TableItem(group.mtime.strftime('%Y/%m/%d %H:%M:%S'), Qt.ItemFlag.ItemIsEnabled))
        finally:
            self.blockSignals(False)

    def setVisible(self, visible: bool) -> None:
        super().setVisible(visible)
        self.refresh()

    def delete_group_action(self, group_id: int):
        confirm = QMessageBox.question(self, '确认删除', f'所有该存档组下的存档均会被删除，确认删除存档组吗？（存档ID：{group_id}）')
        if confirm == QMessageBox.StandardButton.Yes:
            delete_group(group_id)
            self.refresh()

    def click_add_btn(self):
        name = self.item(0, 1).text()
        path = self.item(0, 2).text()
        add_group(name, path)
        self.refresh()

    def right_click_menu(self, pos: QPoint):
        item = self.itemAt(pos)
        if item is None:
            return
        row, column = item.row(), item.column()
        menu = QMenu()
        save_empty_name_action = menu.addAction('保存空名存档')
        save_action = menu.addAction('保存存档')
        update_action = menu.addAction('修改存档组')
        del_action = menu.addAction('删除存档组')
        pos.setY(pos.y() + 25)  # FIXME: 为什么这样才能对齐？
        action = menu.exec(self.mapToGlobal(pos))
        group_id = int(self.item(row, 0).text())
        if action == save_empty_name_action:
            save(group_id)
            self.refresh()
        elif action == save_action:
            dialog = SaveSaveDialog()
            result = dialog.exec()
            if result:
                save(group_id, dialog.message)
                self.refresh()
        elif action == del_action:
            self.delete_group_action(group_id)
        elif action == update_action:
            dialog = GroupDialog(self.item(row, 1).text(), self.item(row, 2).text(), True)
            result = dialog.exec()
            if result:
                update_group(group_id, dialog.name.text(), dialog.path.text())
                self.refresh()


class GroupDialog(QDialog):
    def __init__(self, name: Optional[str] = None, path: Optional[str] = None, is_update: Optional[bool] = False):
        super().__init__()
        self.setWindowTitle('修改存档组' if is_update else '新增存档组')
        layout = QVBoxLayout()
        name_layout = QHBoxLayout()
        name_label = QLabel()
        name_label.setText('存档组名')
        name_layout.addWidget(name_label)
        self.name = QLineEdit()
        if name is not None:
            self.name.setText(name)
        name_layout.addWidget(self.name)
        layout.addLayout(name_layout)
        path_layout = QHBoxLayout()
        path_label = QLabel()
        path_label.setText('存档位置')
        # path_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        path_layout.addWidget(path_label)
        self.path = QLabel()
        self.path.setAlignment(Qt.AlignmentFlag.AlignLeft)
        if path is not None:
            self.path.setText(path)
        path_layout.addWidget(self.path)
        layout.addLayout(path_layout)
        btn_file = QPushButton('选择文件')
        btn_file.clicked.connect(self.btn_file_click)
        btn_dir = QPushButton('选择文件夹')
        btn_dir.clicked.connect(self.btn_dir_click)
        if not is_update:
            btn_layout = QHBoxLayout()
            btn_layout.addWidget(btn_file)
            btn_layout.addWidget(btn_dir)
            layout.addLayout(btn_layout)
        btn_confirm = QPushButton('确定')
        btn_confirm.clicked.connect(self.btn_confirm_click)
        layout.addWidget(btn_confirm)
        self.setLayout(layout)

    def btn_file_click(self):
        file = QFileDialog.getOpenFileName()
        if file[1]:
            self.path.setText(file[0])

    def btn_dir_click(self):
        dire = QFileDialog.getExistingDirectory()
        if dire:
            self.path.setText(dire)

    def btn_confirm_click(self):
        if self.name.text() == '':
            QMessageBox.about(self, ' ', '存档组名不能为空')
            return
        if self.path.text() == '':
            QMessageBox.about(self, ' ', '存档位置不能为空')
            return
        self.accept()


class GroupAddBtn(QPushButton):
    def __init__(self, group_table: GroupTable):
        super().__init__('新增存档组')
        self.clicked.connect(self.click_callback)
        self.group_table = group_table
        control_visible_when_mode(self, 'group')

    def click_callback(self):
        dialog = GroupDialog()
        result = dialog.exec()
        if result:
            add_group(dialog.name.text(), dialog.path.text())
            self.group_table.refresh()


class SaveSaveDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.message: Optional[str] = None
        self.setWindowTitle('保存存档')
        layout = QVBoxLayout()
        layout_editor = QHBoxLayout()
        label = QLabel('存档名')
        self.editor = QLineEdit()
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
