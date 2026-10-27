# -*- coding: utf-8 -*-
"""阶段15：叙事工程学可视化 HTML"""
import json, os, html, csv, collections

OUT = r"D:\aigc_pro\ai-video&draw\DeepSeek Harness\@ D Download 这个人明明很强却_2026-10-27\产出\data"
WEB = r"D:\aigc_pro\ai-video&draw\DeepSeek Harness\@ D Download 这个人明明很强却_2026-10-27\产出"

nv = json.load(open(os.path.join(OUT, "narrative.json"), encoding="utf-8"))
hook, hsamp, voice, fs, scene = (nv["hook"], nv["hook_samp"], nv["voice"],
                                 nv["foreshadow"], nv["scene_vol"])
CJK = "font-family:'PingFang SC','Microsoft YaHei','Noto Sans CJK SC',sans-serif"
def esc(s): return html.escape(str(s))

# ===================== ① 钩子形态饼图 =====================
HC = {"对话式": "#0ea5e9", "叙述式": "#64748b", "省略式": "#94a3b8",
      "感叹式": "#ef4444", "心声式": "#f59e0b", "疑问式": "#8b5cf6"}
types = hook["types"]; tot = hook["total"]
pie, ang = "", 0
cx, cy, R = 175, 168, 112
import math
for k, v in sorted(types.items(), key=lambda x: -x[1]):
    sw = v / tot * 360
    a0, a1 = ang, ang + sw
    x0 = cx + R*math.cos(math.radians(a0-90)); y0 = cy + R*math.sin(math.radians(a0-90))
    x1 = cx + R*math.cos(math.radians(a1-90)); y1 = cy + R*math.sin(math.radians(a1-90))
    laf = 1 if sw > 180 else 0
    pie += ('<path d="M%d,%d L%.1f,%.1f A%d,%d 0 %d 1 %.1f,%.1f Z" fill="%s" '
            'opacity="0.88" stroke="#fff" stroke-width="2"/>'
            % (cx, cy, x0, y0, R, R, laf, x1, y1, HC.get(k, "#94a3b8")))
    if v/tot > 0.04:
        mid = (a0+a1)/2
        lx = cx + (R+26)*math.cos(math.radians(mid-90))
        ly = cy + (R+26)*math.sin(math.radians(mid-90))
        pie += ('<text x="%.0f" y="%.0f" font-size="11.5" fill="#334155" '
                'text-anchor="middle" %s>%s %d</text>' % (lx, ly, CJK, esc(k), v))
    ang += sw

# 钩子按卷堆叠
hkeys = ["对话式", "叙述式", "省略式", "感叹式", "心声式", "疑问式"]
W1, H1 = 1000, 300
ML, MT, PW, PH = 56, 26, 900, 210
bv = hook["by_vol"]
vnames = list(bv.keys())
maxs = max(sum(bv[v].get(k, 0) for k in hkeys) for v in vnames) or 1
bars = ""
for i, vn in enumerate(vnames):
    x = ML + i*PW/len(vnames) + 8
    bw = PW/len(vnames) - 16
    y = MT + PH
    for k in hkeys:
        n = bv[vn].get(k, 0)
        if not n: continue
        h = n/maxs*PH
        y -= h
        bars += ('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" fill="%s" '
                 'opacity="0.88"><title>%s %s %d</title></rect>'
                 % (x, y, bw, h, HC.get(k, "#94a3b8"), esc(vn[:8]), esc(k), n))
    bars += ('<text x="%.0f" y="%d" font-size="10.5" text-anchor="middle" '
             'fill="#475569" %s>卷%d</text>' % (x+bw/2, MT+PH+16, CJK, i+1))

# ===================== ③ 伏笔甘特 =====================
W2 = 1000
rowh = 30
H2 = 60 + len(fs)*rowh + 30
L2, R2m = 110, 40
PW2 = W2 - L2 - R2m
gan = ""
for i, x in enumerate(fs):
    y = 46 + i*rowh
    x0 = L2 + x["first"]/589*PW2
    x1 = L2 + x["last"]/589*PFW2 if False else L2 + x["last"]/589*PW2
    gx0 = L2 + x["gap_from"]/589*PW2
    gx1 = L2 + x["gap_to"]/589*PW2
    gan += ('<text x="%d" y="%d" font-size="12" fill="#334155" %s>%s</text>'
            % (L2-8, y+5, CJK, esc(x["w"])))
    gan += ('<rect x="%.1f" y="%d" width="%.1f" height="13" rx="3" '
            'fill="#cbd5e1" opacity="0.55"/>' % (x0, y-4, max(2, x1-x0)))
    gan += ('<rect x="%.1f" y="%d" width="%.1f" height="13" rx="3" fill="#ef4444" '
            'opacity="0.82"><title>%s：第%d→%d章 空档%d章</title></rect>'
            % (gx0, y-4, max(2, gx1-gx0), esc(x["w"]), x["gap_from"], x["gap_to"], x["gap"]))
    gan += ('<text x="%.1f" y="%d" font-size="10" fill="#94a3b8" %s>%d章</text>'
            % (gx1+6, y+6, CJK, x["gap"]))
