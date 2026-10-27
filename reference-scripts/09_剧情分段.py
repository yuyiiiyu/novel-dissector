# -*- coding: utf-8 -*-
"""阶段5：剧情分段 —— 关键词地标 + 角色活跃度 + 情绪曲线 → 自动分卷与节拍表"""
import re, json, os, collections

SRC = r"D:\Download\这个人明明很强却偏要坑萝莉师傅 - 一条咸鱼c.txt"
OUT = r"D:\aigc_pro\ai-video&draw\DeepSeek Harness\@ D Download 这个人明明很强却_2026-10-27\产出\data"
raw = open(SRC, encoding="utf-8").read()
lines = raw.split("\n")

CH = re.compile(r"^\s*第([0-9]+)章[\s　]*(.*)$")
idx = [(int(m.group(1)), m.group(2).strip(), i) for i, l in enumerate(lines) if (m := CH.match(l))]
idx.sort()
chs = []
for n, (num, title, ln) in enumerate(idx):
    end = idx[n + 1][2] if n + 1 < len(idx) else len(lines)
    chs.append({"num": num, "title": title, "body": "\n".join(lines[ln:end])})

# ===== 地标关键词（用于识别剧情阶段）=====
MARKS = {
    "冬泉谷·养成期": ["冬泉谷", "执事", "学徒", "魔力值", "测试", "大检", "师父", "徒儿"],
    "心声·反差笑点": ["心声", "心声？", "听到", "心声"],
    "系统·咸鱼升级": ["叮！", "咸鱼系统", "自动升级", "睡觉", "春梦", "力量点数"],
    "驱邪·外勤": ["驱邪", "恶魔", "魅魔", "仪式", "深渊"],
    "月儿兰城": ["月儿兰", "怪物", "恶龙", "恶龙mm"],
    "弑神主线": ["弑神", "弑杀神明", "神明", "神灵", "噶韭菜"],
    "紫罗兰大君": ["紫罗兰大君", "大君"],
    "海王线": ["海王", "海神", "海王殿", "大海"],
    "战争线": ["战争", "军团", "冲锋", "出征", "军团长", "敌袭"],
    "教会线": ["教廷", "极光教会", "教会", "圣女", "教皇", "圣安娜"],
    "深渊线": ["深渊", "魔君", "堕落神", "恶魔"],
    "轮回线": ["轮回", "因果", "时间", "命运"],
    "神王·终局": ["神王", "神格", "神界", "初诞者", "沉眠者", "无序", "秩序"],
    "结局": ["大结局", "终末", "未来等你"],
}

# ===== 每章计算 =====
rows = []
for c in chs:
    b = c["body"]
    row = {"num": c["num"], "title": c["title"], "chars": len(re.sub(r"\s", "", b))}
    for mk, kws in MARKS.items():
        row[mk] = sum(b.count(k) for k in kws)
    # 情绪代理指标
    row["感叹"] = b.count("！")
    row["疑问"] = b.count("？")
    row["心声"] = b.count("【")
    row["对话"] = b.count("“")
    row["战斗"] = sum(b.count(k) for k in ["攻击", "轰", "爆炸", "斩", "击杀", "斩杀", "碾压", "灭"])
    row["甜度"] = sum(b.count(k) for k in ["脸红", "害羞", "喜欢", "抱", "亲", "喜欢你", "媳妇", "老婆", "嫁"])
    rows.append(row)

# ===== 分卷：按 地标主信号 + 章节位置 硬切（10卷）=====
# 先找出每个地标的"主峰区间"
def peak(mk, lo, hi):
    best = None
    for r in rows:
        if lo <= r["num"] <= hi:
            if best is None or r[mk] > best[1]:
                best = (r["num"], r[mk])
    return best

VOLUMES = [
    (1,   60,  "第一卷 冬泉谷·咸鱼学徒",      "林恩伪装学徒，心声被师父听见，咸鱼系统开启"),
    (61,  130, "第二卷 驱邪外勤与月儿兰",      "随师父外出驱邪，展露实力，结识各方势力"),
    (131, 200, "第三卷 战争爆发·紫罗兰大君",   "身份逐渐暴露，卷入战争，大君身份浮出水面"),
    (201, 280, "第四卷 东海·海王线",           "前往东海，海神/海王线展开"),
    (281, 360, "第五卷 教廷与深渊",            "极光教会、深渊魔君势力登场"),
    (361, 440, "第六卷 秘源与轮回",            "秘源体系、轮回真相揭露"),
    (441, 500, "第七卷 神格之争",              "神格、神王体系介入"),
    (501, 545, "第八卷 弑神准备",              "多方势力集结，准备弑神"),
    (546, 575, "第九卷 终末之战",              "最终决战，秩序与无序的对抗"),
    (576, 589, "第十卷 大结局",                "尾声与收束"),
]

vol_stats = []
for lo, hi, name, desc in VOLUMES:
    sub = [r for r in rows if lo <= r["num"] <= hi]
    if not sub:
        continue
    v = {"name": name, "desc": desc, "range": f"{lo}-{hi}",
         "chapters": len(sub), "chars": sum(r["chars"] for r in sub)}
    for mk in MARKS:
        v[mk] = sum(r[mk] for r in sub)
    v["感叹"] = sum(r["感叹"] for r in sub)
    v["心声"] = sum(r["心声"] for r in sub)
    v["对话"] = sum(r["对话"] for r in sub)
    v["战斗"] = sum(r["战斗"] for r in sub)
    v["甜度"] = sum(r["甜度"] for r in sub)
    # 代表章：该卷内地标分最高的三章
    top = sorted(sub, key=lambda r: -sum(r[mk] for mk in MARKS))[:5]
    v["代表章"] = [f'{r["num"]}·{r["title"]}' for r in top]
    vol_stats.append(v)

json.dump({"volumes": vol_stats, "rows": rows},
          open(os.path.join(OUT, "plot_arc.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

with open(os.path.join(OUT, "volumes.csv"), "w", encoding="utf-8-sig", newline="") as f:
    f.write("卷,范围,章数,字数,感叹,心声,对话,战斗,甜度,说明,代表章\n")
    for v in vol_stats:
        f.write('{},{},{},{},{},{},{},{},{},{},"{}"\n'.format(
            v["name"], v["range"], v["chapters"], v["chars"], v["感叹"], v["心声"],
            v["对话"], v["战斗"], v["甜度"], v["desc"], " | ".join(v["代表章"])))

with open(os.path.join(OUT, "chapter_signals.csv"), "w", encoding="utf-8-sig", newline="") as f:
    f.write("章,标题,字数," + ",".join(MARKS.keys()) + ",感叹,疑问,心声,对话,战斗,甜度\n")
    for r in rows:
        f.write("{},{},{},".format(r["num"], r["title"], r["chars"])
                + ",".join(str(r[k]) for k in MARKS) + ","
                + ",".join(str(r[k]) for k in ["感叹", "疑问", "心声", "对话", "战斗", "甜度"]) + "\n")

print("=== 分卷统计 ===")
for v in vol_stats:
    print(f'{v["name"]}  [{v["range"]}]  {v["chapters"]}章 {v["chars"]}字  '
          f'心声{v["心声"]} 对话{v["对话"]} 战斗{v["战斗"]} 甜{v["甜度"]}')
    print(f'   代表章：{" | ".join(v["代表章"][:3])}')
