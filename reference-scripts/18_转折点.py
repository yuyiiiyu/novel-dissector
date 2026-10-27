# -*- coding: utf-8 -*-
"""阶段12：四曲线叠合 + 转折点检测 —— 心声/灌水/战斗/甜度的因果关系统一视图"""
import json, csv, os, collections, statistics, re

OUT = r"D:\aigc_pro\ai-video&draw\DeepSeek Harness\@ D Download 这个人明明很强却_2026-10-27\产出\data"
SRC = r"D:\Download\这个人明明很强却偏要坑萝莉师傅 - 一条咸鱼c.txt"
raw = open(SRC, encoding="utf-8").read()
lines = raw.split("\n")

# ================= 章节数据 =================
rows = {}
with open(os.path.join(OUT, "chapters.csv"), encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        rows[int(r["章号"])] = {"title": r["标题"], "chars": int(r["字数"]),
                                "inner": int(r["心声数"]), "d_ratio": float(r["对话密度‰"])}
with open(os.path.join(OUT, "chapter_signals.csv"), encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        n = int(r["章"])
        if n in rows:
            rows[n]["战斗"] = int(r["战斗"]); rows[n]["甜度"] = int(r["甜度"])

vols = []
with open(os.path.join(OUT, "volumes.csv"), encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        lo, hi = r["范围"].split("-")
        vols.append({"name": r["卷"], "lo": int(lo), "hi": int(hi)})

water = set()
with open(os.path.join(OUT, "灌水章检测.csv"), encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        water.add(int(r["章号"]))

# ================= 按卷聚合 =================
VA = []
for v in vols:
    chs = [n for n in rows if v["lo"] <= n <= v["hi"]]
    nch = len(chs)
    w = sum(1 for n in chs if n in water)
    VA.append({
        "卷": v["name"], "lo": v["lo"], "hi": v["hi"], "nch": nch,
        "心声": sum(rows[n]["inner"] for n in chs),
        "战斗": sum(rows[n]["战斗"] for n in chs),
        "甜度": sum(rows[n]["甜度"] for n in chs),
        "灌水率": round(w / nch * 100, 2),
        "灌水章": w,
    })
for a in VA:
    a["心声/章"] = round(a["心声"] / a["nch"], 2)
    a["战斗/章"] = round(a["战斗"] / a["nch"], 2)
    a["甜度/章"] = round(a["甜度"] / a["nch"], 2)

# ================= 归一化（各按自身最大）=================
KEYS = ["心声/章", "灌水率", "战斗/章", "甜度/章"]
META = {
    "心声/章": {"name": "心声密度", "color": "#f59e0b", "unit": "条/章", "inv": False,
                "desc": "喜剧机制强度"},
    "灌水率": {"name": "灌水率", "color": "#64748b", "unit": "%", "inv": True,
               "desc": "节奏塌陷程度（逆向指标）"},
    "战斗/章": {"name": "战斗强度", "color": "#ef4444", "unit": "次/章", "inv": False,
                "desc": "动作戏密度"},
    "甜度/章": {"name": "感情甜度", "color": "#ec4899", "unit": "次/章", "inv": False,
                "desc": "感情戏密度"},
}
for k in KEYS:
    mx = max(a[k] for a in VA) or 1
    for a in VA:
        a[k + "_n"] = round(a[k] / mx, 4)

# ================= 转折点检测：逐卷变化率 =================
turns = []
for i in range(1, len(VA)):
    p, c = VA[i - 1], VA[i]
    deltas = {}
    for k in KEYS:
        nv, pv = c[k], p[k]
        d = (nv - pv) / pv * 100 if pv else (100 if nv else 0)
        deltas[k] = round(d, 1)
    # 转折强度 = 四条曲线归一化后变化的平均绝对值
    mag = sum(abs(c[k + "_n"] - p[k + "_n"]) for k in KEYS) / len(KEYS)
    turns.append({
        "at_vol": i + 1, "from": p["卷"], "to": c["卷"],
        "at_ch": c["lo"],
        "deltas": deltas,
        "mag": round(mag, 4),
    })
turns.sort(key=lambda t: -t["mag"])

# ================= 关键判定：喜剧-灌水负相关 =================
xs = [a["心声/章"] for a in VA]
ys = [a["灌水率"] for a in VA]
def pearson(a, b):
    n = len(a); ma, mb = statistics.mean(a), statistics.mean(b)
    num = sum((a[i] - ma) * (b[i] - mb) for i in range(n))
    da = sum((v - ma) ** 2 for v in a) ** 0.5
    db = sum((v - mb) ** 2 for v in b) ** 0.5
    return num / (da * db) if da and db else 0

corr = {
    "心声 vs 灌水率": round(pearson(xs, ys), 3),
    "心声 vs 战斗": round(pearson(xs, [a["战斗/章"] for a in VA]), 3),
    "心声 vs 甜度": round(pearson(xs, [a["甜度/章"] for a in VA]), 3),
    "战斗 vs 甜度": round(pearson([a["战斗/章"] for a in VA], [a["甜度/章"] for a in VA]), 3),
    "灌水率 vs 甜度": round(pearson(ys, [a["甜度/章"] for a in VA]), 3),
}

# ================= 逐章（平滑后）用于细粒度曲线 =================
N = len(rows)
ch_seq = {k: [rows[n].get(k, 0) for n in sorted(rows)] for k in ["inner", "战斗", "甜度"]}
def smooth(v, w=9):
    return [sum(v[max(0, i - w // 2):min(len(v), i + w // 2 + 1)]) /
            len(v[max(0, i - w // 2):min(len(v), i + w // 2 + 1)]) for i in range(len(v))]
ch_smooth = {k: smooth(v) for k, v in ch_seq.items()}
# 灌水逐章（滑动窗口 20 章内的灌水章比例）
sortedn = sorted(rows)
water_seq = []
for i, n in enumerate(sortedn):
    lo, hi = max(0, i - 10), min(len(sortedn), i + 11)
    win = sortedn[lo:hi]
    water_seq.append(sum(1 for x in win if x in water) / len(win) * 100)

json.dump({"VA": VA, "turns": turns, "corr": corr, "KEYS": KEYS, "META": META,
           "ch_smooth": {k: [round(x, 3) for x in v] for k, v in ch_smooth.items()},
           "water_seq": [round(x, 2) for x in water_seq],
           "ch_nums": sortedn},
          open(os.path.join(OUT, "turning_points.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

with open(os.path.join(OUT, "转折点.csv"), "w", encoding="utf-8-sig", newline="") as f:
    f.write("卷,范围,心声/章,灌水率%,战斗/章,甜度/章,心声变化%,灌水变化%,战斗变化%,甜度变化%\n")
    for i, a in enumerate(VA):
        d = turns[i - 1]["deltas"] if i > 0 else {k: 0 for k in KEYS}
        f.write('{},{}-{},{},{},{},{},{},{},{},{}\n'.format(
            a["卷"], a["lo"], a["hi"], a["心声/章"], a["灌水率"],
            a["战斗/章"], a["甜度/章"],
            d["心声/章"], d["灌水率"], d["战斗/章"], d["甜度/章"]))

print("=== 按卷四曲线 ===")
print(f'{"卷":26s} {"心声/章":>7s} {"灌水%":>6s} {"战斗/章":>7s} {"甜度/章":>7s}')
for a in VA:
    print(f'{a["卷"][:24]:26s} {a["心声/章"]:7.2f} {a["灌水率"]:6.1f} '
          f'{a["战斗/章"]:7.2f} {a["甜度/章"]:7.2f}')

print("\n=== 转折点强度排名 ===")
for t in turns[:5]:
    print(f'  第{t["at_vol"]}卷起点（第{t["at_ch"]}章） 强度{t["mag"]:.3f}')
    print(f'    ' + "  ".join(f'{META[k]["name"]}{t["deltas"][k]:+.0f}%' for k in KEYS))

print("\n=== 相关系数（按卷，10 个样本）===")
for k, v in corr.items():
    tag = "强负相关" if v <= -0.6 else ("强正相关" if v >= 0.6 else
          ("中等负相关" if v <= -0.4 else ("中等正相关" if v >= 0.4 else "弱相关")))
    print(f'  {k:18s} r={v:+.3f}  {tag}')
