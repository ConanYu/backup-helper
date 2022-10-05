import os
import shutil
import time

from sqlalchemy import and_
from sqlalchemy.orm import Session

from backup_helper.backend.database import session, Save, Group
from backup_helper.common import BAK_PATH, SAVE_PATH, ACTIVE
from backup_helper.util import sync


def is_file(path: str) -> bool:
    isfile = os.path.isfile(path)
    isdir = os.path.isdir(path)
    if (isfile and isdir) or (not isfile and not isdir):
        raise RuntimeError(f'unknown error. path: {path}, isfile: {isfile}, isdir: {isdir}.')
    return isfile


@sync
def save(group_id: int, name: str = None):
    with session() as s:  # type: Session
        group = s.query(Group).filter(and_(Group.id == group_id, )).first()
        if group is None:
            raise RuntimeError(f'[save] Group {group_id} not found')
        save_ = Save(name=name, group_id=group_id, status=ACTIVE)
        s.add(save_)
        s.flush()
        s.refresh(save_)
        save_path = os.path.join(SAVE_PATH, str(save_.id))
        os.mkdir(save_path)
        isfile = is_file(group.path)
        dst_path = os.path.join(save_path, os.path.basename(group.path))
        if isfile:
            shutil.copy(group.path, dst_path)
        else:
            shutil.copytree(group.path, dst_path)


@sync
def load(save_id: int) -> None:
    with session() as s:  # type: Session
        save_: Save = s.query(Save).filter(and_(Save.id == save_id, Save.status == ACTIVE)).first()
        if save_ is None:
            raise RuntimeError(f'[load] Save {save_id} not found')
        group: Group = s.query(Group).filter(and_(Group.id == save_.group_id, Group.status == ACTIVE)).first()
        if group is None:
            raise RuntimeError(f'[load] Group {save_.group_id} not found')

        isfile = is_file(group.path)
        # 备份并删除指定位置存档 防止覆盖文件后无法恢复
        bak_path = os.path.join(BAK_PATH, str(time.time_ns()))
        os.mkdir(bak_path)
        bak_path = os.path.join(bak_path, os.path.basename(group.path))
        if isfile:
            shutil.copy(group.path, bak_path)
            os.remove(group.path)
        else:
            shutil.copytree(group.path, bak_path)
            shutil.rmtree(group.path)
        # 复制存档到指定位置
        save_path = os.path.join(SAVE_PATH, str(save_id))
        for root, dirs, files in os.walk(save_path):
            to = os.path.dirname(group.path)
            for file_name in files:
                shutil.copy(os.path.join(root, file_name), os.path.join(to, file_name))
            for dir_name in dirs:
                shutil.copytree(os.path.join(root, dir_name), os.path.join(to, dir_name))
            break  # 只遍历第一层


__all__ = [
    'save',
    'load',
]

if __name__ == '__main__':
    pass
