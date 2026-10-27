# -*- coding: utf-8 -*-
"""阶段13：转折点可视化 —— 四曲线叠合 + 相关系数 + 章节级细粒度视图"""
import json, os, html

OUT = r"D:\aigc_pro\ai-video&draw\DeepSeek Harness\@ D Download 这个人明明很强却_2026-10-27\产出\data"
WEB = r"D:\aigc_pro\ai-video&draw\DeepSeek Harness\@ D Download 这个人明明很强却_2026-10-27\产出"

tp = json.load(open(os.path.join(OUT, "turning_points.json"), encoding="utf-8"))
VA, turns, corr = tp["VA"], tp["turns"], tp["corr"]
KEYS, META = tp["KEYS"], tp["META"]
ch_s, wseq, chnums = tp["ch_smooth"], tp["water_seq"], tp["ch_nums"]

CJK = "font-family:'PingFang SC','Microsoft YaHei','Noto Sans CJK SC',sans-serif"
def esc(s): return html.escape(str(s))

def catmull(pts):
    """生成平滑路径（Catmull-Rom 转 Bezier，Python 端算好）"""
    if len(pts) < 2: return ""
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(len(pts) - 1):
        p0 = pts[i-1] if i > 0 else pts[i]
        p1, p2 = pts[i], pts[i+1]
        p3 = pts[i+2] if i + 2 < len(pts) else p2
        c1x = p1[0] + (p2[0] - p0[0]) / 6; c1y = p1[1] + (p2[1] - p0[1]) / 6
        c2x = p2[0] - (p3[0] - p1[0]) / 6; c2y = p2[1] - (p3[1] - p1[1]) / 6
        d += f" C{c1x:.1f},{c1y:.1f} {c2x:.1f},{c2y:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    return d

# ==================================================================
# 图1：卷级四曲线叠合
# ==================================================================
W1, H1 = 1160, 470
ML1, MR1, MT1, MB1 = 60, 190, 52, 76
PW1, PH1 = W1 - ML1 - MR1, H1 - MT1 - MB1
NV = len(VA)

def x1(i): return ML1 + i * PW1 / (NV - 1)
def y1(v): return MT1 + PH1 - v * PH1 * 0.90

paths, dots, leg = "", "", ""
for k in KEYS:
    m = META[k]
    pts = [[x1(i), y1(a[k + "_n"])] for i, a in enumerate(VA)]
    d = catmull(pts)
    dash = ' stroke-dasharray="7 4"' if m["inv"] else ""
    paths += (f'<path d="{d}" fill="none" stroke="{m["color"]}" stroke-width="2.8" '
              f'opacity="0.92"{dash}/>')
    paths += (f'<path d="{d} L{x1(NV-1):.1f},{MT1+PH1} L{ML1},{MT1+PH1} Z" '
              f'fill="{m["color"]}" opacity="0.05"/>')
    for i, (px, py) in enumerate(pts):
        dots += (f'<circle cx="{px:.1f}" cy="{py:.1f}" r="5" fill="{m["color"]}" '
                 f'stroke="#fff" stroke-width="2" class="pt" data-k="{esc(k)}" '
                 f'data-i="{i}" data-v="{VA[i][k]}" data-u="{esc(m["unit"])}"/>')

for i, m in enumerate(META.values()):
    yy = 90 + i * 40
    leg += (f'<rect x="{W1-MR1+18}" y="{yy-11}" width="14" height="14" rx="3.5" fill="{m["color"]}"/>'
            f'<text x="{W1-MR1+40}" y="{yy}" font-size="13" fill="#1e293b" {CJK} font-weight="600">'
            f'{esc(m["name"])}</text>'
            f'<text x="{W1-MR1+40}" y="{yy+15}" font-size="10" fill="#94a3b8" {CJK}>'
            f'{esc(m["desc"])}</text>')

