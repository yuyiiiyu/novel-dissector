# -*- coding: utf-8 -*-
"""接入⑥：统一导航 + 总览卡片 + 报告章节"""
import os, re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

WEB = r"D:\aigc_pro\ai-video&draw\DeepSeek Harness\@ D Download 这个人明明很强却_2026-10-27\产出"

NAV = [("可视化总览.html", "总览"),
       ("情感曲线.html", "① 情感曲线"),
       ("人物关系网.html", "② 关系网"),
       ("灌水高潮热力图.html", "③ 热力图"),
       ("语言指纹.html", "④ 语言指纹"),
       ("转折点分析.html", "⑤ 转折点"),
       ("叙事工程学.html", "⑥ 叙事工程学")]

def build(cur):
    a = '<a href="可视化总览.html">总览</a>'
    rest = "".join('<a href="%s"%s>%s</a>' % (f, ' class="on"' if f == cur else "", t)
                   for f, t in NAV[1:])
    return ('<div class="nav">\n ' + a + "\n " + rest +
            '\n <a href="拆解总报告.md">📄 总报告</a>\n</div>')

for fn, _ in NAV:
    p = os.path.join(WEB, fn)
    h = open(p, encoding="utf-8").read()
    m = re.search(r'<div class="nav">.*?</div>', h, re.S)
    if not m:
        print("  skip(no nav):", fn); continue
    h = h.replace(m.group(0), build(fn), 1)
    open(p, "w", encoding="utf-8").write(h)
    print("  nav updated:", fn)

# ---- 总览加卡片 ----
p = os.path.join(WEB, "可视化总览.html")
h = open(p, encoding="utf-8").read()
if "叙事工程学.html" not in h:
    card = ''' <a class="card" href="叙事工程学.html">
  <div class="num">⑥</div>
  <div class="t">叙事工程学</div>
  <div class="d">断章钩子形态学（589 条）· 角色音色表 · 伏笔埋设/回收甘特图 ·
  场景迁移堆叠图。四个可直接复用的工程维度。</div>
  <div class="kv"><span>589 钩子</span><span>142 台词</span><span>15 条伏笔</span></div>
 </a>
'''
    h = h.replace(' <a class="card" href="拆解总报告.md">', card + ' <a class="card" href="拆解总报告.md">', 1)
    open(p, "w", encoding="utf-8").write(h)
    print("  overview card added")
else:
    print("  overview already has card")

# ---- 报告补章节 ----
p = os.path.join(WEB, "拆解总报告.md")
h = open(p, encoding="utf-8").read()
if "九之五、叙事工程学" not in h:
    sec = """## 九之五、叙事工程学（新增）

### ① 章末钩子形态（589 章全部有钩子，无断章缺失）

| 形态 | 数量 | 占比 | 均长 |
|---|---|---|---|
| 对话式 | 201 | 34.1% | 22.1 字 |
| 叙述式 | 200 | 34.0% | 27.2 字 |
| 省略式 | 95 | 16.1% | **4.0 字** |
| 感叹式 | 47 | 8.0% | 16.8 字 |
| 心声式 | 41 | 7.0% | 28.3 字 |
| 疑问式 | 5 | 0.8% | 15.4 字 |

**省略式钩子均长仅 4 字**（如「“这是……”」「奈奈子：“？？？”」），
是作者最短促的断章手法 —— 用留白代替叙述。

### ② 角色音色表（142 条干净台词）

| 角色 | 条数 | 均长 | 叹号% | 问号% | 出现区间 |
|---|---|---|---|---|---|
| **林恩** | 86 | 28.7 | 17.4 | **27.9** | 1–580 |
| 神王 | 17 | 36.2 | 0.0 | 17.6 | 522–579 |
| **奈奈子** | 11 | 27.6 | **0.0** | **45.5** | 1–356 |
| 秩序神 | 8 | 26.6 | 12.5 | 25.0 | 275–450 |
| 爱丽丝 | 8 | 28.8 | 25.0 | 50.0 | 181–215 |
| 母神 | 4 | 54.8 | 0.0 | 0.0 | 444–455 |
| 堕落神 | 2 | **67.0** | 0.0 | 0.0 | 498 |

**林恩爱反问（27.9%），奈奈子更爱反问（45.5%）且从不感叹** —— 师徒是对呛式对话。
**堕落神均长 67 字**，是全书的长篇说教位。

### ③ 伏笔埋设 / 回收（最大空档）

| 词条 | 首现 | 末现 | 章数 | 最大空档 |
|---|---|---|---|---|
| **爱丽丝** | 176 | 581 | 40 | **200 章**（242→442） |
| **堕落神** | 180 | 584 | 69 | **192 章**（239→431） |
| 沉眠者 | 330 | 589 | 32 | 174 章（330→504） |
| 路西法 | 2 | 415 | 33 | 172 章（86→258） |
| 源妹 | 100 | 391 | 44 | 168 章（100→268） |
| 秩序神 | 83 | 560 | 125 | 165 章（91→256） |

### ④ 场景迁移

| 卷 | 室内 | 室外 | 战场 | 异空间 |
|---|---|---|---|---|
| 一 冬泉谷 | 34 | 49 | 16 | 87 |
| 三 战争爆发 | 45 | 31 | **72** | 23 |
| 五 教廷与深渊 | 13 | 25 | 57 | **499** |
| 八 弑神准备 | 11 | **4** | 14 | **456** |
| 九 终末之战 | 7 | 1 | 6 | 146 |
| 十 大结局 | **0** | 1 | 1 | 65 |

**第八卷室内仅 11、室外仅 4**，异空间 456 —— 人物从物理世界彻底退出。
第十卷室内归零，故事完全进入概念空间。
这与第 501 章转折（心声 −67%、战斗 +89%）完全咬合，是同一件事的三个面。

> 可视化：见 叙事工程学.html

---

## 十、这套拆解还能怎么继续挖"""
    h = h.replace("## 十、这套拆解还能怎么继续挖", sec, 1)
    open(p, "w", encoding="utf-8").write(h)
    print("  report section added")
else:
    print("  report already has section")
