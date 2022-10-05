import os
import re
import sys


def get_root():
    executable = sys.executable
    if len(executable) > 0:
        executable = executable.split('/')[-1]
        executable = executable.split('\\')[-1]
        if re.match('python', executable) is not None:
            path = os.path.abspath(__file__)
            return os.path.dirname(os.path.dirname(path))
    return os.getcwd()


ROOT_PATH = get_root()
DATA_PATH = os.path.join(ROOT_PATH, '.data')
SAVE_PATH = os.path.join(DATA_PATH, 'save')
BAK_PATH = os.path.join(DATA_PATH, 'bak')

# 自动创建数据文件夹
for path in (DATA_PATH, SAVE_PATH, BAK_PATH):
    if not os.path.exists(path):
        os.mkdir(path)

ACTIVE = 'active'
DELETE = 'delete'

if __name__ == '__main__':
    pass