# 转折带：第8卷起点
t8 = next((t for t in turns if t["at_vol"] == 8), None)
band = ""
if t8:
    bx = x1(7)
    band += (f'<rect x="{ML1}" y="{MT1}" width="{bx-ML1:.1f}" height="{PH1}" '
             f'fill="#10b981" opacity="0.05"/>'
             f'<rect x="{bx:.1f}" y="{MT1}" width="{W1-MR1-bx:.1f}" height="{PH1}" '
             f'fill="#ef4444" opacity="0.05"/>'
             f'<line x1="{bx:.1f}" y1="{MT1}" x2="{bx:.1f}" y2="{MT1+PH1}" '
             f'stroke="#dc2626" stroke-width="2.5" stroke-dasharray="6 4"/>'
             f'<rect x="{bx-52:.0f}" y="{MT1-4}" width="104" height="21" rx="5" fill="#dc2626"/>'
             f'<text x="{bx:.1f}" y="{MT1+11}" font-size="11.5" fill="#fff" text-anchor="middle" '
             f'{CJK} font-weight="700">转折点 第501章</text>')

grid1 = "".join(f'<line x1="{ML1}" y1="{y1(g/4):.1f}" x2="{W1-MR1}" y2="{y1(g/4):.1f}" '
                f'stroke="#e2e8f0"/>' for g in range(5))
xl1 = ""
for i, a in enumerate(VA):
    xl1 += (f'<text x="{x1(i):.1f}" y="{MT1+PH1+20}" font-size="11.5" text-anchor="middle" '
            f'fill="#334155" {CJK} font-weight="600">卷{i+1}</text>'
            f'<text x="{x1(i):.1f}" y="{MT1+PH1+36}" font-size="9.5" text-anchor="middle" '
            f'fill="#94a3b8" {CJK}>{a["lo"]}-{a["hi"]}</text>')

# ==================================================================
# 图2：章节级四曲线（细粒度，平滑窗口 9 / 21）
# ==================================================================
W2, H2 = 1160, 400
ML2, MR2, MT2, MB2 = 60, 24, 46, 58
PW2, PH2 = W2 - ML2 - MR2, H2 - MT2 - MB2
N = len(chnums)

def norm(v):
    mx = max(v) or 1
    return [x / mx for x in v]

SER = [
    ("心声密度", norm(ch_s["inner"]), "#f59e0b", False),
    ("灌水率", norm(wseq), "#64748b", True),
    ("战斗强度", norm(ch_s["战斗"]), "#ef4444", False),
    ("感情甜度", norm(ch_s["甜度"]), "#ec4899", False),
]
def x2(i): return ML2 + i * PW2 / (N - 1)
def y2(v): return MT2 + PH2 - v * PH2 * 0.90

p2 = ""
for name, vals, col, inv in SER:
    pts = [[x2(i), y2(v)] for i, v in enumerate(vals)]
    d = catmull(pts)
    dash = ' stroke-dasharray="6 4"' if inv else ""
    p2 += f'<path d="{d}" fill="none" stroke="{col}" stroke-width="1.5" opacity="0.8"{dash}/>'

# 卷分隔
vsep = ""
for i, a in enumerate(VA):
    xx = x2(a["lo"] - 1)
    vsep += (f'<line x1="{xx:.1f}" y1="{MT2}" x2="{xx:.1f}" y2="{MT2+PH2}" '
             f'stroke="#cbd5e1" stroke-width="1" stroke-dasharray="3 3" opacity="0.7"/>')
    if i < len(VA) - 1:
        cx = (x2(a["lo"] - 1) + x2(VA[i+1]["lo"] - 1)) / 2
        vsep += (f'<text x="{cx:.1f}" y="{MT2-8}" font-size="10.5" text-anchor="middle" '
                 f'fill="#64748b" {CJK}>卷{i+1}</text>')
# 转折线
if t8:
    bx2 = x2(t8["at_ch"] - 1)
    vsep += (f'<line x1="{bx2:.1f}" y1="{MT2}" x2="{bx2:.1f}" y2="{MT2+PH2}" '
             f'stroke="#dc2626" stroke-width="2.2"/>')

