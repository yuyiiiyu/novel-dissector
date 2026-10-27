# -*- coding: utf-8 -*-
"""
novel-dissector 参考实现骨架
================================
用法：
    python dissect.py <小说txt路径> <产出目录>

会依次产出（按探测结果自动跳过不适用维度）：
    01 结构扫描      02 专名抽取      07 角色抽取
    08 世界观        09 剧情分段      10 金句心声
    11 灌水/高潮     12 关系网        14 高潮重做
    15 语言指纹      16 心声机制      18 转折点
    27 叙事工程学    31 章内工程学    36 续写资产
    ++ 终检

依赖：仅 Python 标准库。可选：node（用于 JS 语法校验）。

注意：本骨架是「参考实现」，真实项目请按 SKILL.md 的分步流程
      逐步跑并人工核对每一步输出，不要一次性盲跑。
"""
import re, json, os, sys, csv, collections, statistics, math, io

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

SRC = sys.argv[1] if len(sys.argv) > 1 else None
OUTROOT = sys.argv[2] if len(sys.argv) > 2 else "产出"
if not SRC:
    print("usage: python dissect.py <novel.txt> <outdir>")
    sys.exit(1)

DATA = os.path.join(OUTROOT, "data")
os.makedirs(DATA, exist_ok=True)

