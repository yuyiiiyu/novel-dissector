# 一键发布到 GitHub

仓库已命名为 **`novel-dissector`**（直白、好搜、与功能完全对应）。

本地仓库已初始化并提交完毕：
- 42 个文件
- commit `c037ed5`
- 远端已配 `https://github.com/yuyiiiyu/novel-dissector.git`

---

## 为什么需要你给 token

这台机器上：
- ❌ `gh` CLI 没装
- ❌ SSH key 没有（`~/.ssh` 不存在）
- ❌ 凭据管理器里那条 GitHub 凭据已失效（实测 API 返回 401）

所以推送需要你提供一个 **Personal Access Token**。

---

## 方式 A：给我 token，我直接推（最快）

1. 打开 https://github.com/settings/tokens/new
2. 勾 **`repo`**（完整仓库权限）
3. 生成后把 token 发我
4. 我执行：

```powershell
cd "D:\aigc_pro\ai-video&draw\DeepSeek Harness\@ D Download 这个人明明很强却_2026-10-27\产出\novel-dissector-release"
git push -u origin main
```

（我会用 `https://<token>@github.com/...` 形式推，推完立刻把 remote 改回干净 URL）

---

## 方式 B：你自己推

```powershell
cd "D:\aigc_pro\ai-video&draw\DeepSeek Harness\@ D Download 这个人明明很强却_2026-10-27\产出\novel-dissector-release"
git push -u origin main
```

会弹 GitHub 登录窗，用你浏览器里已登录的账号授权即可。

---

## 方式 C：用 GitHub Desktop（最省事）

1. 打开 GitHub Desktop
2. `File` → `Add Local Repository`
3. 选 `...\产出\novel-dissector-release`
4. 点 `Publish repository`
5. Name 填 `novel-dissector`，勾掉 "Keep this code private" 就是公开
6. 点 Publish

---

## 仓库信息（已定好）

| 项 | 值 |
|---|---|
| 名称 | `novel-dissector` |
| 描述 | 把一本地 txt 长篇小说拆成结构化数据与交互可视化报告：18 维度、逐章量化、8 个离线 HTML 页面，并产出续写资产包。纯 Python 标准库 + 手写 SVG，零第三方依赖、无 CDN、断网可用。 |
| 可见性 | 公开 |
| License | MIT |
| Topics | `novel` `text-analysis` `nlp` `visualization` `writing` `skill` `python` `svg` |

## 推完之后（可选优化）

在仓库页面补 Topics：
`novel` `text-analysis` `web-novel` `visualization` `writing-assistant` `python` `svg` `no-dependencies`