for t in range(1, 590, 100):
    gx = L2 + t/589*PW2
    gan += ('<line x1="%.1f" y1="30" x2="%.1f" y2="%d" stroke="#e2e8f0"/>'
            '<text x="%.1f" y="24" font-size="10" fill="#94a3b8" %s>%d</text>'
            % (gx, gx, H2-24, gx, CJK, t))

# ===================== ④ 场景堆叠面积 =====================
SCK = ["室内", "室外", "战场", "异空间"]
SCC = {"室内": "#f59e0b", "室外": "#10b981", "战场": "#ef4444", "异空间": "#8b5cf6"}
W3, H3 = 1000, 320
ML3, MT3, PW3, PH3 = 56, 26, 900, 225
mx3 = max(sum(r[k] for k in SCK) for r in scene) or 1
area = ""
prev = [MT3+PH3]*len(scene)
cum = [0]*len(scene)
for k in SCK:
    pts = []
    for i, r in enumerate(scene):
        cum[i] += r[k]
        pts.append((ML3 + i*PW3/(len(scene)-1), MT3 + PH3 - cum[i]/mx3*PH3))
    d = "M" + " L".join("%.1f,%.1f" % p for p in pts)
    back = " L" + " L".join("%.1f,%.1f" % p for p in reversed(pts)) + " Z"
    area += ('<path d="%s%s" fill="%s" opacity="0.55" stroke="%s" stroke-width="1.6"/>'
             % (d, back, SCC[k], SCC[k]))
for i, r in enumerate(scene):
    area += ('<text x="%.0f" y="%d" font-size="10.5" text-anchor="middle" '
             'fill="#475569" %s>卷%d</text>'
             % (ML3 + i*PW3/(len(scene)-1), MT3+PH3+18, CJK, i+1))

# 场景表格
srows = ""
for r in scene:
    t = r["合计"]
    srows += ('<tr><td>%s</td><td>%d-%d</td><td>%d</td><td>%d</td><td>%d</td>'
              '<td><b>%d</b></td><td>%.0f%%</td></tr>'
              % (esc(r["卷"][:18]), r["lo"], r["hi"], r["室内"], r["室外"],
                 r["战场"], r["异空间"], r["异空间"]/t*100 if t else 0))

# ===================== ② 音色卡 =====================
vcards = ""
for v in voice:
    vcards += ('<div class="vc"><div class="vh"><b>%s</b><span>%d 条 · 第%d-%d章</span></div>'
               '<div class="vm">均长 <b>%.1f</b> 字　最长 %d 字</div>'
               '<div class="vb"><div class="bi" style="width:%.0f%%;background:#ef4444" '
               'title="叹号 %.1f%%"></div></div>'
               '<div class="vb"><div class="bi" style="width:%.0f%%;background:#0ea5e9" '
               'title="问号 %.1f%%"></div></div>'
               '<div class="vb"><div class="bi" style="width:%.0f%%;background:#94a3b8" '
               'title="省略号 %.1f%%"></div></div>'
               '<div class="vs">%s</div></div>'
               % (esc(v["name"]), v["n"], v["first_ch"], v["last_ch"],
                  v["avg"], v["max"],
                  v["excl"]*2, v["excl"], v["quest"]*2, v["quest"],
                  v["ellip"]*2, v["ellip"],
                  esc(v["samples"][0][:52]) if v["samples"] else ""))

# 钩子样例
hsamp_html = ""
for t in ["对话式", "叙述式", "省略式", "感叹式", "心声式", "疑问式"]:
    lst = hsamp.get(t, [])
    if not lst: continue
    hsamp_html += ('<div class="hc"><div class="ht" style="color:%s">%s · 均长%.1f字</div>'
                   % (HC.get(t, "#64748b"), esc(t), hook["avg_len"].get(t, 0)))
    for s in lst[:3]:
        hsamp_html += '<div class="hq">[%s] %s</div>' % (s["ch"], esc(s["t"]))
    hsamp_html += '</div>'

