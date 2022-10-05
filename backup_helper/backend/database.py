import logging
import os
from contextlib import contextmanager
from datetime import datetime

from sqlalchemy import Column, Integer, Text, DateTime, create_engine, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from backup_helper.common import DATA_PATH

Base = declarative_base()


# 存档表
class Save(Base):
    __tablename__ = 'save'

    id = Column(Integer, primary_key=True, autoincrement=True)  # ID
    name = Column(Text)  # 存档名
    group_id = Column(Integer, index=True)  # 游戏名
    status = Column(String(20), index=True)  # 状态： 'active' | 'deleted'
    ctime = Column(DateTime, default=datetime.now)  # 创建时间
    mtime = Column(DateTime, default=datetime.now, onupdate=datetime.now)  # 修改时间


# 更新存档日志表
class Group(Base):
    __tablename__ = 'group'

    id = Column(Integer, primary_key=True, autoincrement=True)  # ID
    name = Column(Text, index=True)
    path = Column(Text)
    status = Column(String(20), index=True)  # 状态： 'active' | 'deleted'
    ctime = Column(DateTime, default=datetime.now)  # 创建时间
    mtime = Column(DateTime, default=datetime.now, onupdate=datetime.now)  # 修改时间


path = os.path.join(DATA_PATH, 'database.sqlite3')
engine = create_engine(f'sqlite:///{path}')
SessionMaker = sessionmaker(bind=engine)

# 当表不存在时创建表
Save.__table__.create(bind=engine, checkfirst=True)
Group.__table__.create(bind=engine, checkfirst=True)


@contextmanager
def session() -> Session:
    try:
        s = SessionMaker()
        yield s
        s.commit()
    except Exception as e:
        logging.exception(e)
        raise


__all__ = [
    'Save',
    'Group',
    'session',
]

if __name__ == '__main__':
    pass
