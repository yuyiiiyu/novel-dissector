# -*- coding: utf-8 -*-
"""阶段8：生成三个可视化 HTML（纯手写 SVG，无 CDN / 无第三方库）
   ① 情感曲线  ② 人物关系网  ③ 灌水&高潮热力图
"""
import json, csv, os, statistics, collections, math, html

OUT = r"D:\aigc_pro\ai-video&draw\DeepSeek Harness\@ D Download 这个人明明很强却_2026-10-27\产出\data"
WEB = r"D:\aigc_pro\ai-video&draw\DeepSeek Harness\@ D Download 这个人明明很强却_2026-10-27\产出"
os.makedirs(WEB, exist_ok=True)

# ================= 读数据 =================
rows = []
with open(os.path.join(OUT, "chapters.csv"), encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        rows.append({"num": int(r["章号"]), "title": r["标题"], "chars": int(r["字数"]),
                     "paras": int(r["段落数"]), "dialog": int(r["对话引号数"]),
                     "inner": int(r["心声数"]), "sys": int(r["系统提示数"]),
                     "excl": int(r["感叹号"]), "quest": int(r["问号"]),
                     "ellip": int(r["省略号"]), "d_ratio": float(r["对话密度‰"])})
sig = {}
with open(os.path.join(OUT, "chapter_signals.csv"), encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        sig[int(r["章"])] = {"战斗": int(r["战斗"]), "甜度": int(r["甜度"])}
for r in rows:
    r.update(sig.get(r["num"], {"战斗": 0, "甜度": 0}))

vols = []
with open(os.path.join(OUT, "volumes.csv"), encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        lo, hi = r["范围"].split("-")
        vols.append({"name": r["卷"], "desc": r["说明"], "lo": int(lo), "hi": int(hi)})

net = json.load(open(os.path.join(OUT, "network_clean.json"), encoding="utf-8"))
extra = json.load(open(os.path.join(OUT, "analysis_extra.json"), encoding="utf-8"))

CJK = "font-family:'PingFang SC','Microsoft YaHei','Noto Sans CJK SC',sans-serif"

def wrap(txt, size=11, maxw=None, maxlines=2, maxchars=None):
    pass

def svg_text(x, y, s, size=12, fill="#334155", anchor="middle", weight="400", extra_attr=""):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
            f'font-weight="{weight}" {CJK} {extra_attr}>{html.escape(str(s))}</text>')

def smooth(vals, w=5):
    """移动平均"""
    out = []
    for i in range(len(vals)):
        lo, hi = max(0, i - w // 2), min(len(vals), i + w // 2 + 1)
        out.append(sum(vals[lo:hi]) / (hi - lo))
    return out

catmull = """function catmullRom2bezier(points) {
  // points: [[x,y],...] → SVG path with Catmull-Rom smoothing
  if (points.length < 2) return '';
  let d = 'M' + points[0][0] + ',' + points[0][1];
  for (let i = 0; i < points.length - 1; i++) {
    const p0 = points[i - 1] || points[i];
    const p1 = points[i];
    const p2 = points[i + 1];
    const p3 = points[i + 2] || p2;
    const cp1x = p1[0] + (p2[0] - p0[0]) / 6;
    const cp1y = p1[1] + (p2[1] - p0[1]) / 6;
    const cp2x = p2[0] - (p3[0] - p1[0]) / 6;
    const cp2y = p2[1] - (p3[1] - p1[1]) / 6;
    d += ` C${cp1x},${cp1y} ${cp2x},${cp2y} ${p2[0]},${p2[1]}`;
  }
  return d;
}"""

# ==========================================================
# ① 情感曲线
# ==========================================================
def build_curve():
    W, H = 1400, 980
    ML, MR, MT, MB = 68, 200, 60, 150
    pw, ph = W - ML - MR, H - MT - MB
    N = len(rows)

    SERIES = [
        ("心声密度", [r["inner"] for r in rows], "#f59e0b", "心声【】章计数"),
        ("对话密度", [r["d_ratio"] for r in rows], "#3b82f6", "引号数/千字 ‰"),
        ("战斗值",   [r["战斗"] for r in rows],   "#ef4444", "攻击/爆炸/斩杀等词频"),
        ("甜度值",   [r["甜度"] for r in rows],   "#ec4899", "脸红/喜欢/抱/媳妇等词频"),
        ("字数",     [r["chars"] / 1000 for r in rows], "#10b981", "千字"),
    ]

    # 全局归一化到 0-1（按各自 max）
    norm = []
    for name, vals, col, desc in SERIES:
        mx = max(vals) or 1
        norm.append([v / mx for v in vals])

    svgs = []
    for si, (name, vals, col, desc) in enumerate(SERIES):
        sm = smooth(norm[si], 9)
        pts = [[ML + i * pw / (N - 1), MT + ph - sm[i] * ph * 0.92] for i in range(N)]
        area = f"M{ML},{MT+ph} " + " ".join(f"L{x},{y}" for x, y in pts) + f" L{W-MR},{MT+ph} Z"
        dline = " ".join(f"{'M' if i==0 else 'L'}{x},{y}" for i, (x, y) in enumerate(pts))
        svgs.append(
            f'<path d="{area}" fill="{col}" opacity="0.07"/>'
            f'<path class="ln" d="{dline}" fill="none" stroke="{col}" stroke-width="1.6" '
            f'opacity="0.85" data-s="{si}"/>')
        if si == 0:
            grid = ""
            for gy in range(5):
                yy = MT + ph * gy / 4
                grid += (f'<line x1="{ML}" y1="{yy}" x2="{W-MR}" y2="{yy}" '
                         f'stroke="#e2e8f0" stroke-width="1"/>')
            for gx in range(11):
                xx = ML + pw * gx / 10
                grid += (f'<line x1="{xx}" y1="{MT}" x2="{xx}" y2="{MT+ph}" '
                         f'stroke="#eef2f7" stroke-width="1"/>')
            svgs.insert(0, grid)

    # 卷分隔 & 卷标签
    vol_marks = ""
    for vi, v in enumerate(vols):
        x = ML + (v["lo"] - 1) * pw / (N - 1)
        vol_marks += (f'<line x1="{x:.1f}" y1="{MT}" x2="{x:.1f}" y2="{MT+ph}" '
                      f'stroke="#94a3b8" stroke-width="1" stroke-dasharray="3 3" opacity="0.6"/>')
        cx = (ML + (v["lo"] - 1) * pw / (N - 1) + ML + (v["hi"] - 1) * pw / (N - 1)) / 2
        band = ["#fef3c7","#dbeafe","#fce7f3","#d1fae5","#fee2e2",
                "#e0e7ff","#fae8ff","#ffedd5","#cffafe","#f1f5f9"][vi % 10]
        vol_marks += (f'<rect x="{ML + (v["lo"]-1)*pw/(N-1):.1f}" y="{MT}" '
                      f'width="{(v["hi"]-v["lo"]+1)*pw/(N-1):.1f}" height="{ph}" '
                      f'fill="{band}" opacity="0.14"/>')
        vol_marks += svg_text(cx, MT + ph + 22, f"卷{vi+1}", 12, "#475569", weight="700")
        short = v["name"].split(" ", 1)[-1] if " " in v["name"] else v["name"]
        words = short
        vol_marks += svg_text(cx, MT + ph + 40, words[:8], 10, "#64748b")
        vol_marks += svg_text(cx, MT + ph + 56, words[8:16], 10, "#64748b")

    # X 轴
    xticks = ""
    for t in range(1, N + 1, 50):
        xx = ML + (t - 1) * pw / (N - 1)
        xticks += svg_text(xx, MT + ph + 84, str(t), 11, "#94a3b8")

    legend = ""
    for si, (name, vals, col, desc) in enumerate(SERIES):
        yy = 120 + si * 34
        legend += (f'<rect x="{W-MR+16}" y="{yy-11}" width="13" height="13" rx="3" fill="{col}"/>'
                   f'<text x="{W-MR+36}" y="{yy}" font-size="13" fill="#1e293b" {CJK} '
                   f'font-weight="600">{name}</text>'
                   f'<text x="{W-MR+36}" y="{yy+15}" font-size="10" fill="#94a3b8" {CJK}>'
                   f'{desc}</text>'
                   f'<text x="{W-MR+36}" y="{yy+30}" font-size="10" fill="#cbd5e1" {CJK}>'
                   f'峰值 {max(vals)}</text>')

    svg = f'''<svg viewBox="0 0 {W} {H}" width="100%" style="background:#fff">
  <rect width="{W}" height="{H}" fill="#fff"/>
  {svg_text(W/2, 40, "《这个人明明很强却偏要坑萝莉师傅》589 章情感/节奏曲线", 20, "#0f172a", weight="700")}
  {svg_text(W/2, 64, "移动平均窗口=9章 · 各序列按自身峰值归一化 · 悬停曲线查看数值", 12, "#94a3b8")}
  {legend}
  {vol_marks}
  {xticks}
  {''.join(svgs)}
  <line x1="{ML}" y1="{MT}" x2="{ML}" y2="{MT+ph}" stroke="#cbd5e1" stroke-width="1.5"/>
  <line x1="{ML}" y1="{MT+ph}" x2="{W-MR}" y2="{MT+ph}" stroke="#cbd5e1" stroke-width="1.5"/>
  {svg_text(ML-14, MT+ph/2, "归一化强度", 12, "#64748b", extra_attr=f'transform="rotate(-90 {ML-14} {MT+ph/2})"')}
  {svg_text(W/2, H-24, "章号 →", 13, "#475569", weight="600")}
</svg>'''

    js = f'''
const RAW={json.dumps({r["num"]: {"心声": r["inner"], "对话‰": r["d_ratio"], "战斗": r["战斗"],
                                  "甜度": r["甜度"], "字数": r["chars"]} for r in rows})};
const NAMES={json.dumps([s[0] for s in SERIES])};
const KEYS={json.dumps(["心声","对话‰","战斗","甜度","字数"])};
const RAWV={json.dumps([[r["inner"] for r in rows],[r["d_ratio"] for r in rows],
                        [r["战斗"] for r in rows],[r["甜度"] for r in rows],
                        [r["chars"] for r in rows]])};
const ML={ML},MR={MR},MT={MT},PW={pw},PH={ph},N={N};
document.querySelectorAll('.ln').forEach(p=>{{
  p.addEventListener('mousemove',e=>{{
    const si=+p.dataset.s;
    const r=p.ownerSVGElement.getBoundingClientRect();
    const x=(e.clientX-r.left)/r.width*{W};
    let i=Math.round((x-ML)/PW*(N-1));
    i=Math.max(0,Math.min(N-1,i));
    const rv=RAWV[si][i];
    const tip=document.getElementById('tip');
    const others=NAMES.map((n,k)=>k===si?`<b style="color:#0f172a">${{n}}: ${{RAWV[k][i]}}</b>`:`${{n}}: ${{RAWV[k][i]}}`).join('　');
    tip.innerHTML=`<div style="font-weight:700;margin-bottom:4px">第${{i+1}}章</div>`+others;
    tip.style.display='block';
    const px=(ML+i*PW/(N-1))/ {W} *r.width+r.left;
    tip.style.left=Math.min(px+14,window.innerWidth-280)+'px';
    tip.style.top=(e.clientY+16)+'px';
  }});
  p.addEventListener('mouseleave',()=>document.getElementById('tip').style.display='none');
}});
'''

    return f'''<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<title>情感曲线</title><style>
body{{margin:0;background:#f1f5f9;{CJK}}}
.wrap{{max-width:1440px;margin:0 auto;padding:18px}}
.card{{background:#fff;border-radius:14px;box-shadow:0 2px 14px rgba(0,0,0,.07);padding:10px}}
#tip{{position:fixed;display:none;background:rgba(15,23,42,.94);color:#fff;padding:9px 13px;
 border-radius:8px;font-size:12px;{CJK};pointer-events:none;z-index:99;line-height:1.7}}
.nav{{display:flex;gap:10px;margin-bottom:14px;flex-wrap:wrap}}
.nav a{{padding:8px 16px;background:#fff;border-radius:9px;color:#334155;text-decoration:none;
 font-size:13px;font-weight:600;box-shadow:0 1px 5px rgba(0,0,0,.06)}}
.nav a.on{{background:#0f172a;color:#fff}}
</style></head><body>
<div class="wrap">
<div class="nav">
 <a href="情感曲线.html" class="on">① 情感曲线</a>
 <a href="人物关系网.html">② 人物关系网</a>
 <a href="灌水高潮热力图.html">③ 灌水/高潮热力图</a>
 <a href="拆解总报告.md">📄 总报告</a>
</div>
<div class="card">{svg}</div>
</div>
<div id="tip"></div>
<script>{catmull}{js}</script></body></html>'''

# ==========================================================
# ② 人物关系网（力导向布局，纯 JS 实现）
# ==========================================================
def build_network():
    nodes = net["nodes"][:15]
    edges = [e for e in net["edges"]
             if e["source"] in {n["id"] for n in nodes}
             and e["target"] in {n["id"] for n in nodes}][:70]

    data = {"nodes": nodes, "edges": edges}

    js = f'''
const DATA={json.dumps(data, ensure_ascii=False)};
const W=1180,H=760,CX=W/2,CY=H/2;
const NS=DATA.nodes,ES=DATA.edges;
const maxt=Math.max(...NS.map(n=>n.total)),maxw=Math.max(...ES.map(e=>e.weight));
// 初始圆形布局
NS.forEach((n,i)=>{{
  const a=i/NS.length*Math.PI*2;
  const R=n.id==='林恩'?0:(n.id==='奈奈子'?90:210+Math.random()*60);
  n.x=CX+Math.cos(a)*R; n.y=CY+Math.sin(a)*R;
  n.r=8+Math.sqrt(n.total/maxt)*26;
  n.vx=0;n.vy=0;
}});
const byId={{}};NS.forEach(n=>byId[n.id]=n);
// 力导向迭代
for(let it=0;it<420;it++){{
  const k=Math.sqrt(NS.length*26000/NS.length);
  for(let i=0;i<NS.length;i++)for(let j=i+1;j<NS.length;j++){{
    const a=NS[i],b=NS[j];let dx=b.x-a.x,dy=b.y-a.y,d=Math.hypot(dx,dy)||1;
    const rep=k*k/d*0.55;
    a.vx-=dx/d*rep;a.vy-=dy/d*rep;b.vx+=dx/d*rep;b.vy+=dy/d*rep;
  }}
  ES.forEach(e=>{{
    const a=byId[e.source],b=byId[e.target];
    let dx=b.x-a.x,dy=b.y-a.y,d=Math.hypot(dx,dy)||1;
    const target=60+(1-e.weight/maxw)*190;
    const f=(d-target)*0.022*(0.35+e.weight/maxw);
    a.vx+=dx/d*f*10;a.vy+=dy/d*f*10;b.vx-=dx/d*f*10;b.vy-=dy/d*f*10;
  }});
  NS.forEach(n=>{{
    n.vx+=(CX-n.x)*0.012;n.vy+=(CY-n.y)*0.012;
    n.vx*=0.82;n.vy*=0.82;
    n.x+=Math.max(-24,Math.min(24,n.vx));n.y+=Math.max(-24,Math.min(24,n.vy));
    n.x=Math.max(n.r+16,Math.min(W-n.r-16,n.x));
    n.y=Math.max(n.r+16,Math.min(H-n.r-16,n.y));
  }});
}}
const svg=document.getElementById('net');
const PAL=['#0ea5e9','#f43f5e','#f59e0b','#10b981','#8b5cf6','#ec4899','#06b6d4','#84cc16','#f97316','#6366f1','#14b8a6','#eab308','#a855f7','#22c55e','#3b82f6'];
NS.forEach((n,i)=>n.color=PAL[i%PAL.length]);
let html='';
// 边
ES.forEach(e=>{{
  const a=byId[e.source],b=byId[e.target];
  const op=0.16+e.weight/maxw*0.62;
  const sw=0.7+e.weight/maxw*4.4;
  html+=`<line x1="${{a.x}}" y1="${{a.y}}" x2="${{b.x}}" y2="${{b.y}}" stroke="#64748b"
    stroke-width="${{sw.toFixed(2)}}" opacity="${{op.toFixed(2)}}" class="e"
    data-s="${{e.source}}" data-t="${{e.target}}" data-w="${{e.weight}}" data-c="${{e.co}}"/>`;
}});
// 节点
NS.forEach(n=>{{
  html+=`<g class="nd" data-id="${{n.id}}">
   <circle cx="${{n.x}}" cy="${{n.y}}" r="${{n.r}}" fill="${{n.color}}" opacity="0.9"
     stroke="#fff" stroke-width="2.5"/>
   <text x="${{n.x}}" y="${{n.y+4}}" font-size="${{Math.max(9,Math.min(14,n.r*0.62))}}"
     fill="#fff" text-anchor="middle" font-weight="700"
     style="pointer-events:none;font-family:'PingFang SC','Microsoft YaHei',sans-serif">${{n.id}}</text>
  </g>`;
}});
svg.innerHTML=html;
// 交互
const tip=document.getElementById('tip');
document.querySelectorAll('.nd').forEach(g=>{{
  g.addEventListener('mouseenter',e=>{{
    const id=g.dataset.id;
    const nb=ES.filter(x=>x.source===id||x.target===id)
      .sort((a,b)=>b.weight-a.weight).slice(0,7)
      .map(x=>`${{x.source===id?x.target:x.source}} (共现${{x.co}}章)`).join('<br>');
    const self=NS.find(n=>n.id===id);
    tip.innerHTML=`<div style="font-weight:700;font-size:14px;margin-bottom:5px">${{id}}</div>
      <div>提及 ${{self.total}} 次 · 覆盖 ${{self.span}} 章</div>
      <div>登场 ${{self.first}} → ${{self.last}} 章</div>
      <div style="margin-top:6px;color:#93c5fd">最强关联：<br>${{nb}}</div>`;
    tip.style.display='block';
    document.querySelectorAll('.e').forEach(l=>{{
      l.style.opacity=(l.dataset.s===id||l.dataset.t===id)?'0.85':'0.05';
      l.style.stroke=(l.dataset.s===id||l.dataset.t===id)?'#f43f5e':'#64748b';
    }});
  }});
  g.addEventListener('mousemove',e=>{{
    tip.style.left=(e.clientX+18)+'px';tip.style.top=(e.clientY+18)+'px';
  }});
  g.addEventListener('mouseleave',()=>{{
    tip.style.display='none';
    document.querySelectorAll('.e').forEach(l=>{{
      const op=0.16+(+l.dataset.w)/maxw*0.62;
      l.style.opacity=op;l.style.stroke='#64748b';
    }});
  }});
}});
'''

    # 静态侧边表格
    top_e = edges[:14]
    trows = "".join(
        f"<tr><td>{html.escape(e['source'])}</td><td>{html.escape(e['target'])}</td>"
        f"<td><b>{e['co']}</b></td><td>{e['jaccard']}</td>"
        f"<td><div class='bar' style='width:{min(100,e['weight']/2.6)}%'></div></td></tr>"
        for e in top_e)

    return f'''<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<title>人物关系网</title><style>
body{{margin:0;background:#f1f5f9;font-family:'PingFang SC','Microsoft YaHei','Noto Sans CJK SC',sans-serif}}
.wrap{{max-width:1500px;margin:0 auto;padding:18px}}
.nav{{display:flex;gap:10px;margin-bottom:14px;flex-wrap:wrap}}
.nav a{{padding:8px 16px;background:#fff;border-radius:9px;color:#334155;text-decoration:none;
 font-size:13px;font-weight:600;box-shadow:0 1px 5px rgba(0,0,0,.06)}}
.nav a.on{{background:#0f172a;color:#fff}}
.grid{{display:grid;grid-template-columns:1fr 380px;gap:14px}}
.card{{background:#fff;border-radius:14px;box-shadow:0 2px 14px rgba(0,0,0,.07);padding:14px}}
h2{{margin:0 0 4px;font-size:18px;color:#0f172a}}
.sub{{color:#94a3b8;font-size:12px;margin-bottom:10px}}
table{{width:100%;border-collapse:collapse;font-size:12.5px}}
th{{text-align:left;padding:7px 6px;border-bottom:2px solid #e2e8f0;color:#475569;font-size:11px}}
td{{padding:6px;border-bottom:1px solid #f1f5f9;color:#334155}}
.bar{{height:7px;background:linear-gradient(90deg,#38bdf8,#0ea5e9);border-radius:4px}}
#tip{{position:fixed;display:none;background:rgba(15,23,42,.95);color:#fff;padding:10px 14px;
 border-radius:9px;font-size:12.5px;pointer-events:none;z-index:99;line-height:1.75;max-width:280px}}
</style></head><body>
<div class="wrap">
<div class="nav">
 <a href="情感曲线.html">① 情感曲线</a>
 <a href="人物关系网.html" class="on">② 人物关系网</a>
 <a href="灌水高潮热力图.html">③ 灌水/高潮热力图</a>
 <a href="拆解总报告.md">📄 总报告</a>
</div>
<div class="grid">
 <div class="card">
  <h2>人物共现关系网</h2>
  <div class="sub">力导向布局 · 圆越大＝提及越多 · 线越粗＝共现章数越多 · 悬停高亮邻居</div>
  <svg id="net" viewBox="0 0 1180 760" width="100%" style="background:#fafbfc;border-radius:10px"></svg>
 </div>
 <div class="card">
  <h2>最强关系 Top14</h2>
  <div class="sub">共现章数 / Jaccard 相似度 / 边权重</div>
  <table><tr><th>角色A</th><th>角色B</th><th>共现</th><th>J</th><th>权重</th></tr>
  {trows}</table>
  <h2 style="margin-top:18px">角色总览</h2>
  <div class="sub">按提及次数排序</div>
  <table><tr><th>角色</th><th>提及</th><th>覆盖章</th><th>登场</th></tr>
  {"".join(f"<tr><td><b>{html.escape(n['id'])}</b></td><td>{n['total']}</td><td>{n['span']}</td><td>{n['first']}→{n['last']}</td></tr>" for n in net["nodes"][:15])}
  </table>
 </div>
</div>
</div>
<div id="tip"></div>
<script>{js}</script></body></html>'''

# ==========================================================
# ③ 灌水 / 高潮热力图
# ==========================================================
def build_heat():
    water = {w["num"]: w for w in extra["water"]}
    peak = {p["num"]: p for p in extra["peak"]}
    N = len(rows)
    COLS = 30
    ROWSN = (N + COLS - 1) // COLS          # 20 行
    cell, gap = 38, 4
    W = 90 + COLS * (cell + gap)
    H = 200 + ROWSN * (cell + gap)

    maxb = max(r["战斗"] for r in rows) or 1
    maxs = max(r["甜度"] for r in rows) or 1
    maxc = max(r["chars"] for r in rows)
    minc = min(r["chars"] for r in rows)

    def heat_color(r):
        # 综合热度：战斗+甜度为主，字数为辅
        v = r["战斗"] / maxb * 0.5 + r["甜度"] / maxs * 0.35 + \
            (r["chars"] - minc) / (maxc - minc) * 0.15
        v = min(1, v)
        # 冷蓝 → 青 → 黄 → 橙 → 红
        stops = [(0.0, (226, 240, 250)), (0.25, (125, 211, 252)),
                 (0.45, (52, 211, 153)), (0.65, (250, 204, 21)),
                 (0.82, (249, 115, 22)), (1.0, (225, 29, 72))]
        for i in range(len(stops) - 1):
            a, b = stops[i], stops[i + 1]
            if a[0] <= v <= b[0]:
                t = (v - a[0]) / (b[0] - a[0])
                return "#%02x%02x%02x" % tuple(int(a[1][k] + (b[1][k] - a[1][k]) * t) for k in range(3))
        return "#e11d48"

    cells = ""
    for i, r in enumerate(rows):
        cx = i % COLS; cy = i // COLS
        x = 90 + cx * (cell + gap); y = 130 + cy * (cell + gap)
        fill = heat_color(r)
        stroke = ""
        badge = ""
        if r["num"] in water:
            stroke = 'stroke="#1e293b" stroke-width="2.2" stroke-dasharray="3 2"'
            badge = (f'<circle cx="{x+cell-6}" cy="{y+6}" r="4.5" fill="#1e293b"/>')
        elif r["num"] in peak:
            stroke = 'stroke="#fbbf24" stroke-width="2.2"'
            badge = (f'<circle cx="{x+cell-6}" cy="{y+6}" r="4.5" fill="#fbbf24"/>')
        cells += (f'<g class="cl" data-n="{r["num"]}" data-t="{html.escape(r["title"])}" '
                  f'data-c="{r["chars"]}" data-b="{r["战斗"]}" data-s="{r["甜度"]}" '
                  f'data-i="{r["inner"]}" data-d="{r["d_ratio"]}" '
                  f'data-w="{"灌水" if r["num"] in water else ("高潮" if r["num"] in peak else "常规")}">'
                  f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="5" fill="{fill}" {stroke}/>'
                  f'{badge}'
                  f'<text x="{x+cell/2}" y="{y+cell/2+4}" font-size="10.5" text-anchor="middle" '
                  f'fill="{"#fff" if r["num"] in water or r["num"] in peak else "#475569"}" '
                  f'font-weight="600" style="pointer-events:none;'
                  f'font-family:\'PingFang SC\',\'Microsoft YaHei\',sans-serif">{r["num"]}</text>'
                  f'</g>')

    # 图例
    lg = ""
    for i in range(60):
        x = 90 + i * 6.6
        v = i / 59
        stops = [(0.0, (226, 240, 250)), (0.25, (125, 211, 252)),
                 (0.45, (52, 211, 153)), (0.65, (250, 204, 21)),
                 (0.82, (249, 115, 22)), (1.0, (225, 29, 72))]
        for j in range(len(stops) - 1):
            a, b = stops[j], stops[j + 1]
            if a[0] <= v <= b[0]:
                t = (v - a[0]) / (b[0] - a[0])
                c = "#%02x%02x%02x" % tuple(int(a[1][k] + (b[1][k] - a[1][k]) * t) for k in range(3))
                lg += f'<rect x="{x}" y="96" width="7" height="14" fill="{c}"/>'
                break
    lg += svg_text(90, 90, "低", 11, "#64748b", anchor="start")
    lg += svg_text(90 + 60 * 6.6, 90, "高 ← 综合热度（战斗50% + 甜度35% + 字数15%）", 11,
                   "#64748b", anchor="start")

    # 灌水统计
    vw = extra["vol_water"]
    bars = ""
    maxrate = max(v["灌水率"] for v in vw) or 1
    for i, v in enumerate(vw):
        yy = 130 + i * 32
        wd = v["灌水率"] / maxrate * 250
        col = "#ef4444" if v["灌水率"] >= 10 else ("#f59e0b" if v["灌水率"] >= 4 else "#10b981")
        bars += (f'<text x="0" y="{yy+11}" font-size="11.5" fill="#334155" '
                 f'font-family="\'PingFang SC\',\'Microsoft YaHei\',sans-serif">{html.escape(v["卷"][:16])}</text>'
                 f'<rect x="200" y="{yy}" width="{wd:.0f}" height="15" rx="4" fill="{col}" opacity="0.85"/>'
                 f'<text x="{200+wd+8}" y="{yy+12}" font-size="11" fill="#475569" '
                 f'font-family="\'PingFang SC\',\'Microsoft YaHei\',sans-serif">'
                 f'{v["灌水率"]}% ({v["灌水章"]}/{v["章数"]}章)</text>')

    statW = 620
    panel = (f'<g transform="translate({W - statW - 20}, 150)">'
             f'<text x="0" y="0" font-size="15" font-weight="700" fill="#0f172a" '
             f'font-family="\'PingFang SC\',\'Microsoft YaHei\',sans-serif">各卷灌水率</text>'
             f'<g transform="translate(0,20)">{bars}</g></g>')

    js = '''
const tip=document.getElementById('tip');
document.querySelectorAll('.cl').forEach(g=>{
  g.addEventListener('mousemove',e=>{
    const w=g.dataset.w;
    const col=w==='灌水'?'#94a3b8':(w==='高潮'?'#fbbf24':'#7dd3fc');
    tip.innerHTML=`<div style="font-weight:700;font-size:13.5px;margin-bottom:5px">
      第${g.dataset.n}章 ${g.dataset.t}</div>
      <div style="color:${col};font-weight:600;margin-bottom:4px">${w}章</div>
      <div>字数 ${g.dataset.c} · 对话 ${g.dataset.d}‰</div>
      <div>战斗 ${g.dataset.b} · 甜度 ${g.dataset.s} · 心声 ${g.dataset.i}</div>`;
    tip.style.display='block';
    tip.style.left=(e.clientX+16)+'px';tip.style.top=(e.clientY+16)+'px';
  });
  g.addEventListener('mouseleave',()=>tip.style.display='none');
});
'''

    svg = f'''<svg viewBox="0 0 {W} {H}" width="100%" style="background:#fff">
  {svg_text(90, 40, "589 章全景热力图 · 灌水章 / 高潮章定位", 20, "#0f172a", "start", "700")}
  {svg_text(90, 62, "每格 = 1 章（共 30 列）· 悬停查看明细", 12, "#94a3b8", "start")}
  {lg}
  {cells}
  {panel}
  <g transform="translate(90,{H-46})">
    <circle cx="6" cy="0" r="5" fill="#1e293b"/>
    <text x="18" y="4" font-size="12" fill="#334155" font-family="'PingFang SC','Microsoft YaHei',sans-serif">疑似灌水章（{len(water)} 章 / {len(water)/N*100:.1f}%）</text>
    <circle cx="230" cy="0" r="5" fill="#fbbf24"/>
    <text x="242" y="4" font-size="12" fill="#334155" font-family="'PingFang SC','Microsoft YaHei',sans-serif">高潮章（战斗/甜度/心声高强度）</text>
  </g>
</svg>'''

    wlist = sorted(water.values(), key=lambda x: (-x["score"], x["num"]))
    wrows = "".join(
        f"<tr><td>{w['num']}</td><td>{html.escape(w['title'][:18])}</td>"
        f"<td>{w['chars']}</td><td>{w['d_ratio']}‰</td>"
        f"<td><b>{w['score']}</b></td><td style='font-size:11px;color:#64748b'>"
        f"{html.escape(w['reason'][:34])}</td></tr>" for w in wlist[:20])

    return f'''<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<title>灌水/高潮热力图</title><style>
body{{margin:0;background:#f1f5f9;font-family:'PingFang SC','Microsoft YaHei','Noto Sans CJK SC',sans-serif}}
.wrap{{max-width:1500px;margin:0 auto;padding:18px}}
.nav{{display:flex;gap:10px;margin-bottom:14px;flex-wrap:wrap}}
.nav a{{padding:8px 16px;background:#fff;border-radius:9px;color:#334155;text-decoration:none;
 font-size:13px;font-weight:600;box-shadow:0 1px 5px rgba(0,0,0,.06)}}
.nav a.on{{background:#0f172a;color:#fff}}
.card{{background:#fff;border-radius:14px;box-shadow:0 2px 14px rgba(0,0,0,.07);padding:14px;margin-bottom:14px}}
h2{{margin:0 0 4px;font-size:18px;color:#0f172a}}
.sub{{color:#94a3b8;font-size:12px;margin-bottom:10px}}
table{{width:100%;border-collapse:collapse;font-size:12.5px}}
th{{text-align:left;padding:7px 6px;border-bottom:2px solid #e2e8f0;color:#475569;font-size:11px}}
td{{padding:6px;border-bottom:1px solid #f1f5f9;color:#334155}}
#tip{{position:fixed;display:none;background:rgba(15,23,42,.95);color:#fff;padding:10px 14px;
 border-radius:9px;font-size:12.5px;pointer-events:none;z-index:99;line-height:1.7}}
</style></head><body>
<div class="wrap">
<div class="nav">
 <a href="情感曲线.html">① 情感曲线</a>
 <a href="人物关系网.html">② 人物关系网</a>
 <a href="灌水高潮热力图.html" class="on">③ 灌水/高潮热力图</a>
 <a href="拆解总报告.md">📄 总报告</a>
</div>
<div class="card">{svg}</div>
<div class="card">
 <h2>疑似灌水章清单（按风险分排序）</h2>
 <div class="sub">判定：字数&lt;1900 · 对话密度&lt;8‰ · 心声/系统全无 · 战斗/感情均无 · 信息量极低 → 命中≥3 项即标记</div>
 <table><tr><th>章</th><th>标题</th><th>字数</th><th>对话‰</th><th>风险分</th><th>判定依据</th></tr>
 {wrows}</table>
</div>
</div>
<div id="tip"></div>
<script>{js}</script></body></html>'''

# ================= 写文件 =================
for fn, content in (("情感曲线.html", build_curve()),
                    ("人物关系网.html", build_network()),
                    ("灌水高潮热力图.html", build_heat())):
    p = os.path.join(WEB, fn)
    open(p, "w", encoding="utf-8").write(content)
    print(f"✓ {fn}  {len(content)/1024:.1f} KB")
