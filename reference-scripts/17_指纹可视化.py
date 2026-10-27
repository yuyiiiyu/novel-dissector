# -*- coding: utf-8 -*-
"""阶段11：生成语言指纹可视化 HTML（套路用词 + 标题公式 + 心声机制）"""
import json, csv, os, html, collections

OUT = r"D:\aigc_pro\ai-video&draw\DeepSeek Harness\@ D Download 这个人明明很强却_2026-10-27\产出\data"
WEB = r"D:\aigc_pro\ai-video&draw\DeepSeek Harness\@ D Download 这个人明明很强却_2026-10-27\产出"

lf = json.load(open(os.path.join(OUT, "language_fingerprint.json"), encoding="utf-8"))
im = json.load(open(os.path.join(OUT, "inner_monologue.json"), encoding="utf-8"))
vols = []
with open(os.path.join(OUT, "volumes.csv"), encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        lo, hi = r["范围"].split("-")
        vols.append({"name": r["卷"], "lo": int(lo), "hi": int(hi)})

CJK = "font-family:'PingFang SC','Microsoft YaHei','Noto Sans CJK SC',sans-serif"

def esc(s):
    return html.escape(str(s))

# ================= A. 套路用词条形图 =================
words = lf["words"]
order = sorted(words.items(), key=lambda x: -x[1]["total"])
maxv = max(d["total"] for _, d in order)
bars = ""
for i, (g, d) in enumerate(order):
    w = d["total"] / maxv * 620
    col = ["#ef4444","#f97316","#f59e0b","#eab308","#84cc16","#10b981","#06b6d4",
           "#0ea5e9","#6366f1","#8b5cf6","#d946ef"][i % 11]
    top3 = " ".join(f'{x["w"]}({x["n"]})' for x in d["items"][:3])
    bars += (f'<g class="wb" data-g="{esc(g)}" data-t="{d["total"]}" '
             f'data-p="{d["per10k"]}" data-k="{esc(top3)}">'
             f'<rect x="150" y="{18+i*36}" width="{w:.0f}" height="24" rx="5" '
             f'fill="{col}" opacity="0.88"/>'
             f'<text x="144" y="{35+i*36}" font-size="12.5" text-anchor="end" '
             f'fill="#334155" {CJK}>{esc(g)}</text>'
             f'<text x="{150+w+8}" y="{35+i*36}" font-size="11.5" fill="#64748b" {CJK}>'
             f'{d["total"]} 次 · {d["per10k"]}/万字</text></g>')

# 词云式高频词
top_words = []
for g, d in order:
    for it in d["items"][:3]:
        top_words.append((it["w"], it["n"], g))
top_words.sort(key=lambda x: -x[1])
tw = top_words[:26]
mxn = tw[0][1]
cloud = ""
import random
random.seed(7)
for i, (w, n, g) in enumerate(tw):
    size = 13 + (n / mxn) ** 0.42 * 30
    col = ["#ef4444","#f97316","#f59e0b","#0ea5e9","#8b5cf6","#10b981"][i % 6]
    cloud += (f'<text x="{60+ (i%7)*122 + random.randint(-8,8)}" '
              f'y="{40 + (i//7)*48 + random.randint(-6,6)}" '
              f'font-size="{size:.0f}" fill="{col}" opacity="0.85" font-weight="600" '
              f'{CJK}>{esc(w)}</text>')

# ================= B. 标题语言学 =================
ts = lf["title"]
tstat = ts["总览"]
persons = ts["人称"]
types = ts["类型分布"]

tpie = ""
TCOL = {"陈述式": "#94a3b8", "第一人称宣言": "#0ea5e9", "悬念疑问式": "#f59e0b",
        "第二人称对话": "#ec4899", "复句转折": "#8b5cf6", "指示代词起手": "#10b981",
        "否定反转": "#ef4444", "内含疑问": "#f97316", "爆发感叹式": "#eab308"}
tot_t = sum(types.values())
ang = 0
cx, cy, R = 175, 175, 118
for k, v in sorted(types.items(), key=lambda x: -x[1]):
    sweep = v / tot_t * 360
    col = TCOL.get(k, "#94a3b8")
    a0, a1 = ang, ang + sweep
    x0 = cx + R * __import__("math").cos(__import__("math").radians(a0 - 90))
    y0 = cy + R * __import__("math").sin(__import__("math").radians(a0 - 90))
    x1 = cx + R * __import__("math").cos(__import__("math").radians(a1 - 90))
    y1 = cy + R * __import__("math").sin(__import__("math").radians(a1 - 90))
    laf = 1 if sweep > 180 else 0
    tpie += (f'<path d="M{cx},{cy} L{x0:.1f},{y0:.1f} A{R},{R} 0 {laf} 1 {x1:.1f},{y1:.1f} Z" '
             f'fill="{col}" opacity="0.87" stroke="#fff" stroke-width="2"/>')
    mid = (a0 + a1) / 2
    lx = cx + (R + 30) * __import__("math").cos(__import__("math").radians(mid - 90))
    ly = cy + (R + 30) * __import__("math").sin(__import__("math").radians(mid - 90))
    if v / tot_t > 0.03:
        tpie += (f'<text x="{lx:.0f}" y="{ly:.0f}" font-size="11.5" fill="#334155" '
                 f'text-anchor="middle" {CJK}>{esc(k)} {v}</text>')
    ang += sweep

# 人称条形
pbar = ""
mp = max(p["n"] for p in persons.values())
for i, (p, d) in enumerate(sorted(persons.items(), key=lambda x: -x[1]["n"])[:9]):
    w = d["n"] / mp * 300
    pbar += (f'<rect x="70" y="{14+i*30}" width="{w:.0f}" height="19" rx="4" fill="#0ea5e9" opacity="0.8"/>'
             f'<text x="64" y="{28+i*30}" font-size="12" text-anchor="end" fill="#334155" {CJK}>{esc(p)}</text>'
             f'<text x="{70+w+7}" y="{28+i*30}" font-size="11" fill="#64748b" {CJK}>'
             f'{d["n"]} ({d["pct"]}%)</text>')

# ================= C. 心声机制 =================
cats = im["cats"]
maxc = max(cats.values())
cbar = ""
for i, (c, n) in enumerate(sorted(cats.items(), key=lambda x: -x[1])):
    w = n / maxc * 560
    col = ["#ef4444","#f97316","#f59e0b","#eab308","#84cc16","#10b981",
           "#06b6d4","#0ea5e9","#6366f1","#8b5cf6"][i % 10]
    rep = im["rep"].get(c, [""])[0]
    cbar += (f'<g class="cb" data-c="{esc(c)}" data-n="{n}" data-r="{esc(rep[:70])}">'
             f'<rect x="112" y="{16+i*33}" width="{w:.0f}" height="23" rx="5" fill="{col}" opacity="0.88"/>'
             f'<text x="106" y="{32+i*33}" font-size="12.5" text-anchor="end" fill="#334155" {CJK}>{esc(c)}</text>'
             f'<text x="{112+w+8}" y="{32+i*33}" font-size="11" fill="#64748b" {CJK}>{n} ({n/im["total"]*100:.1f}%)</text></g>')

# 逐卷演变曲线
ve = im["vol_evo"]
W2, H2 = 1000, 330
ML, MT, PW, PH = 60, 30, 890, 240
mxv = max(v["章均"] for v in ve) or 1
pts = [[ML + i * PW / (len(ve) - 1), MT + PH - v["章均"] / mxv * PH * 0.9]
       for i, v in enumerate(ve)]
pl = " ".join(f"{'M' if i==0 else 'L'}{x:.0f},{y:.0f}" for i, (x, y) in enumerate(pts))
dots = ""
for i, (x, y) in enumerate(pts):
    dots += (f'<circle cx="{x:.0f}" cy="{y:.0f}" r="5.5" fill="#ef4444" stroke="#fff" stroke-width="2"/>'
             f'<text x="{x:.0f}" y="{y-13:.0f}" font-size="11.5" text-anchor="middle" '
             f'fill="#0f172a" font-weight="700" {CJK}>{ve[i]["章均"]}</text>')
xl = ""
for i, v in enumerate(ve):
    xl += (f'<text x="{ML+i*PW/(len(ve)-1):.0f}" y="{MT+PH+22}" font-size="10.5" '
           f'text-anchor="middle" fill="#475569" {CJK}>卷{i+1}</text>'
           f'<text x="{ML+i*PW/(len(ve)-1):.0f}" y="{MT+PH+38}" font-size="9" '
           f'text-anchor="middle" fill="#94a3b8" {CJK}>{v["心声数"]}条</text>')
grid2 = "".join(f'<line x1="{ML}" y1="{MT+PH*g/4:.0f}" x2="{ML+PW}" y2="{MT+PH*g/4:.0f}" '
                f'stroke="#e2e8f0"/>' for g in range(5))

# 情绪特征卡
feat = im["feat"]
fkeys = [("感叹号结尾_占比","33.6","以！收尾，情绪外放"),
         ("省略号结尾_占比","13.8","以…/~收尾，拖尾自嘲"),
         ("问号结尾_占比","10.9","以？收尾，自我质疑"),
         ("含颜文字_占比","5.4","带颜文字"),
         ("第一人称我_占比","32.1","含第一人称「我」"),
         ("提到萝莉_占比","13.4","提到萝莉"),
         ("提到师父_占比","12.8","提到师父")]
fcards = ""
for i, (k, _, desc) in enumerate(fkeys):
    v = feat.get(k, 0)
    col = "#ef4444" if v > 25 else ("#f59e0b" if v > 10 else "#0ea5e9")
    fcards += (f'<div class="fc"><div class="fv" style="color:{col}">{v}%</div>'
               f'<div class="fd">{desc}</div></div>')

# 代表句
reps = ""
for c, ss in im["rep"].items():
    if not ss: continue
    reps += (f'<div class="rc"><div class="rt">{esc(c)}</div>'
             + "".join(f'<div class="rq">{esc(s)}</div>' for s in ss[:2]) + '</div>')

# 长度分布
bk = im["buckets"]
bk_order = ["≤10字","11-20字","21-35字","36-60字",">60字"]
mxb = max(bk.get(k,0) for k in bk_order)
lbars = ""
for i, k in enumerate(bk_order):
    n = bk.get(k, 0)
    w = n / mxb * 340
    lbars += (f'<rect x="86" y="{14+i*30}" width="{w:.0f}" height="19" rx="4" fill="#8b5cf6" opacity="0.82"/>'
              f'<text x="80" y="{28+i*30}" font-size="11.5" text-anchor="end" fill="#334155" {CJK}>{k}</text>'
              f'<text x="{86+w+7}" y="{28+i*30}" font-size="11" fill="#64748b" {CJK}>{n}</text>')

lang = lf["lang"]
HTML = f'''<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<title>语言指纹</title><style>
body{{margin:0;background:#f1f5f9;{CJK};color:#0f172a}}
.wrap{{max-width:1400px;margin:0 auto;padding:20px}}
.nav{{display:flex;gap:10px;margin-bottom:16px;flex-wrap:wrap}}
.nav a{{padding:8px 15px;background:#fff;border-radius:9px;color:#334155;text-decoration:none;
 font-size:13px;font-weight:600;box-shadow:0 1px 5px rgba(0,0,0,.06)}}
.nav a.on{{background:#0f172a;color:#fff}}
.card{{background:#fff;border-radius:15px;box-shadow:0 2px 14px rgba(0,0,0,.07);padding:18px;margin-bottom:16px}}
h2{{margin:0 0 4px;font-size:19px}}
h3{{margin:0 0 10px;font-size:15px;color:#475569}}
.sub{{color:#94a3b8;font-size:12px;margin-bottom:14px;line-height:1.7}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
.fcards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:11px}}
.fc{{background:#f8fafc;border-radius:10px;padding:13px;text-align:center}}
.fv{{font-size:24px;font-weight:800}}
.fd{{font-size:11.5px;color:#64748b;margin-top:3px}}
.rc{{background:#f8fafc;border-radius:10px;padding:12px;margin-bottom:9px}}
.rt{{font-size:13px;font-weight:700;color:#0ea5e9;margin-bottom:6px}}
.rq{{font-size:12px;color:#475569;line-height:1.8;padding-left:9px;border-left:2.5px solid #e2e8f0;margin-bottom:5px}}
#tip{{position:fixed;display:none;background:rgba(15,23,42,.95);color:#fff;padding:10px 14px;
 border-radius:9px;font-size:12.5px;pointer-events:none;z-index:99;line-height:1.75;max-width:330px}}
.kv{{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:9px;margin-top:6px}}
.kv div{{background:#f8fafc;padding:9px;border-radius:8px;font-size:12px}}
.kv b{{display:block;font-size:17px;color:#0ea5e9}}
</style></head><body><div class="wrap">
<div class="nav">
 <a href="可视化总览.html">← 总览</a>
 <a href="情感曲线.html">① 情感曲线</a>
 <a href="人物关系网.html">② 关系网</a>
 <a href="灌水高潮热力图.html">③ 热力图</a>
 <a href="语言指纹.html" class="on">④ 语言指纹</a>
</div>

<div class="card">
<h2>④ 作者语言指纹</h2>
<div class="sub">套路用词 · 章节标题公式 · 心声机制 —— 三项可直接复用的写作特征</div>
</div>

<div class="card">
<h2>A · 套路用词画像</h2>
<div class="sub">11 类套路词 / 共 {sum(d["total"] for _,d in order)} 次。条形＝该类总次数，悬停看 Top3 词条。</div>
<svg viewBox="0 0 1000 {40+len(order)*36}" width="100%">{bars}</svg>
<h3 style="margin-top:18px">高频词云（字号 ∝ 频次）</h3>
<svg viewBox="0 0 900 {60 + ((len(tw)+6)//7)*48}" width="100%">{cloud}</svg>
</div>

<div class="grid2">
<div class="card">
<h2>B · 章节标题语言学</h2>
<div class="sub">589 个标题，均长 {tstat["均长"]} 字。疑问句 {tstat["疑问句占比"]}% · 感叹句 {tstat["感叹句占比"]}% · 纯陈述 {tstat["纯陈述占比"]}%</div>
<svg viewBox="0 0 360 360" width="100%">{tpie}</svg>
</div>
<div class="card">
<h2>标题人称分布</h2>
<div class="sub">「我」+「你」合计 {(persons["我"]["n"]+persons["你"]["n"])} / 589 = {(persons["我"]["n"]+persons["你"]["n"])/589*100:.0f}% —— 强对话感标题</div>
<svg viewBox="0 0 520 {30+9*30}" width="100%">{pbar}</svg>
<h3 style="margin-top:16px">标题公式</h3>
<div class="sub">
<b>我/你 + 反转短句</b>（占 36%）<br>
例：「我窜稀了」「你师父我看得上啊」「蠢师父是最好骗的」<br><br>
<b>首字 Top：</b>{" · ".join(f'{k}({v})' for k,v in ts["首字Top"][:6])}<br>
<b>类型：</b>{" · ".join(f'{k}({v})' for k,v in list(types.items())[:5])}
</div>
</div>
</div>

<div class="card">
<h2>C · 心声机制（{im["total"]} 条）</h2>
<div class="sub">全书核心喜剧装置。悬停分类看代表句。</div>
<svg viewBox="0 0 900 {30+len(cats)*33}" width="100%">{cbar}</svg>
</div>

<div class="grid2">
<div class="card">
<h2>心声逐卷演变（章均条数）</h2>
<div class="sub">第 8 卷起断崖关闭 —— 喜剧退场，风格转严肃</div>
<svg viewBox="0 0 {W2} {H2}" width="100%">
{grid2}
<path d="{pl}" fill="none" stroke="#ef4444" stroke-width="2.6"/>
<path d="{pl} L{W2-70},{MT+PH} L{ML},{MT+PH} Z" fill="#ef4444" opacity="0.08"/>
{dots}{xl}
<line x1="{ML}" y1="{MT}" x2="{ML}" y2="{MT+PH}" stroke="#cbd5e1" stroke-width="1.5"/>
<line x1="{ML}" y1="{MT+PH}" x2="{W2-70}" y2="{MT+PH}" stroke="#cbd5e1" stroke-width="1.5"/>
</svg>
</div>
<div class="card">
<h2>情绪特征</h2>
<div class="fcards">{fcards}</div>
<h3 style="margin-top:16px">心声长度分布</h3>
<svg viewBox="0 0 520 {24+5*30}" width="100%">{lbars}</svg>
<div class="sub" style="margin-top:8px">均长 {feat["均长"]} 字 · 中位 {feat["中位"]} · 最长 {feat["最长"]} 字</div>
</div>
</div>

<div class="card">
<h2>各分类代表心声</h2>
{reps}
</div>

<div class="card">
<h2>文体硬指标</h2>
<div class="kv">
<div><b>{lang["段均汉字"]}</b>段均汉字（中位 {lang["段长中位数"]}）</div>
<div><b>{lang["句均汉字"]}</b>句均汉字（中位 {lang["句中位数"]}）</div>
<div><b>{lang["短句(≤10字)占比"]}%</b>短句 ≤10 字占比</div>
<div><b>{lang["长句(>30字)占比"]}%</b>长句 &gt;30 字占比</div>
<div><b>{lang["一字句占比"]}%</b>一字句占比</div>
<div><b>{lang["段落数"]}</b>总段落数</div>
</div>
<div class="sub" style="margin-top:10px">段均 {lang["段均汉字"]} 字、句均 {lang["句均汉字"]} 字 ——
近 40% 是 ≤10 字短句，典型手机端快节奏网文体。</div>
</div>
</div>
<div id="tip"></div>
<script>
const tip=document.getElementById('tip');
document.querySelectorAll('.wb,.cb').forEach(g=>{{
  g.addEventListener('mousemove',e=>{{
    const kind=g.classList.contains('wb');
    tip.innerHTML=kind
      ? `<div style="font-weight:700;margin-bottom:4px">${{g.dataset.g}}</div>
         <div>合计 ${{g.dataset.t}} 次 · ${{g.dataset.p}}/万字</div>
         <div style="color:#93c5fd;margin-top:4px">Top3：${{g.dataset.k}}</div>`
      : `<div style="font-weight:700;margin-bottom:4px">${{g.dataset.c}}（${{g.dataset.n}} 条）</div>
         <div style="color:#cbd5e1;line-height:1.7">${{g.dataset.r}}…</div>`;
    tip.style.display='block';
    tip.style.left=Math.min(e.clientX+16,window.innerWidth-350)+'px';
    tip.style.top=(e.clientY+16)+'px';
  }});
  g.addEventListener('mouseleave',()=>tip.style.display='none');
}});
</script></body></html>'''

p = os.path.join(WEB, "语言指纹.html")
open(p, "w", encoding="utf-8").write(HTML)
print(f"✓ 语言指纹.html  {len(HTML)/1024:.1f} KB")
