# -*- coding: utf-8 -*-
"""阶段7c：高潮章重做 —— 分三类（战斗/感情/喜剧）独立识别 + 综合高潮章"""
import csv, json, os, statistics, collections

OUT = r"D:\aigc_pro\ai-video&draw\DeepSeek Harness\@ D Download 这个人明明很强却_2026-10-27\产出\data"

rows = []
with open(os.path.join(OUT, "chapters.csv"), encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        rows.append({"num": int(r["章号"]), "title": r["标题"], "chars": int(r["字数"]),
                     "inner": int(r["心声数"]), "sys": int(r["系统提示数"]),
                     "d_ratio": float(r["对话密度‰"])})
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
        vols.append({"name": r["卷"], "lo": int(lo), "hi": int(hi)})
def volof(n):
    return next((v["name"] for v in vols if v["lo"] <= n <= v["hi"]), "")

mb = max(r["战斗"] for r in rows) or 1
ms = max(r["甜度"] for r in rows) or 1
mi = max(r["inner"] for r in rows) or 1

# ===== 三类高分章 =====
def rank(key, topn=30, minv=1):
    sel = [r for r in rows if r[key] >= minv]
    sel.sort(key=lambda r: -r[key])
    return sel[:topn]

battle = rank("战斗", 30, 5)
sweet = rank("甜度", 30, 4)
comedy = rank("inner", 30, 8)

# ===== 综合高潮章：三维加权（战斗/甜度/心声各自归一化）=====
for r in rows:
    r["score"] = round(r["战斗"] / mb * 45 + r["甜度"] / ms * 30 + r["inner"] / mi * 25, 2)
combo = sorted(rows, key=lambda r: -r["score"])[:40]

# ===== 卷内高潮章（每卷 Top3）=====
per_vol = {}
for v in vols:
    sub = [r for r in rows if v["lo"] <= r["num"] <= v["hi"]]
    sub.sort(key=lambda r: -r["score"])
    per_vol[v["name"]] = sub[:3]

def wr(name, lst, cols):
    with open(os.path.join(OUT, name), "w", encoding="utf-8-sig", newline="") as f:
        f.write(",".join(cols) + "\n")
        for r in lst:
            f.write(f'{r["num"]},{r["title"]},{r.get("vol","")},'
                    + ",".join(str(r.get(c, "")) for c in cols[3:]) + "\n")

for r in battle + sweet + comedy + combo:
    r["vol"] = volof(r["num"])

wr("高潮章.csv", combo,
   ["章号", "标题", "所属卷", "综合分", "战斗", "甜度", "心声", "字数", "对话密度‰"])
wr("高潮章_战斗.csv", battle, ["章号", "标题", "所属卷", "战斗", "字数", "对话密度‰"])
wr("高潮章_感情.csv", sweet, ["章号", "标题", "所属卷", "甜度", "字数", "对话密度‰"])
wr("高潮章_喜剧.csv", comedy, ["章号", "标题", "所属卷", "心声", "字数", "对话密度‰"])

json.dump({"combo": combo, "battle": battle, "sweet": sweet,
           "comedy": comedy, "per_vol": per_vol},
          open(os.path.join(OUT, "peaks.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

print("=== 综合高潮章 Top15 ===")
for r in combo[:15]:
    print(f' 第{r["num"]:3d}章 [{r["vol"][:5]}] 分{r["score"]:5.1f} '
          f'战{r["战斗"]:2d} 甜{r["甜度"]:2d} 心{r["inner"]:2d} | {r["title"][:24]}')
print("\n=== 战斗 peak Top8 ===")
for r in battle[:8]:
    print(f' 第{r["num"]:3d}章 战{r["战斗"]:2d} | {r["title"][:26]}')
print("\n=== 感情 peak Top8 ===")
for r in sweet[:8]:
    print(f' 第{r["num"]:3d}章 甜{r["甜度"]:2d} | {r["title"][:26]}')
print("\n=== 喜剧 peak Top8 ===")
for r in comedy[:8]:
    print(f' 第{r["num"]:3d}章 心声{r["inner"]:2d} | {r["title"][:26]}')
print("\n=== 每卷 Top3 高潮章 ===")
for v, lst in per_vol.items():
    print(f'  {v[:22]:24s} ' + " / ".join(f'{r["num"]}({r["score"]})' for r in lst))
