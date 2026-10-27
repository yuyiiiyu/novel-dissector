# novel-dissector v1.0.0

发布日期：2026-10-27

## 包含

- `SKILL.md` — skill 主文件（装进 `.dsh/skills/novel-dissector/` 即可用）
- `dissect.py` — 参考实现骨架（python dissect.py <小说> <产出目录>）
- `README.md` — 说明
- `LICENSE` — MIT
- `.gitignore`
- `reference-scripts/` — 34 个实战脚本（来自真实拆解案例，供抄写法）

## 安装

把整个 `novel-dissector` 目录放进任一工作区的 `.dsh/skills/`：

```
<工作区>/.dsh/skills/novel-dissector/
├── SKILL.md
├── dissect.py
└── ...
```

重启 DSH 后生效（改 SKILL.md 内容不用重启）。

## 实测

《这个人明明很强却偏要坑萝莉师傅》132.6万字 / 589章：
8 个交互页 · 43 份数据 · 终检 ALL PASS。