HTML = '''<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<title>叙事工程学</title><style>
body{margin:0;background:#f1f5f9;__CJK__;color:#0f172a}
.wrap{max-width:1260px;margin:0 auto;padding:20px}
.nav{display:flex;gap:9px;margin-bottom:16px;flex-wrap:wrap}
.nav a{padding:8px 14px;background:#fff;border-radius:9px;color:#334155;
 text-decoration:none;font-size:13px;font-weight:600;box-shadow:0 1px 5px rgba(0,0,0,.06)}
.nav a.on{background:#0f172a;color:#fff}
.card{background:#fff;border-radius:15px;box-shadow:0 2px 14px rgba(0,0,0,.07);
 padding:18px;margin-bottom:16px}
h2{margin:0 0 4px;font-size:19px}
.sub{color:#94a3b8;font-size:12px;margin-bottom:14px;line-height:1.7}
.grid2{display:grid;grid-template-columns:380px 1fr;gap:16px}
.vcards{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px}
.vc{background:#f8fafc;border-radius:11px;padding:13px}
.vh{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:6px}
.vh b{font-size:14px;color:#0f172a}
.vh span{font-size:11px;color:#94a3b8}
.vm{font-size:12px;color:#475569;margin-bottom:8px}
.vb{height:6px;background:#e2e8f0;border-radius:3px;overflow:hidden;margin-bottom:4px}
.bi{height:100%;border-radius:3px}
.vs{font-size:11.5px;color:#64748b;margin-top:8px;line-height:1.7;
 padding-left:8px;border-left:2.5px solid #e2e8f0}
.hc{background:#f8fafc;border-radius:10px;padding:12px;margin-bottom:9px}
.ht{font-size:13px;font-weight:700;margin-bottom:6px}
.hq{font-size:11.5px;color:#475569;line-height:1.8;padding-left:9px;
 border-left:2.5px solid #e2e8f0;margin-bottom:4px}
table{width:100%;border-collapse:collapse;font-size:12.5px}
th{text-align:left;padding:8px 6px;border-bottom:2px solid #e2e8f0;color:#475569;font-size:11px}
td{padding:7px 6px;border-bottom:1px solid #f1f5f9}
</style></head><body><div class="wrap">
<div class="nav">
 <a href="可视化总览.html">← 总览</a>
 <a href="情感曲线.html">① 情感曲线</a>
 <a href="人物关系网.html">② 关系网</a>
 <a href="灌水高潮热力图.html">③ 热力图</a>
 <a href="语言指纹.html">④ 语言指纹</a>
 <a href="转折点分析.html">⑤ 转折点</a>
 <a href="叙事工程学.html" class="on">⑥ 叙事工程学</a>
</div>

<div class="card">
<h2>⑥ 叙事工程学</h2>
<div class="sub">断章钩子 · 角色音色 · 伏笔时间线 · 场景迁移 —— 四个可复用的工程维度</div>
</div>

<div class="grid2">
<div class="card">
<h2>① 章末钩子形态</h2>
<div class="sub">589 章全部有钩子，无断章缺失</div>
<svg viewBox="0 0 360 350" width="100%">__PIE__</svg>
</div>
<div class="card">
<h2>钩子按卷堆叠</h2>
<div class="sub">各卷钩子形态构成变化</div>
<svg viewBox="0 0 __W1__ __H1__" width="100%">__BARS__</svg>
</div>
</div>

<div class="card">
<h2>各类钩子样例</h2>
__HSAMP__
</div>

<div class="card">
<h2>② 角色音色表</h2>
<div class="sub">红＝叹号占比　蓝＝问号占比　灰＝省略号占比（条宽按比例×2 便于观察）</div>
<div class="vcards">__VCARDS__</div>
<div class="sub" style="margin-top:12px">
<b>林恩</b>爱反问（问号 27.9%）｜<b>奈奈子</b>更爱反问（45.5%）且从不感叹 —— 师徒是对呛式对话。
<b>堕落神</b>均长 67 字，是全书长篇说教位。
</div>
</div>

<div class="card">
<h2>③ 伏笔埋设 / 回收时间线</h2>
<div class="sub">灰条＝该词存续区间，<b style="color:#ef4444">红段＝最大空档</b>（埋下后长期不再提及的章数）</div>
<svg viewBox="0 0 __W2__ __H2__" width="100%">__GAN__</svg>
<div class="sub" style="margin-top:10px">
<b>爱丽丝</b>空档 200 章（第242→442）、<b>堕落神</b>192 章（第239→431）为最长伏笔线。
</div>
</div>

<div class="card">
<h2>④ 场景迁移</h2>
<div class="sub">堆叠面积：室内 / 室外 / 战场 / 异空间</div>
<svg viewBox="0 0 __W3__ __H3__" width="100%">__AREA__</svg>
<table>
<tr><th>卷</th><th>范围</th><th>室内</th><th>室外</th><th>战场</th><th>异空间</th><th>异空间占比</th></tr>
__SROWS__
</table>
<div class="sub" style="margin-top:12px">
第八卷<b>室内仅 11、室外仅 4</b>，异空间 456 —— 人物从物理世界彻底退出，
故事跑进概念空间。这与第 501 章转折完全咬合。
</div>
</div>
</div></body></html>'''

HTML = (HTML.replace("__CJK__", CJK).replace("__PIE__", pie)
        .replace("__W1__", str(W1)).replace("__H1__", str(H1))
        .replace("__BARS__", bars).replace("__HSAMP__", hsamp_html)
        .replace("__VCARDS__", vcards)
        .replace("__W2__", str(W2)).replace("__H2__", str(H2))
        .replace("__GAN__", gan)
        .replace("__W3__", str(W3)).replace("__H3__", str(H3))
        .replace("__AREA__", area).replace("__SROWS__", srows))

p = os.path.join(WEB, "叙事工程学.html")
open(p, "w", encoding="utf-8").write(HTML)
print("OK", p, round(len(HTML)/1024, 1), "KB")
