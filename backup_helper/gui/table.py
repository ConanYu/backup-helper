from PyQt6.QtWidgets import (
    QBoxLayout,
    QVBoxLayout,
)

from backup_helper.gui.group import GroupAddBtn, GroupTable
from backup_helper.gui.save import SaveEditor, SaveTable
from backup_helper.gui.visible import set_vis_mode


def table() -> QBoxLayout:
    layout = QVBoxLayout()
    group_table = GroupTable()
    layout.addWidget(GroupAddBtn(group_table))
    layout.addWidget(group_table)
    save_editor = SaveEditor()
    layout.addLayout(save_editor)
    layout.addWidget(SaveTable(save_editor))
    set_vis_mode('group')  # 默认进入存档组管理
    return layout


__all__ = [
    'table',
]
