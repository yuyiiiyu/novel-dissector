# -*- coding: utf-8 -*-
"""终检2：全面复查全部产物（含叙事工程学新增项）"""
import os, re, json, csv, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

WEB = r"D:\aigc_pro\ai-video&draw\DeepSeek Harness\@ D Download 这个人明明很强却_2026-10-27\产出"
D = os.path.join(WEB, "data")
SCR = os.path.join(WEB, "scripts")
L = []
def p(s): L.append(str(s))
ok = True
def chk(cond, msg):
    global ok
    if cond: p("  OK   " + msg)
    else:
        ok = False; p("  FAIL " + msg)

p("=" * 62)
p("终检 2 —— 全面复查")
p("=" * 62)

# 1 HTML
p("\n[1] HTML 页面")
htmls = [f for f in os.listdir(WEB) if f.endswith(".html")]
for fn in sorted(htmls):
    h = open(os.path.join(WEB, fn), encoding="utf-8").read()
    bad = []
    if "NaN" in h: bad.append("NaN")
    if "undefined" in h: bad.append("undefined")
    if "__" in h and re.search(r"__[A-Z0-9]+__", h): bad.append("placeholder")
    if h.count("<svg") == 0 and fn != "可视化总览.html": bad.append("no-svg")
    chk(not bad, "%-20s %6.1fKB svg=%d %s" % (fn, len(h)/1024.0, h.count("<svg"),
        ("-> " + ",".join(bad)) if bad else ""))

# 2 导航互链
p("\n[2] 导航互链（每页应链到全部 6 个分析页 + 总览 + 报告）")
expect = {"可视化总览.html", "情感曲线.html", "人物关系网.html", "灌水高潮热力图.html",
          "语言指纹.html", "转折点分析.html", "叙事工程学.html", "拆解总报告.md"}
for fn in sorted(htmls):
    h = open(os.path.join(WEB, fn), encoding="utf-8").read()
    links = set(re.findall(r'href="([^"]+\.(?:html|md))"', h))
    miss = expect - links if fn != "可视化总览.html" else (expect - links - {"可视化总览.html"})
    chk(not miss, "%-20s links=%d %s" % (fn, len(links), ("缺:" + ",".join(miss)) if miss else ""))

# 3 JS 语法
p("\n[3] JS 语法")
import subprocess, tempfile
for fn in sorted(htmls):
    h = open(os.path.join(WEB, fn), encoding="utf-8").read()
    js = "\n".join(re.findall(r"<script>(.*?)</script>", h, re.S))
    t = os.path.join(tempfile.gettempdir(), "_c.js")
    open(t, "w", encoding="utf-8").write(js if js.strip() else "void 0")
    r = subprocess.run(["node", "--check", t], capture_output=True, text=True)
    chk(r.returncode == 0, "%-20s %s" % (fn, r.stderr.strip()[:60] if r.returncode else "OK"))

# 4 数据引用
p("\n[4] HTML 引用的数据文件")
refs = set()
for fn in htmls:
    h = open(os.path.join(WEB, fn), encoding="utf-8").read()
    refs |= set(re.findall(r'data/[A-Za-z0-9_\u4e00-\u9fa5]+\.(?:csv|json|txt)', h))
for r in sorted(refs):
    chk(os.path.exists(os.path.join(WEB, r)), r)

# 5 行数一致性
p("\n[5] 数据行数")
def rows(f):
    with open(os.path.join(D, f), encoding="utf-8-sig") as x:
        return sum(1 for _ in csv.DictReader(x))
C = [("chapters.csv",589),("chapter_signals.csv",589),("roles.csv",50),
     ("worldbuilding.csv",360),("volumes.csv",10),("灌水章检测.csv",28),
     ("高潮章.csv",40),("人物关系边表.csv",62),("标题语言学.csv",589),
     ("心声分类.csv",2129),("心声分卷演变.csv",10),("转折点.csv",10),
     ("章末钩子分类.csv",589),("角色音色.csv",10),("伏笔时间线.csv",15),
     ("场景迁移.csv",10),("套路用词.csv",67)]
for f, e in C:
    try: a = rows(f)
    except Exception as ex: chk(False, "%s err %s" % (f, ex)); continue
    chk(a == e, "%-24s rows=%d (expect %d)" % (f, a, e))

# 6 跨文件口径
p("\n[6] 跨文件口径")
q = json.load(open(os.path.join(D, "quotes.json"), encoding="utf-8"))
im = json.load(open(os.path.join(D, "inner_monologue.json"), encoding="utf-8"))
net = json.load(open(os.path.join(D, "network_clean.json"), encoding="utf-8"))
tp = json.load(open(os.path.join(D, "turning_points.json"), encoding="utf-8"))
nv = json.load(open(os.path.join(D, "narrative.json"), encoding="utf-8"))
chkv = [("心声", len(q["inner"]), im["total"]),
        ("系统", 42, len(q["system"])),
        ("金句", 4025, len(q["gold"])),
        ("钩子", 589, len(q["hooks"])),
        ("关系网节点", 15, len(net["nodes"])),
        ("关系网边", 62, len(net["edges"])),
        ("转折卷", 10, len(tp["VA"])),
        ("钩子分类总数", 589, nv["hook"]["total"]),
        ("伏笔条数", 15, len(nv["foreshadow"])),
        ("场景卷数", 10, len(nv["scene_vol"]))]
for n, e, a in chkv:
    chk(e == a, "%-14s %s" % (n, a))

# 7 台词库行数（142 条）
tl = rows("角色台词库.csv")
chk(tl == 142, "角色台词库 rows=%d (expect 142)" % tl)

# 8 清单
p("\n[7] 产出清单")
p("  HTML   : %d" % len(htmls))
p("  data   : %d" % len(os.listdir(D)))
p("  scripts: %d" % len([f for f in os.listdir(SCR) if f.endswith(".py")]))
p("  MD     : %d" % len([f for f in os.listdir(WEB) if f.endswith(".md")]))

# 9 报告章节完整性
p("\n[8] 报告章节")
rp = open(os.path.join(WEB, "拆解总报告.md"), encoding="utf-8").read()
for s in ["一、书籍元数据", "二、结构层", "三、人物层", "四、世界观层",
          "五、剧情层", "六、节拍层", "七、节奏层", "九之二、高潮章分类",
          "九之三、作者语言指纹", "九之四、转折点", "九之五、叙事工程学",
          "十、这套拆解还能怎么继续挖"]:
    chk(s in rp, s)

p("\n" + "=" * 62)
p("RESULT: " + ("ALL PASS" if ok else "HAS FAILURE"))
p("=" * 62)

out = os.path.join(SCR, "final_check2.txt")
open(out, "w", encoding="utf-8").write("\n".join(L))
print("written:", out)
