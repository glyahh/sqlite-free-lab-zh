#!/usr/bin/env python3
"""Offline SQLite backup bundles; never overwrite an existing restore target."""
import argparse
from contextlib import closing
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import tempfile
import time


def digest(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def connect_ro(path, immutable=False):
    p = Path(path).absolute()
    if not p.is_file() or p.is_symlink():
        raise ValueError('源必须是存在的普通文件，不接受符号链接')
    return sqlite3.connect(p.as_uri() + '?mode=ro' + ('&immutable=1' if immutable else ''), uri=True, timeout=0.1)


def integrity(con):
    result = con.execute('PRAGMA integrity_check').fetchall()
    if result != [('ok',)]:
        raise ValueError('SQLite 完整性检查失败')


def backup(source, output, seconds=30):
    source, output = Path(source).absolute(), Path(output).absolute()
    if seconds <= 0:
        raise ValueError('超时必须大于零')
    # Exclusive mkdir: refusal, rather than accidental replacement of old backups.
    output.mkdir(mode=0o700, parents=False, exist_ok=False)
    try:
        db = output / 'snapshot.db'
        deadline = time.monotonic() + seconds
        def progress(status, remaining, total):
            if time.monotonic() > deadline:
                raise TimeoutError('备份超过时间预算；已取消，请降低写入负载后重试')
        with closing(connect_ro(source)) as src, closing(sqlite3.connect(db)) as dst:
            src.backup(dst, pages=128, progress=progress, sleep=0.05)
            # A standalone snapshot must not rely on a sidecar WAL.
            dst.execute('PRAGMA journal_mode=DELETE')
            integrity(dst)
        os.chmod(db, 0o600)
        manifest = {'format': 1, 'sha256': digest(db), 'bytes': db.stat().st_size,
                    'sqlite_version': sqlite3.sqlite_version, 'created_utc': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
        (output / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        os.chmod(output, 0o700)
        return manifest
    except BaseException:
        shutil.rmtree(output)
        raise


def verify(bundle):
    bundle = Path(bundle)
    db = bundle / 'snapshot.db'
    manifest = json.loads((bundle / 'manifest.json').read_text(encoding='utf-8'))
    if manifest.get('format') != 1 or db.is_symlink():
        raise ValueError('不支持的备份格式或符号链接')
    if db.stat().st_size != manifest['bytes'] or digest(db) != manifest['sha256']:
        raise ValueError('备份大小或 SHA-256 不匹配')
    with closing(connect_ro(db, immutable=True)) as con:
        integrity(con)
    return manifest


def restore(bundle, target):
    manifest = verify(bundle)
    target = Path(target).absolute()
    if target.exists() or target.is_symlink():
        raise FileExistsError('恢复目标已存在；禁止覆盖')
    if any(Path(str(target) + suffix).exists() for suffix in ('-wal', '-shm', '-journal')):
        raise FileExistsError('恢复目标有遗留 SQLite 边车文件；请使用新文件名')
    fd, temp = tempfile.mkstemp(prefix='.rescue-', dir=target.parent)
    try:
        with os.fdopen(fd, 'wb') as out, open(Path(bundle) / 'snapshot.db', 'rb') as src:
            shutil.copyfileobj(src, out)
            out.flush()
            os.fsync(out.fileno())
        if digest(temp) != manifest['sha256']:
            raise ValueError('复制期间备份发生变化')
        # Atomic no-clobber publish on filesystems supporting hard links.
        os.link(temp, target)
    finally:
        os.unlink(temp)
    return manifest


def main():
    parser = argparse.ArgumentParser(description='SQLite 备份、校验和不覆盖恢复工具（标准库，无网络）')
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('backup'); p.add_argument('source'); p.add_argument('bundle'); p.add_argument('--timeout', type=float, default=30)
    p = sub.add_parser('verify'); p.add_argument('bundle')
    p = sub.add_parser('restore'); p.add_argument('bundle'); p.add_argument('target')
    args = parser.parse_args()
    try:
        if args.command == 'backup': result = backup(args.source, args.bundle, args.timeout)
        elif args.command == 'verify': result = verify(args.bundle)
        else: result = restore(args.bundle, args.target)
        print(json.dumps({'ok': True, **result}, ensure_ascii=False))
        return 0
    except (OSError, ValueError, KeyError, sqlite3.Error, TimeoutError) as exc:
        print(json.dumps({'ok': False, 'error': str(exc)}, ensure_ascii=False))
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
