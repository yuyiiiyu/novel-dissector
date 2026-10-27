# -*- coding: utf-8 -*-
"""阶段1：结构层扫描 —— 章节切分 / 字数 / 段落 / 对话 / 心声 / 端句"""
import re, json, os, collections

SRC = r"D:\Download\这个人明明很强却偏要坑萝莉师傅 - 一条咸鱼c.txt"
OUT = r"D:\aigc_pro\ai-video&draw\DeepSeek Harness\@ D Download 这个人明明很强却_2026-10-27\产出\data"
os.makedirs(OUT, exist_ok=True)

raw = open(SRC, encoding="utf-8").read()
lines = raw.split("\n")

# ---------- 元数据 ----------
head = raw[:1200]
meta = {}
for k in ["书名", "作者", "连载状态", "字数", "章节数", "书籍 ID", "阅读量"]:
    m = re.search(re.escape(k) + r"：(.+)", head)
    if m:
        meta[k] = m.group(1).strip()
m = re.search(r"【简介】\n(.+?)\n———", raw, re.S)
meta["简介"] = m.group(1).strip() if m else ""

# ---------- 章节切分 ----------
CH = re.compile(r"^\s*第([0-9]+)章[\s　]*(.*)$")
idx = []
for i, ln in enumerate(lines):
    mm = CH.match(ln)
    if mm:
        idx.append((int(mm.group(1)), mm.group(2).strip(), i))
idx.sort()
print("章节数：", len(idx))

# 正文起点：第一个"第1章"之后
first_ch_line = idx[0][2]

def clean_block(ls):
    """去掉分隔线、空行，返回段落列表"""
    ps, buf = [], []
    for l in ls:
        s = l.strip()
        if not s:
            if buf:
                ps.append(" ".join(buf)); buf = []
            continue
        if set(s) <= set("—-_=*·"):
            continue
        buf.append(s)
    if buf:
        ps.append(" ".join(buf))
    return ps

chapters = []
for n, (num, title, ln) in enumerate(idx):
    end = idx[n + 1][2] if n + 1 < len(idx) else len(lines)
    body_lines = lines[ln + 1:end]
    paras = clean_block(body_lines)
    text = "\n".join(body_lines)
    text_nc = re.sub(r"\s", "", text)
    # 去掉系统/心声标记后的纯叙述
    ch = {
        "num": num,
        "title": title,
        "line": ln,
        "end_line": end,
        "chars": len(text_nc),
        "paras": len(paras),
        "dialog": len(re.findall(r"“", text)),
        "inner": len(re.findall(r"【", text)),
        "sys": len(re.findall(r"【\s*叮", text)),
        "excl": text.count("！") + text.count("!"),
        "quest": text.count("？") + text.count("?"),
        "ellip": text.count("……"),
        "first": paras[0][:60] if paras else "",
        "last": paras[-1][:60] if paras else "",
    }
    ch["d_ratio"] = round(ch["dialog"] / max(ch["chars"], 1) * 1000, 2)
    chapters.append(ch)

json.dump({"meta": meta, "chapters": chapters},
          open(os.path.join(OUT, "chapters.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

# ---------- CSV ----------
with open(os.path.join(OUT, "chapters.csv"), "w", encoding="utf-8-sig", newline="") as f:
    f.write("章号,标题,字数,段落数,对话引号数,心声数,系统提示数,感叹号,问号,省略号,对话密度‰,首句,末句\n")
    for c in chapters:
        f.write("{},{},{},{},{},{},{},{},{},{},{},「{}」,「{}」\n".format(
            c["num"], c["title"], c["chars"], c["paras"], c["dialog"], c["inner"],
            c["sys"], c["excl"], c["quest"], c["ellip"], c["d_ratio"],
            c["first"].replace(",", "，"), c["last"].replace(",", "，")))

total = sum(c["chars"] for c in chapters)
print("正文总字数(去空白)：", total)
print("章均字数：", total // len(chapters))
print("最短/最长章：", min(chapters, key=lambda c: c["chars"])["num"], min(c["chars"] for c in chapters),
      "|", max(chapters, key=lambda c: c["chars"])["num"], max(c["chars"] for c in chapters))
print("心声总数：", sum(c["inner"] for c in chapters))
print("系统叮总数：", sum(c["sys"] for c in chapters))
print("对话引号总数：", sum(c["dialog"] for c in chapters))
print("元数据：", meta)
