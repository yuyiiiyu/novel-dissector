# -*- coding: utf-8 -*-
"""阶段7：①灌水章检测 ②人物共现关系网 ③角色分卷活跃曲线 —— 输出 analysis_extra.json"""
import re, json, os, csv, collections, statistics

OUT = r"D:\aigc_pro\ai-video&draw\DeepSeek Harness\@ D Download 这个人明明很强却_2026-10-27\产出\data"

# ========== 读 chapters.csv ==========
rows = []
with open(os.path.join(OUT, "chapters.csv"), encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        rows.append({
            "num": int(r["章号"]), "title": r["标题"], "chars": int(r["字数"]),
            "paras": int(r["段落数"]), "dialog": int(r["对话引号数"]),
            "inner": int(r["心声数"]), "sys": int(r["系统提示数"]),
            "excl": int(r["感叹号"]), "quest": int(r["问号"]), "ellip": int(r["省略号"]),
            "d_ratio": float(r["对话密度‰"]),
        })

# ========== 读 chapter_signals.csv（战斗/甜度）==========
sig = {}
with open(os.path.join(OUT, "chapter_signals.csv"), encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        sig[int(r["章"])] = {"战斗": int(r["战斗"]), "甜度": int(r["甜度"])}
for r in rows:
    r.update(sig.get(r["num"], {"战斗": 0, "甜度": 0}))

# ========== 读卷信息 ==========
vols = []
with open(os.path.join(OUT, "volumes.csv"), encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        lo, hi = r["范围"].split("-")
        vols.append({"name": r["卷"], "lo": int(lo), "hi": int(hi), "desc": r["说明"]})

def z(v, arr):
    m, sd = statistics.mean(arr), statistics.pstdev(arr) or 1
    return (v - m) / sd

# ================= ① 灌水章检测 =================
# 定义：低字数 + 低对话密度 + 低信息量（无战斗/甜度/心声/系统）
chars = [r["chars"] for r in rows]
dr = [r["d_ratio"] for r in rows]
WATER = []
for r in rows:
    info = r["战斗"] + r["甜度"] + r["inner"] * 3 + r["sys"] * 5
    score = 0
    reason = []
    if r["chars"] < 1900:
        score += 1; reason.append(f'字数偏少({r["chars"]})')
    if r["d_ratio"] < 8.0:
        score += 1; reason.append(f'对话稀薄({r["d_ratio"]}‰)')
    if r["inner"] == 0 and r["sys"] == 0:
        score += 1; reason.append("无机杼（心声/系统全无）")
    if r["战斗"] == 0 and r["甜度"] == 0:
        score += 1; reason.append("无推进（战斗/感情均无）")
    if info <= 2:
        score += 1; reason.append("信息量极低")
    if score >= 3:
        WATER.append({"num": r["num"], "title": r["title"], "chars": r["chars"],
                      "d_ratio": r["d_ratio"], "score": score,
                      "reason": " · ".join(reason),
                      "vol": next((v["name"] for v in vols if v["lo"] <= r["num"] <= v["hi"]), "")})

# 反向：爆更章 / 高潮章（高潮 = 高战斗 or 高甜度 or 高心声）
PEAK = []
for r in rows:
    s = 0
    if r["战斗"] >= 12: s += 2
    elif r["战斗"] >= 7: s += 1
    if r["甜度"] >= 12: s += 2
    elif r["甜度"] >= 6: s += 1
    if r["inner"] >= 12: s += 1
    if r["chars"] >= 2800: s += 1
    if s >= 3:
        PEAK.append({"num": r["num"], "title": r["title"], "chars": r["chars"],
                     "战斗": r["战斗"], "甜度": r["甜度"], "心声": r["inner"],
                     "score": s,
                     "vol": next((v["name"] for v in vols if v["lo"] <= r["num"] <= v["hi"]), "")})
PEAK.sort(key=lambda x: (-x["score"], -x["战斗"]))

# 卷内灌水率
vol_water = []
for v in vols:
    sub = [r for r in rows if v["lo"] <= r["num"] <= v["hi"]]
    w = [x for x in WATER if v["lo"] <= x["num"] <= v["hi"]]
    vol_water.append({"卷": v["name"], "章数": len(sub), "灌水章": len(w),
                      "灌水率": round(len(w) / len(sub) * 100, 1),
                      "章均字数": round(statistics.mean(x["chars"] for x in sub))})

# ================= ② 人物共现关系网 =================
rm = json.load(open(os.path.join(OUT, "role_matrix.json"), encoding="utf-8"))
matrix = rm["matrix"]          # {角色: {"ch": {章号: 次数}}}
roles = list(matrix.keys())

# 只保留有实质戏份的角色
core = [w for w in roles if matrix[w]["span"] >= 5][:40]

edges = []
for i, a in enumerate(core):
    ca = set(int(k) for k in matrix[a]["ch"])
    for b in core[i + 1:]:
        cb = set(int(k) for k in matrix[b]["ch"])
        inter = ca & cb
        if len(inter) < 5:
            continue
        union = ca | cb
        jac = len(inter) / len(union) if union else 0
        # 同框强度：共现章数 × Jaccard
        w = len(inter) * (0.4 + 0.6 * jac)
        edges.append({"source": a, "target": b, "co": len(inter),
                      "jaccard": round(jac, 3), "weight": round(w, 1)})
edges.sort(key=lambda e: -e["weight"])

nodes = [{"id": w, "span": matrix[w]["span"], "total": matrix[w]["total"],
          "first": matrix[w]["first"], "last": matrix[w]["last"]} for w in core]
nodes.sort(key=lambda n: -n["total"])

# 社区（贪心：按最强边合并）—— 简单标签传播
adj = collections.defaultdict(list)
for e in edges:
    adj[e["source"]].append((e["target"], e["weight"]))
    adj[e["target"]].append((e["source"], e["weight"]))
lab = {n["id"]: n["id"] for n in nodes}
for _ in range(12):
    changed = False
    for n in nodes:
        if not adj[n["id"]]: continue
        best = max(adj[n["id"]], key=lambda x: x[1])[0]
        if lab[n["id"]] != lab[best]:
            lab[n["id"]] = lab[best]; changed = True
    if not changed: break
groups = collections.defaultdict(list)
for n in nodes:
    groups[lab[n["id"]]].append(n["id"])

# ================= ③ 角色分卷活跃曲线 =================
vol_curve = {}
for w in core[:20]:
    d = matrix[w]["ch"]
    series = []
    for v in vols:
        c = sum(int(d.get(str(k), d.get(k, 0))) for k in range(v["lo"], v["hi"] + 1))
        series.append(c)
    vol_curve[w] = series

# ================= 输出 =================
extra = {
    "water": WATER, "peak": PEAK[:60], "vol_water": vol_water,
    "edges": edges[:400], "nodes": nodes, "communities": dict(groups),
    "vol_curve": vol_curve, "vol_names": [v["name"] for v in vols],
    "vols": vols,
}
json.dump(extra, open(os.path.join(OUT, "analysis_extra.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

with open(os.path.join(OUT, "灌水章检测.csv"), "w", encoding="utf-8-sig", newline="") as f:
    f.write("章号,标题,所属卷,字数,对话密度‰,风险分,判定依据\n")
    for w in sorted(WATER, key=lambda x: (-x["score"], x["num"])):
        f.write('{},{},{},{},{},{},"{}"\n'.format(w["num"], w["title"], w["vol"],
                w["chars"], w["d_ratio"], w["score"], w["reason"]))

with open(os.path.join(OUT, "高潮章.csv"), "w", encoding="utf-8-sig", newline="") as f:
    f.write("章号,标题,所属卷,字数,战斗,甜度,心声,强度分\n")
    for p in PEAK:
        f.write('{},{},{},{},{},{},{},{}\n'.format(p["num"], p["title"], p["vol"],
                p["chars"], p["战斗"], p["甜度"], p["心声"], p["score"]))

with open(os.path.join(OUT, "人物关系边表.csv"), "w", encoding="utf-8-sig", newline="") as f:
    f.write("角色A,角色B,共现章数,Jaccard,边权重\n")
    for e in edges:
        f.write(f'{e["source"]},{e["target"]},{e["co"]},{e["jaccard"]},{e["weight"]}\n')

print("=== ①灌水章检测 ===")
print(f"疑似灌水章 {len(WATER)} / 589 = {len(WATER)/589*100:.1f}%")
for w in sorted(WATER, key=lambda x: -x["score"])[:15]:
    print(f' 第{w["num"]}章[{w["vol"][:6]}] {w["chars"]}字 {w["d_ratio"]}‰ 分{w["score"]} | {w["reason"]}')
print("\n各卷灌水率：")
for v in vol_water:
    print(f'  {v["卷"]:28s} {v["章数"]:3d}章 灌水{v["灌水章"]:2d} ({v["灌水率"]:4.1f}%) 章均{v["章均字数"]}字')

print(f"\n=== ②人物关系网 ===")
print(f"节点 {len(nodes)} / 边 {len(edges)}")
for e in edges[:15]:
    print(f'  {e["source"]:8s} — {e["target"]:8s} 共现{e["co"]:3d}章 J={e["jaccard"]:.2f} W={e["weight"]:.1f}')
print("\n社区：")
for k, v in sorted(groups.items(), key=lambda x: -len(x[1])):
    if len(v) >= 2:
        print(f'  [{k}] {len(v)}人: ' + " ".join(v[:10]))

print(f"\n=== ③高潮章 Top15 ===")
for p in PEAK[:15]:
    print(f' 第{p["num"]}章 {p["title"][:22]:24s} 战{p["战斗"]:3d} 甜{p["甜度"]:3d} 心{p["心声"]:3d} 分{p["score"]}')
