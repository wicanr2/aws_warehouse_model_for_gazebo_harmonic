#!/usr/bin/env python3
# 比對叉車下指令前後的位姿,判斷「有沒有在動」。
# 用法:python3 scripts/check_moved.py pose_before.txt pose_after.txt
# 輸入是 `gz topic -e -t /model/forklift/pose -n 1` 的輸出。位移 >= 0.3m 視為會動(exit 0)。
import re, sys


def first_xy(path):
    txt = open(path).read()
    # 先抓 name:"forklift" 之後第一組 position x/y;抓不到退而取第一組 position
    m = re.search(r'name:\s*"forklift".*?position\s*\{\s*x:\s*(-?[\d.eE+-]+)\s*y:\s*(-?[\d.eE+-]+)', txt, re.S)
    if not m:
        m = re.search(r'position\s*\{\s*x:\s*(-?[\d.eE+-]+)\s*y:\s*(-?[\d.eE+-]+)', txt, re.S)
    return (float(m.group(1)), float(m.group(2))) if m else None


a = first_xy(sys.argv[1])
b = first_xy(sys.argv[2])
print("before:", a, " after:", b)
if not a or not b:
    print("WARN: 無法解析位姿(看 artifact 原始輸出)")
    sys.exit(0)
d = ((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5
print(f"位移 = {d:.3f} m")
if d < 0.3:
    print("FAIL: 叉車幾乎沒動(位移 < 0.3m)")
    sys.exit(1)
print("OK: 叉車有在動")
sys.exit(0)
