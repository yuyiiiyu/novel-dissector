# -*- coding: utf-8 -*-
"""统一所有 HTML 的导航栏（五页互链 + 总览 + 报告）"""
import os, re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

WEB = r"D:\aigc_pro\ai-video&draw\DeepSeek Harness\@ D Download 这个人明明很强却_2026-10-27\产出"

NAV_ITEMS = [
    ("可视化总览.html", "总览"),
    ("情感曲线.html", "① 情感曲线"),
    ("人物关系网.html", "② 关系网"),
    ("灌水高潮热力图.html", "③ 热力图"),
    ("语言指纹.html", "④ 语言指纹"),
    ("转折点分析.html", "⑤ 转折点"),
]

def build_nav(cur):
    a = '<a href="可视化总览.html"{}>总览</a>'.format(
        ' class="on"' if cur == "可视化总览.html" else "")
    rest = "".join(
        '<a href="{}"{}>{}</a>'.format(f, ' class="on"' if f == cur else "", t)
        for f, t in NAV_ITEMS[1:])
    rep = '<a href="拆解总报告.md">📄 总报告</a>'
    return ('<div class="nav">\n ' + a + "\n " + rest + "\n " + rep + "\n</div>")

for fn in [x[0] for x in NAV_ITEMS]:
    p = os.path.join(WEB, fn)
    h = open(p, encoding="utf-8").read()
    # 匹配现有 nav 块
    m = re.search(r'<div class="nav">.*?</div>', h, re.S)
    if not m:
        print(f"  ✗ {fn} 未找到 nav 块")
        continue
    old = m.group(0)
    new = build_nav(fn)
    if old.strip() == new.strip():
        print(f"  · {fn} 已是最新")
        continue
    h = h.replace(old, new, 1)
    open(p, "w", encoding="utf-8").write(h)
    print(f"  ✓ {fn} 导航已更新")

print("\n=== 校验 ===")
for fn in [x[0] for x in NAV_ITEMS]:
    p = os.path.join(WEB, fn)
    h = open(p, encoding="utf-8").read()
    links = re.findall(r'href="([^"]+\.html)"', h)
    miss = [l for l in set(links) if not os.path.exists(os.path.join(WEB, l))]
    on = re.findall(r'class="on"', h)
    print(f"  {fn:22s} 链接{len(set(links))}个 高亮{len(on)}个 "
          + ("缺失:" + ",".join(miss) if miss else "✓"))
