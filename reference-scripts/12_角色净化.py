# -*- coding: utf-8 -*-
"""阶段7b：角色白名单净化 —— 剔除虚词噪声，只留可信人名/称号，重建关系网"""
import re, json, os, collections

OUT = r"D:\aigc_pro\ai-video&draw\DeepSeek Harness\@ D Download 这个人明明很强却_2026-10-27\产出\data"
SRC = r"D:\Download\这个人明明很强却偏要坑萝莉师傅 - 一条咸鱼c.txt"
raw = open(SRC, encoding="utf-8").read()

rm = json.load(open(os.path.join(OUT, "role_matrix.json"), encoding="utf-8"))
matrix = rm["matrix"]

# ===== 噪声黑名单：虚词/副词/口语/通用称谓 =====
NOISE = set("""
没错 认真 微笑 低声 咬牙 啊嘞 大喝 颤抖 不好 不行 淡笑 瞪眼 摇头 放心 放心吧 哼唧 没事 没什么
淡漠 眨眼 抬头 既然 既然如此 住手 思索 沙哑 抱歉 各位 什么人 窃取 皱眉 闭眼 呆滞 嘟囔 原来
原来如此 可恶 救命 犹疑 傲娇 卧槽 笑呵呵 大吼 严肃 嘴角 嘴角一翘 深深 猛然 缓缓 平静 不错
不好意思 快跑 吾王 真的吗 骑士长 快看 没事儿 敌袭 该死 哎呀 怎么样 不用担心 大姐 毕竟 确实
走吧 小秘 阿喂 吾神 不然呢 好厉害 剑傀爷爷 冲锋 军团长 吾等 禁咒 魔镜魔镜 什么情况 快退
二话不 可恶啊 没事儿 怎么样 真的吗 不用担心 不好意思 快看 敌袭 该死 哎呀 走吧 好厉害
瞬间 什么 已经 知道 如果 无数 时候 无序 几乎 非常 可能 仿佛 突然 出现 顿时 双眼 萝莉 千年
开始 应该 似乎 虽然 周围 注视 甚至 直接 东西 居然 现实 疯狂 神界 无法 依然 难道 深处 身边
浮现 只要 眸子 女孩 扭曲 虚空 曾经 真正 无比 脑袋 刚才 强大 漆黑 随即 瞬间便 只见 意志 彻底
奇怪 呆毛 即便 混乱 身影 生灵 位神 恐怖 领域 样子 某种 记忆 告诉 完全 降临 情况 清楚 本源
满脸 转过头 萝莉 海王 神王 秩序神 盗日者 初诞者 堕落神 母神 海神 女神 魔君 大君 主宰
""".split())

# ===== 人工确认的白名单（真实角色/重要称号）=====
WHITELIST = [
    # 核心
    "林恩", "奈奈子",
    # 重要角色（高提及 + 人名形态）
    "艾维儿", "爱丽丝", "安德鲁", "薇薇安", "路西法", "马绍尔", "雷蒙", "格林",
    "阿诺德", "安德烈", "摩洛克", "塞莉娜", "艾玲娜", "圣安娜", "凯尔",
    # 神祇/称号（叙事实体，非虚词）
    "秩序神", "现实神", "命运神", "堕落神", "海神", "海王", "母神", "元素母神",
    "因果神王", "空间神王", "轮回神王", "神王", "盗日者", "源王", "源妹",
    "命运女神", "初诞者", "沉眠者", "禁忌龙", "剑傀", "骨王", "魂王", "魔君",
    "大君", "主宰", "半神", "天使", "精灵", "恶魔",
]

# 保留：白名单 ∪ （非噪声 且 覆盖章数≥6 且 提及≥60）
keep = []
for w, m in matrix.items():
    if w in WHITELIST:
        keep.append(w); continue
    if w in NOISE:
        continue
    if m["span"] >= 6 and m["total"] >= 60:
        keep.append(w)
keep = sorted(set(keep))
print("净化后角色：", len(keep))
print(keep)

