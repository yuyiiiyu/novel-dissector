# -*- coding: utf-8 -*-
"""阶段3：人物抽取 —— 说话人模式 + 称谓模式，生成角色表与别名归一"""
import re, json, os, collections

SRC = r"D:\Download\这个人明明很强却偏要坑萝莉师傅 - 一条咸鱼c.txt"
OUT = r"D:\aigc_pro\ai-video&draw\DeepSeek Harness\@ D Download 这个人明明很强却_2026-10-27\产出\data"
raw = open(SRC, encoding="utf-8").read()

# ---------- A. 说话人抽取："XX道/说/问/喊/笑/..." 或 XX：“ ----------
SPEAK = re.compile(r"([\u4e00-\u9fa5]{1,6})(?:皱眉|微笑|冷笑|苦笑|轻笑|淡淡|缓缓|继续|立刻|急忙|连忙|兴奋|震惊|疑惑|无奈|愤怒|平静|认真|严肃|缓缓地|小声|大声)(?:地|的)?(?:说|道|问|答|喊|叫|回)")
SPEAK2 = re.compile(r"([\u4e00-\u9fa5]{1,6})[：:]\s*[“\"']")
SPEAK3 = re.compile(r"“[^”]{0,40}”[,，]?\s*([\u4e00-\u9fa5]{1,6})(?:说|道|问|答|喊|回|笑|补充|继续)")
SPEAK4 = re.compile(r"“[^”]{0,60}[？?！!][”\"]?\s*([\u4e00-\u9fa5]{1,6})(?:问道|问道。)")

cnt = collections.Counter()
for rgx in (SPEAK, SPEAK2, SPEAK3, SPEAK4):
    for m in rgx.finditer(raw):
        w = m.group(1)
        cnt[w] += 1

# ---------- B. 称谓/头衔 ----------
TITLE = re.compile(r"([\u4e00-\u9fa5]{2,6})(?:大人|殿下|陛下|小姐|阁下|长老|执事|教皇|圣女|魔女|大君|主宰|神明|老祖|尊者|神官|骑士长)")
titles = collections.Counter()
for m in TITLE.finditer(raw):
    titles[m.group(1)] += 1

# ---------- C. 候选词表（来自 02）做交叉验证 ----------
cands = json.load(open(os.path.join(OUT, "ngram_candidates.json"), encoding="utf-8"))
cf = {c["w"]: c["f"] for c in cands}

# 已知主干角色（人工锚点，来自抽样阅读）
SEED = {
    "林恩": "男主·法神穿越者·伪装学徒",
    "奈奈子": "萝莉师父·冬泉谷第七执事·暴风魔女",
}

# ---------- D. 过滤出像人名的词 ----------
NOISE = set("""已经 自己 什么 怎么 如果 虽然 但是 因为 所以 而且 然后 现在 顿时 猛然 突然 瞬间 立刻 缓缓
继续 开始 准备 进行 能够 可以 应该 必须 知道 告诉 想要 希望 喜欢 确实 依然 仍然 依然 彻底 完全
全部 周围 一起 一下 一个 这样 那样 这里 那里 此时 此刻 之后 之前 当中 其中 于是 不过 只是 还是
确实 当然 居然 竟然 甚至 几乎 稍微 越来越 越来越 直接 重新 再次 终于 刚刚 刚才 曾经 本来 原本
世界 元素 法则 领域 诅咒 命运 深渊 骑士 金币 脑袋 力量 魔法 魔兽 法师 魔法师 神明 神灵 主宰
徒儿 师父 师徒 弟子 老师 学生 孩子 少年 少女 男人 女人 老头 老太 家伙 人们 众人 大家 其他人
一个 两个 三个 什么 怎么 为什么 多少 很多 太多 有些 所有 每个 任何 更多 最多 最少 不少
冬泉谷 海王殿 紫罗兰 月儿兰 圣殿 教会 王国 帝国 城市 大陆 山脉 森林 森林 房间 大厅 广场
前方 后方 上面 下面 里面 外面 左边 右边 中间 中央 远处 近处 对面 身后 面前 眼前 身上 手中
时间 时候 事情 问题 答案 结果 原因 方法 办法 机会 危险 死亡 生命 灵魂 身体 血液 眼睛 声音
非常 特别 十分 极其 无比 真正 一样 不同 各种 许多 大量 众多 一些 一点 一半 全部 整个
声音 气息 光芒 火焰 冰霜 黑暗 光明 天空 地面 大地 海洋 河流 树木 花草 石头 金属
""".split())

