# -*- coding: utf-8 -*-
"""阶段9：语言指纹 —— 套路用词画像 + 章节标题语言学"""
import re, json, os, csv, collections, statistics

SRC = r"D:\Download\这个人明明很强却偏要坑萝莉师傅 - 一条咸鱼c.txt"
OUT = r"D:\aigc_pro\ai-video&draw\DeepSeek Harness\@ D Download 这个人明明很强却_2026-10-27\产出\data"
raw = open(SRC, encoding="utf-8").read()
lines = raw.split("\n")
TOTAL_HAN = len(re.findall(r"[\u4e00-\u9fa5]", raw))

# ==================================================================
# A. 套路用词画像
# ==================================================================
GROUPS = {
    "时间副词（瞬时）": ["瞬间", "刹那", "霎时", "顷刻", "转瞬", "一瞬", "电光火石"],
    "时间副词（突发）": ["突然", "忽然", "猛地", "骤然", "蓦地", "陡然", "猝然", "忽地"],
    "时间副词（接续）": ["立刻", "顿时", "随即", "马上", "赶紧", "连忙", "急忙", "当即", "立即"],
    "速度副词": ["缓缓", "慢慢", "徐徐", "迅速", "飞快", "急速", "闪电般", "刹那间"],
    "程度副词": ["微微", "淡淡", "稍稍", "略微", "极其", "无比", "万分", "异常", "格外", "十分"],
    "情态副词": ["似乎", "仿佛", "宛如", "犹如", "好像", "仿佛是", "好似", "恰似"],
    "心理自动词": ["下意识", "不由得", "忍不住", "情不自禁", "本能地", "潜意识"],
    "夸张成语": ["前所未有", "空前绝后", "铺天盖地", "遮天蔽日", "惊天动地", "毁天灭地",
                 "难以置信", "不可思议", "匪夷所思", "闻所未闻", "史无前例"],
    "身体反应模板": ["倒吸一口凉气", "瞳孔一缩", "浑身一震", "心中一凛", "脸色微变",
                     "嘴角抽搐", "呼吸一滞", "心头一紧", "遍体生寒", "毛骨悚然",
                     "冷汗直流", "头皮发麻", "如坠冰窖", "五雷轰顶"],
    "视觉模板": ["映入眼帘", "尽收眼底", "一览无余", "赫然", "放眼望去", "定睛一看"],
    "听觉模板": ["传入耳中", "响彻", "回荡", "萦绕", "震耳欲聋", "戛然而止"],
}

words_stat = {}
for g, ws in GROUPS.items():
    items = []
    for w in ws:
        n = raw.count(w)
        if n:
            items.append({"w": w, "n": n, "per10k": round(n / TOTAL_HAN * 10000, 2)})
    items.sort(key=lambda x: -x["n"])
    words_stat[g] = {"items": items, "total": sum(i["n"] for i in items),
                     "types": len(items)}
    words_stat[g]["per10k"] = round(words_stat[g]["total"] / TOTAL_HAN * 10000, 2)

# 单字级高频虚词
CHARS = ["的", "了", "是", "在", "和", "与", "就", "也", "都", "这", "那", "你", "我",
         "他", "她", "它", "们", "个", "为", "被", "把", "给", "对", "从", "到", "很",
         "更", "最", "再", "又", "之", "而", "其", "及", "以", "于", "所"]
char_stat = [{"w": c, "n": raw.count(c), "per10k": round(raw.count(c) / TOTAL_HAN * 10000, 1)}
             for c in CHARS]
char_stat.sort(key=lambda x: -x["n"])

# 标点指纹
PUNCT = {"，": "逗号", "。": "句号", "！": "叹号", "？": "问号", "…": "省略号点",
         "；": "分号", "：": "冒号", "、": "顿号", "“": "左引号", "”": "右引号",
         "【": "心声左", "】": "心声右", "—": "破折号"}