# ===== 重建矩阵（只保留白名单角色，用精确词频重新统计）=====
lines = raw.split("\n")
CH = re.compile(r"^\s*第([0-9]+)章[\s　]*(.*)$")
idx = [(int(m.group(1)), m.group(2).strip(), i) for i, l in enumerate(lines) if (m := CH.match(l))]
idx.sort()
chunks = []
for n, (num, title, ln) in enumerate(idx):
    end = idx[n + 1][2] if n + 1 < len(idx) else len(lines)
    chunks.append((num, "\n".join(lines[ln:end])))

matrix2 = {}
for w in keep:
    p = re.compile(re.escape(w))
    d = {}
    for num, body in chunks:
        c = len(p.findall(body))
        if c: d[num] = c
    matrix2[w] = {"ch": d, "total": sum(d.values()), "span": len(d),
                  "first": min(d) if d else None, "last": max(d) if d else None}

# ===== 关系网 =====
core = [w for w in keep if matrix2[w]["span"] >= 5]
edges = []
for i, a in enumerate(core):
    ca = set(matrix2[a]["ch"])
    for b in core[i + 1:]:
        cb = set(matrix2[b]["ch"])
        inter = ca & cb
        if len(inter) < 4: continue
        union = ca | cb
        jac = len(inter) / len(union) if union else 0
        edges.append({"source": a, "target": b, "co": len(inter),
                      "jaccard": round(jac, 3),
                      "weight": round(len(inter) * (0.4 + 0.6 * jac), 1)})
edges.sort(key=lambda e: -e["weight"])

nodes = [{"id": w, "span": matrix2[w]["span"], "total": matrix2[w]["total"],
          "first": matrix2[w]["first"], "last": matrix2[w]["last"]} for w in core]
nodes.sort(key=lambda n: -n["total"])

# 社区（标签传播）
adj = collections.defaultdict(list)
for e in edges:
    adj[e["source"]].append((e["target"], e["weight"]))
    adj[e["target"]].append((e["source"], e["weight"]))
lab = {n["id"]: n["id"] for n in nodes}
for _ in range(20):
    ch = False
    for n in nodes:
        if not adj[n["id"]]: continue
        best = max(adj[n["id"]], key=lambda x: x[1])[0]
        if lab[n["id"]] != lab[best]:
            lab[n["id"]] = lab[best]; ch = True
    if not ch: break
groups = collections.defaultdict(list)
for n in nodes:
    groups[lab[n["id"]]].append(n["id"])

# ===== 分卷活跃曲线 =====
vols = []
import csv
with open(os.path.join(OUT, "volumes.csv"), encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        lo, hi = r["范围"].split("-")
        vols.append({"name": r["卷"], "lo": int(lo), "hi": int(hi)})

vol_curve = {}
for w in core:
    d = matrix2[w]["ch"]
    vol_curve[w] = [sum(d.get(k, 0) for k in range(v["lo"], v["hi"] + 1)) for v in vols]

json.dump({"matrix": matrix2, "edges": edges, "nodes": nodes,
           "communities": dict(groups), "vol_curve": vol_curve,
           "vol_names": [v["name"] for v in vols]},
          open(os.path.join(OUT, "network_clean.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

with open(os.path.join(OUT, "人物关系边表.csv"), "w", encoding="utf-8-sig", newline="") as f:
    f.write("角色A,角色B,共现章数,Jaccard,边权重\n")
    for e in edges:
        f.write(f'{e["source"]},{e["target"]},{e["co"]},{e["jaccard"]},{e["weight"]}\n')

print(f"\n节点 {len(nodes)} / 边 {len(edges)}")
print("--- 最强关系 Top20 ---")
for e in edges[:20]:
    print(f'  {e["source"]:8s} — {e["target"]:8s} 共现{e["co"]:3d}章 J={e["jaccard"]:.2f} W={e["weight"]:.1f}')
print("\n--- 社区 ---")
for k, v in sorted(groups.items(), key=lambda x: -len(x[1])):
    if len(v) >= 2:
        print(f'  [{k}] {len(v)}人: ' + " ".join(v[:12]))
