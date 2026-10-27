# -*- coding: utf-8 -*-
"""阶段3b：人物提纯 —— 只用「说话人/动作主语」硬证据，排除动词副词"""
import re, json, os, collections

SRC = r"D:\Download\这个人明明很强却偏要坑萝莉师傅 - 一条咸鱼c.txt"
OUT = r"D:\aigc_pro\ai-video&draw\DeepSeek Harness\@ D Download 这个人明明很强却_2026-10-27\产出\data"
raw = open(SRC, encoding="utf-8").read()

# ---------- 硬证据模式：X 施事 + 言说/心理动词 ----------
VERB = "(?:说|道|问|答|喊|叫|回|吼|怒|笑|叹|惊|愣|皱|摇|点|摆|挥|转|抬|低|闭|睁|看|望|盯|瞧|想|知|明白|发现|感觉|听到|看见|记得|以为|觉得|继续|补充|解释|提醒|安慰|命令|吩咐|自语|嘀咕|喃喃|沉默|开口|出声|反问|追问|回应|接话|插嘴)"
ADV = "(?:皱眉|微笑|冷笑|苦笑|轻笑|淡笑|傻笑|阴沉|平静|淡然|缓缓|缓慢|急忙|连忙|兴奋|激动|震惊|疑惑|不解|无奈|愤怒|认真|严肃|小声|大声|轻声|低声|好奇|惊讶|诧异|得意|失落|沮丧|绝望|兴奋|不安|恐惧|害怕|骄傲|自豪|温柔|宠溺|戏谑|调侃|玩味|悠悠|淡淡|默默|静静|呆呆|怔怔|猛地|忽地|蓦地|骤然|忽然|突然|立刻|顿时|立马|赶紧|赶忙|慌忙|匆忙|悄悄|偷偷|直直|死死|紧紧|缓缓地|慢慢地|轻轻地|深深地|长长地|下意识|忍不住|不由得|情不自禁)"

PATS = [
    # X 道：“...”
    re.compile(r"([\u4e00-\u9fa5]{1,5})(?:又|也|便|却|则|还|才|就|直接|立刻|马上|随即|继而|然后|同时)?(?:%s)?(?:地|的)?(?:对[^，。！？]{0,12})?%s[：:]?\s*[“\"']" % (ADV, VERB)),
    # “...”X 道
    re.compile(r"[”\"'][，,]?\s*([\u4e00-\u9fa5]{1,5})(?:%s)?(?:地|的)?%s" % (ADV, VERB)),
    # “...”X 道。
    re.compile(r"[”\"']\s*([\u4e00-\u9fa5]{1,5})(?:%s)?%s[。！？，,]" % (ADV, VERB)),
    # X：“...”
    re.compile(r"^[\s　]*([\u4e00-\u9fa5]{1,5})[：:]\s*[“\"']", re.M),
    re.compile(r"[。！？\n]\s*([\u4e00-\u9fa5]{1,5})[：:]\s*[“\"']"),
    # X 心中/心里/暗道
    re.compile(r"([\u4e00-\u9fa5]{1,5})(?:心[中里]|暗|内)[暗自]?(?:道|想|说|骂|叹)"),
    # X 的 X 动作：X伸手/X站起
    re.compile(r"([\u4e00-\u9fa5]{1,5})(?:伸[出手]|站起|坐下|转身|回头|抬[起头]|低[下头]|握紧|松开|眯起|皱起|张[开口]|闭上|咽|吞|咬|摇头|点头|摆手|挥手|迈步|后退|上前|靠近|离开|冲出|飞出|落下|倒下|跪下)"),
]

cnt = collections.Counter()
for p in PATS:
    for m in p.finditer(raw):
        w = m.group(1)
        cnt[w] += 1