punct = [{"w": k, "name": v, "n": raw.count(k),
          "per10k": round(raw.count(k) / TOTAL_HAN * 10000, 1)}
         for k, v in PUNCT.items()]
punct.sort(key=lambda x: -x["n"])

# 段落与句长
paras = [l.strip() for l in lines if l.strip() and not set(l.strip()) <= set("—-_=*·")]
para_len = [len(re.findall(r"[\u4e00-\u9fa5]", p)) for p in paras]
sent = re.split(r"[。！？…]+", raw)
sent_len = [len(re.findall(r"[\u4e00-\u9fa5]", s)) for s in sent if s.strip()]

lang_stats = {
    "总汉字": TOTAL_HAN,
    "段落数": len(paras),
    "段均汉字": round(statistics.mean(para_len), 1),
    "段长中位数": statistics.median(para_len),
    "最短段": min(para_len), "最长段": max(para_len),
    "句数": len(sent_len),
    "句均汉字": round(statistics.mean(sent_len), 1),
    "句中位数": statistics.median(sent_len),
    "一字句占比": round(sum(1 for x in sent_len if x <= 1) / len(sent_len) * 100, 1),
    "短句(≤10字)占比": round(sum(1 for x in sent_len if x <= 10) / len(sent_len) * 100, 1),
    "长句(>30字)占比": round(sum(1 for x in sent_len if x > 30) / len(sent_len) * 100, 1),
}

# ==================================================================
# B. 章节标题语言学
# ==================================================================
CH = re.compile(r"^\s*第([0-9]+)章[\s　]*(.*)$")
titles = [(int(m.group(1)), m.group(2).strip())
          for l in lines if (m := CH.match(l))]
titles.sort()
ts = [t for _, t in titles]

tf = {
    "标题数": len(ts),
    "均长": round(statistics.mean(len(t) for t in ts), 1),
    "最长": max(len(t) for t in ts),
    "最短": min(len(t) for t in ts),
    "疑问句": sum(1 for t in ts if "？" in t or "?" in t),
    "感叹句": sum(1 for t in ts if "！" in t or "!" in t),
    "省略号": sum(1 for t in ts if "…" in t),
    "逗号": sum(1 for t in ts if "，" in t),
    "纯陈述": sum(1 for t in ts if not re.search(r"[？?！!…，]", t)),
}
for k in ["疑问句", "感叹句", "省略号", "逗号", "纯陈述"]:
    tf[k + "占比"] = round(tf[k] / len(ts) * 100, 1)

# 人称
persons = {}
for p in ["我", "你", "他", "她", "师父", "徒儿", "萝莉", "林恩", "奈奈子", "神", "王"]:
    c = sum(1 for t in ts if p in t)
    persons[p] = {"n": c, "pct": round(c / len(ts) * 100, 1)}

# 首字 / 首词
first_char = collections.Counter(t[0] for t in ts if t)
first_two = collections.Counter(t[:2] for t in ts if len(t) >= 2)

# 标题类型分类（规则）
def classify(t):
    if re.search(r"[？?]$", t): return "悬念疑问式"
    if re.search(r"[！!]$", t): return "爆发感叹式"
    if re.search(r"[？?]", t): return "内含疑问"
    if re.match(r"^我", t): return "第一人称宣言"
    if re.match(r"^你", t): return "第二人称对话"
    if re.match(r"^(这|那)", t): return "指示代词起手"
    if re.match(r"^(不|没|别)", t): return "否定反转"
    if re.search(r"[，,]", t): return "复句转折"
    return "陈述式"

tc = collections.Counter(classify(t) for t in ts)

# 含数字/口语/玩梗
slang = sum(1 for t in ts if re.search(r"(卧槽|我靠|妈的|靠|坑|骚|装|x|装x|牛|绝|狗|蛋)", t))
num = sum(1 for t in ts if re.search(r"[0-9一二三四五六七八九十百千万亿]", t))

