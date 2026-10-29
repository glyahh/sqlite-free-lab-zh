#!/usr/bin/env python3
"""Read-only exact-row acceptance of the original practice snapshot."""
import sqlite3
import sys
from pathlib import Path

p = Path(sys.argv[1] if len(sys.argv) > 1 else 'recovered.db').absolute()
with sqlite3.connect(p.as_uri() + '?mode=ro', uri=True) as con:
    rows = con.execute('SELECT id, title, done FROM tasks ORDER BY id').fetchall()
expected = [
    (1, '练习：创建本地数据库', 1),
    (2, '练习：备份并校验', 0),
    (3, '练习：恢复到新文件', 0),
]
if rows != expected:
    raise SystemExit('业务验收失败：任务编号、标题或逐条完成状态不符合练习初始数据')
print('业务验收通过：3 条任务，完成 1 条；中文内容一致。')
