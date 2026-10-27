# -*- coding: utf-8 -*-
"""阶段3c：人物终筛 —— 仅保留「说话人」硬证据 + 相邻字校验，产出可信角色表"""
import re, json, os, collections

SRC = r"D:\Download\这个人明明很强却偏要坑萝莉师傅 - 一条咸鱼c.txt"
OUT = r"D:\aigc_pro\ai-video&draw\DeepSeek Harness\@ D Download 这个人明明很强却_2026-10-27\产出\data"
raw = open(SRC, encoding="utf-8").read()

VERB = "(?:说|道|问|答|喊|叫|回|吼|怒|笑|叹|惊|愣|想|知|明白|发现|感觉|听到|看见|记得|以为|觉得|继续|补充|解释|提醒|安慰|命令|吩咐|喃喃|沉默|开口|反问|追问|回应)"
ADV = "(?:皱眉|微笑|冷笑|苦笑|轻笑|淡笑|平静|淡然|缓缓|急忙|连忙|兴奋|激动|震惊|疑惑|不解|无奈|愤怒|认真|严肃|小声|大声|轻声|低声|好奇|惊讶|诧异|得意|失落|沮丧|绝望|不安|恐惧|害怕|骄傲|自豪|温柔|宠溺|戏谑|调侃|玩味|悠悠|淡淡|默默|静静|呆呆|怔怔|猛地|忽地|蓦地|骤然|忽然|突然|立刻|顿时|立马|赶紧|赶忙|慌忙|悄悄|偷偷|直直|死死|紧紧|下意识|忍不住|不由得|情不自禁)"

# 唯一可信模式：X + 副词? + 言说动词 + 冒号/引号  或  引号 + X + 言说动词
PAT_A = re.compile(r"([\u4e00-\u9fa5]{1,5})(?:%s)?(?:地|的)?%s\s*[：:]\s*[\"'“]" % (ADV, VERB))
PAT_B = re.compile(r"[\"'”][，,]?\s*([\u4e00-\u9fa5]{1,5})(?:%s)?(?:地|的)?%s" % (ADV, VERB))
PAT_C = re.compile(r"[\"'”]\s*([\u4e00-\u9fa5]{1,5})(?:%s)?%s[。！？，,]" % (ADV, VERB))

cnt = collections.Counter()
for p in (PAT_A, PAT_B, PAT_C):
    for m in p.finditer(raw):
        cnt[m.group(1)] += 1

# 强噪声：以虚词/体标记结尾，或是高频副词
TAIL = set("着了地得起的过是在和有与就也都这那你我他她它们个为被把给对从到很更最再也又之而及其以于所上下中前后里外时后会能要来去出进回让使但还把把被让给对从向往拿用打做")
def noise(w):
    if len(w) < 2 or len(w) > 4:
        return True
    if w[-1] in TAIL or w[0] in TAIL:
        return True
    if re.search(r"[着了地得]", w):
        return True
    if len(set(w)) == 1:
        return True
    return False

BLACK = set("""众人 大家 有人 没人 那人 此人 其人 一人 二人 三人 敌人 友人 亲人 家人 族人
少年 少女 男人 女人 老头 老太 孩子 孩童 青年 中年 老人 病人 客人 主人 仆人 侍女 侍从 随从
法师 魔法师 巫师 术士 骑士 战士 刺客 弓手 牧师 祭司 神官 修女 圣女 教皇 主教 长老 执事 弟子
师父 师傅 老师 学生 徒儿 徒弟 师兄 师姐 师弟 师妹 师叔 师伯 师祖 老祖 祖宗 祖先 后人
老公 老婆 父亲 母亲 爸爸 妈妈 儿子 女儿 哥哥 姐姐 弟弟 妹妹 爷爷 奶奶 叔叔 阿姨
声音 气息 话语 眼神 目光 表情 脸色 面容 身体 双手 心脏 脑海 意识 灵魂 精神 力量 魔力 能量
时间 空间 世界 大陆 城市 王国 帝国 山脉 森林 海洋 河流 天空 大地 地面 房间 大厅 广场 街道
前方 后方 上面 下面 里面 外面 旁边 中间 中央 远处 近处 对面 身后 面前 眼前 身上 手中 头顶
事情 问题 答案 结果 原因 方法 办法 机会 危险 死亡 生命 血液 眼睛 耳朵 嘴巴 鼻子 手指 脚步
神明 神灵 主宰 大君 魔王 恶魔 魔鬼 妖精 精灵 矮人 巨人 巨龙 恶龙 魔兽 怪物 凶兽 野兽 动物
他们 她们 它们 我们 你们 自己 别人 他人 某人 每个人 任何人 所有人 部分 少数 多数 许多
突然 忽然 顿时 立刻 瞬间 马上 赶紧 连忙 急忙 悄悄 偷偷 缓缓 慢慢 逐渐 渐渐 猛然 骤然 蓦地
什么 怎么 为什么 多少 很多 太多 有些 所有 每个 任何 更多 最多 最少 不少 已经 正在 将要
知道 明白 发现 感觉 觉得 以为 记得 想到 看到 听到 看见 听说 说话 回答 提问 继续 准备 开始
能够 可以 应该 必须 需要 想要 希望 喜欢 讨厌 害怕 担心 惊讶 震惊 疑惑 无奈 愤怒 高兴 开心
全身 双手 双眼 双眸 额头 脸上 嘴角 眉头 心中 心里 体内 体内 脑中 口中 手上 身上 脚下
""".split())

pool = collections.Counter()
for w, f in cnt.items():
    if noise(w) or w in BLACK:
        continue
    if f < 20:
        continue
    pool[w] = f

# 用候选 ngram 补叙述中提及的名字（需频次高且不与动词词表撞）
cands = json.load(open(os.path.join(OUT, "ngram_candidates.json"), encoding="utf-8"))
for c in cands:
    w, f = c["w"], c["f"]
    if not (2 <= len(w) <= 4) or f < 40 or w in BLACK:
        continue
    if re.search(r"[着了地得的是在和与就也都很更最把被让给对从向往拿用打做出来去进回上下中前后里外]", w):
        continue
    if w in pool:
        continue
    pool[w] = f

items = sorted(pool.items(), key=lambda x: -x[1])
groups, used = [], set()
for w, f in items:
    if w in used:
        continue
    g = {"main": w, "freq": f, "alias": []}
    for w2, f2 in items:
        if w2 == w or w2 in used:
            continue
        if len(w2) >= 2 and len(w) >= 2 and (w2 in w or w in w2):
            g["alias"].append({"w": w2, "f": f2}); used.add(w2)
    used.add(w)
    groups.append(g)

TOP = 90
json.dump(groups[:TOP], open(os.path.join(OUT, "characters_final.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
with open(os.path.join(OUT, "characters_final.csv"), "w", encoding="utf-8-sig", newline="") as f:
    f.write("排名,主名,证据频次,别名,角色定位(待人工)\n")
    for i, g in enumerate(groups[:TOP], 1):
        f.write('{},{},{},"{}",\n'.format(i, g["main"], g["freq"],
                " / ".join(f'{a["w"]}({a["f"]})' for a in g["alias"])))

print("终筛角色：", len(groups))
for i, g in enumerate(groups[:TOP], 1):
    print(f'{i:3d} {g["main"]}({g["freq"]}) ' + "/".join(a["w"] for a in g["alias"]))
