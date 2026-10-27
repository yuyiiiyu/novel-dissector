# -*- coding: utf-8 -*-
"""阶段10：心声机制深挖 —— 功能分类 + 逐卷演变 + 情绪符号 + 对象分布"""
import re, json, os, csv, collections, statistics

SRC = r"D:\Download\这个人明明很强却偏要坑萝莉师傅 - 一条咸鱼c.txt"
OUT = r"D:\aigc_pro\ai-video&draw\DeepSeek Harness\@ D Download 这个人明明很强却_2026-10-27\产出\data"
raw = open(SRC, encoding="utf-8").read()
lines = raw.split("\n")

CH = re.compile(r"^\s*第([0-9]+)章[\s　]*(.*)$")
idx = [(int(m.group(1)), m.group(2).strip(), i) for i, l in enumerate(lines) if (m := CH.match(l))]
idx.sort()

INNER = re.compile(r"【([^】]{4,120})】")
SYSPT = re.compile(r"【\s*叮")

# ===== 收集所有心声（带章号）=====
inner = []
for n, (num, tt, ln) in enumerate(idx):
    end = idx[n + 1][2] if n + 1 < len(idx) else len(lines)
    body = "\n".join(lines[ln:end])
    for m in INNER.finditer(body):
        t = m.group(1).strip()
        # 与 10_金句心声.py 保持同一口径：排除系统提示类
        if SYSPT.match(t) or re.search(r"^叮|系统|奖励|任务|魔力值|力量点数", t):
            continue
        inner.append({"ch": num, "text": t})

# 去重（与 10_金句心声.py 的 2129 口径保持一致）
_seen = set()
_uniq = []
for it in inner:
    if it["text"] in _seen:
        continue
    _seen.add(it["text"])
    _uniq.append(it)
print("心声总数：{}（去重后 {}，与 quotes.json 口径一致）".format(len(inner), len(_uniq)))
inner = _uniq

# ==================================================================
# A. 功能分类（多标签，一条可命中多类）
# ==================================================================
CATS = {
    "实力反差自嘲": ["一亿分之一", "五亿分之一", "魔力值", "二阶", "实力", "暴露",
                    "藏", "太强", "满级", "成神", "苟", "阶", "法神", "无敌",
                    "打不过", "碾压", "随手", "轻松", "小意思", "不值一提"],
    "咸鱼懒惰哲学": ["咸鱼", "睡觉", "午觉", "懒", "不想动", "躺着", "休息", "惬意",
                    "麻烦", "累", "出门", "锻炼", "苟着", "摸鱼", "摆烂", "躺平",
                    "不想", "懒得", "费劲", "折腾"],
    "吐槽师父": ["师父", "萝莉", "狗萝莉", "百年萝莉", "老萝莉", "打屁屁", "蓝毛",
                 "奈奈子", "呆毛", "马尾", "小矮子", "平", "发育"],
    "求生避险": ["苟", "神灵", "韭菜", "割", "换地方", "危险", "暴露", "被发现",
                 "算账", "躲", "逃", "小心", "谨慎", "保险", "万一", "不能让"],
    "得意炫耀": ["稳", "简单", "轻松", "随手", "不屑", "小意思", "就这", "垃圾", "弱",
                 "哈", "爽", "舒服", "美滋滋", "赚了", "值了", "天才"],
    "计划布局": ["计划", "打算", "准备", "安排", "布局", "下一步", "得想", "不如",
                 "要不", "先", "再说", "到时候", "等着", "慢慢来"],
    "情感流露": ["喜欢", "可爱", "心疼", "感动", "幸福", "想保护", "漂亮", "萌",
                 "好看", "温柔", "舍不得", "担心", "陪", "一辈子", "娶"],
    "震惊吐槽": ["卧槽", "我靠", "什么鬼", "？？", "！！！", "离谱", "疯了", "不可能",
                 "变态", "卧艹", "妈的", "坑", "有毒", "奇葩", "离了大谱"],
    "无奈叹气": ["哎", "唉", "可恶", "无奈", "无语", "服了", "认了", "算了",
                 "没办法", "命", "倒霉", "难受", "委屈"],
}

def cat_of(t):
    hits = []
    for c, kws in CATS.items():
        if any(k in t for k in kws):
            hits.append(c)
    return hits or ["其他"]

cat_cnt = collections.Counter()
cat_by_ch = collections.defaultdict(collections.Counter)
for it in inner:
    cs = cat_of(it["text"])
    it["cats"] = cs
    for c in cs:
        cat_cnt[c] += 1
        cat_by_ch[it["ch"]][c] += 1

