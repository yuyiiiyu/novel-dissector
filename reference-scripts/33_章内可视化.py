# -*- coding: utf-8 -*-
"""阶段17：章内工程学可视化 HTML ⑦"""
import json, os, html, csv

OUT = r"D:\aigc_pro\ai-video&draw\DeepSeek Harness\@ D Download 这个人明明很强却_2026-10-27\产出\data"
WEB = r"D:\aigc_pro\ai-video&draw\DeepSeek Harness\@ D Download 这个人明明很强却_2026-10-27\产出"

ci = json.load(open(os.path.join(OUT, "chapter_internal.json"), encoding="utf-8"))
op = json.load(open(os.path.join(OUT, "opening.json"), encoding="utf-8"))
tmpl, bridge, bv = ci["tmpl"], ci["bridge"], ci["bridge_vol"]
ts, topb, tt = ci["turn_stat"], ci["top_bridge"], ci["turn_top"]
fmode = op["first_mode"]

CJK = "font-family:'PingFang SC','Microsoft YaHei','Noto Sans CJK SC',sans-serif"
def esc(s): return html.escape(str(s))

# ============ 图1：章内节奏模板（折线）============
W1, H1 = 1060, 360
ML1, MT1, PW1, PH1 = 60, 30, 940, 260
KEYS = [("心声", "#f59e0b"), ("对话", "#0ea5e9"), ("战斗", "#ef4444"),
        ("甜度", "#ec4899"), ("感叹", "#8b5cf6"), ("疑问", "#10b981")]
NB = len(tmpl["心声"])

def catmull(pts):
    if len(pts) < 2: return ""
    d = "M%.1f,%.1f" % pts[0]
    for i in range(len(pts)-1):
        p0 = pts[i-1] if i > 0 else pts[i]
        p1, p2 = pts[i], pts[i+1]
        p3 = pts[i+2] if i+2 < len(pts) else p2
        d += (" C%.1f,%.1f %.1f,%.1f %.1f,%.1f"
              % (p1[0]+(p2[0]-p0[0])/6, p1[1]+(p2[1]-p0[1])/6,
                 p2[0]-(p3[0]-p1[0])/6, p2[1]-(p3[1]-p1[1])/6, p2[0], p2[1]))
    return d

# 对话值域远大于其他，单独放右侧轴 → 对话用虚线并缩放到 0-300 视觉高度
mx_all = max(max(tmpl[k]) for k, _ in KEYS)
lines1 = ""
for k, col in KEYS:
    vs = tmpl[k]
    m = max(vs) or 1
    pts = [(ML1 + i*PW1/(NB-1), MT1 + PH1 - v/m*PH1*0.88) for i, v in enumerate(vs)]
    lines1 += ('<path d="%s" fill="none" stroke="%s" stroke-width="2.4" opacity="0.9"/>'
               % (catmull(pts), col))
    for i, (x, y) in enumerate(pts):
        lines1 += ('<circle cx="%.1f" cy="%.1f" r="3.8" fill="%s" stroke="#fff" '
                   'stroke-width="1.6"><title>%s %d%%位置: %.1f</title></circle>'
                   % (x, y, col, k, i*10, vs[i]))
xl1 = "".join('<text x="%.1f" y="%d" font-size="10.5" text-anchor="middle" '
              'fill="#475569" %s>%d%%</text>' % (ML1+i*PW1/(NB-1), MT1+PH1+20, CJK, i*10)
              for i in range(NB))
grid1 = "".join('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="#e2e8f0"/>'
                % (ML1, MT1+PH1*g/4, ML1+PW1, MT1+PH1*g/4) for g in range(5))
leg1 = ""
for i, (k, col) in enumerate(KEYS):
    yy = 100 + i*26
    leg1 += ('<rect x="%d" y="%d" width="13" height="13" rx="3" fill="%s"/>'
             '<text x="%d" y="%d" font-size="12.5" fill="#334155" %s>%s</text>'
             % (W1-140, yy-11, col, W1-122, yy, CJK, k))