xl2 = "".join(f'<text x="{x2(i):.1f}" y="{MT2+PH2+18}" font-size="10" text-anchor="middle" '
              f'fill="#94a3b8" {CJK}>{n}</text>'
              for i, n in enumerate(chnums) if n % 50 == 0 or n == 1)

# ==================================================================
# 相关系数卡
# ==================================================================
ccards = ""
for k, v in corr.items():
    av = abs(v)
    if av >= 0.8: tag, col, st = "强", "#dc2626", "★"
    elif av >= 0.6: tag, col, st = "强", "#f59e0b", "★"
    elif av >= 0.4: tag, col, st = "中等", "#0ea5e9", "○"
    else: tag, col, st = "弱", "#94a3b8", "·"
    direction = "负" if v < 0 else "正"
    wpx = min(100, av * 100)
    ccards += (
        f'<div class="cc"><div class="cn">{esc(k)}</div>'
        f'<div class="cv" style="color:{col}">{v:+.3f}</div>'
        f'<div class="cb"><div class="cbi" style="width:{wpx:.0f}%;background:{col}"></div></div>'
        f'<div class="ct">{st} {tag}{direction}相关</div></div>')

# ==================================================================
# 转折点表
# ==================================================================
trows = ""
for t in turns[:6]:
    ds = "　".join(f'{META[k]["name"]}<b style="color:{"#dc2626" if t["deltas"][k]<0 else "#16a34a"}">'
                   f'{t["deltas"][k]:+.0f}%</b>' for k in KEYS)
    trows += (f'<tr><td><b>卷{t["at_vol"]}</b></td><td>第{t["at_ch"]}章</td>'
              f'<td>{esc(t["from"][:14])} → {esc(t["to"][:14])}</td>'
              f'<td style="font-size:11.5px">{ds}</td>'
              f'<td><div class="mg"><div class="mgi" style="width:{t["mag"]/0.32*100:.0f}%"></div>'
              f'</div>{t["mag"]:.3f}</td></tr>')

# 卷数据表
vrows = ""
for i, a in enumerate(VA):
    hl = ' style="background:#fef2f2"' if i >= 7 else ""
    vrows += (f'<tr{hl}><td>{esc(a["卷"][:20])}</td><td>{a["lo"]}-{a["hi"]}</td>'
              f'<td>{a["心声/章"]}</td><td>{a["灌水率"]}%</td>'
              f'<td>{a["战斗/章"]}</td><td>{a["甜度/章"]}</td></tr>')