title_stat = {"总览": tf, "人称": persons,
              "首字Top": first_char.most_common(14),
              "首词Top": first_two.most_common(12),
              "类型分布": dict(tc.most_common()),
              "口语玩梗": slang, "含数字": num}

# ==================================================================
# C. 颜文字 / 情绪符号
# ==================================================================
KAOMOJI = re.compile(r"[╬◣◢皿￣▽╥﹏≧∀≦´▽｀#`Д´ー_。＞д＜]{3,}")
kao = collections.Counter(m.group(0) for m in KAOMOJI.finditer(raw))
# 更准确的完整颜文字
KAO_FULL = re.compile(r"\(?[╬ヽO][^()（）\s]{0,12}[)）]|[╬][^╬]{0,3}")
kao2 = collections.Counter()
for m in re.finditer(r"\(╬[^)]*\)|ヽ\([^)]*\)|O\([^)]*\)|\(\^?[^)]{0,8}[╬皿]\)", raw):
    kao2[m.group(0)] += 1

# 定位颜文字所在章
kao_ch = collections.defaultdict(collections.Counter)
idx = [(int(m.group(1)), m.group(2).strip(), i)
       for i, l in enumerate(lines) if (m := CH.match(l))]
idx.sort()
for n, (num, tt, ln) in enumerate(idx):
    end = idx[n + 1][2] if n + 1 < len(idx) else len(lines)
    body = "\n".join(lines[ln:end])
    for m in re.finditer(r"\(╬[^)]*\)|ヽ\([^)]*\)|O\([^)]*\)", body):
        kao_ch[m.group(0)][num] += 1

json.dump({"words": words_stat, "chars": char_stat, "punct": punct,
           "lang": lang_stats, "title": title_stat,
           "kaomoji": dict(kao2.most_common(30)),
           "kaomoji_ch": {k: dict(v) for k, v in list(kao_ch.items())[:10]}},
          open(os.path.join(OUT, "language_fingerprint.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

# CSV 输出
with open(os.path.join(OUT, "套路用词.csv"), "w", encoding="utf-8-sig", newline="") as f:
    f.write("类别,词条,出现次数,每万字频次\n")
    for g, d in words_stat.items():
        for it in d["items"]:
            f.write(f'{g},{it["w"]},{it["n"]},{it["per10k"]}\n')

with open(os.path.join(OUT, "标题语言学.csv"), "w", encoding="utf-8-sig", newline="") as f:
    f.write("章号,标题,字数,类型,含人称\n")
    for num, t in titles:
        ps = "".join(p for p in ["我", "你", "他", "她", "师父", "徒儿", "萝莉"] if p in t)
        f.write(f'{num},{t},{len(t)},{classify(t)},{ps}\n')

print("总汉字：", TOTAL_HAN)
print("\n=== 段落/句长 ===")
for k, v in lang_stats.items():
    print(f"  {k}: {v}")
print("\n=== 套路用词（按类别）===")
for g, d in sorted(words_stat.items(), key=lambda x: -x[1]["total"]):
    print(f'  {g:16s} 合计{d["total"]:5d} ({d["per10k"]}/万字) '
          + " ".join(f'{i["w"]}({i["n"]})' for i in d["items"][:5]))
print("\n=== 标点指纹 ===")
for p in punct[:9]:
    print(f'  {p["name"]:6s} {p["w"]}  {p["n"]:6d}  ({p["per10k"]}/万字)')
print("\n=== 标题语言学 ===")
for k, v in tf.items():
    print(f"  {k}: {v}")
print("  人称:", {k: v["n"] for k, v in persons.items()})
print("  类型:", dict(tc.most_common()))
print("  首字Top:", dict(first_char.most_common(8)))
print("  口语玩梗:", slang, " 含数字:", num)
print("\n=== 颜文字 ===")
for k, v in kao2.most_common(12):
    print(f"  {k}  ×{v}")
