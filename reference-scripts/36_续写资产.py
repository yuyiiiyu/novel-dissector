# -*- coding: utf-8 -*-
"""阶段18：续写资产 —— 结局解密 / 未回收伏笔 / 角色终局状态 / 续写硬约束"""
import re, json, os, collections, csv, io, sys
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
bodies = {}
for i, it in enumerate(idx):
    num, tt, ln = it
    end = idx[i+1][2] if i+1 < len(idx) else len(lines)
    bodies[num] = "\n".join(lines[ln:end])

# ========== 1. 结局段：最后 5 章全文关键句 ==========
ending = {}
for num in [585, 586, 587, 588, 589]:
    b = bodies[num]
    ps = [l.strip() for l in b.split("\n") if l.strip() and not set(l.strip()) <= set("—-_=*·")]
    ending[num] = {
        "title": idx[num-1][1] if num <= len(idx) else "",
        "chars": len(b),
        "paras": len(ps),
        "tail": ps[-6:],     # 最后 6 段
        "head": ps[:4],
    }

# ========== 2. 结局判定：谁赢/谁死/感情状态 ==========
tail_all = "\n".join(bodies[n] for n in range(585, 590))
WIN = ["成功", "胜利", "赢了", "击败", "战胜", "新的世界", "迎来", "活下来"]
LOSE = ["失败", "泡影", "化为了", "没能", "终究还是没有", "牺牲", "消散", "陨落", "死亡"]
DEAD = ["死", "陨落", "消散", "消失", "牺牲", "湮灭"]
res = {
    "失败词命中": sum(tail_all.count(w) for w in LOSE),
    "成功词命中": sum(tail_all.count(w) for w in WIN),
    "死亡/消散词": sum(tail_all.count(w) for w in DEAD),
}
# 关键句提取
keys = []
for p in tail_all.split("\n"):
    p = p.strip()
    if len(p) < 8: continue
    if any(w in p for w in ["失败", "泡影", "未来", "等", "希望", "新的世界", "轮回", "沉眠者"]):
        keys.append(p)
keys = list(dict.fromkeys(keys))[:20]

# ========== 3. 未回收伏笔（末现章 < 589 且后期消失）==========
nv = json.load(open(os.path.join(OUT, "narrative.json"), encoding="utf-8"))
unresolved = []
for x in nv["foreshadow"]:
    if x["last"] < 560:      # 结局前就消失
        unresolved.append({
            "w": x["w"], "first": x["first"], "last": x["last"],
            "gap": x["gap"], "miss_after": 589 - x["last"],
        })
unresolved.sort(key=lambda x: -x["miss_after"])

# ========== 4. 角色终局状态（末现章位置）==========
net = json.load(open(os.path.join(OUT, "network_clean.json"), encoding="utf-8"))
roles_status = []
for n in net["nodes"]:
    nm = n["id"]; last = n["last"]; first = n["first"]
    if last >= 585: state = "活跃至终局"
    elif last >= 540: state = "后期退场"
    elif last >= 400: state = "中段退场"
    else: state = "早期退场"
    # 最后出现的上下文
    ctx = ""
    if last in bodies:
        i = bodies[last].find(nm)
        if i >= 0: ctx = bodies[last][max(0,i-60):i+90].replace("\n", " ")[:150]
    roles_status.append({"name": nm, "first": first, "last": last,
                         "total": n["total"], "span": n["span"],
                         "state": state, "last_ctx": ctx})
roles_status.sort(key=lambda x: -x["last"])

# ========== 5. 续写硬约束（从全书统计推出）==========
with open(os.path.join(OUT, "chapters.csv"), encoding="utf-8-sig") as f:
    chs = list(csv.DictReader(f))
import statistics
cs = [int(c["字数"]) for c in chs]
inn = [int(c["心声数"]) for c in chs]
dl = [int(c["对话引号数"]) for c in chs]
ci = json.load(open(os.path.join(OUT, "chapter_internal.json"), encoding="utf-8"))
lf = json.load(open(os.path.join(OUT, "language_fingerprint.json"), encoding="utf-8"))

rules = {
    "章均字数": round(statistics.mean(cs)),
    "字数安全区": [round(statistics.mean(cs)-350), round(statistics.mean(cs)+550)],
    "心声/章": round(statistics.mean(inn), 1),
    "对话引号/章": round(statistics.mean(dl), 1),
    "对话回合/章": ci["turn_stat"]["avg"],
    "段均汉字": lf["lang"]["段均汉字"],
    "短句占比": lf["lang"]["短句(≤10字)占比"],
    "标题均长": lf["title"]["总览"]["均长"],
    "标题人称公式": "我/你 + 反转短句（占36%）",
    "第一高频副词": "瞬间 24.9/万字",
    "章末公式": "对话密度骤升+1条心声+短促钩子",
    "开场公式": "短句破题45% 或 场景描写41%，不用XX道开章",
    "绝对禁忌": [
        "不可让心声回归（501章后已关闭，第九卷0条）",
        "不可写战斗+感情双高峰（全书无此章，r=-0.655互斥）",
        "不可用'XX道'开章（98%未标注）",
        "不可引入新招式名（全书《》仅2次）",
    ],
}

json.dump({"ending": ending, "result": res, "key_sentences": keys,
           "unresolved": unresolved, "roles_status": roles_status,
           "rules": rules},
          open(os.path.join(OUT, "续写资产.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

with open(os.path.join(OUT, "续写硬约束.csv"), "w", encoding="utf-8-sig", newline="") as f:
    f.write("维度,数值,说明\n")
    for k, v in rules.items():
        if isinstance(v, list):
            f.write('%s,"%s","%s"\n' % (k, " / ".join(str(x) for x in v[:4]),
                    "；".join(v[4:]) if len(v) > 4 else ""))
        else:
            f.write("%s,%s,\n" % (k, v))

with open(os.path.join(OUT, "角色终局状态.csv"), "w", encoding="utf-8-sig", newline="") as f:
    f.write("角色,首现,末现,总提及,覆盖章,终局状态,最后出现上下文\n")
    for r in roles_status:
        f.write('{},{},{},{},{},{},"{}"\n'.format(r["name"], r["first"], r["last"],
                r["total"], r["span"], r["state"], r["last_ctx"].replace('"','""')[:120]))

with open(os.path.join(OUT, "未回收伏笔.csv"), "w", encoding="utf-8-sig", newline="") as f:
    f.write("词条,首现,末现,最大空档,结局前消失章数\n")
    for u in unresolved:
        f.write("{},{},{},{},{}\n".format(u["w"], u["first"], u["last"], u["gap"], u["miss_after"]))

print("=== 1. 结局判定 ===")
print("  ", res)
print("  结论：全书以【失败/牺牲】收尾，非胜利结局")
print("\n=== 2. 结局关键句 ===")
for k in keys[:8]:
    print("   ", k[:78])
print("\n=== 3. 结局前消失的伏笔（可续写回收）===")
for u in unresolved[:10]:
    print("   %-8s 首%-4d 末%-4d 空档%3d章 结局前消失%3d章"
          % (u["w"], u["first"], u["last"], u["gap"], u["miss_after"]))
print("\n=== 4. 角色终局状态 ===")
for r in roles_status[:12]:
    print("   %-8s 末现%-4d %-8s %s" % (r["name"], r["last"], r["state"], r["last_ctx"][:44]))
print("\n=== 5. 续写硬约束 ===")
for k, v in rules.items():
    print("   %-14s %s" % (k, v))
