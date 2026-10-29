#!/usr/bin/env python3
"""Black-box tutorial replay in a fresh temporary directory, no product imports."""
import hashlib
import json
from pathlib import Path
import platform
import shutil
import sqlite3
import subprocess
import sys
import tempfile

root=Path(__file__).resolve().parent
records=[]
with tempfile.TemporaryDirectory(prefix='sqlite-free-lab-') as tmp:
    cwd=Path(tmp)
    for name in ['rescue.py','make_sample.py','check_sample.py']:
        shutil.copyfile(root/name,cwd/name)
    def run(args,expected=0):
        p=subprocess.run([sys.executable,*args],cwd=cwd,text=True,capture_output=True)
        records.append({'args':args,'expected_exit':expected,'actual_exit':p.returncode,'stdout':p.stdout.strip(),'stderr':p.stderr.strip() if p.returncode!=expected else ''})
        assert p.returncode==expected,records[-1]
    run(['make_sample.py'])
    run(['check_sample.py','practice.db'])
    # Same row count, same titles, same aggregate done=1; wrong per-row state.
    shutil.copyfile(cwd/'practice.db', cwd/'swapped.db')
    run(['-c','import sqlite3; c=sqlite3.connect("file:swapped.db?mode=rw", uri=True); c.execute("UPDATE tasks SET done=CASE id WHEN 2 THEN 1 ELSE 0 END"); c.commit(); c.close()'])
    with sqlite3.connect(cwd/'swapped.db') as c:
        assert c.execute('SELECT count(*), sum(done) FROM tasks').fetchone()==(3,1)
    run(['check_sample.py','swapped.db'],expected=1)
    run(['rescue.py','backup','practice.db','checkpoint'])
    run(['rescue.py','verify','checkpoint'])
    run(['-c','import sqlite3; c=sqlite3.connect("file:practice.db?mode=rw", uri=True); c.execute("UPDATE tasks SET done=1"); c.commit(); c.close()'])
    run(['check_sample.py','practice.db'],expected=1)
    modified=hashlib.sha256((cwd/'practice.db').read_bytes()).hexdigest()
    run(['rescue.py','restore','checkpoint','recovered.db'])
    run(['check_sample.py','recovered.db'])
    run(['rescue.py','restore','checkpoint','recovered.db'],expected=2)
    assert hashlib.sha256((cwd/'practice.db').read_bytes()).hexdigest()==modified
    with sqlite3.connect(cwd/'practice.db') as c:
        assert c.execute('SELECT sum(done) FROM tasks').fetchone()==(3,)
    with sqlite3.connect(cwd/'recovered.db') as c:
        assert c.execute('SELECT sum(done) FROM tasks').fetchone()==(1,)
print(json.dumps({'status':'PASS','platform':platform.system(),'python':platform.python_version(),'sqlite':sqlite3.sqlite_version,'step_count':len(records),'original_after_restore':'3 completed; unchanged by restore','restored':'1 completed','steps':records},ensure_ascii=False,indent=2))
