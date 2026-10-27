# -*- coding: utf-8 -*-
"""阶段16：章内工程学 —— 章内节奏模板 / 爽文桥段 / 对话轮次结构"""
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

# 收集每章的段落序列（去标题/分隔线）
ch_paras = {}
for i, it in enumerate(idx):
    num, tt, ln = it
    end = idx[i+1][2] if i+1 < len(idx) else len(lines)
    ps = []
    for l in lines[ln+1:end]:
        s = l.strip()
        if not s: continue
        if set(s) <= set("—-_=*·"): continue
        ps.append(s)
    ch_paras[num] = ps

vols = []
with open(os.path.join(OUT, "volumes.csv"), encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        lo, hi = r["范围"].split("-")
        vols.append({"name": r["卷"], "lo": int(lo), "hi": int(hi)})
def volof(n):
    return next((v["name"] for v in vols if v["lo"] <= n <= v["hi"]), "")

# ==================================================================
# A. 章内节奏模板：按段落位置分 10 档
# ==================================================================
NB = 10
buckets = collections.defaultdict(lambda: collections.Counter())
bcount = collections.Counter()
for num, ps in ch_paras.items():
    if len(ps) < 10: continue
    n = len(ps)
    for j, s in enumerate(ps):
        b = min(NB - 1, int(j / n * NB))
        bcount[b] += 1
        if "【" in s: buckets[b]["心声"] += 1
        if "“" in s: buckets[b]["对话"] += 1
        if re.search(r"攻击|爆炸|斩|轰|击杀|碾压|灭|冲", s): buckets[b]["战斗"] += 1
        if re.search(r"脸红|害羞|喜欢|抱|亲|媳妇|老婆|嫁", s): buckets[b]["甜度"] += 1
        if s.endswith(("！", "!")): buckets[b]["感叹"] += 1
        if s.endswith(("？", "?")): buckets[b]["疑问"] += 1

# 归一化：每档每千段落的命中率
tmpl = {}
for k in ["心声", "对话", "战斗", "甜度", "感叹", "疑问"]:
    vs = [buckets[b][k] / bcount[b] * 1000 if bcount[b] else 0 for b in range(NB)]
    tmpl[k] = [round(v, 2) for v in vs]

# ==================================================================
# B. 爽文桥段检测（震惊 - 打脸 - 反转）
# ==================================================================
SHOCK = ["不可能", "怎么可能", "难以置信", "震惊", "呆滞", "瞪大眼睛", "倒吸一口凉气",
         "浑身一震", "瞳孔一缩", "傻了", "愣住", "麻木", "窒息"]
FACE = ["打脸", "跪下", "求饶", "认输", "服了", "错了", "道歉", "磕头", "狼狈",
        "灰溜溜", "落荒而逃", "闭嘴", "哑口无言"]
REV = ["然而", "但是", "没想到", "谁料", "谁知", "却", "反而", "竟然", "居然", "原来"]

bridge = collections.Counter()
bridge_vol = collections.defaultdict(collections.Counter)
bridge_ch = []
for num, ps in ch_paras.items():
    txt = "\n".join(ps)
    s = sum(txt.count(w) for w in SHOCK)
    f = sum(txt.count(w) for w in FACE)
    r = sum(txt.count(w) for w in REV)
    bridge["震惊"] += s; bridge["打脸"] += f; bridge["反转"] += r
    bridge_vol[volof(num)]["震惊"] += s
    bridge_vol[volof(num)]["打脸"] += f
    bridge_vol[volof(num)]["反转"] += r
    bridge_ch.append((num, s, f, r))
# 三件套最齐全的章
bridge_ch.sort(key=lambda x: -(min(x[1], x[2], x[3]) * 3 + x[1] + x[2] + x[3]))
top_bridge = bridge_ch[:20]

bridge_vol_out = []
for v in vols:
    n = v["hi"] - v["lo"] + 1
    bv = bridge_vol[v["name"]]
    bridge_vol_out.append({"卷": v["name"], "震惊": bv["震惊"], "打脸": bv["打脸"],
                           "反转": bv["反转"],
                           "震惊/章": round(bv["震惊"]/n, 2),
                           "打脸/章": round(bv["打脸"]/n, 2),
                           "反转/章": round(bv["反转"]/n, 2)})

# ==================================================================
# C. 对话轮次结构
# ==================================================================
DLG = re.compile(r"[“\"']([^\"“”']{2,80})[\"”']")
turn_ch = []
for num, ps in ch_paras.items():
    txt = "\n".join(ps)
    turns = len(DLG.findall(txt))
    # 首个说话人
    m = DLG.search(txt)
    first = ""
    if m:
        seg = txt[:m.start()]
        mm = re.findall(r"([\u4e00-\u9fa5]{2,4})(?:皱眉|微笑|冷笑|平静|淡淡|缓缓|大声|小声|轻声)?(?:地)?(?:说|道|问|答|喊|叫|回|叹|喃喃|开口)", seg)
        if mm: first = mm[-1]
    turn_ch.append({"ch": num, "turns": turns, "first": first})

tvals = [t["turns"] for t in turn_ch]
turn_stat = {
    "total": sum(tvals),
    "avg": round(statistics.mean(tvals), 1),
    "median": statistics.median(tvals),
    "max": max(tvals),
    "min": min(tvals),
    "zero": sum(1 for v in tvals if v == 0),
}
# 首个说话人分布
fs_cnt = collections.Counter(t["first"] for t in turn_ch if t["first"])
# 对话最多的章
turn_top = sorted(turn_ch, key=lambda x: -x["turns"])[:15]

json.dump({"tmpl": tmpl, "bcount": dict(bcount),
           "bridge": dict(bridge), "bridge_vol": bridge_vol_out,
           "top_bridge": top_bridge,
           "turn_stat": turn_stat, "first_speaker": dict(fs_cnt.most_common(20)),
           "turn_top": turn_top},
          open(os.path.join(OUT, "chapter_internal.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

with open(os.path.join(OUT, "章内节奏模板.csv"), "w", encoding="utf-8-sig", newline="") as f:
    f.write("位置档," + ",".join(tmpl.keys()) + "\n")
    for b in range(NB):
        f.write("%d-%d%%," % (b*10, (b+1)*10) +
                ",".join(str(tmpl[k][b]) for k in tmpl) + "\n")

with open(os.path.join(OUT, "爽文桥段.csv"), "w", encoding="utf-8-sig", newline="") as f:
    f.write("卷,震惊,打脸,反转,震惊/章,打脸/章,反转/章\n")
    for r in bridge_vol_out:
        f.write("%s,%d,%d,%d,%s,%s,%s\n" % (r["卷"], r["震惊"], r["打脸"], r["反转"],
                r["震惊/章"], r["打脸/章"], r["反转/章"]))

with open(os.path.join(OUT, "对话轮次.csv"), "w", encoding="utf-8-sig", newline="") as f:
    f.write("章号,对话回合数,首个说话人\n")
    for t in turn_ch:
        f.write("%d,%d,%s\n" % (t["ch"], t["turns"], t["first"]))

print("=== A 章内节奏模板（每千段落命中率，按位置 0→100%）===")
hdr = "位置   " + "".join("%-8s" % k for k in tmpl)
print("  " + hdr)
for b in range(NB):
    print("  %3d%%  " % (b*10) + "".join("%-8.1f" % tmpl[k][b] for k in tmpl))

print("\n=== B 爽文桥段（全书命中）===")
print("  ", dict(bridge))
print("  按卷（每章均值）:")
for r in bridge_vol_out:
    print("    %-20s 震惊%5.2f 打脸%5.2f 反转%5.2f"
          % (r["卷"][:18], r["震惊/章"], r["打脸/章"], r["反转/章"]))
print("\n  三件套最齐全的章 Top8:")
for num, s, f2, r in top_bridge[:8]:
    print("    第%-4d章 震惊%-3d 打脸%-3d 反转%-3d | %s"
          % (num, s, f2, r, idx[num-1][1][:24] if num <= len(idx) else ""))

print("\n=== C 对话轮次 ===")
print("  总回合 %d  章均 %.1f  中位 %.0f  最多 %d  最少 %d  零对话章 %d"
      % (turn_stat["total"], turn_stat["avg"], turn_stat["median"],
         turn_stat["max"], turn_stat["min"], turn_stat["zero"]))
print("  首个说话人 Top10:", dict(fs_cnt.most_common(10)))
print("  对话最密章 Top8:")
for t in turn_top[:8]:
    print("    第%-4d章 %3d 回合" % (t["ch"], t["turns"]))
