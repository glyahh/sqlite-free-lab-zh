# 官方来源与许可核对

核对日期：2026-10-29。以下为官方一手页面，摘要为原创改述，未复制上游教程或源码。

1. Python sqlite3：<https://docs.python.org/3/library/sqlite3.html>。`Connection.backup()` 提供数据库备份接口，支持分页和进度回调；模块可能是可选模块，须先验证安装。
2. SQLite Online Backup API：<https://www.sqlite.org/backup.html>。在线备份 API 为数据库建立快照，避免依赖不受协调的文件复制。本包只使用该 API，不直接解析 SQLite 文件。
3. SQLite 官方版权声明：<https://www.sqlite.org/copyright.html>。SQLite 可交付代码和文档奉献为公共领域，可商业或非商业使用；构建脚本可能有其他许可。公共领域不被承认的辖区或需要权属保证的组织，应进行专门法律核查。
4. Python 官方许可：<https://docs.python.org/3/license.html>。Python 软件和文档采用 PSF License Version 2；部分内含组件另有许可，文档代码示例自指定版本起双许可。本包不捆绑 Python 可执行文件或上游源码，避免把解释器分发义务错误简化为本包 MIT。

## 本包权利清单

- 原创 Python CLI、测试、演示数据、中文教材：本包 LICENSE 的 MIT 文本；没有引入第三方 Python 包。
- SQLite/Python：仅依赖用户已有安装，不重新授权、不声称独家、不售卖其所有权。
- 不含商标素材、客户数据库、第三方付费课程或抓取内容。
- “官方技术来源”不表示获得官方背书。
- 如果将来改为分发解释器、数据库二进制或其他依赖，发布前必须重新整理第三方 NOTICE 与许可证，不沿用本清单当成覆盖全部依赖的法律意见。
