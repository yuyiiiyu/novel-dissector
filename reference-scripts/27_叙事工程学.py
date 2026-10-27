# -*- coding: utf-8 -*-
"""阶段14：叙事工程学 —— ①章末钩子 ②角色台词 ③伏笔时间线 ④场景迁移"""
import re, json, os, collections, csv, io, sys, statistics
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

SRC = r"D:\Download\这个人明明很强却偏要坑萝莉师傅 - 一条咸鱼c.txt"
OUT = r"D:\aigc_pro\ai-video&draw\DeepSeek Harness\@ D Download 这个人明明很强却_2026-10-27\产出\data"
raw = open(SRC, encoding="utf-8").read()
lines = raw.split("\n")

CH = re.compile(r"^\s*第([0-9]+)章[\s　]*(.*)$")
idx = []
for i, l in enumerate(lines):
    m = CH.match(l)
    if m: idx.append((int(m.group(1)), m.group(2).strip(), i))
idx.sort()
bodies, titles = {}, {}
for i, it in enumerate(idx):
    num, tt, ln = it
    end = idx[i+1][2] if i+1 < len(idx) else len(lines)
    bodies[num] = "\n".join(lines[ln:end])
    titles[num] = tt

vols = []
with open(os.path.join(OUT, "volumes.csv"), encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        lo, hi = r["范围"].split("-")
        vols.append({"name": r["卷"], "lo": int(lo), "hi": int(hi)})
def volof(n):
    return next((v["name"] for v in vols if v["lo"] <= n <= v["hi"]), "")

# ==================================================================
# ① 章末钩子形态学
# ==================================================================
q = json.load(open(os.path.join(OUT, "quotes.json"), encoding="utf-8"))
hooks = q["hooks"]

def htype(t):
    if t.endswith(("？", "?")): return "疑问式"
    if t.endswith(("！", "!")): return "感叹式"
    if t.endswith("…"): return "省略式"
    if t.startswith("【"): return "心声式"
    if t.startswith("“"): return "对话式"
    return "叙述式"

hc = collections.Counter()
h_vol = collections.defaultdict(collections.Counter)
h_len = collections.defaultdict(list)
for h in hooks:
    t = htype(h["hook"])
    hc[t] += 1
    h_vol[volof(h["ch"])][t] += 1
    h_len[t].append(len(h["hook"]))

hook_stat = {
    "total": len(hooks),
    "types": dict(hc.most_common()),
    "avg_len": {k: round(statistics.mean(v), 1) for k, v in h_len.items()},
    "by_vol": {v["name"]: dict(h_vol[v["name"]]) for v in vols},
}
# 每类样例
hook_samp = {}
for t in hc:
    s = [h for h in hooks if htype(h["hook"]) == t]
    s.sort(key=lambda h: -len(h["hook"]))
    hook_samp[t] = [{"ch": h["ch"], "t": h["hook"][:70]} for h in s[:6]]

# ==================================================================
# ② 角色台词库与音色
# ==================================================================
net = json.load(open(os.path.join(OUT, "network_clean.json"), encoding="utf-8"))
NAMES = [n["id"] for n in net["nodes"]]

ADV = ("皱眉|微笑|冷笑|苦笑|轻笑|平静|淡然|缓缓|震惊|疑惑|无奈|愤怒|严肃|小声|大声|"
       "轻声|低声|好奇|惊讶|温柔|淡淡|默默|静静|猛地|忽然|突然|立刻|顿时|赶紧|"
       "悄悄|下意识|忍不住|叹了口气")
VERB = "说|道|问|答|喊|叫|回|吼|叹|喃喃|开口|补充|解释|提醒|安慰|命令|追问|回应"

tlines = collections.defaultdict(list)
for nm in NAMES:
    pat = re.compile(re.escape(nm) + "(?:" + ADV + ")?(?:地)?(?:" + VERB +
                     ")[：:]\\s*[\u201c\"']([^\u201d\"']{4,90})")
    for num in sorted(bodies):
        for m in pat.finditer(bodies[num]):
            tlines[nm].append((num, m.group(1).strip()))

voice = []
for nm in NAMES:
    lst = tlines[nm]
    if not lst: continue
    L = [len(t) for _, t in lst]
    ex = sum(1 for _, t in lst if t.rstrip().endswith(("！", "!")))/len(lst)*100
    qu = sum(1 for _, t in lst if t.rstrip().endswith(("？", "?")))/len(lst)*100
    el = sum(1 for _, t in lst if "…" in t)/len(lst)*100
    voice.append({
        "name": nm, "n": len(lst),
        "avg": round(statistics.mean(L), 1),
        "max": max(L),
        "excl": round(ex, 1), "quest": round(qu, 1), "ellip": round(el, 1),
        "first_ch": min(c for c, _ in lst), "last_ch": max(c for c, _ in lst),
        "samples": [t for _, t in sorted(lst, key=lambda x: -len(x[1]))[:4]],
    })
voice.sort(key=lambda v: -v["n"])

# ==================================================================
# ③ 伏笔埋设 / 回收时间线
# ==================================================================
FS_TERMS = ["路西法", "堕落神", "沉眠者", "初诞者", "源妹", "秩序神", "盗日者",
            "禁忌龙", "母神", "剑傀", "魔君", "海王", "薇薇安", "马绍尔", "爱丽丝"]
fs = []
for w in FS_TERMS:
    hits = [num for num in sorted(bodies) if w in bodies[num]]
    if len(hits) < 5: continue
    bg, gp = 0, None
    for i in range(1, len(hits)):
        g = hits[i] - hits[i-1]
        if g > bg: bg, gp = g, (hits[i-1], hits[i])
    fs.append({
        "w": w, "first": hits[0], "last": hits[-1], "n": len(hits),
        "gap": bg, "gap_from": gp[0], "gap_to": gp[1],
        "hits": hits,
    })
fs.sort(key=lambda x: -x["gap"])

# ==================================================================
# ④ 场景迁移
# ==================================================================
SC = {
    "室内": ["房间", "大厅", "宫殿", "书房", "教堂", "屋内", "厅堂", "卧室", "厨房"],
    "室外": ["广场", "街道", "森林", "山脉", "野外", "城外", "海边", "荒野", "山谷"],
    "战场": ["战场", "前线", "阵地", "冲锋", "军营", "城墙"],
    "异空间": ["位面", "神界", "虚空", "梦境", "深渊", "神国", "结界"],
}
scene_vol = []
for v in vols:
    row = {"卷": v["name"], "lo": v["lo"], "hi": v["hi"]}
    tot = 0
    for s, kws in SC.items():
        n = sum(bodies[num].count(k) for num in range(v["lo"], v["hi"]+1)
                if num in bodies for k in kws)
        row[s] = n; tot += n
    row["合计"] = tot
    scene_vol.append(row)

# 逐章主导场景
dom_by_ch = {}
for num in sorted(bodies):
    b = bodies[num]
    sc = {s: sum(b.count(k) for k in kws) for s, kws in SC.items()}
    m = max(sc.values())
    dom_by_ch[num] = max(sc, key=sc.get) if m else "无"

json.dump({"hook": hook_stat, "hook_samp": hook_samp, "voice": voice,
           "foreshadow": fs, "scene_vol": scene_vol,
           "dom_by_ch": {str(k): v for k, v in dom_by_ch.items()}},
          open(os.path.join(OUT, "narrative.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

# CSV
with open(os.path.join(OUT, "章末钩子分类.csv"), "w", encoding="utf-8-sig", newline="") as f:
    f.write("章号,标题,形态,长度,钩子内容\n")
    for h in hooks:
        f.write('{},{},{},{},"{}"\n'.format(h["ch"], titles.get(h["ch"], ""),
                htype(h["hook"]), len(h["hook"]), h["hook"].replace('"', '""')))

with open(os.path.join(OUT, "角色台词库.csv"), "w", encoding="utf-8-sig", newline="") as f:
    f.write("角色,章号,台词\n")
    for nm in NAMES:
        for c, t in tlines[nm]:
            f.write('{},{},"{}"\n'.format(nm, c, t.replace('"', '""')))

with open(os.path.join(OUT, "角色音色.csv"), "w", encoding="utf-8-sig", newline="") as f:
    f.write("角色,台词数,均长,最长,叹号%,问号%,省略号%,首现,末现\n")
    for v in voice:
        f.write("{},{},{},{},{},{},{},{},{}\n".format(
            v["name"], v["n"], v["avg"], v["max"], v["excl"], v["quest"],
            v["ellip"], v["first_ch"], v["last_ch"]))

with open(os.path.join(OUT, "伏笔时间线.csv"), "w", encoding="utf-8-sig", newline="") as f:
    f.write("词条,首现章,末现章,出现章数,最大空档,空档起点,空档终点\n")
    for x in fs:
        f.write("{},{},{},{},{},{},{}\n".format(
            x["w"], x["first"], x["last"], x["n"], x["gap"], x["gap_from"], x["gap_to"]))

with open(os.path.join(OUT, "场景迁移.csv"), "w", encoding="utf-8-sig", newline="") as f:
    f.write("卷,范围,室内,室外,战场,异空间,合计\n")
    for r in scene_vol:
        f.write("{},{}-{},{},{},{},{},{}\n".format(
            r["卷"], r["lo"], r["hi"], r["室内"], r["室外"], r["战场"],
            r["异空间"], r["合计"]))

print("=== ① 章末钩子形态 ===")
print("  总数:", hook_stat["total"])
for t, n in hook_stat["types"].items():
    print("  %-6s %3d (%.1f%%)  均长 %.1f 字" % (t, n, n/hook_stat["total"]*100,
          hook_stat["avg_len"][t]))
print("\n=== ② 角色音色 ===")
for v in voice:
    print("  %-7s %3d条 均%5.1f 叹%5.1f%% 问%5.1f%% 省%5.1f%%  第%d-%d章"
          % (v["name"], v["n"], v["avg"], v["excl"], v["quest"], v["ellip"],
             v["first_ch"], v["last_ch"]))
print("\n=== ③ 伏笔空档 Top ===")
for x in fs[:8]:
    print("  %-7s 首%-4d 末%-4d 共%-4d章 最大空档%3d章 (第%d→%d)"
          % (x["w"], x["first"], x["last"], x["n"], x["gap"], x["gap_from"], x["gap_to"]))
print("\n=== ④ 场景迁移 ===")
for r in scene_vol:
    print("  %-20s 室内%4d 室外%4d 战场%4d 异空间%5d"
          % (r["卷"][:18], r["室内"], r["室外"], r["战场"], r["异空间"]))
print("\nfiles written to:", OUT)
