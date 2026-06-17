<h1 align="center">GitHub PM</h1>

<p align="center">
  <a href="./README.md">English</a> | <a href="./README.zh.md"><strong>繁體中文</strong></a>
</p>

<p align="center">
  <a href="https://github.com/joneshong-skills/github-pm/stargazers"><img src="https://img.shields.io/github/stars/joneshong-skills/github-pm?style=flat-square" alt="GitHub Stars"></a>
  <a href="https://github.com/joneshong-skills/github-pm/blob/main/LICENSE"><img src="https://img.shields.io/github/license/joneshong-skills/github-pm?style=flat-square" alt="License"></a>
</p>

<p align="center">
  GitHub 專案管理工具 -- 以 GitHub Issues 為唯一事實來源的議題追蹤與工作流程自動化。
</p>

---

## 功能特色

- **議題生命週期管理** -- 透過自然語言建立、啟動、同步與關閉議題
- **藍圖轉議題流程** -- 自動從藍圖文件生成關聯議題
- **Worktree 整合** -- 啟動議題時自動建立分支與 worktree
- **進度同步** -- 透過 commit 引用與留言將進度推送至議題
- **優先順序建議** -- 根據專案狀態推薦下一個任務
- **專案儀表板** -- 依議題生命週期階段分組檢視專案狀態

## 使用方式

### 動作

透過自然語言觸發，而非斜線命令 -- 描述意圖，skill 便會經 `gh` CLI 執行對應動作。

| 動作 | 觸發語（範例）| 用途 |
|------|--------------|------|
| create | 「幫我建一個 issue」 | 從藍圖或描述建立議題 |
| list   | 「列出未結 issue」 | 列出未結議題（按狀態分組）|
| next   | 「下一個任務是什麼？」 | 建議下一個優先任務 |
| start  | 「開始處理 #42」 | 開始處理議題（worktree + 標籤）|
| sync   | 「同步進度到 #42」 | 推送進度更新至議題 |
| close  | 「關閉 #42 並附摘要」 | 以摘要關閉議題 |
| status | 「顯示專案儀表板」 | 專案儀表板 |

### 範例

```
「從 docs/plans/feature-x-blueprint.md 建立議題」

「開始處理議題 #42」

「同步我的進度到議題 #42」

「顯示專案狀態」
```

## 工作流程

```
待辦 --> 開啟 --> 進行中 --> 審查完成 --> 已關閉
```

1. **建立** -- 從藍圖或描述生成議題
2. **啟動** -- 選取議題，建立 worktree 與分支
3. **同步** -- 開發過程中推送進度更新
4. **關閉** -- 以摘要完成議題

## 整合

| 技能 | 關係 |
|------|------|
| `blueprint` | 給它一份藍圖即自動建立關聯議題 |
| `forge` | 每個 forge 階段對應議題生命週期 |
| `git-worktrees` | 分支命名：`feature/<slug>-#<number>` |
| `executor` | 每個階段完成時同步進度 |

自動化掛鉤：commit 訊息中的 `#N` 引用會自動在議題留言；工作階段啟動時載入未結議題至上下文。

## 安裝

```bash
# 複製到你的 Claude skills 目錄
cp -r github-pm/ ~/.claude/skills/github-pm/
```

**需求：** `gh` CLI（已認證）、Claude Code 搭配 `Bash` 工具。

## 授權

[MIT](./LICENSE)