# ============ 图2：爽文桥段按卷 ============
W2, H2 = 1060, 300
ML2, MT2, PW2, PH2 = 56, 26, 940, 210
BC = {"震惊": "#f59e0b", "打脸": "#ef4444", "反转": "#8b5cf6"}
mxb = max(max(r["震惊/章"], r["打脸/章"], r["反转/章"]) for r in bv) or 1
bars2 = ""
ngrp = len(bv)
gw = PW2/ngrp
for i, r in enumerate(bv):
    for j, k in enumerate(["震惊", "打脸", "反转"]):
        v = r[k+"/章"]
        bw = gw/3 - 8
        x = ML2 + i*gw + j*(gw/3) + 5
        h = v/mxb*PH2
        bars2 += ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="4" fill="%s" '
                  'opacity="0.88"><title>%s %s %.2f/章</title></rect>'
                  % (x, MT2+PH2-h, bw, h, BC[k], esc(r["卷"][:12]), k, v))
    bars2 += ('<text x="%.0f" y="%d" font-size="10.5" text-anchor="middle" fill="#475569" %s>卷%d</text>'
              % (ML2+i*gw+gw/2, MT2+PH2+18, CJK, i+1))
xl2 = ('<text x="%d" y="%d" font-size="11" fill="#64748b" %s>每章均值（条/章）</text>'
       % (ML2, MT2-8, CJK))

# ============ 图3：开场方式饼 ============
import math
MC = {"短句破题": "#0ea5e9", "场景描写": "#64748b", "对话开场": "#f59e0b",
      "心声开场": "#ec4899", "承接上章": "#8b5cf6"}
totm = sum(fmode.values())
pie2, ang = "", 0
cx3, cy3, R3 = 160, 155, 100
for k, v in sorted(fmode.items(), key=lambda x: -x[1]):
    sw = v/totm*360
    a0, a1 = ang, ang+sw
    x0 = cx3+R3*math.cos(math.radians(a0-90)); y0 = cy3+R3*math.sin(math.radians(a0-90))
    x1 = cx3+R3*math.cos(math.radians(a1-90)); y1 = cy3+R3*math.sin(math.radians(a1-90))
    laf = 1 if sw > 180 else 0
    pie2 += ('<path d="M%d,%d L%.1f,%.1f A%d,%d 0 %d 1 %.1f,%.1f Z" fill="%s" '
             'opacity="0.88" stroke="#fff" stroke-width="2"/>'
             % (cx3, cy3, x0, y0, R3, R3, laf, x1, y1, MC.get(k, "#94a3b8")))
    if v/totm > 0.04:
        mid = (a0+a1)/2
        lx = cx3+(R3+24)*math.cos(math.radians(mid-90))
        ly = cy3+(R3+24)*math.sin(math.radians(mid-90))
        pie2 += ('<text x="%.0f" y="%.0f" font-size="11" fill="#334155" text-anchor="middle" '
                 '%s>%s %d</text>' % (lx, ly, CJK, esc(k), v))
    ang += sw

trows = "".join(
    '<tr><td>第%d章</td><td>%d</td><td>%d</td><td>%d</td></tr>' % (n, s, f, r)
    for n, s, f, r in topb[:10])
trrows = "".join('<tr><td>第%d章</td><td><b>%d</b> 回合</td></tr>' % (t["ch"], t["turns"])
                 for t in tt[:10])
srows = "".join(
    '<tr><td>%s</td><td>%.2f</td><td>%.2f</td><td>%.2f</td></tr>'
    % (esc(r["卷"][:18]), r["震惊/章"], r["打脸/章"], r["反转/章"]) for r in bv)

