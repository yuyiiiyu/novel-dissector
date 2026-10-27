# -*- coding: utf-8 -*-
"""修正首个说话人（白名单锚定）+ 补充开场方式分类"""
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
ch_paras = {}
titles = {}
for i, it in enumerate(idx):
    num, tt, ln = it
    end = idx[i+1][2] if i+1 < len(idx) else len(lines)
    ps = [l.strip() for l in lines[ln+1:end]
          if l.strip() and not set(l.strip()) <= set("—-_=*·")]
    ch_paras[num] = ps
    titles[num] = tt

net = json.load(open(os.path.join(OUT, "network_clean.json"), encoding="utf-8"))
NAMES = [n["id"] for n in net["nodes"]] + ["师父", "徒儿"]

VERB = "说|道|问|答|喊|叫|回|吼|叹|喃喃|开口|补充|解释|提醒|安慰|命令|追问|回应"
ADV = ("皱眉|微笑|冷笑|苦笑|轻笑|平静|淡然|缓缓|震惊|疑惑|无奈|愤怒|严肃|小声|大声|"
       "轻声|低声|好奇|惊讶|温柔|淡淡|默默|静静|猛地|忽然|突然|立刻|顿时|赶紧|"
       "悄悄|下意识|忍不住|叹了口气")

DLG = re.compile(r"[“\"']([^\"“”']{2,80})[\"”']")
first_spk = collections.Counter()
first_mode = collections.Counter()      # 开场方式
per_ch = []
for num, ps in ch_paras.items():
    txt = "\n".join(ps)
    m = DLG.search(txt)
    seg = txt[:m.start()] if m else txt[:200]
    # 白名单角色
    who = ""
    best = None
    for nm in NAMES:
        mm = re.findall(re.escape(nm) + r"(?:" + ADV + r")?(?:地)?(?:" + VERB + r")", seg)
        if mm:
            pos = seg.rfind(nm)
            if best is None or pos > best[1]: best = (nm, pos)
    if best: who = best[0]
    first_spk[who if who else "叙述/未标注"] += 1
    # 开场方式
    head = ps[0] if ps else ""
    if head.startswith("【"): mode = "心声开场"
    elif head.startswith("“"): mode = "对话开场"
    elif len(head) <= 12: mode = "短句破题"
    elif re.search(r"^(这|那|此时|此刻|与此同时)", head): mode = "承接上章"
    else: mode = "场景描写"
    first_mode[mode] += 1
    per_ch.append({"ch": num, "first": who, "mode": mode})

top_spk = first_spk.most_common(12)
json.dump({"first_speaker": dict(top_spk), "first_mode": dict(first_mode),
           "per_ch": per_ch},
          open(os.path.join(OUT, "opening.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

with open(os.path.join(OUT, "章首结构.csv"), "w", encoding="utf-8-sig", newline="") as f:
    f.write("章号,标题,首个说话人,开场方式\n")
    for x in per_ch:
        f.write("%d,%s,%s,%s\n" % (x["ch"], titles.get(x["ch"], ""),
                x["first"] or "叙述", x["mode"]))

print("=== 首个说话人（白名单锚定）===")
tot = sum(first_spk.values())
for k, v in top_spk:
    print("  %-12s %4d (%.1f%%)" % (k or "叙述/未标注", v, v/tot*100))
print("\n=== 章首开场方式 ===")
for k, v in first_mode.most_common():
    print("  %-8s %4d (%.1f%%)" % (k, v, v/tot*100))