HTML = f'''<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<title>转折点分析</title><style>
body{{margin:0;background:#f1f5f9;{CJK};color:#0f172a}}
.wrap{{max-width:1260px;margin:0 auto;padding:20px}}
.nav{{display:flex;gap:10px;margin-bottom:16px;flex-wrap:wrap}}
.nav a{{padding:8px 15px;background:#fff;border-radius:9px;color:#334155;text-decoration:none;
 font-size:13px;font-weight:600;box-shadow:0 1px 5px rgba(0,0,0,.06)}}
.nav a.on{{background:#0f172a;color:#fff}}
.card{{background:#fff;border-radius:15px;box-shadow:0 2px 14px rgba(0,0,0,.07);padding:18px;margin-bottom:16px}}
h2{{margin:0 0 4px;font-size:19px}}
.sub{{color:#94a3b8;font-size:12px;margin-bottom:14px;line-height:1.7}}
table{{width:100%;border-collapse:collapse;font-size:12.5px}}
th{{text-align:left;padding:8px 6px;border-bottom:2px solid #e2e8f0;color:#475569;font-size:11px}}
td{{padding:7px 6px;border-bottom:1px solid #f1f5f9}}
.ccards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}}
.cc{{background:#f8fafc;border-radius:11px;padding:13px}}
.cn{{font-size:12.5px;color:#475569;font-weight:600}}
.cv{{font-size:25px;font-weight:800;margin:3px 0}}
.cb{{height:6px;background:#e2e8f0;border-radius:3px;overflow:hidden}}
.cbi{{height:100%;border-radius:3px}}
.ct{{font-size:11.5px;color:#64748b;margin-top:5px}}
.mg{{height:6px;background:#e2e8f0;border-radius:3px;overflow:hidden;min-width:60px}}
.mgi{{height:100%;background:#dc2626;border-radius:3px}}
#tip{{position:fixed;display:none;background:rgba(15,23,42,.95);color:#fff;padding:10px 14px;
 border-radius:9px;font-size:12.5px;pointer-events:none;z-index:99}}
.hero{{background:linear-gradient(135deg,#1e293b,#334155);color:#fff;border-radius:15px;
 padding:22px;margin-bottom:16px}}
.hero h2{{color:#fff;font-size:21px;margin-bottom:8px}}
.hero .sub{{color:#cbd5e1;font-size:13px;margin:0}}
.hero b{{color:#fbbf24}}
</style></head><body><div class="wrap">
<div class="nav">
 <a href="可视化总览.html">← 总览</a>
 <a href="情感曲线.html">① 情感曲线</a>
 <a href="人物关系网.html">② 关系网</a>
 <a href="灌水高潮热力图.html">③ 热力图</a>
 <a href="语言指纹.html">④ 语言指纹</a>
 <a href="转折点分析.html" class="on">⑤ 转折点</a>
</div>

<div class="hero">
<h2>⑤ 转折点：四条曲线的因果交叉点</h2>
<div class="sub">
把分散在三个页面里的 <b>心声密度</b>、<b>灌水率</b>、<b>战斗强度</b>、<b>感情甜度</b>
叠到同一坐标系 —— 全书的结构性转折发生在 <b>第 501 章（第八卷起点）</b>，
此刻心声机制关闭 <b>−67%</b>，甜度同步崩塌 <b>−68%</b>，而战斗强度逆势拉升 <b>+89%</b>。
</div>
</div>

<div class="card">
<h2>卷级四曲线叠合</h2>
<div class="sub">各曲线按自身峰值归一化 · 虚线＝逆向指标（灌水率）· 悬停数据点看原值 ·
左侧绿区＝喜剧主导期，右侧红区＝严肃终局期</div>
<svg viewBox="0 0 {W1} {H1}" width="100%">
{grid1}{band}
{paths}{dots}{leg}{xl1}
<line x1="{ML1}" y1="{MT1}" x2="{ML1}" y2="{MT1+PH1}" stroke="#cbd5e1" stroke-width="1.5"/>
<line x1="{ML1}" y1="{MT1+PH1}" x2="{W1-MR1}" y2="{MT1+PH1}" stroke="#cbd5e1" stroke-width="1.5"/>
<text x="{ML1-12}" y="{MT1+PH1/2}" font-size="12" fill="#64748b" {CJK}
 transform="rotate(-90 {ML1-12} {MT1+PH1/2})" text-anchor="middle">归一化强度</text>
</svg>
</div>

<div class="card">
<h2>章节级细粒度（589 章，平滑窗口 9 / 灌水用 21 章滑动窗口）</h2>
<div class="sub">红线＝第 501 章转折点。心声（橙）在此后彻底走平，灌水（灰虚线）持续爬升。</div>
<svg viewBox="0 0 {W2} {H2}" width="100%">
{vsep}{p2}{xl2}
<line x1="{ML2}" y1="{MT2}" x2="{ML2}" y2="{MT2+PH2}" stroke="#cbd5e1" stroke-width="1.5"/>
<line x1="{ML2}" y1="{MT2+PH2}" x2="{W2-MR2}" y2="{MT2+PH2}" stroke="#cbd5e1" stroke-width="1.5"/>
</svg>
</div>

<div class="card">
<h2>相关系数（按卷，n=10）</h2>
<div class="sub">验证因果假设：心声供给与节奏塌陷是否真的反向联动</div>
<div class="ccards">{ccards}</div>
<div class="sub" style="margin-top:14px;color:#dc2626;font-weight:600">
关键判定：心声 vs 灌水率 r = {corr["心声 vs 灌水率"]:+.3f} —— 强负相关，
喜剧机制退场与节奏塌陷几乎完全同步。
</div>
</div>

<div class="card">
<h2>转折点强度排名</h2>
<div class="sub">强度＝四条曲线归一化变化的平均绝对值</div>
<table>
<tr><th>位置</th><th>章</th><th>跨越</th><th>四项变化</th><th>强度</th></tr>
{trows}</table>
</div>

<div class="card">
<h2>按卷数据表</h2>
<div class="sub">红底＝转折点之后（第八卷起）</div>
<table>
<tr><th>卷</th><th>范围</th><th>心声/章</th><th>灌水率</th><th>战斗/章</th><th>甜度/章</th></tr>
{vrows}</table>
</div>

<div class="card">
<h2>结论</h2>
<div style="font-size:13.5px;line-height:2;color:#334155">
<b>1. 第 501 章是全书唯一的硬转折。</b>心声 −67%、甜度 −68% 同时崩塌，
战斗 +89% 逆势拉升 —— 作者在这一章同时按下三个开关：关闭喜剧、抽走感情、拉满冲突。<br>
<b>2. 灌水率是滞后指标。</b>灌水率在第六卷（+100%）就开始抬头，比心声崩塌早了一卷半，
说明节奏问题在喜剧退场之前已现端倪，第 501 章只是让它彻底暴露。<br>
<b>3. 「战斗 vs 甜度」r = {corr["战斗 vs 甜度"]:+.3f} 强负相关。</b>
动作戏和感情戏在全书中是互斥的 —— 战斗强度峰值（第五卷 2.88、第十卷 3.36）
恰好对应甜度谷值（1.81、0.93）。作者的笔墨分配是二选一，不是并行推进。<br>
<b>4. 第三卷是甜度孤峰（3.81），第五卷是战斗孤峰（2.88），两者不重合。</b>
全书没有一章是"战斗 + 感情"双高峰，这解释了为什么感情线在中段完成后就被搁置。
</div>
</div>
</div>
<div id="tip"></div>
<script>
const META={json.dumps({k:{"name":v["name"],"unit":v["unit"]} for k,v in META.items()}, ensure_ascii=False)};
const VA={json.dumps(VA, ensure_ascii=False)};
const tip=document.getElementById('tip');
document.querySelectorAll('.pt').forEach(c=>{{
  c.addEventListener('mouseenter',e=>{{
    const k=c.dataset.k,i=+c.dataset.i;
    const vals=Object.keys(META).map(kk=>
      `<div>${{META[kk].name}}: <b>${{VA[i][kk]}}${{META[kk].unit}}</b></div>`).join('');
    tip.innerHTML=`<div style="font-weight:700;margin-bottom:5px">${{VA[i]["卷"]}}</div>`
      +`<div style="color:#94a3b8;font-size:11px;margin-bottom:5px">第${{VA[i]["lo"]}}-${{VA[i]["hi"]}}章 · ${{VA[i]["nch"]}}章</div>`+vals;
    tip.style.display='block';
  }});
  c.addEventListener('mousemove',e=>{{
    tip.style.left=Math.min(e.clientX+16,window.innerWidth-260)+'px';
    tip.style.top=(e.clientY+16)+'px';}});
  c.addEventListener('mouseleave',()=>tip.style.display='none');
}});
</script></body></html>'''

p = os.path.join(WEB, "转折点分析.html")
open(p, "w", encoding="utf-8").write(HTML)
print(f"✓ 转折点分析.html  {len(HTML)/1024:.1f} KB")
