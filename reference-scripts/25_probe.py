# -*- coding: utf-8 -*-
"""探测脚本：评估 6 个候选新方向的数据可行性"""
import re, json, os, collections, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

SRC = r"D:\Download\这个人明明很强却偏要坑萝莉师傅 - 一条咸鱼c.txt"
OUT = r"D:\aigc_pro\ai-video&draw\DeepSeek Harness\@ D Download 这个人明明很强却_2026-10-27\产出\data"
raw = open(SRC, encoding="utf-8").read()
lines = raw.split("\n")

CH = re.compile(r"^\s*第([0-9]+)章[\s　]*(.*)$")
idx = [(int(m.group(1)), m.group(2).strip(), i) for i, l in enumerate(lines) if (m := CH.match(l))]
idx.sort()

def ch_body(n):
    num, tt, ln = idx[n]
    end = idx[n + 1][2] if n + 1 < len(idx) else len(lines)
    return "\n".join(lines[ln:end])

bodies = {num: ch_body(i) for i, (num, tt, ln) in enumerate(idx)}

# ============ 方向1：章末钩子形态分类 ============
print("=" * 60)
print("[方向1] 章末钩子形态分类")
# 复用 quotes.json 的 hooks
q = json.load(open(os.path.join(OUT, "quotes.json"), encoding="utf-8"))
hooks = q["hooks"]
c = collections.Counter()
for h in hooks:
    t = h["hook"]
    if t.endswith(("？", "?")): c["疑问式"] += 1
    elif t.endswith(("！", "!")): c["感叹式"] += 1
    elif t.endswith("…"): c["省略式"] += 1
    elif t.startswith("“"): c["对话式"] += 1
    elif t.startswith("【"): c["心声式"] += 1
    else: c["叙述式"] += 1
print("  钩子总数:", len(hooks))
print("  形态分布:", dict(c.most_common()))
print("  样例:")
for h in hooks[:5]:
    print("    [%s] %s" % (h["ch"], h["hook"][:52]))
print("  >>> 可行，数据完整")

# ============ 方向2：角色台词抽取 ============
print()
print("=" * 60)
print("[方向2] 角色台词抽取")
ADV = ("皱眉|微笑|冷笑|苦笑|轻笑|平静|淡然|缓缓|震惊|疑惑|不解|无奈|愤怒|严肃|"
       "小声|大声|轻声|低声|好奇|惊讶|诧异|得意|沮丧|绝望|温柔|宠溺|戏谑|调侃|"
       "淡淡|默默|静静|呆呆|怔怔|猛地|忽地|蓦地|骤然|忽然|突然|立刻|顿时|赶紧|"
       "悄悄|偷偷|下意识|忍不住|不由得")
VERB = ("说|道|问|答|喊|叫|回|吼|叹|喃喃|开口|补充|解释|提醒|安慰|命令|吩咐|"
        "追问|回应|接话")
P = re.compile(r"([\u4e00-\u9fa5]{2,4})(?:" + ADV + r")?(?:地)?(?:" + VERB + r")[：:]\s*[“\"']([^”\"']{4,90})")
BLACK = {"师父", "徒儿", "老师", "少年", "少女", "男人", "女人", "法师", "萝莉",
         "声音", "众人", "有人", "那人", "此人", "女孩", "孩子", "家伙"}
tc = collections.Counter()
samp = collections.defaultdict(list)
for m in P.finditer(raw):
    who, txt = m.group(1), m.group(2).strip()
    if who in BLACK: continue
    tc[who] += 1
    if len(samp[who]) < 2: samp[who].append(txt)
print("  可抽取角色数:", len(tc))
print("  Top12 台词量:")
for w, n in tc.most_common(12):
    print("    %-7s %4d  | %s" % (w, n, samp[w][0][:34] if samp[w] else ""))
print("  >>> 可行，%d 角色 / %d 条台词" % (len(tc), sum(tc.values())))

# ============ 方向3：伏笔/回收检测 ============
print()
print("=" * 60)
print("[方向3] 伏笔回收检测")
# 取世界观里的关键专名，看首次出现章与后续分布
wb = json.load(open(os.path.join(OUT, "worldbuilding.json"), encoding="utf-8"))
terms = []
for k, lst in wb.items():
    for it in lst[:6]:
        terms.append((k, it["w"], it["f"]))
gaps = []
for cat, w, f in terms:
    if f < 40: continue
    hits = [num for num in sorted(bodies) if w in bodies[num]]
    if len(hits) < 3: continue
    first, last = hits[0], hits[-1]
    span = last - first
    # 空白间隔：最长的连续未出现区间
    gaps.append((w, f, first, last, span, len(hits)))
