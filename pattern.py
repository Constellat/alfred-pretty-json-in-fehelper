#!/usr/bin/env python
# coding:utf-8
#
# Alfred Workflow: Pretty JSON in FeHelper
#
# 用法：python pattern.py "<浏览器名称>" "<FeHelper JSON页面URL>"
#
# 功能：读取剪贴板内容，将 Python dict/CSV 数据清洗为合法 JSON，
#       写回剪贴板，并通过 AppleScript 在浏览器 FeHelper 插件中格式化展示。

import sys
import re
import pyperclip
from subprocess import Popen, PIPE

# 从命令行参数获取目标浏览器和 FeHelper URL，均有默认值
args = sys.argv
application = args[1] if len(args) > 1 else "Microsoft Edge"
json_url = args[2] if len(args) > 2 else "chrome-extension://feolnkbgcbjmamimpfcnklggdcbgakhe/json-format/index.html"

# 读取当前剪贴板内容
out_string = pyperclip.paste()

# ── Python 字面量 → JSON 合法字符串 ──────────────────────────────────────────
# Python dict 中 None/True/False 不是合法 JSON，替换为带引号的字符串形式。
# 匹配模式：冒号后（允许任意空格）紧跟字面量，且其后为逗号或 } （即 dict value 位置）。
for literal in ('None', 'True', 'False'):
    out_string = re.sub(rf'(:\s*){literal}(?=\s*[,}}])', rf'\1"{literal}"', out_string)

# ── 三引号字符串 → 普通双引号字符串 ─────────────────────────────────────────
# Python 多行字符串 """...""" 不是合法 JSON，去掉多余的两个引号。
# 分两步：先替换开头的 """，再替换结尾的 """。
out_string = re.sub(r'(:\s*)"""', r'\1"', out_string)   # 开头：: """ → : "
out_string = re.sub(r'"""(?=\s*[,}])', '"', out_string)  # 结尾：""" → "

# ── datetime.datetime → ISO 格式字符串 ──────────────────────────────────────
# 将 datetime.datetime(y, m, d, H, M, S) 替换为 "YYYY-MM-DD HH:MM:SS"。
# 时间部分（H, M, S）可选：若缺省则默认补 00:00:00。
# 使用 re.split(r',\s*') 兼容有无空格的写法（如 datetime(2024,1,1) 或 datetime(2024, 1, 1)）。
def _fmt_datetime(m):
    prefix = m.group(1)                                             # 保留冒号及其后的空格
    parts = [p.strip().zfill(2) for p in re.split(r',\s*', m.group(2))]  # 各数字补零至2位
    date_str = '-'.join(parts[:3])                                  # YYYY-MM-DD
    time_str = ':'.join(parts[3:]) if parts[3:] else '00:00:00'    # HH:MM:SS
    return f'{prefix}"{date_str} {time_str}"'

out_string = re.sub(r'(:\s*)datetime\.datetime\(([\d, ]*)\)(?=\s*[,}])', _fmt_datetime, out_string)

# ── datetime.date → ISO 日期字符串 ───────────────────────────────────────────
# 将 datetime.date(y, m, d) 替换为 "YYYY-MM-DD"。
def _fmt_date(m):
    prefix = m.group(1)
    parts = [p.strip().zfill(2) for p in re.split(r',\s*', m.group(2))]
    return f'{prefix}"{"-".join(parts)}"'

out_string = re.sub(r'(:\s*)datetime\.date\(([\d, ]*)\)(?=\s*[,}])', _fmt_date, out_string)

# ── 换行分隔的纯文本 → JSON 数组 ────────────────────────────────────────────
# 若剪贴板内容每行均为纯字母/数字/邮箱/域名格式（不含 {}[](): 等特殊字符），
# 则认为是 CSV 列表数据，整体转换为 JSON 数组 ["a", "b", ...] 或 [1, 2, ...]。
# 纯数字行不加引号，含字母的行加引号。
is_list = True
info_list = out_string.split('\n')
for i, item in enumerate(info_list):
    if not item:                              # 跳过空行
        continue
    if item[0] == '"' and item[-1] == '"':   # 已带引号，无需处理
        continue
    if re.search(r'[^\w@.]', item):          # 含特殊字符（如 {, :, [ 等），说明不是简单列表
        is_list = False
        break
    if re.search(r'\D', item):               # 含非数字字符 → 字符串，加引号
        info_list[i] = f'"{item}"'
    # 纯数字 → JSON number，不加引号

if is_list:
    info_list = [item for item in info_list if item]  # 过滤空行
    out_string = '[' + ','.join(info_list) + ']'

print(out_string)

# 将处理后的内容写回剪贴板，供 FeHelper 页面读取
pyperclip.copy(out_string)

# ── 通过 AppleScript 打开浏览器并粘贴内容 ───────────────────────────────────
# 1. 激活目标浏览器
# 2. 打开 FeHelper JSON 格式化页面（open location 会复用已有 tab 或新建）
# 3. 等待页面加载后，向当前 tab 发送粘贴命令，触发 FeHelper 自动解析剪贴板中的 JSON
script = """
set jsonUrl to "{}"
tell application "{}"
    activate
    open location jsonUrl
    delay 0.5
    set tab1 to (active tab of window 0)
    paste selection tab1
end tell
""".format(json_url, application)

proc = Popen(['osascript', '-'], stdin=PIPE, stdout=PIPE, universal_newlines=True)
proc.communicate(script)
