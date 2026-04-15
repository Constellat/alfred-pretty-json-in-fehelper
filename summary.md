# alfred-pretty-json-in-fehelper

## 项目概述

一个 Alfred Workflow，用于将剪贴板中的 JSON 或 Python dict 内容，经过清洗转换后，在浏览器的 [FeHelper](https://chrome.google.com/webstore/detail/fehelper/pkgccpejnmalmdinmhkkfafefagiiiad) 插件中格式化展示。

## 使用场景

开发者日常调试时，经常需要查看 JSON 数据或 Python `print()` 输出的字典内容。直接粘贴到 FeHelper 时，Python 特有的语法（如 `None`、`True`、`False`、`datetime` 对象）会导致 JSON 解析失败。本工具会自动将这些内容预处理为合法 JSON，再一键打开 FeHelper 展示。

## 使用方式

1. 复制 JSON 或 Python dict 内容（`Cmd+C`）
2. 打开 Alfred，输入关键词 `json` 并回车
3. 自动在 Microsoft Edge 中打开 FeHelper JSON 格式化页面并展示结果

## 核心逻辑（pattern.py）

脚本执行流程：

1. **读取剪贴板**：通过 `pyperclip` 获取当前剪贴板文本
2. **Python 语法转换**：
   - `None` → `"None"`
   - `True` → `"True"`
   - `False` → `"False"`
   - `"""..."""`（三引号）→ `"..."`（普通双引号）
3. **datetime 对象转换**：
   - `datetime.datetime(2024, 1, 15, 10, 30, 0)` → `"2024-01-15 10:30:00"`
   - `datetime.date(2024, 1, 15)` → `"2024-01-15"`
4. **CSV 行数据转 JSON 数组**：若剪贴板内容为换行分隔的纯文本（每行仅含字母/数字/`@`/`.`），自动转换为 `["item1","item2",...]` 格式
5. **写回剪贴板**：将处理后的内容重新写入剪贴板
6. **自动打开浏览器**：通过 AppleScript 在 Microsoft Edge 中打开 FeHelper JSON 格式化页面，并自动粘贴内容

## 依赖

| 依赖 | 说明 |
|------|------|
| Alfred | macOS 效率启动器，需支持 Workflow |
| Python 3 + pyperclip | 运行 `pattern.py` 脚本 |
| Microsoft Edge | 目标浏览器（可通过参数修改） |
| FeHelper 插件 | Chrome/Edge 前端助手插件，提供 JSON 格式化功能 |

## 参数说明

`pattern.py` 支持两个命令行参数：

```bash
python pattern.py "<浏览器名称>" "<FeHelper JSON页面URL>"
```

默认值：
- 浏览器：`Microsoft Edge`
- URL：`chrome-extension://feolnkbgcbjmamimpfcnklggdcbgakhe/json-format/index.html`