# ---------- 噪声过滤 ----------
TAIL_BAD = "着了地得起的过是在和有与就也都这那你我他她它们个为被把给对从到很更最再也又之而及其以于所上下中前后里外时后会能要来去出进回让使但还把很"
def is_noise(w, f):
    if len(w) < 2 or len(w) > 4:
        return True
    if w[-1] in TAIL_BAD or w[0] in TAIL_BAD:
        return True
    if re.search(r"[着了地得]", w):
        return True
    if f < 25:
        return True
    # 单字重复
    if len(set(w)) == 1:
        return True
    return False

# 通用非人名黑名单词表
BLACK = set("""
众人 大家 有人 没人 那人 此人 其人 何人 谁人 一人 二人 三人 敌人 友人 敌人 亲人 家人 族人 众人
少年 少女 男人 女人 老头 老太 孩子 孩童 婴儿 青年 中年 老人 病人 客人 主人 仆人 侍女 侍从 随从
法师 魔法师 巫师 术士 骑士 战士 刺客 弓手 牧师 祭司 神官 修女 圣女 教皇 主教 长老 执事 弟子
师父 师傅 老师 学生 徒儿 徒弟 师傅 师兄 师姐 师弟 师妹 师叔 师伯 师祖 老祖 祖宗 祖先 后人
男人 女人 老公 老婆 父亲 母亲 爸爸 妈妈 儿子 女儿 哥哥 姐姐 弟弟 妹妹 爷爷 奶奶 叔叔 阿姨
声音 气息 话语 眼神 目光 表情 脸色 面容 身体 双手 心脏 脑海 意识 灵魂 精神 力量 魔力 能量
时间 空间 世界 大陆 城市 王国 帝国 山脉 森林 海洋 河流 天空 大地 地面 房间 大厅 广场 街道
前方 后方 上面 下面 里面 外面 旁边 中间 中央 远处 近处 对面 身后 面前 眼前 身上 手中 头顶
事情 问题 答案 结果 原因 方法 办法 机会 危险 死亡 生命 血液 眼睛 耳朵 嘴巴 鼻子 手指 脚步
神明 神灵 主宰 大君 魔王 恶魔 魔鬼 妖精 精灵 矮人 巨人 巨龙 恶龙 魔兽 怪物 凶兽 野兽 动物
他们 她们 它们 我们 你们 自己 别人 他人 某人 每个人 任何人 所有人 大部分 少数 多数 许多
林恩 奈奈子
""".split())

pool = collections.Counter()
for w, f in cnt.items():
    if is_noise(w, f) or w in BLACK:
        continue
    pool[w] = f

# ---------- 用 02 的候选词补充纯叙述中提到的人物 ----------
cands = json.load(open(os.path.join(OUT, "ngram_candidates.json"), encoding="utf-8"))
cf = {c["w"]: c["f"] for c in cands}
SURNAME_SET = set("林恩奈安德艾维爱德薇弗蕾雅莫莉丝蒂娜莎露茜安妮玛莉亚当夏娃约瑟路西法加百列米迦勒拉斐尔乌列雷蒙罗兰亚瑟兰斯洛高文凯文布莱恩查理亨利威廉理查爱德华乔治查尔斯")
for w, f in cf.items():
    if 2 <= len(w) <= 4 and f >= 30 and w not in BLACK and not re.search(r"[着了地得的是在和与就也都很更最]",
            w):
        if w not in pool:
            pool[w] = f
        else:
            pool[w] = max(pool[w], f)

# ---------- 归一 ----------
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

json.dump(groups[:200], open(os.path.join(OUT, "characters_clean.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
with open(os.path.join(OUT, "characters_clean.csv"), "w", encoding="utf-8-sig", newline="") as f:
    f.write("排名,主名,施事频次,别名\n")
    for i, g in enumerate(groups[:200], 1):
        f.write('{},{},{},"{}"\n'.format(i, g["main"], g["freq"],
                " / ".join(f'{a["w"]}({a["f"]})' for a in g["alias"])))

print("提纯后角色：", len(groups))
for i, g in enumerate(groups[:70], 1):
    print(f'{i:3d} {g["main"]}({g["freq"]}) ' + "/".join(a["w"] for a in g["alias"]))