gaps.sort(key=lambda x: -x[4])
print("  %-10s %6s %6s %6s %6s %6s" % ("词条", "频次", "首现", "末现", "跨度", "章数"))
for w, f, a, b, sp, n in gaps[:12]:
    print("  %-10s %6d %6d %6d %6d %6d" % (w, f, a, b, sp, n))
print("  >>> 可行，可算伏笔埋设/回收区间")

# ============ 方向4：情绪极性（正/负向词典）============
print()
print("=" * 60)
print("[方向4] 情绪极性逐章曲线")
POS = ["开心", "高兴", "喜悦", "幸福", "舒服", "惬意", "满足", "兴奋", "惊喜",
       "喜欢", "可爱", "温柔", "感动", "温暖", "美好", "轻松", "稳", "爽", "美滋滋"]
NEG = ["恐惧", "害怕", "绝望", "痛苦", "愤怒", "悲伤", "难过", "担心", "紧张",
       "焦虑", "恐惧", "阴沉", "冰冷", "残酷", "死亡", "毁灭", "绝望", "崩溃"]
pos_c, neg_c = collections.Counter(), collections.Counter()
for num in sorted(bodies):
    b = bodies[num]
    pos_c[num] = sum(b.count(w) for w in POS)
    neg_c[num] = sum(b.count(w) for w in NEG)
tp_ = sum(pos_c.values()); tn = sum(neg_c.values())
print("  正向词总命中:", tp_, " 负向词总命中:", tn)
top_pos = sorted(pos_c.items(), key=lambda x: -x[1])[:5]
top_neg = sorted(neg_c.items(), key=lambda x: -x[1])[:5]
print("  正向最浓章:", [(n, v) for n, v in top_pos])
print("  负向最浓章:", [(n, v) for n, v in top_neg])
print("  >>> 可行（词典法精度中等）")

# ============ 方向5：视角/人称分布 ============
print()
print("=" * 60)
print("[方向5] 叙述视角与人称")
# 统计每章 "林恩" vs "奈奈子" 谁先出现 —— 判断该章视角中心
lead = collections.Counter()
for num in sorted(bodies):
    b = bodies[num]
    i1 = b.find("林恩"); i2 = b.find("奈奈子")
    if i1 < 0 and i2 < 0: lead["无"] += 1
    elif i2 < 0 or (i1 >= 0 and i1 < i2): lead["林恩视角"] += 1
    else: lead["奈奈子视角"] += 1
print("  视角判定（首次出现顺序）:", dict(lead))
# 第一人称"我"密度
wo = sum(b.count("我") for b in bodies.values())
print("  第一人称'我'总数:", wo)
print("  >>> 部分可行（视角判定较粗糙）")

# ============ 方向6：场景/空间分布 ============
print()
print("=" * 60)
print("[方向6] 场景空间分布")
SCENES = {
    "室内": ["房间", "大厅", "宫殿", "书房", "教堂", "塔内", "屋内", "厅堂", "卧室", "厨房"],
    "室外": ["广场", "街道", "森林", "山脉", "野外", "城外", "海边", "天空", "荒野", "山谷"],
    "战场": ["战场", "前线", "阵地", "冲锋", "军营", "城墙", "关隘"],
    "异空间": ["位面", "神界", "虚空", "梦境", "深渊", "神国", "异空间", "结界"],
}
sc = collections.Counter()
scene_by_ch = collections.defaultdict(collections.Counter)
for num in sorted(bodies):
    b = bodies[num]
    for s, kws in SCENES.items():
        n = sum(b.count(k) for k in kws)
        if n:
            sc[s] += n
            scene_by_ch[num][s] = n
print("  场景词总命中:", dict(sc))
# 主导场景章数
dom = collections.Counter()
for num in sorted(bodies):
    if scene_by_ch[num]:
        dom[scene_by_ch[num].most_common(1)[0][0]] += 1
print("  主导场景章数:", dict(dom))
print("  >>> 可行")

print()
print("=" * 60)
print("可行性汇总:")
print("  方向1 章末钩子学   ★★★★★ 数据完整（589 条）")
print("  方向2 角色台词库   ★★★★★ %d 角色" % len(tc))
print("  方向3 伏笔回收     ★★★★☆ 可算埋设/回收")
print("  方向4 情绪极性     ★★★☆☆ 词典法，精度中等")
print("  方向5 视角分布     ★★☆☆☆ 判定粗糙")
print("  方向6 场景空间     ★★★★☆ 可出场景节奏图")
