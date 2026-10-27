# -*- coding: utf-8 -*-
"""阶段2：专名抽取 —— n-gram + 凝固度(PMI) + 左右邻字熵，无第三方依赖"""
import re, json, os, math, collections

SRC = r"D:\Download\这个人明明很强却偏要坑萝莉师傅 - 一条咸鱼c.txt"
OUT = r"D:\aigc_pro\ai-video&draw\DeepSeek Harness\@ D Download 这个人明明很强却_2026-10-27\产出\data"
DD = os.path.join(OUT, "..")
os.makedirs(OUT, exist_ok=True)

raw = open(SRC, encoding="utf-8").read()

# 只保留 CJK 连续片段做抽词
CJK = re.compile(r"[\u4e00-\u9fa5]+")
seg = CJK.findall(raw)
print("CJK 片段数：", len(seg), "总汉字：", sum(len(s) for s in seg))

# ---------- 1. 频次统计 ----------
uni = collections.Counter()
for s in seg:
    for ch in s:
        uni[ch] += 1
TOTAL = sum(uni.values())

MAXN = 4
ngram = {n: collections.Counter() for n in range(2, MAXN + 1)}
for s in seg:
    L = len(s)
    for n in range(2, MAXN + 1):
        if L < n:
            continue
        c = ngram[n]
        for i in range(L - n + 1):
            c[s[i:i + n]] += 1

# ---------- 2. 左右邻字熵 ----------
left = collections.defaultdict(collections.Counter)
right = collections.defaultdict(collections.Counter)
for s in seg:
    L = len(s)
    for n in range(1, MAXN):          # 为长度 n 的词统计邻居
        for i in range(L - n + 1):
            w = s[i:i + n]
            if i > 0:
                left[w][s[i - 1]] += 1
            if i + n < L:
                right[w][s[i + n]] += 1

def entropy(c):
    t = sum(c.values())
    if t == 0:
        return 0.0
    return -sum((v / t) * math.log(v / t, 2) for v in c.values())

# ---------- 3. 凝固度：取所有二分方式中最小的 PMI ----------
def solidarity(w):
    f = ngram[len(w)][w] if len(w) in ngram else uni.get(w, 0)
    if f == 0:
        return 0.0
    best = float("inf")
    for i in range(1, len(w)):
        a, b = w[:i], w[i:]
        fa = uni.get(a, 0) if len(a) == 1 else ngram[len(a)].get(a, 0)
        fb = uni.get(b, 0) if len(b) == 1 else ngram[len(b)].get(b, 0)
        if fa == 0 or fb == 0:
            return 0.0
        pmi = math.log((f * TOTAL) / (fa * fb), 2)
        best = min(best, pmi)
    return best

# ---------- 4. 停用/虚词过滤 ----------
STOP1 = set("的了是在有和与就不也都这那我你他她它们个上下中前后里外为被把给对从到过还很更最再也又之一不没没")
BAD_PAT = re.compile(r"^[的了是在有和与就不也都这那我你他她它们个为被把给对从到过还很更最再也又之而及其以于所]$")
def bad(w):
    if len(w) < 2:
        return True
    if w[0] in STOP1 or w[-1] in STOP1:
        return True
    if len(set(w)) == 1:
        return True
    if BAD_PAT.match(w[0]) or BAD_PAT.match(w[-1]):
        return True
    return False

# ---------- 5. 打分 ----------
cand = []
seen = set()
for n in range(2, MAXN + 1):
    for w, f in ngram[n].items():
        if f < 25 or bad(w) or w in seen:
            continue
        sol = solidarity(w)
        if sol < 3.0:
            continue
        le, re_ = entropy(left[w]), entropy(right[w])
        if min(le, re_) < 1.2:
            continue
        seen.add(w)
        cand.append({"w": w, "f": f, "sol": round(sol, 2),
                     "le": round(le, 2), "re": round(re_, 2),
                     "score": round(sol * min(le, re_) * math.log(f + 1, 2), 2)})

cand.sort(key=lambda x: -x["score"])
json.dump(cand, open(os.path.join(OUT, "ngram_candidates.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("候选词：", len(cand))
for c in cand[:80]:
    print(c["w"], c["f"], c["score"])
