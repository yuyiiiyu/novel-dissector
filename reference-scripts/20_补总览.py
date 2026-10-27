# -*- coding: utf-8 -*-
"""向可视化总览.html 插入第 4 条核心发现"""
import os, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

WEB = r"D:\aigc_pro\ai-video&draw\DeepSeek Harness\@ D Download 这个人明明很强却_2026-10-27\产出"
p = os.path.join(WEB, "可视化总览.html")
h = open(p, encoding="utf-8").read()

OLD = """<div class="fi"><b>3. 甜度峰值在第三卷，早于战斗峰值。</b>"""
NEW = """<div class="fi"><b>4. 四条曲线在第 501 章同时转折。</b>
心声 <b style="color:#dc2626">\u221267%</b>、甜度 <b style="color:#dc2626">\u221268%</b>、
战斗 <b style="color:#16a34a">+89%</b> \u2014\u2014 作者在同一章按下三个开关。
心声 vs 灌水率相关系数 <b>r = \u22120.844\uff08\u5f3a\u8d1f\u76f8\u5173\uff09</b>\uff1a
\u559c\u5267\u673a\u5236\u9000\u5734\u4e0e\u8282\u594f\u5854\u9677\u5b8c\u5168\u540c\u6b65\u3002
\u2192 <a href="\u8f6c\u6298\u70b9\u5206\u6790.html" style="color:#0ea5e9">\u770b\u53cc\u89c6\u56fe\u53e0\u5408</a></div>

<div class="fi"><b>3. \u751c\u5ea6\u5cf0\u503c\u5728\u7b2c\u4e09\u5377\uff0c\u65e9\u4e8e\u6218\u6597\u5cf0\u503c\u3002</b>"""

if "四条曲线在第 501 章" in h:
    print("已存在，跳过")
elif OLD in h:
    h = h.replace(OLD, NEW, 1)
    open(p, "w", encoding="utf-8").write(h)
    print("✓ 已插入第 4 条核心发现")
else:
    print("✗ 未找到锚点")
