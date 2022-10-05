from typing import List, Optional

from sqlalchemy.orm import Session, Query

from backup_helper.backend.database import session, Group, Save
from backup_helper.common import ACTIVE, DELETE


def add_group(name: str, path: str) -> None:
    with session() as s:  # type: Session
        s.add(Group(name=name, path=path, status=ACTIVE))


def get_group() -> List[Group]:
    with session() as s:  # type: Session
        groups = s.query(Group).filter(Group.status == ACTIVE).all()
        s.expunge_all()
        return groups


def update_group(group_id: int, name: Optional[str] = None, path: Optional[str] = None,
                 status: Optional[str] = None) -> None:
    update = {}
    if name is not None:
        update[Group.name] = name
    if path is not None:
        update[Group.path] = path
    if status is not None:
        update[Group.status] = status
    with session() as s:  # type: Session
        s.query(Group).filter(Group.id == group_id).update(update)


def delete_group(group_id: int) -> None:
    with session() as s:
        s.query(Group).filter(Group.id == group_id).update({Group.status: DELETE})
        s.query(Save).filter(Save.group_id == group_id).update({Save.status: DELETE})

def get_save(name: Optional[str] = None, group_name: Optional[str] = None) -> List:
    with session() as s:  # type: Session
        q: Query = s.query(Save, Group).filter(Save.status == ACTIVE)
        q = q.filter(Save.group_id == Group.id and Group.status == ACTIVE)
        if name is not None:
            q = q.filter(Save.name.like(f'%{name}%'))
        if group_name is not None:
            q = q.filter(Group.name.like(f'%{group_name}%'))
        ret = q.all()
        s.expunge_all()
        return ret


def update_save(save_id: int, name: Optional[str] = None, status: Optional[str] = None) -> None:
    update = {}
    if name is not None:
        update[Group.name] = name
    if status is not None:
        update[Group.status] = status
    with session() as s:  # type: Session
        s.query(Save).filter(Save.id == save_id).update(update)


if __name__ == '__main__':
    pass
