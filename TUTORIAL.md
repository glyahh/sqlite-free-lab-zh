# 免费小课：备份了 SQLite，真的能恢复吗？

**亲手验证一次备份与恢复。** 这是一份免费中文实战练习，全部样本为原创虚构任务；不需要注册、付费、API Key 或 pip。本包不收集资料、不联网上传。

我们只做一件事：把一个小数据库备份，再恢复到**新文件**，确认表里的内容正确。不要拿生产数据库开始练习，也不要把本课当作生产灾备方案。

## 准备：在空练习目录中解压

兼容目标为 Python 3.10+ 且带 `sqlite3` 模块即可。以下命令针对 Linux／macOS 的终端写法；**实际仅在 Linux、Python 3.12.14、SQLite 3.53.1 验证**。其他平台未验证。运行前先切换到解压后含 `qa_lab.py` 的目录。

```sh
python3 -c 'import sqlite3; print(sqlite3.sqlite_version)'
```

若提示没有 Python 或 sqlite3，请先处理自己的 Python 安装；本课不下载或更改系统软件。恢复文件所在磁盘必须支持硬链接。

## 第一步：造一份无隐私样本

```sh
python3 make_sample.py
python3 check_sample.py practice.db
```

预期：`业务验收通过：3 条任务，完成 1 条；中文内容一致。`

样本只有编号、练习标题和完成状态，没有客户资料、账号、密码、真实订单或联系人。脚本遇到已有 `practice.db` 会报错拒绝覆盖；重复练习请换一个新解压目录。

## 第二步：备份，再校验

```sh
python3 rescue.py backup practice.db checkpoint
python3 rescue.py verify checkpoint
```

两次输出都应含 `"ok": true`。`checkpoint/` 下有快照 `snapshot.db` 和记录字节数、SHA-256 的 `manifest.json`。工具使用 Python 的 SQLite Backup API，而不是直接复制数据库主文件。[官方接口](https://docs.python.org/3/library/sqlite3.html#sqlite3.Connection.backup)

为什么不直接复制？开启 WAL 模式时，已提交内容可能还在 `-wal` 文件里，仅复制主文件可能遗漏内容。SQLite 官方介绍了在线备份 API 的用途。[官方说明](https://www.sqlite.org/backup.html)

## 第三步：模拟“一次误改”

下面命令**只针对本课刚生成的 `practice.db`**，把所有练习任务标为完成。不要替换成真实数据库路径。

```sh
python3 -c 'import sqlite3; c=sqlite3.connect("file:practice.db?mode=rw", uri=True); c.execute("UPDATE tasks SET done=1"); c.commit(); c.close()'
python3 check_sample.py practice.db
```

这一次**应失败**，出现“业务验收失败”。这是有意制造的状态变化，并不意味着备份坏了。

## 第四步：恢复，但绝不覆盖原文件

```sh
python3 rescue.py restore checkpoint recovered.db
python3 check_sample.py recovered.db
```

预期：恢复输出 `"ok": true`，业务验收再次通过。说明恢复副本回到了“3 条任务、完成 1 条”的备份状态。原来的 `practice.db` 仍保持改后的状态，我们没有偷偷覆盖它。

再运行同一条恢复命令，会输出 `"ok": false` 和“恢复目标已存在；禁止覆盖”，退出码为 2。这是保护机制，不要为了让命令成功就随意删除重要文件。

## 你刚刚学会的关键区别

- **校验成功**：备份文件与清单匹配，SQLite 内部完整性检查通过。
- **恢复成功**：能把备份复制到一个新路径。
- **业务验收成功**：你的查询证实业务内容符合预期。本课逐行比对任务编号、中文标题和完成状态（不是只比较总完成数）；真实系统要自己定义正确标准。

三件事不是一回事。只有“备份命令没报错”，并不能证明应用能够恢复服务。

## 真实限制，请读完再迁移到自己的项目

1. 本课不修复损坏数据库，不恢复备份之后的修改，不备份外部附件或 ATTACH 的其他数据库。
2. SHA-256 不是加密或签名；有人同时改快照和清单时，不能靠它证明来源可信。
3. 只使用自己控制的本地目录和可信数据库，练习期间不要让其他程序写入备份或恢复目标。
4. 没有大型数据库、高并发、断电、磁盘满、网络磁盘或跨平台保证。恢复依赖硬链接，掉电持久性并未全面实现。
5. 工具不自动切换应用数据库，不代办生产维护，不含托管、人工支持或持续更新承诺。
6. 备份不加密。真实数据库可能含个人信息与密钥，不要放进公开仓库或上传给陌生人。

本课原创源码与文字按 MIT 许可提供，允许商用和改编，须保留许可声明；Python／SQLite 仍适用各自权利声明，见 `LICENSE`、`SOURCES.md`。免费材料不代表官方背书。

**完成标准：你能解释为什么恢复到了新文件，并亲眼看到恢复副本通过业务验收。**
