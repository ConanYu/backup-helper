from typing import List, Callable

from PyQt6.QtWidgets import QWidget

VIS_MODE: str = 'group'
CALLBACK: List[Callable] = []


def set_vis_mode(mode: str) -> None:
    if mode not in ('group', 'save'):
        raise RuntimeError(f'table mode `{mode}` is undefined')
    global VIS_MODE, CALLBACK
    VIS_MODE = mode
    for callback in CALLBACK:
        callback(mode)


def control_visible_when_mode(widget: QWidget, mode: str) -> None:
    def callback(m: str) -> None:
        widget.setVisible(m == mode)

    CALLBACK.append(callback)
