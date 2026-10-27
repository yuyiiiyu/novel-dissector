# -*- coding: utf-8 -*-
"""接入⑦：导航 + 总览卡片 + 报告章节"""
import os, re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

WEB = r"D:\aigc_pro\ai-video&draw\DeepSeek Harness\@ D Download 这个人明明很强却_2026-10-27\产出"

NAV = [("可视化总览.html", "总览"),
       ("情感曲线.html", "① 情感曲线"),
       ("人物关系网.html", "② 关系网"),
       ("灌水高潮热力图.html", "③ 热力图"),
       ("语言指纹.html", "④ 语言指纹"),
       ("转折点分析.html", "⑤ 转折点"),
       ("叙事工程学.html", "⑥ 叙事工程学"),
       ("章内工程学.html", "⑦ 章内工程学")]

def build(cur):
    a = '<a href="可视化总览.html">总览</a>'
    rest = "".join('<a href="%s"%s>%s</a>' % (f, ' class="on"' if f == cur else "", t)
                   for f, t in NAV[1:])
    return ('<div class="nav">\n ' + a + "\n " + rest +
            '\n <a href="拆解总报告.md">总报告</a>\n</div>')

for fn, _ in NAV:
    p = os.path.join(WEB, fn)
    h = open(p, encoding="utf-8").read()
    m = re.search(r'<div class="nav">.*?</div>', h, re.S)
    if not m:
        print("  skip:", fn); continue
    h = h.replace(m.group(0), build(fn), 1)
    open(p, "w", encoding="utf-8").write(h)
print("  nav updated (7 pages)")

p = os.path.join(WEB, "可视化总览.html")
h = open(p, encoding="utf-8").read()
if "章内工程学.html" not in h:
    card = ''' <a class="card" href="章内工程学.html">
  <div class="num">⑦</div>
  <div class="t">章内工程学</div>
  <div class="d">下沉到章内：节奏模板（段落位置 10 档）· 爽文三件套 ·
  对话轮次结构 · 开场方式。看作者怎么拼出一章。</div>
  <div class="kv"><span>13433 回合</span><span>章均 22.8</span><span>零对话 0 章</span></div>
 </a>
'''
    h = h.replace(' <a class="card" href="拆解总报告.md">', card + ' <a class="card" href="拆解总报告.md">', 1)
    open(p, "w", encoding="utf-8").write(h)
    print("  overview card added")
else:
    print("  overview has card")

p = os.path.join(WEB, "拆解总报告.md")
h = open(p, encoding="utf-8").read()
if "九之六、章内工程学" not in h:
    sec = """## 九之六、章内工程学（新增）

从"章"下沉到"章内"——作者如何用 100 多个短段落拼出一章。

### A · 章内节奏模板（段落位置 10 档，每千段落命中率）

| 位置 | 心声 | 对话 | 战斗 | 甜度 | 感叹 | 疑问 |
|---|---|---|---|---|---|---|
| 0-10% | 42.4 | 204.1 | 30.9 | 18.0 | 59.2 | 9.2 |
| 30-40% | 46.9 | 225.2 | 30.3 | 19.2 | **74.5** | 8.8 |
| 80-90% | 37.7 | 232.2 | 25.2 | 23.3 | 57.2 | 10.4 |
| **90-100%** | **50.1** | **271.1** | 29.1 | **23.1** | 58.4 | 9.5 |

**关键形状**：
- 对话在最后 10% 骤升到 **271**（全章最高）——用高密度对话收尾
- 心声在 90-100% 升到 **50.1**——章末心声是固定收尾手法
- 战斗在 80% 后下降（30.9→25.2），甜度一路爬升（18.0→23.3）
- **章末偏感情与对话，不偏打斗**

### B · 爽文三件套

全书命中：**震惊 1001 · 打脸 173 · 反转 2837**

**反转远超另两者**——这本书靠"转折"而非"打脸"驱动。

| 卷 | 震惊/章 | 打脸/章 | 反转/章 |
|---|---|---|---|
| 一 冬泉谷 | **3.50** | 0.33 | 5.68 |
| 四 东海·海王线 | 1.51 | 0.51 | 5.60 |
| 八 弑神准备 | 1.02 | **0.07** | 5.24 |
| 九 终末之战 | 0.93 | 0.23 | 3.87 |

第一卷震惊 3.50/章为全书最高（扮猪吃虎期）；第八卷打脸降到 0.07/章。
三件套最齐全的章：**第 376 章「那东西是不能拔的」**（震惊 9 / 打脸 5 / 反转 4）。

### C · 对话轮次结构

| 指标 | 值 |
|---|---|
| 总回合 | 13,433 |
| 章均 | **22.8** |
| 中位 | 23 |
| 最多单章 | 54（第 567 章） |
| 最少单章 | 3 |
| **零对话章** | **0** |

**589 章无一章零对话**——对话是绝对骨架。章均 22.8、中位 23，节奏高度模板化。

### D · 章首开场方式

| 方式 | 数量 | 占比 |
|---|---|---|
| **短句破题** | 266 | **45.2%** |
| **场景描写** | 241 | **40.9%** |
| 对话开场 | 36 | 6.1% |
| 心声开场 | 25 | 4.2% |
| 承接上章 | 21 | 3.6% |

短句破题 + 场景描写 = **86%**。
**首个说话人 98% 未标注**——作者几乎不用"XX道"开章，先给画面或短句再进对话。

> 可视化：见 章内工程学.html

---

## 十、这套拆解还能怎么继续挖"""
    h = h.replace("## 十、这套拆解还能怎么继续挖", sec, 1)
    open(p, "w", encoding="utf-8").write(h)
    print("  report section added")
else:
    print("  report has section")
