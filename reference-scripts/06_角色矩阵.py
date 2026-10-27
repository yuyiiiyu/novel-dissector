# -*- coding: utf-8 -*-
"""阶段3d：对话呼语硬证据 → 可信角色表 + 角色×章节共现矩阵 + 首次登场"""
import re, json, os, collections

SRC = r"D:\Download\这个人明明很强却偏要坑萝莉师傅 - 一条咸鱼c.txt"
OUT = r"D:\aigc_pro\ai-video&draw\DeepSeek Harness\@ D Download 这个人明明很强却_2026-10-27\产出\data"
raw = open(SRC, encoding="utf-8").read()
lines = raw.split("\n")

# ---------- 章节边界 ----------
CH = re.compile(r"^\s*第([0-9]+)章[\s　]*(.*)$")
idx = [(int(m.group(1)), m.group(2).strip(), i) for i, l in enumerate(lines)
       if (m := CH.match(l))]
idx.sort()
ch_ranges = []
for n, (num, title, ln) in enumerate(idx):
    end = idx[n + 1][2] if n + 1 < len(idx) else len(lines)
    ch_ranges.append((num, title, ln, end))

# ---------- 硬证据1：对话中的呼语 “XX， / “XX！ / “XX？ ----------
VOC = re.compile(r"[“\"']\s*([\u4e00-\u9fa5]{2,5})\s*[，,！!？?。…]")
# ---------- 硬证据2：X道：/X说：/X问： ----------
SAY = re.compile(r"([\u4e00-\u9fa5]{2,5})(?:皱眉|微笑|冷笑|苦笑|轻笑|平静|淡然|缓缓|急忙|连忙|兴奋|震惊|疑惑|无奈|愤怒|严肃|小声|大声|轻声|好奇|惊讶|得意|沮丧|绝望|温柔|戏谑|淡淡|默默|静静|猛地|忽然|突然|立刻|顿时|赶紧|悄悄|偷偷|下意识|忍不住)?(?:地)?(?:说|道|问|答|喊|叫|回|吼|叹|喃喃|开口|补充|解释|提醒|安慰|命令|吩咐|追问|回应)\s*[：:]")
# ---------- 硬证据3：X 的心声标记 【...X...】 里少见，改用 X「动作」主语 ----------
ACT = re.compile(r"([\u4e00-\u9fa5]{2,5})(?:伸[出手]|站起|坐下|转身|回头|抬[起头]|低[下头]|握紧|松开|眯[起眼]|皱[起眉]|张[开口]|咽[了口]|摇头|点头|摆手|挥手|后退|上前|靠近|跪下|倒下|飞出)")

voc = collections.Counter(); say = collections.Counter(); act = collections.Counter()
for m in VOC.finditer(raw):   voc[m.group(1)] += 1
for m in SAY.finditer(raw):   say[m.group(1)] += 1
for m in ACT.finditer(raw):   act[m.group(1)] += 1

# ---------- 噪声过滤 ----------
GENERIC = set("""
师父 师傅 徒儿 徒弟 老师 学生 师兄 师姐 师弟 师妹 师叔 师伯 师祖 老祖 祖宗 前辈 后辈 前辈
少年 少女 男人 女人 老头 老太 孩子 孩童 青年 中年 老人 病人 客人 主人 仆人 侍女 侍从 随从
法师 魔法师 巫师 术士 骑士 战士 刺客 弓手 牧师 祭司 神官 修女 圣女 教皇 主教 长老 执事 弟子
小子 丫头 姑娘 小子 家伙 混蛋 笨蛋 傻瓜 蠢货 废物 垃圾 恶心 变态 混账 王八 畜生 白痴
父亲 母亲 爸爸 妈妈 儿子 女儿 哥哥 姐姐 弟弟 妹妹 爷爷 奶奶 叔叔 阿姨 舅舅 外婆 外公
大人 殿下 陛下 小姐 阁下 公子 少爷 夫人 太太 老爷 老板 头儿 老大 兄弟 朋友 兄弟 姐妹
神明 神灵 主宰 大君 魔王 恶魔 魔鬼 妖精 精灵 矮人 巨人 巨龙 恶龙 魔兽 怪物 凶兽 野兽 动物
声音 气息 话语 眼神 目光 表情 脸色 面容 身体 双手 心脏 脑海 意识 灵魂 精神 力量 魔力 能量
时间 空间 世界 大陆 城市 王国 帝国 山脉 森林 海洋 河流 天空 大地 地面 房间 大厅 广场 街道
事情 问题 答案 结果 原因 方法 办法 机会 危险 死亡 生命 血液 眼睛 耳朵 嘴巴 鼻子 手指 脚步
他们 她们 它们 我们 你们 自己 别人 他人 某人 每人 任何 所有 大家 众人 有人 没人 那人 此人
突然 忽然 顿时 立刻 瞬间 马上 赶紧 连忙 急忙 悄悄 偷偷 缓缓 慢慢 逐渐 渐渐 猛然 骤然 蓦地
什么 怎么 为啥 多少 很多 太多 有些 每个 更多 最多 最少 不少 已经 正在 将要 当然 果然 居然
知道 明白 发现 感觉 觉得 以为 记得 想到 看到 听到 看见 听说 说话 回答 提问 继续 准备 开始
能够 可以 应该 必须 需要 想要 希望 喜欢 讨厌 害怕 担心 惊讶 震惊 疑惑 无奈 愤怒 高兴 开心
全身 双手 双眼 双眸 额头 脸上 嘴角 眉头 心中 心里 体内 脑中 口中 手上 身上 脚下 面前 身后
真的 假的 好的 行了 够了 算了 好吧 喂喂 那个 这个 这里 那里 这样 那样 如此 这样 怎样
林恩 奈奈子
""".split())

