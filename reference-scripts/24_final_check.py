# -*- coding: utf-8 -*-
"""终检：渲染健康 + 导航 + 数据引用 + 一致性，输出 final_check.txt"""
import os, re, json, csv, io, sys

WEB = r"D:\aigc_pro\ai-video&draw\DeepSeek Harness\@ D Download 这个人明明很强却_2026-10-27\产出"
D = os.path.join(WEB, "data")
SCRIPTS = os.path.join(WEB, "scripts")
L = []
def p(s): L.append(str(s))
ok = True

p("=" * 60)
p("终检报告")
p("=" * 60)

# 1 渲染健康
p("\n[1] HTML 渲染健康")
for fn in sorted(os.listdir(WEB)):
    if not fn.endswith(".html"): continue
    h = open(os.path.join(WEB, fn), encoding="utf-8").read()
    bad = []
    if "NaN" in h: bad.append("NaN")
    if "undefined" in h: bad.append("undefined")
    # 总览页是卡片索引页，本就不含图表 SVG
    if h.count("<svg") == 0 and fn != "可视化总览.html": bad.append("no-svg")
    if bad:
        ok = False; p("  FAIL %s -> %s" % (fn, ",".join(bad)))
    else:
        p("  OK   %s  (%.1f KB, svg=%d)" % (fn, len(h)/1024.0, h.count("<svg")))

# 2 导航
p("\n[2] 导航链接")
for fn in sorted(os.listdir(WEB)):
    if not fn.endswith(".html"): continue
    h = open(os.path.join(WEB, fn), encoding="utf-8").read()
    links = set(re.findall(r'href="([^"]+\.(?:html|md))"', h))
    miss = [x for x in links if not os.path.exists(os.path.join(WEB, x))]
    if miss:
        ok = False; p("  FAIL %s missing=%s" % (fn, miss))
    else:
        p("  OK   %s  links=%d" % (fn, len(links)))

# 3 数据引用
p("\n[3] HTML 引用数据文件")
refs = set()
for fn in os.listdir(WEB):
    if fn.endswith(".html"):
        h = open(os.path.join(WEB, fn), encoding="utf-8").read()
        refs |= set(re.findall(r'data/[A-Za-z0-9_\u4e00-\u9fa5]+\.(?:csv|json|txt)', h))
for r in sorted(refs):
    if os.path.exists(os.path.join(WEB, r)):
        p("  OK   %s" % r)
    else:
        ok = False; p("  FAIL missing %s" % r)

# 4 一致性
p("\n[4] 数据一致性")
def rows(f):
    with open(os.path.join(D, f), encoding="utf-8-sig") as x:
        return sum(1 for _ in csv.DictReader(x))
CHECKS = [("chapters.csv",589),("chapter_signals.csv",589),("roles.csv",50),
          ("worldbuilding.csv",360),("volumes.csv",10),("灌水章检测.csv",28),
          ("高潮章.csv",40),("人物关系边表.csv",62),("标题语言学.csv",589),
          ("心声分类.csv",2129),("心声分卷演变.csv",10),("转折点.csv",10)]
for f, exp in CHECKS:
    try:
        a = rows(f)
    except Exception as e:
        ok = False; p("  FAIL %s err=%s" % (f, e)); continue
    if a == exp: p("  OK   %s rows=%d" % (f, a))
    else:
        ok = False; p("  FAIL %s expect=%d actual=%d" % (f, exp, a))

q = json.load(open(os.path.join(D, "quotes.json"), encoding="utf-8"))
im = json.load(open(os.path.join(D, "inner_monologue.json"), encoding="utf-8"))
net = json.load(open(os.path.join(D, "network_clean.json"), encoding="utf-8"))
tp = json.load(open(os.path.join(D, "turning_points.json"), encoding="utf-8"))
for name, exp, act in [("心声总数", len(q["inner"]), im["total"]),
                       ("系统提示", 42, len(q["system"])),
                       ("金句", 4025, len(q["gold"])),
                       ("钩子", 589, len(q["hooks"])),
                       ("关系网节点", 15, len(net["nodes"])),
                       ("关系网边", 62, len(net["edges"])),
                       ("转折卷数", 10, len(tp["VA"]))]:
    if exp == act: p("  OK   %s = %s" % (name, act))
    else:
        ok = False; p("  FAIL %s %s vs %s" % (name, exp, act))

# 5 清单
p("\n[5] 产出清单")
p("  HTML  : %d" % len([f for f in os.listdir(WEB) if f.endswith('.html')]))
p("  data  : %d" % len(os.listdir(D)))
p("  script: %d" % len([f for f in os.listdir(SCRIPTS) if f.endswith('.py')]))

p("\n" + "=" * 60)
p("RESULT: " + ("ALL PASS" if ok else "HAS FAILURE"))
p("=" * 60)

out = os.path.join(SCRIPTS, "final_check.txt")
open(out, "w", encoding="utf-8").write("\n".join(L))
print("written:", out)
