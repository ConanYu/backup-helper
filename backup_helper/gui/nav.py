from PyQt6.QtWidgets import QBoxLayout, QVBoxLayout, QPushButton

from backup_helper.gui.visible import set_vis_mode


def nav() -> QBoxLayout:
    group_btn = QPushButton('存档组管理')
    group_btn.clicked.connect(lambda: set_vis_mode('group'))
    save_btn = QPushButton('存档管理')
    save_btn.clicked.connect(lambda: set_vis_mode('save'))
    layout = QVBoxLayout()
    layout.addWidget(group_btn)
    layout.addWidget(save_btn)
    layout.addStretch(1)
    return layout