SURNAME = "赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨朱秦尤许何吕施张孔曹严华金魏陶姜戚谢邹喻柏水窦章云苏潘葛奚范彭郎鲁韦昌马苗凤花方俞任袁柳酆鲍史唐费廉岑薛雷贺倪汤滕殷罗毕郝邬安常乐于时傅皮卞齐康伍余元卜顾孟平黄和穆萧尹姚邵湛汪祁毛禹狄米贝明臧计伏成戴谈宋茅庞熊纪舒屈项祝董梁杜阮蓝闵席季麻强贾路娄危江童颜郭梅盛林刁钟徐邱骆高夏蔡田樊胡凌霍虞万支柯昝管卢莫经房裘缪干解应宗丁宣贲邓郁单杭洪包诸左石崔吉钮龚程嵇邢滑裴陆荣翁荀羊於惠甄曲家封芮羿储靳汲邴糜松井段富巫乌焦巴弓牧隗山谷车侯宓蓬全郗班仰秋仲伊宫宁仇栾暴甘钭厉戎祖武符刘景詹束龙叶幸司韶郜黎蓟薄印宿白怀蒲邰从鄂索咸籍赖卓蔺屠蒙池乔阴鬱胥能苍双闻莘党翟谭贡劳逄姬申扶堵冉宰郦雍卻璩桑桂濮牛寿通边扈燕冀郏浦尚农温别庄晏柴瞿阎充慕连茹习宦艾鱼容向古易慎戈廖庾终暨居衡步都耿满弘匡国文寇广禄阙东欧殳沃利蔚越夔隆师巩厍聂晁勾敖融冷訾辛阚那简饶空曾毋沙乜养鞠须丰巢关蒯相查后荆红游竺权逯盖益桓公上官欧阳夏侯诸葛闻人东方赫连皇甫尉迟公羊澹台公冶宗政濮阳淳于单于太叔申屠公孙仲孙轩辕令狐钟离宇文长孙慕容鲜于闾丘司徒司空亓官司寇仉督子车颛孙端木巫马公西漆雕乐正壤驷公良拓跋夹谷宰父榖梁晋楚闫法汝鄢涂钦段干百里东郭南门呼延归海羊舌微生岳帅缑亢况后有琴梁丘左丘东门西门商牟佘佴伯赏南宫墨哈谯笪年爱阳佟第五言福"

def looks_name(w, f):
    if w in NOISE or len(w) < 2 or len(w) > 4:
        return False
    if f < 20:
        return False
    # 中文姓氏开头
    if w[0] in SURNAME:
        return True
    # 外语译名常见字组合（2-4字，无常见虚词）
    if re.fullmatch(r"[\u4e00-\u9fa5]{2,4}", w) and not re.search(
            r"[的了是在有和与就不也都这那我你他她它们个为被把给对从到过还很更最再也又之而及其以于所]", w):
        return True
    return False

pool = collections.Counter()
for w, f in cf.items():
    if looks_name(w, f):
        pool[w] = f
for w, f in cnt.items():
    if looks_name(w, f) and f >= 15:
        pool[w] = max(pool[w], f)
for w, f in titles.items():
    if looks_name(w, f) and f >= 10:
        pool[w] = max(pool[w], f)

# ---------- E. 别名归一：包含关系（长名包含短名且短名>=2） ----------
names = sorted(pool.items(), key=lambda x: -x[1])
groups = []
used = set()
for w, f in names:
    if w in used:
        continue
    grp = {"main": w, "freq": f, "alias": []}
    for w2, f2 in names:
        if w2 == w or w2 in used:
            continue
        if len(w2) >= 2 and (w2 in w or w in w2):
            # 只有当短名频次接近或更高才合并，避免误吞
            grp["alias"].append({"w": w2, "f": f2})
            used.add(w2)
    used.add(w)
    groups.append(grp)

groups.sort(key=lambda g: -g["freq"])

json.dump({"speakers": cnt.most_common(300),
           "titles": titles.most_common(200),
           "characters": groups[:120]},
          open(os.path.join(OUT, "characters.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

with open(os.path.join(OUT, "characters.csv"), "w", encoding="utf-8-sig", newline="") as f:
    f.write("排名,主名,词频,别名\n")
    for i, g in enumerate(groups[:120], 1):
        al = " / ".join(f'{a["w"]}({a["f"]})' for a in g["alias"])
        f.write(f'{i},{g["main"]},{g["freq"]},{al}\n')

print("角色候选：", len(groups))
for i, g in enumerate(groups[:60], 1):
    al = "/".join(a["w"] for a in g["alias"])
    print(f'{i:3d} {g["main"]}({g["freq"]}) {al}')
