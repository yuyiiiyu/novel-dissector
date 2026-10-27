# -*- coding: utf-8 -*-
"""阶段3-final：位置锚定的说话人/呼语硬证据 → 可信角色表 + 章节矩阵 + 首次登场"""
import re, json, os, collections

SRC = r"D:\Download\这个人明明很强却偏要坑萝莉师傅 - 一条咸鱼c.txt"
OUT = r"D:\aigc_pro\ai-video&draw\DeepSeek Harness\@ D Download 这个人明明很强却_2026-10-27\产出\data"
raw = open(SRC, encoding="utf-8").read()
NM = r"[\u4e00-\u9fa5]{2,5}"

# ===== 硬证据：全部要求"名字处于主语/呼语位置"，前后有强边界 =====
# E1 段首/句首呼语： "名字，" 或 "名字！" 或 "名字？" （引号刚打开）
E1 = re.compile(r"[“\"']\s*(%s)\s*[，,！!？?]" % NM)
# E2 引号后呼语带后缀： "名字啊/名字呢/名字吧/名字大人/名字小姐/名字师父
E2 = re.compile(r"[“\"']\s*(%s)(?:啊|呢|吧|嘛|哦|呀|大人|小姐|殿下|陛下|阁下|师父|老师|先生|兄弟|老弟|大哥|姐姐|妹妹)\s*[，,！!？。]" % NM)
# E3 说话人：句首/换行后 名字(副词)?(道|说|问|答...)
E3 = re.compile(r"(?:^|[。！？\n“”\"']\s*)(%s)(?:皱眉|微笑|冷笑|苦笑|轻笑|平静|淡然|缓缓|急忙|连忙|兴奋|震惊|疑惑|无奈|愤怒|严肃|小声|大声|轻声|好奇|惊讶|得意|沮丧|绝望|温柔|戏谑|淡淡|默默|静静|猛地|忽然|突然|立刻|顿时|赶紧|悄悄|偷偷|下意识|忍不住|又是|也是|便是|却是|则是|还是|才|就|直接|立刻|马上|随即|然后|同时)?(?:地)?(?:说|道|问|答|喊|叫|回|吼|叹|喃喃|开口|补充|解释|提醒|安慰|命令|吩咐|追问|回应)\s*[：:]" % NM)
# E4 引号前说话人：名字(副词)?言说动词 + “   （行首）
E4 = re.compile(r"^\s*(%s)(?:皱眉|微笑|冷笑|平静|淡然|缓缓|震惊|疑惑|无奈|愤怒|严肃|小声|大声|轻声|好奇|惊讶|温柔|淡淡|默默|静静|猛地|忽然|突然|立刻|顿时|赶紧|悄悄)?(?:地)?(?:说|道|问|答|喊|叫|回|吼|叹|喃喃|开口|补充|解释|提醒|安慰|命令|追问|回应)[：:]?\s*[“\"']" % NM)
# E5 反引号人称：……XX道。  （引号刚闭合）
E5 = re.compile(r"[”\"']\s*(%s)(?:皱眉|微笑|冷笑|平静|淡然|缓缓|震惊|疑惑|无奈|愤怒|严肃|小声|大声|轻声|好奇|惊讶|温柔|淡淡|默默|静静|猛地|忽然|突然|立刻|顿时)?(?:地)?(?:说|道|问|答|喊|回|叹|喃喃|补充|解释|追问|回应)[。！？，,]" % NM)

# ===== 黑名单：明确非人名的语法/通用词 =====
BLACK = set("""
没错 认真 微笑 低声 咬牙 啊嘞 大喝 颤抖 不好 不行 淡笑 瞪眼 摇头 放心 放心吧 哼唧 没事 没什么
淡漠 眨眼 抬头 既然 既然如此 住手 思索 沙哑 抱歉 各位 什么人 窃取 皱眉 闭眼 呆滞 嘟囔 原来
原来如此 可恶 救命 犹疑 傲娇 卧槽 笑呵呵 大吼 严肃 嘴角 嘴角一翘 深深 猛然 缓缓 平静 认真
林恩深深 林恩猛然 林恩平静 林恩缓缓 林恩微笑 林恩低声 林恩瞪眼 林恩摇头 林恩淡漠 林恩思索
林恩皱眉 林恩闭眼 林恩呆滞 林恩犹疑 林恩严肃 林恩认真 林恩大哥 林恩淡淡 林恩苦笑 林恩轻笑
师父 师傅 徒儿 徒弟 老师 学生 师兄 师姐 师弟 师妹 师叔 师伯 师祖 老祖 祖宗 前辈 后辈
少年 少女 男人 女人 老头 老太 孩子 孩童 青年 中年 老人 病人 客人 主人 仆人 侍女 侍从 随从
法师 魔法师 巫师 术士 骑士 战士 刺客 弓手 牧师 祭司 神官 修女 圣女 教皇 主教 长老 执事 弟子
小子 丫头 姑娘 家伙 混蛋 笨蛋 傻瓜 蠢货 废物 垃圾 恶心 变态 混账 畜生 白痴 狗徒儿 狗萝莉
父亲 母亲 爸爸 妈妈 儿子 女儿 哥哥 姐姐 弟弟 妹妹 爷爷 奶奶 叔叔 阿姨 舅舅 外婆 外公 大哥
大人 殿下 陛下 小姐 阁下 公子 少爷 夫人 太太 老爷 老板 头儿 老大 兄弟 朋友 姐妹 各位
神明 神灵 主宰 大君 魔王 恶魔 魔鬼 妖精 精灵 矮人 巨人 巨龙 恶龙 魔兽 怪物 凶兽 野兽 动物
声音 气息 话语 眼神 目光 表情 脸色 面容 身体 双手 心脏 脑海 意识 灵魂 精神 力量 魔力 能量
时间 空间 世界 大陆 城市 王国 帝国 山脉 森林 海洋 河流 天空 大地 地面 房间 大厅 广场 街道
事情 问题 答案 结果 原因 方法 办法 机会 危险 死亡 生命 血液 眼睛 耳朵 嘴巴 鼻子 手指 脚步
他们 她们 它们 我们 你们 自己 别人 他人 某人 每人 任何 所有 大家 众人 有人 没人 那人 此人
突然 忽然 顿时 立刻 瞬间 马上 赶紧 连忙 急忙 悄悄 偷偷 慢慢 逐渐 渐渐 骤然 蓦地
什么 怎么 为啥 多少 很多 太多 有些 每个 更多 最多 最少 不少 已经 正在 将要 当然 果然 居然
知道 明白 发现 感觉 觉得 以为 记得 想到 看到 听到 看见 听说 说话 回答 提问 继续 准备 开始
能够 可以 应该 必须 需要 想要 希望 喜欢 讨厌 害怕 担心 惊讶 震惊 疑惑 无奈 愤怒 高兴 开心
全身 双眼 双眸 额头 脸上 嘴角 眉头 心中 心里 体内 脑中 口中 手上 身上 脚下 面前 身后 族长
真的 假的 好的 行了 够了 算了 好吧 那个 这个 这里 那里 这样 那样 如此 怎样 怎么回事
""".split())