TAILBAD = set("着了地得起的过是在和有与就也都这那你我他她它们个为被把给对从到很更最再也又之而及其以于所上下中前后里外时后会能要来去出进回让使但还打做说问道答喊叫")

def ok(w):
    if len(w) < 2 or len(w) > 4:      return False
    if w in GENERIC:                  return False
    if w[-1] in TAILBAD or w[0] in TAILBAD: return False
    if re.search(r"[着了地得]", w):   return False
    if len(set(w)) == 1:              return False
    return True

score = collections.Counter()
for d, wt in ((voc, 3), (say, 3), (act, 1)):
    for w, f in d.items():
        if ok(w):
            score[w] += f * wt

# ---------- 归并别名（长名吃掉短名，如 "艾维儿" vs "维儿"） ----------
items = sorted(score.items(), key=lambda x: -x[1])
groups, used = [], set()
for w, f in items:
    if w in used: continue
    g = {"main": w, "score": f, "voc": voc.get(w, 0), "say": say.get(w, 0),
         "act": act.get(w, 0), "alias": []}
    for w2, f2 in items:
        if w2 == w or w2 in used: continue
        if len(w2) >= 2 and len(w) >= 2 and (w2 in w or w in w2):
            g["alias"].append({"w": w2, "f": f2}); used.add(w2)
    used.add(w); groups.append(g)

# ---------- 主角强制保留 ----------
for anchor in ["林恩", "奈奈子"]:
    if not any(g["main"] == anchor for g in groups):
        groups.insert(0, {"main": anchor, "score": 0, "voc": 0, "say": 0,
                          "act": 0, "alias": [], "anchor": True})

TOPN = 60
top = groups[:TOPN]
names = [g["main"] for g in top]

# ---------- 角色 × 章节矩阵 ----------
chunks = [(num, title, "\n".join(lines[a:b])) for num, title, a, b in ch_ranges]
matrix = {}
for g in top:
    w = g["main"]
    pat = re.compile(re.escape(w))
    row = {}
    for num, title, body in chunks:
        c = len(pat.findall(body))
        if c: row[num] = c
    matrix[w] = {"chapters": row, "total": sum(row.values()),
                 "span": len(row),
                 "first": min(row) if row else None,
                 "last": max(row) if row else None}
    g["total"] = matrix[w]["total"]
    g["span"] = matrix[w]["span"]
    g["first_ch"] = matrix[w]["first"]
    g["last_ch"] = matrix[w]["last"]
    # 首次登场上下文
    if matrix[w]["first"]:
        n = matrix[w]["first"]
        _, t, b = chunks[n - 1]
        i = b.find(w)
        g["debut"] = (b[max(0, i - 90):i + 90]).replace("\n", " ")

json.dump({"matrix": matrix, "characters": top},
          open(os.path.join(OUT, "role_matrix.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

with open(os.path.join(OUT, "roles.csv"), "w", encoding="utf-8-sig", newline="") as f:
    f.write("排名,角色,加权分,被称呼,说话,动作,总提及,覆盖章数,首现章,末现章,别名\n")
    for i, g in enumerate(top, 1):
        f.write('{},{},{},{},{},{},{},{},{},"{}"\n'.format(
            i, g["main"], g["score"], g["voc"], g["say"], g["act"],
            g.get("total", 0), g.get("span", 0), g.get("first_ch", ""),
            g.get("last_ch", ""), " / ".join(a["w"] for a in g["alias"])))

print(f"可信角色 Top{TOPN}：")
for i, g in enumerate(top, 1):
    print(f'{i:3d} {g["main"]:6s} 分{g["score"]:5d} 提{g.get("total",0):5d} 章{g.get("span",0):4d} '
          f'首{g.get("first_ch","")}-{g.get("last_ch","")} /' + "/".join(a["w"] for a in g["alias"]))
