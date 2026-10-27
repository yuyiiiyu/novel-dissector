# -*- coding: utf-8 -*-
"""修正总览页核心发现的顺序（第4条应在第3条之后）"""
import os, re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

WEB = r"D:\aigc_pro\ai-video&draw\DeepSeek Harness\@ D Download 这个人明明很强却_2026-10-27\产出"
p = os.path.join(WEB, "可视化总览.html")
h = open(p, encoding="utf-8").read()

# 切出所有 fi 块
blocks = re.findall(r'<div class="fi">.*?</div>', h, re.S)
print("发现 fi 块：", len(blocks))
for i, b in enumerate(blocks):
    m = re.search(r"<b>(\d)\.", b)
    print(f"  [{i}] 编号 {m.group(1) if m else '?'} | {b[:46]}")

# 按编号重排
def num(b):
    m = re.search(r"<b>(\d)\.", b)
    return int(m.group(1)) if m else 99

order = sorted(range(len(blocks)), key=lambda i: num(blocks[i]))
print("重排后顺序：", [num(blocks[i]) for i in order])

# 只替换编号 1-4 的块（保留其它）
idx4 = [i for i in range(len(blocks)) if num(blocks[i]) <= 4]
sorted4 = sorted(idx4, key=lambda i: num(blocks[i]))
new_blocks = list(blocks)
for pos, orig in zip(idx4, sorted4):
    new_blocks[pos] = blocks[orig]

for pos, orig in zip(idx4, sorted4):
    h = h.replace(blocks[pos], "@@TMP%d@@" % pos, 1) if False else h

# 逐个替换（用唯一占位符）
for pos in idx4:
    h = h.replace(blocks[pos], "@@PH%d@@" % pos, 1)
for pos, orig in zip(idx4, sorted4):
    h = h.replace("@@PH%d@@" % pos, blocks[orig], 1)

open(p, "w", encoding="utf-8").write(h)
print("✓ 顺序已修正")

# 验证
h2 = open(p, encoding="utf-8").read()
b2 = re.findall(r'<div class="fi">.*?</div>', h2, re.S)
print("校验顺序：", [num(b) for b in b2])
