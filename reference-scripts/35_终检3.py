# -*- coding: utf-8 -*-
"""终检3：含⑦章内工程学的最终复查"""
import os, re, json, csv, io, sys, subprocess, tempfile
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

WEB = r"D:\aigc_pro\ai-video&draw\DeepSeek Harness\@ D Download 这个人明明很强却_2026-10-27\产出"
D = os.path.join(WEB, "data"); SCR = os.path.join(WEB, "scripts")
L = []; ok = True
def p(s): L.append(str(s))
def chk(c, m):
    global ok
    if c: p("  OK   " + m)
    else: ok = False; p("  FAIL " + m)

p("=" * 62); p("终检 3 —— 最终复查（含⑦）"); p("=" * 62)

htmls = sorted(f for f in os.listdir(WEB) if f.endswith(".html"))
p("\n[1] HTML 页面 (%d)" % len(htmls))
for fn in htmls:
    h = open(os.path.join(WEB, fn), encoding="utf-8").read()
    bad = []
    if "NaN" in h: bad.append("NaN")
    if "undefined" in h: bad.append("undefined")
    if re.search(r"__[A-Z0-9]+__", h): bad.append("placeholder")
    if h.count("<svg") == 0 and fn != "可视化总览.html": bad.append("no-svg")
    chk(not bad, "%-22s %6.1fKB svg=%d %s" % (fn, len(h)/1024.0, h.count("<svg"),
        ("-> " + ",".join(bad)) if bad else ""))

p("\n[2] 导航互链")
expect = set(htmls) | {"拆解总报告.md"}
for fn in htmls:
    h = open(os.path.join(WEB, fn), encoding="utf-8").read()
    links = set(re.findall(r'href="([^"]+\.(?:html|md))"', h))
    miss = expect - links - ({fn} if fn == "可视化总览.html" else set())
    chk(not miss, "%-22s links=%d %s" % (fn, len(links), ("缺:" + ",".join(miss)) if miss else ""))

p("\n[3] JS 语法")
for fn in htmls:
    h = open(os.path.join(WEB, fn), encoding="utf-8").read()
    js = "\n".join(re.findall(r"<script>(.*?)</script>", h, re.S))
    t = os.path.join(tempfile.gettempdir(), "_c3.js")
    open(t, "w", encoding="utf-8").write(js if js.strip() else "void 0")
    r = subprocess.run(["node", "--check", t], capture_output=True, text=True)
    chk(r.returncode == 0, "%-22s %s" % (fn, "OK" if r.returncode == 0 else r.stderr[:50]))

p("\n[4] HTML 引用数据文件")
refs = set()
for fn in htmls:
    h = open(os.path.join(WEB, fn), encoding="utf-8").read()
    refs |= set(re.findall(r'data/[A-Za-z0-9_\u4e00-\u9fa5]+\.(?:csv|json|txt)', h))
for r in sorted(refs): chk(os.path.exists(os.path.join(WEB, r)), r)

p("\n[5] 数据行数")
def rows(f):
    with open(os.path.join(D, f), encoding="utf-8-sig") as x: return sum(1 for _ in csv.DictReader(x))
C = [("chapters.csv",589),("chapter_signals.csv",589),("roles.csv",50),
     ("worldbuilding.csv",360),("volumes.csv",10),("灌水章检测.csv",28),
     ("高潮章.csv",40),("人物关系边表.csv",62),("标题语言学.csv",589),
     ("心声分类.csv",2129),("心声分卷演变.csv",10),("转折点.csv",10),
     ("章末钩子分类.csv",589),("角色音色.csv",10),("伏笔时间线.csv",15),
     ("场景迁移.csv",10),("套路用词.csv",67),("角色台词库.csv",142),
     ("章内节奏模板.csv",10),("爽文桥段.csv",10),("对话轮次.csv",589),
     ("章首结构.csv",589)]
for f, e in C:
    try: a = rows(f)
    except Exception as ex: chk(False, "%s err" % f); continue
    chk(a == e, "%-24s rows=%d" % (f, a))

p("\n[6] 跨文件口径")
q = json.load(open(os.path.join(D,"quotes.json"),encoding="utf-8"))
im = json.load(open(os.path.join(D,"inner_monologue.json"),encoding="utf-8"))
net = json.load(open(os.path.join(D,"network_clean.json"),encoding="utf-8"))
tp = json.load(open(os.path.join(D,"turning_points.json"),encoding="utf-8"))
nv = json.load(open(os.path.join(D,"narrative.json"),encoding="utf-8"))
ci = json.load(open(os.path.join(D,"chapter_internal.json"),encoding="utf-8"))
op = json.load(open(os.path.join(D,"opening.json"),encoding="utf-8"))
for n, e, a in [("心声",len(q["inner"]),im["total"]),("系统",42,len(q["system"])),
                ("金句",4025,len(q["gold"])),("钩子",589,len(q["hooks"])),
                ("关系网节点",15,len(net["nodes"])),("关系网边",62,len(net["edges"])),
                ("转折卷",10,len(tp["VA"])),("钩子分类",589,nv["hook"]["total"]),
                ("伏笔条",15,len(nv["foreshadow"])),("场景卷",10,len(nv["scene_vol"])),
                ("对话总回合",13433,ci["turn_stat"]["total"]),
                ("开场方式合计",589,sum(op["first_mode"].values()))]:
    chk(e == a, "%-14s %s" % (n, a))

p("\n[7] 报告章节")
rp = open(os.path.join(WEB,"拆解总报告.md"),encoding="utf-8").read()
for s in ["一、书籍元数据","二、结构层","三、人物层","四、世界观层","五、剧情层",
          "六、节拍层","七、节奏层","九之二、高潮章分类","九之三、作者语言指纹",
          "九之四、转折点","九之五、叙事工程学","九之六、章内工程学",
          "十、这套拆解还能怎么继续挖"]:
    chk(s in rp, s)

p("\n[8] 产出清单")
p("  HTML   : %d" % len(htmls))
p("  data   : %d" % len(os.listdir(D)))
p("  scripts: %d" % len([f for f in os.listdir(SCR) if f.endswith(".py")]))

p("\n" + "=" * 62)
p("RESULT: " + ("ALL PASS" if ok else "HAS FAILURE"))
p("=" * 62)

out = os.path.join(SCR, "final_check3.txt")
open(out, "w", encoding="utf-8").write("\n".join(L))
print("written:", out)