TAILBAD = set("着了地得起的过是在和有与就也都这那你我他她它们个为被把给对从到很更最再也又之而及其以于所上下中前后里外时后会能要来去出进回让使但还打做说问道答喊叫")

def ok(w):
    if len(w) < 2 or len(w) > 4:            return False
    if w in BLACK:                          return False
    if w[-1] in TAILBAD or w[0] in TAILBAD: return False
    if re.search(r"[着了地得]", w):          return False
    if len(set(w)) == 1:                    return False
    return True

ev = collections.Counter(); detail = collections.defaultdict(collections.Counter)
for name, pat, wt in (("呼语", E1, 4), ("称呼", E2, 4), ("说话", E3, 3),
                      ("行首说话", E4, 3), ("引后说话", E5, 2)):
    for m in pat.finditer(raw):
        w = m.group(1)
        if ok(w):
            ev[w] += wt; detail[w][name] += 1

# ===== 归并别名 =====
items = sorted(ev.items(), key=lambda x: -x[1])
groups, used = [], set()
for w, f in items:
    if w in used: continue
    g = {"main": w, "score": f, "ev": dict(detail[w]), "alias": []}
    for w2, f2 in items:
        if w2 == w or w2 in used: continue
        if len(w2) >= 2 and len(w) >= 2 and (w2 in w or w in w2):
            g["alias"].append({"w": w2, "f": f2}); used.add(w2)
    used.add(w); groups.append(g)

# ===== 主角锚点强制置顶（用真实全名频次） =====
for anchor in ["林恩", "奈奈子"]:
    if not any(g["main"] == anchor for g in groups):
        groups.insert(0, {"main": anchor, "score": 10**6, "ev": {}, "alias": [], "anchor": True})
groups.sort(key=lambda g: -g["score"])

TOPN = 50
top = groups[:TOPN]

# ===== 章节切分 & 角色×章节矩阵 =====
lines = raw.split("\n")
CH = re.compile(r"^\s*第([0-9]+)章[\s　]*(.*)$")
idx = [(int(m.group(1)), m.group(2).strip(), i) for i, l in enumerate(lines) if (m := CH.match(l))]
idx.sort()
chunks = []
for n, (num, title, ln) in enumerate(idx):
    end = idx[n + 1][2] if n + 1 < len(idx) else len(lines)
    chunks.append((num, title, "\n".join(lines[ln:end])))

matrix = {}
for g in top:
    w = g["main"]
    p = re.compile(re.escape(w))
    row = {num: len(p.findall(body)) for num, title, body in chunks if w in body}
    matrix[w] = {"ch": row, "total": sum(row.values()), "span": len(row),
                 "first": min(row) if row else None, "last": max(row) if row else None}
    g["total"] = matrix[w]["total"]; g["span"] = matrix[w]["span"]
    g["first_ch"] = matrix[w]["first"]; g["last_ch"] = matrix[w]["last"]
    if matrix[w]["first"]:
        num, title, body = chunks[matrix[w]["first"] - 1]
        i = body.find(w)
        g["debut"] = body[max(0, i - 100):i + 100].replace("\n", " ")

json.dump({"matrix": matrix, "characters": top},
          open(os.path.join(OUT, "role_matrix.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
with open(os.path.join(OUT, "roles.csv"), "w", encoding="utf-8-sig", newline="") as f:
    f.write("排名,角色,证据分,总提及,覆盖章数,首现章,末现章,证据构成,别名\n")
    for i, g in enumerate(top, 1):
        f.write('{},{},{},{},{},{},{},"{}","{}"\n'.format(
            i, g["main"], g["score"], g.get("total", 0), g.get("span", 0),
            g.get("first_ch", ""), g.get("last_ch", ""),
            " ".join(f'{k}:{v}' for k, v in g["ev"].items()),
            " / ".join(a["w"] for a in g["alias"])))

print(f"=== 可信角色 Top{TOPN} ===")
for i, g in enumerate(top, 1):
    print(f'{i:3d} {g["main"]:8s} 证据{g["score"]:5d} 提及{g.get("total",0):5d} '
          f'章{g.get("span",0):4d} 首{g.get("first_ch","")}-{g.get("last_ch","")} /'
          + "/".join(a["w"] for a in g["alias"]))