HTML = '''<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<title>章内工程学</title><style>
body{margin:0;background:#f1f5f9;__CJK__;color:#0f172a}
.wrap{max-width:1260px;margin:0 auto;padding:20px}
.nav{display:flex;gap:9px;margin-bottom:16px;flex-wrap:wrap}
.nav a{padding:8px 14px;background:#fff;border-radius:9px;color:#334155;
 text-decoration:none;font-size:13px;font-weight:600;box-shadow:0 1px 5px rgba(0,0,0,.06)}
.nav a.on{background:#0f172a;color:#fff}
.card{background:#fff;border-radius:15px;box-shadow:0 2px 14px rgba(0,0,0,.07);
 padding:18px;margin-bottom:16px}
h2{margin:0 0 4px;font-size:19px}
.sub{color:#94a3b8;font-size:12px;margin-bottom:14px;line-height:1.75}
.grid2{display:grid;grid-template-columns:1fr 380px;gap:16px}
table{width:100%;border-collapse:collapse;font-size:12.5px}
th{text-align:left;padding:8px 6px;border-bottom:2px solid #e2e8f0;color:#475569;font-size:11px}
td{padding:7px 6px;border-bottom:1px solid #f1f5f9}
.kv{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:9px;margin-top:8px}
.kv div{background:#f8fafc;padding:10px;border-radius:8px;font-size:12px}
.kv b{display:block;font-size:18px;color:#0ea5e9}
</style></head><body><div class="wrap">
<div class="nav">
 <a href="可视化总览.html">← 总览</a>
 <a href="情感曲线.html">① 情感曲线</a>
 <a href="人物关系网.html">② 关系网</a>
 <a href="灌水高潮热力图.html">③ 热力图</a>
 <a href="语言指纹.html">④ 语言指纹</a>
 <a href="转折点分析.html">⑤ 转折点</a>
 <a href="叙事工程学.html">⑥ 叙事工程学</a>
 <a href="章内工程学.html" class="on">⑦ 章内工程学</a>
</div>

<div class="card">
<h2>⑦ 章内工程学</h2>
<div class="sub">从"章"下沉到"章内"：作者如何用 100 多个短段落拼出一章。
节奏模板 · 爽文桥段 · 对话轮次 · 开场方式。</div>
</div>

<div class="card">
<h2>A · 章内节奏模板</h2>
<div class="sub">把每章的段落按位置分成 10 档（0%→100%），统计各档每千段落的命中率。
各序列按自身峰值归一化（对话绝对值最高，单独看趋势）。悬停圆点看数值。</div>
<svg viewBox="0 0 __W1__ __H1__" width="100%">__G1____L1____XL1__ __LEG1__
<line x1="__ML1__" y1="__MT1__" x2="__ML1__" y2="__MT1PH1__" stroke="#cbd5e1" stroke-width="1.5"/>
<line x1="__ML1__" y1="__MT1PH1__" x2="__ML1PW1__" y2="__MT1PH1__" stroke="#cbd5e1" stroke-width="1.5"/>
<text x="__ML1__" y="__MT1PH1p__" font-size="11" fill="#64748b" __CJK__ text-anchor="middle" transform="rotate(0)">章内位置 →</text>
</svg>
<div class="sub" style="margin-top:10px">
<b>关键形状：</b>对话在章首 0-10% 略低（204→233）后走平，
<b>在最后 10% 骤升到 271</b> —— 作者习惯用对话高密度收尾。
心声在 90-100% 位置升到 50.1（全章最高），<b>章末心声是固定收尾手法</b>。
战斗在 80% 后下降（30.9→25.2），甜度则一路爬升（18.0→23.3）——
<b>章末偏感情与对话，不偏打斗</b>。
</div>
</div>

<div class="grid2">
<div class="card">
<h2>B · 爽文三件套（震惊 / 打脸 / 反转）</h2>
<div class="sub">按卷每章均值</div>
<svg viewBox="0 0 __W2__ __H2__" width="100%">__B2____XL2__
<line x1="__ML2__" y1="__MT2__" x2="__ML2__" y2="__MT2PH2__" stroke="#cbd5e1" stroke-width="1.5"/>
<line x1="__ML2__" y1="__MT2PH2__" x2="__ML2PW2__" y2="__MT2PH2__" stroke="#cbd5e1" stroke-width="1.5"/>
</svg>
<div class="sub" style="margin-top:8px">
全书命中：震惊 __SH__ · 打脸 __FA__ · 反转 __RE__。
<b>反转远超另两者</b>（2837 vs 1001/173）—— 这本书靠"转折"而非"打脸"驱动。
第一卷震惊 3.50/章为全书最高，第八卷打脸降到 0.07/章。
</div>
</div>
<div class="card">
<h2>开场方式</h2>
<div class="sub">589 章的章首第一句写法</div>
<svg viewBox="0 0 330 310" width="100%">__PIE2__</svg>
<div class="sub" style="margin-top:8px">
<b>短句破题 45.2% + 场景描写 40.9% = 86%</b>。
作者几乎不用"XX道"开章（首个说话人 98% 未标注）——
先给画面或短句，再进对话。
</div>
</div>
</div>

<div class="card">
<h2>C · 对话轮次结构</h2>
<div class="kv">
<div><b>__TT__</b>总回合</div>
<div><b>__TA__</b>章均回合</div>
<div><b>__TM__</b>中位数</div>
<div><b>__TX__</b>最多单章</div>
<div><b>__TZ__</b>零对话章</div>
</div>
<div class="sub" style="margin-top:10px">
<b>589 章无一章零对话</b>（最少 3 回合）—— 对话是绝对骨架。
章均 22.8 回合、中位 23，节奏高度模板化。
</div>
<table style="margin-top:12px">
<tr><th>对话最密章</th><th>回合数</th></tr>__TRROWS__
</table>
</div>

<div class="card">
<h2>三件套最齐全的章 Top10</h2>
<table>
<tr><th>章</th><th>震惊</th><th>打脸</th><th>反转</th></tr>__TROWS__
</table>
</div>

<div class="card">
<h2>按卷桥段表</h2>
<table>
<tr><th>卷</th><th>震惊/章</th><th>打脸/章</th><th>反转/章</th></tr>__SROWS__
</table>
</div>
</div></body></html>'''

