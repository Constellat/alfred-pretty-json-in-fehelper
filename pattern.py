#!/usr/bin/env python
# coding:utf-8


# 获取命令行输入参数
import sys
# 获取指定位置的参数
args = sys.argv
arg1 = args[1] if len(args) > 1 else "Microsoft Edge"
arg2 = args[2] if len(args) > 2 else "chrome-extension://feolnkbgcbjmamimpfcnklggdcbgakhe/json-format/index.html"

application = arg1
jsonUrl = arg2

import pyperclip
from subprocess import Popen, PIPE
## 实现复制当前选中或者复制的
#script = "set the clipboard to selection"
#proc = Popen(['osascript', '-'], stdin=PIPE, stdout=PIPE, universal_newlines=True)
#out = proc.communicate(script)[0]

out_string = pyperclip.paste()
print(out_string)
out_string = str(out_string)

out_string += "//niujianyu_test"
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