# ==================================================================
# B. 逐卷演变
# ==================================================================
vols = []
with open(os.path.join(OUT, "volumes.csv"), encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        lo, hi = r["范围"].split("-")
        vols.append({"name": r["卷"], "lo": int(lo), "hi": int(hi)})

vol_evo = []
for v in vols:
    sub = [it for it in inner if v["lo"] <= it["ch"] <= v["hi"]]
    nch = v["hi"] - v["lo"] + 1
    c = collections.Counter()
    for it in sub:
        for cc in it["cats"]:
            c[cc] += 1
    vol_evo.append({
        "卷": v["name"], "章数": nch, "心声数": len(sub),
        "章均": round(len(sub) / nch, 2),
        "分类": dict(c.most_common()),
    })

# ==================================================================
# C. 情绪特征
# ==================================================================
feat = {
    "感叹号结尾": sum(1 for it in inner if it["text"].rstrip().endswith(("！", "!"))),
    "问号结尾": sum(1 for it in inner if it["text"].rstrip().endswith(("？", "?"))),
    "省略号结尾": sum(1 for it in inner if it["text"].rstrip().endswith(("…", "~", "～"))),
    "含颜文字": sum(1 for it in inner if re.search(r"[╬ヽ皿▽￣╥﹏≧∀≦ﾉ´｀#Дー＞д＜]", it["text"])),
    "含省略号": sum(1 for it in inner if "…" in it["text"]),
    "含波浪号": sum(1 for it in inner if re.search(r"[~～]", it["text"])),
    "第一人称我": sum(1 for it in inner if "我" in it["text"]),
    "提到师父": sum(1 for it in inner if "师父" in it["text"]),
    "提到萝莉": sum(1 for it in inner if "萝莉" in it["text"]),
}
for k in list(feat):
    feat[k + "_占比"] = round(feat[k] / len(inner) * 100, 1)

lens = [len(it["text"]) for it in inner]
feat["均长"] = round(statistics.mean(lens), 1)
feat["最长"] = max(lens)
feat["中位"] = statistics.median(lens)

# ==================================================================
# D. 长度分布 & 高光心声
# ==================================================================
buckets = collections.Counter()
for L in lens:
    if L <= 10: buckets["≤10字"] += 1
    elif L <= 20: buckets["11-20字"] += 1
    elif L <= 35: buckets["21-35字"] += 1
    elif L <= 60: buckets["36-60字"] += 1
    else: buckets[">60字"] += 1

# 每类代表句（取该类中最长的 3 条，信息量最大）
rep = {}
for c in CATS:
    s = sorted([it for it in inner if c in it["cats"]], key=lambda x: -len(x["text"]))[:3]
    rep[c] = [f'[第{x["ch"]}章] {x["text"]}' for x in s]
rep["其他"] = [f'[第{x["ch"]}章] {x["text"]}'
               for x in sorted([it for it in inner if "其他" in it["cats"]],
                               key=lambda x: -len(x["text"]))[:3]]

# ==================================================================
# E. 章级心声密度 Top
# ==================================================================
by_ch = collections.Counter(it["ch"] for it in inner)
top_ch = by_ch.most_common(20)

json.dump({"total": len(inner), "cats": dict(cat_cnt), "vol_evo": vol_evo,
           "feat": feat, "buckets": dict(buckets), "rep": rep,
           "top_ch": top_ch, "cat_by_ch": {str(k): dict(v) for k, v in cat_by_ch.items()}},
          open(os.path.join(OUT, "inner_monologue.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

with open(os.path.join(OUT, "心声分类.csv"), "w", encoding="utf-8-sig", newline="") as f:
    f.write("章号,分类,心声内容\n")
    for it in inner:
        f.write('{},{},"{}"\n'.format(it["ch"], "|".join(it["cats"]),
                                      it["text"].replace('"', '""')))

with open(os.path.join(OUT, "心声分卷演变.csv"), "w", encoding="utf-8-sig", newline="") as f:
    f.write("卷,章数,心声数,章均," + ",".join(CATS.keys()) + ",其他\n")
    for v in vol_evo:
        f.write('{},{},{},{},'.format(v["卷"], v["章数"], v["心声数"], v["章均"])
                + ",".join(str(v["分类"].get(c, 0)) for c in CATS) + ","
                + str(v["分类"].get("其他", 0)) + "\n")

print("\n=== 功能分类 ===")
for c, n in cat_cnt.most_common():
    print(f"  {c:12s} {n:5d}  ({n/len(inner)*100:4.1f}%)")
print("\n=== 逐卷演变（章均心声）===")
for v in vol_evo:
    print(f'  {v["卷"][:22]:24s} {v["章均"]:5.2f} 条/章  '
          + " ".join(f'{k[:2]}:{x}' for k, x in list(v["分类"].items())[:5]))
print("\n=== 情绪特征 ===")
for k, v in feat.items():
    print(f"  {k}: {v}")
print("\n=== 长度分布 ===")
for k in ["≤10字", "11-20字", "21-35字", "36-60字", ">60字"]:
    print(f"  {k}: {buckets.get(k,0)}")
print("\n=== 心声密度 Top10 章 ===")
for ch, n in top_ch[:10]:
    t = next((x[1] for x in idx if x[0] == ch), "")
    print(f"  第{ch}章 {n:2d}条 | {t[:26]}")
print("\n=== 各类代表句 ===")
for c, ss in rep.items():
    print(f"  【{c}】")
    for s in ss[:2]:
        print(f"    {s[:88]}")