R = (HTML.replace("__CJK__", CJK)
     .replace("__W1__", str(W1)).replace("__H1__", str(H1))
     .replace("__ML1__", str(ML1)).replace("__MT1__", str(MT1))
     .replace("__MT1PH1__", str(MT1+PH1)).replace("__MT1PH1p__", str(MT1+PH1+40))
     .replace("__ML1PW1__", str(ML1+PW1))
     .replace("__G1__", grid1).replace("__L1__", lines1)
     .replace("__XL1__", xl1).replace("__LEG1__", leg1)
     .replace("__W2__", str(W2)).replace("__H2__", str(H2))
     .replace("__ML2__", str(ML2)).replace("__MT2__", str(MT2))
     .replace("__MT2PH2__", str(MT2+PH2)).replace("__ML2PW2__", str(ML2+PW2))
     .replace("__B2__", bars2).replace("__XL2__", xl2)
     .replace("__PIE2__", pie2)
     .replace("__SH__", str(bridge["震惊"])).replace("__FA__", str(bridge["打脸"]))
     .replace("__RE__", str(bridge["反转"]))
     .replace("__TT__", str(ts["total"])).replace("__TA__", str(ts["avg"]))
     .replace("__TM__", str(int(ts["median"]))).replace("__TX__", str(ts["max"]))
     .replace("__TZ__", str(ts["zero"]))
     .replace("__TRROWS__", trrows).replace("__TROWS__", trows)
     .replace("__SROWS__", srows))

p = os.path.join(WEB, "章内工程学.html")
open(p, "w", encoding="utf-8").write(R)
print("OK", round(len(R)/1024, 1), "KB  placeholders_left:", "__" in R)
