#!/usr/bin/env python3
"""Original synthetic practice data only. Refuse overwrite. No network."""
import os
from pathlib import Path
import sqlite3

path = Path('practice.db')
fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
os.close(fd)
con = sqlite3.connect(path)
try:
    con.execute('CREATE TABLE tasks(id INTEGER PRIMARY KEY, title TEXT NOT NULL, done INTEGER NOT NULL CHECK(done IN (0,1)))')
    con.executemany('INSERT INTO tasks VALUES(?,?,?)', [
        (1, '练习：创建本地数据库', 1),
        (2, '练习：备份并校验', 0),
        (3, '练习：恢复到新文件', 0),
    ])
    con.commit()
finally:
    con.close()
print('已创建 practice.db；3 条虚构任务，完成 1 条。已有文件不会覆盖。')