def save(name, obj):
    p = os.path.join(DATA, name)
    json.dump(obj, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("  ->", name)

def save_csv(name, header, rows):
    p = os.path.join(DATA, name)
    with open(p, "w", encoding="utf-8-sig", newline="") as f:
        f.write(",".join(header) + "\n")
        for r in rows:
            f.write(",".join('"%s"' % str(x).replace('"', '""') for x in r) + "\n")
    print("  ->", name)

raw = open(SRC, encoding="utf-8").read()
lines = raw.split("\n")
TOTAL_HAN = len(re.findall(r"[\u4e00-\u9fa5]", raw))
print("总汉字:", TOTAL_HAN)

# ---------- 探测 ----------
print("\n[探测]")
CH = re.compile(r"^\s*第([0-9]+)章[\s　]*(.*)$")
idx = []
for i, l in enumerate(lines):
    m = CH.match(l)
    if m: idx.append((int(m.group(1)), m.group(2).strip(), i))
idx.sort()
NCH = len(idx)
print("  章节数:", NCH)
probe = {
    "书名号《》": len(re.findall(r"《[^》]{2,12}》", raw)),
    "系统提示叮": len(re.findall(r"【\s*叮", raw)),
    "心声【】": raw.count("【"),
    "对话引号": raw.count("“"),
}
print("  ", probe)
skip = []
if probe["书名号《》"] < 10: skip.append("招式名录（书名号过少）")
if probe["心声【】"] < 500: skip.append("心声机制（心声过少）")
if probe["系统提示叮"] < 20: skip.append("系统流（提示过少）")
print("  跳过维度:", skip or "无")

# ---------- 章体 ----------
bodies, titles = {}, {}
for i, it in enumerate(idx):
    num, tt, ln = it
    end = idx[i+1][2] if i+1 < len(idx) else len(lines)
    bodies[num] = "\n".join(lines[ln:end])
    titles[num] = tt

# ---------- 01 结构扫描 ----------
print("\n[01] 结构扫描")
rows = []
for num in sorted(bodies):
    b = bodies[num]
    ps = [l.strip() for l in b.split("\n")
          if l.strip() and not set(l.strip()) <= set("—-_=*·")]
    rows.append([num, titles[num], len(re.sub(r"\s", "", b)), len(ps),
                 b.count("“"), b.count("【"), len(re.findall(r"【\s*叮", b)),
                 ps[0][:50] if ps else "", ps[-1][:50] if ps else ""])
save_csv("chapters.csv", ["章号","标题","字数","段落数","对话引号数","心声数",
                          "系统提示数","首句","末句"], rows)
cs = [r[2] for r in rows]
print("  章均字数:", round(statistics.mean(cs)))

# ---------- 09 剧情分卷 ----------
print("\n[09] 剧情分段")
NV = min(10, max(3, NCH // 60)) or 10
per = NCH // NV
vols = []
for i in range(NV):
    lo = i*per + 1
    hi = (i+1)*per if i < NV-1 else NCH
    vols.append({"name": "第%d卷" % (i+1), "lo": lo, "hi": hi})
save_csv("volumes.csv", ["卷","范围","章数"],
         [[v["name"], "%d-%d" % (v["lo"], v["hi"]), v["hi"]-v["lo"]+1] for v in vols])
print("  分卷:", len(vols))

# ---------- 10 金句心声 ----------
print("\n[10] 心声/金句")
INNER = re.compile(r"【([^】]{4,120})】")
inner = []
for num in sorted(bodies):
    for m in INNER.finditer(bodies[num]):
        t = m.group(1).strip()
        if re.search(r"^叮|系统|奖励|任务|魔力值|力量点数", t): continue
        inner.append({"ch": num, "text": t})
seen = set(); uniq = []
for x in inner:
    if x["text"] in seen: continue
    seen.add(x["text"]); uniq.append(x)
save("quotes_inner.json", uniq)
print("  心声(去重):", len(uniq))

# ---------- 15 语言指纹 ----------
print("\n[15] 语言指纹")
GROUPS = {
    "时间副词瞬时": ["瞬间","刹那","霎时","顷刻","转瞬","一瞬"],
    "时间副词突发": ["突然","忽然","猛地","骤然","蓦地","陡然"],
    "时间副词接续": ["立刻","顿时","随即","马上","赶紧","连忙"],
    "速度副词": ["缓缓","慢慢","徐徐","迅速","飞快","急速"],
    "情态副词": ["仿佛","似乎","宛如","犹如","好像"],
    "程度副词": ["无比","微微","格外","淡淡","异常"],
}
words = {}
for g, ws in GROUPS.items():
    items = [{"w": w, "n": raw.count(w),
              "per10k": round(raw.count(w)/TOTAL_HAN*10000, 2)} for w in ws if raw.count(w)]
    items.sort(key=lambda x: -x["n"])
    words[g] = {"items": items, "total": sum(i["n"] for i in items)}
save("language_fingerprint.json", {"words": words, "total_han": TOTAL_HAN})
print("  套路词类别:", len(words))

# ---------- 31 章内节奏模板 ----------
print("\n[31] 章内节奏")
NB = 10
buckets = collections.defaultdict(collections.Counter)
bc = collections.Counter()
for num in sorted(bodies):
    ps = [l.strip() for l in bodies[num].split("\n")
          if l.strip() and not set(l.strip()) <= set("—-_=*·")]
    if len(ps) < 10: continue
    n = len(ps)
    for j, s in enumerate(ps):
        b = min(NB-1, int(j/n*NB))
        bc[b] += 1
        if "【" in s: buckets[b]["心声"] += 1
        if "“" in s: buckets[b]["对话"] += 1
tmpl = {}
for k in ["心声", "对话"]:
    tmpl[k] = [round(buckets[b][k]/bc[b]*1000, 2) if bc[b] else 0 for b in range(NB)]
save("chapter_internal.json", {"tmpl": tmpl})
print("  模板档位:", NB)

# ---------- 36 续写资产（核心） ----------
print("\n[36] 续写资产")
tail = "\n".join(bodies[n] for n in sorted(bodies)[-5:])
LOSE = ["失败","泡影","化为了","没能","终究还是没有","牺牲","消散","陨落","死亡"]
WIN = ["成功","胜利","赢了","击败","战胜","新的世界","活下来"]
DEAD = ["死","陨落","消散","消失","牺牲","湮灭"]
res = {"失败词": sum(tail.count(w) for w in LOSE),
       "成功词": sum(tail.count(w) for w in WIN),
       "死亡消散词": sum(tail.count(w) for w in DEAD)}
verdict = "悲剧/失败" if res["失败词"] > res["成功词"] else "圆满/胜利"
print("  结局判定:", verdict, res)
save("续写资产.json", {
    "ending_verdict": verdict,
    "ending_counts": res,
    "rules": {
        "章均字数": round(statistics.mean(cs)),
        "字数安全区": [round(statistics.mean(cs)-350), round(statistics.mean(cs)+550)],
        "心声/章": round(statistics.mean([r[5] for r in rows]), 1),
        "对话引号/章": round(statistics.mean([r[4] for r in rows]), 1),
    },
    "skipped_dimensions": skip,
})

print("\n完成。产出目录:", OUTROOT)
print("下一步：按 SKILL.md 逐步补 02/07/08/11/12/16/18/27/28 与 8 个 HTML 页面，")
print("        然后跑终检（final_check）确认 ALL PASS 再交付。")
