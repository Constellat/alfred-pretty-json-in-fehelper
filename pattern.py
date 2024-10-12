#!/usr/bin/env python
# coding:utf-8

import sys
import pyperclip
from subprocess import Popen, PIPE
import re

# 获取指定位置的参数
args = sys.argv
arg1 = args[1] if len(args) > 1 else "Microsoft Edge"
arg2 = args[2] if len(args) > 2 else "chrome-extension://feolnkbgcbjmamimpfcnklggdcbgakhe/json-format/index.html"

application = arg1
jsonUrl = arg2

## 实现复制当前选中或者复制的
# script = "set the clipboard to selection"
# proc = Popen(['osascript', '-'], stdin=PIPE, stdout=PIPE, universal_newlines=True)
# out = proc.communicate(script)[0]

# 获取当前剪贴板内容
out_string = pyperclip.paste()

# 处理常见的Python内属性 如: None False True
out_string = re.sub('(?<=:)None(?=(\s*[,}]))', '"None"', out_string)
out_string = re.sub('(?<=:\s)None(?=(\s*[,}]))', '"None"', out_string)
out_string = re.sub('(?<=:)False(?=(\s*[,}]))', '"False"', out_string)
out_string = re.sub('(?<=:\s)False(?=(\s*[,}]))', '"False"', out_string)
out_string = re.sub('(?<=:)True(?=(\s*[,}]))', '"True"', out_string)
out_string = re.sub('(?<=:\s)True(?=(\s*[,}]))', '"True"', out_string)
# 处理时间常见的datetime
datetime_pattern_list = re.findall('(?<=:\s)datetime\.datetime\(([\d, ]*)\)(?=(\s*[,}]))', out_string)
for _datetime_pattern, _ in datetime_pattern_list:
    datetime_list = _datetime_pattern.split(', ')
    date_list = list(map(lambda _: str(_) if int(_) > 9 else '0' + str(_), datetime_list[0:3]))
    date_str = '-'.join(date_list)
    time_list = list(map(lambda _: str(_) if int(_) > 9 else '0' + str(_), datetime_list[3:]))
    time_str = ':'.join(time_list)
    datetime_str = '"' + date_str + " " + time_str + '"'
    out_string = re.sub(f'(?<=:\s)datetime\.datetime\({_datetime_pattern}\)(?=(\s*[,' + '}]))',
                        datetime_str,
                        out_string)

# 处理csv数据为数组， 1\n2\n3 变为 [1,2,3]
is_list = True
info_list = out_string.split('\n')
for i in range(len(info_list)):
    _info = info_list[i]
    if not _info:
        continue
    if _info[0] == '"' and _info[-1] == '"':
        continue
    # 字符中包含非预想字符，不进行处理
    is_not_all_word = re.search(r'[^\w@\.]', _info)
    if is_not_all_word:
        is_list = False
        break
    # 如果包含非数字字符，考虑是否前后加上"
    is_not_all_digit = re.search(r'[\D]', _info)
    if is_not_all_digit:
        info_list[i] = '"' + _info + '"'
if is_list:
    info_list = [_ for _ in info_list if _]
    list_string = ','.join(info_list)
    list_string = '[' + list_string + ']'
    out_string = list_string

print(out_string)
out_string = str(out_string)

# 复制修改后的内容到剪贴板
pyperclip.copy(out_string)

## 实现 打开tab标签
script = """
set jsonUrl to "{}"
tell application "{}"
	activate
	open location jsonUrl
	delay 0.5
	set tab1 to (active tab of window 0)
	paste selection tab1
end tell
""".format(jsonUrl, application)
# print(script)
proc = Popen(['osascript', '-'], stdin=PIPE, stdout=PIPE, universal_newlines=True)
out = proc.communicate(script)[0]
