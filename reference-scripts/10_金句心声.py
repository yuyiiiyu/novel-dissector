# -*- coding: utf-8 -*-
"""阶段6：心声/金句/章末钩子 抽取"""
import re, json, os, collections

SRC = r"D:\Download\这个人明明很强却偏要坑萝莉师傅 - 一条咸鱼c.txt"
OUT = r"D:\aigc_pro\ai-video&draw\DeepSeek Harness\@ D Download 这个人明明很强却_2026-10-27\产出\data"
raw = open(SRC, encoding="utf-8").read()
lines = raw.split("\n")

CH = re.compile(r"^\s*第([0-9]+)章[\s　]*(.*)$")
idx = [(int(m.group(1)), m.group(2).strip(), i) for i, l in enumerate(lines) if (m := CH.match(l))]
idx.sort()

# ===== A. 心声（【...】）=====
INNER = re.compile(r"【([^】]{4,120})】")
inner = []
for n, (num, title, ln) in enumerate(idx):
    end = idx[n + 1][2] if n + 1 < len(idx) else len(lines)
    body = "\n".join(lines[ln:end])
    for m in INNER.finditer(body):
        t = m.group(1).strip()
        if re.search(r"^叮|系统|奖励|任务|魔力值|力量点数", t):
            continue  # 系统提示单独处理
        inner.append({"ch": num, "text": t})

# ===== B. 系统提示 =====
SYS = re.compile(r"【\s*叮！?\s*([^】]{2,80})】")
sysp = [{"ch": None, "text": m.group(1).strip()} for m in SYS.finditer(raw)]
# 归属章节
for n, (num, title, ln) in enumerate(idx):
    end = idx[n + 1][2] if n + 1 < len(idx) else len(lines)
    for m in SYS.finditer("\n".join(lines[ln:end])):
        sysp.append({"ch": num, "text": m.group(1).strip()})

# ===== C. 章末钩子（每章最后一句）=====
hooks = []
for n, (num, title, ln) in enumerate(idx):
    end = idx[n + 1][2] if n + 1 < len(idx) else len(lines)
    seg = [l.strip() for l in lines[max(ln, end - 12):end] if l.strip()]
    seg = [s for s in seg if not set(s) <= set("—-_=*·")]
    if seg:
        hooks.append({"ch": num, "title": title, "hook": seg[-1][:90]})

# ===== D. 章首开场 =====
opens = []
for n, (num, title, ln) in enumerate(idx):
    for l in lines[ln + 1:ln + 12]:
        s = l.strip()
        if s and not set(s) <= set("—-_=*·"):
            opens.append({"ch": num, "title": title, "open": s[:90]})
            break

# ===== E. 金句：带强烈情绪且结构完整的短句 =====
GOLD = re.compile(r"[“\"']([^“”\"']{10,60}[！？])[\"”']")
gold = []
for n, (num, title, ln) in enumerate(idx):
    end = idx[n + 1][2] if n + 1 < len(idx) else len(lines)
    body = "\n".join(lines[ln:end])
    for m in GOLD.finditer(body):
        t = m.group(1).strip()
        if t.startswith("【") or "叮" in t[:4]:
            continue
        gold.append({"ch": num, "text": t})

# 去重
def dedup(lst, key="text"):
    seen, out = set(), []
    for it in lst:
        k = it[key]
        if k in seen: continue
        seen.add(k); out.append(it)
    return out

inner = dedup(inner); gold = dedup(gold); sysp = dedup(sysp)

json.dump({"inner": inner, "system": sysp, "hooks": hooks,
           "opens": opens, "gold": gold},
          open(os.path.join(OUT, "quotes.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

for tag, lst, fw in (("心声", inner, "text"), ("系统", sysp, "text"),
                     ("金句", gold, "text")):
    with open(os.path.join(OUT, f"{tag}.txt"), "w", encoding="utf-8") as f:
        for it in lst[:400]:
            f.write(f'[第{it["ch"]}章] {it[fw]}\n')

print("心声条数：", len(inner))
print("系统提示：", len(sysp))
print("金句：", len(gold))
print("章末钩子：", len(hooks))
print("\n--- 心声样例 25 ---")
for it in inner[:25]:
    print(f'[第{it["ch"]}章] {it["text"]}')
print("\n--- 系统提示样例 20 ---")
for it in sysp[:20]:
    print(f'[第{it["ch"]}章] {it["text"]}')
print("\n--- 金句样例 20 ---")
for it in gold[:20]:
    print(f'[第{it["ch"]}章] {it["text"]}')
print("\n--- 章末钩子样例 15 ---")
for it in hooks[:15]:
    print(f'[第{it["ch"]}章] {it["hook"]}')
