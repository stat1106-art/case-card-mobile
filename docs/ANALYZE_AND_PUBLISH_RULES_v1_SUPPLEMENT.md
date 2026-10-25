# 分析並上架規則 v1｜補充說明

需求／裁定：發包人（2026-10-25）｜整理：Claude（雲端）
本檔補充並優先於 `ANALYZE_AND_PUBLISH_RULES_v1.md` 的對應條文；原檔不改。

## 1. 示意圖（取代第五章 `hero` 中 `photo` 的寫法）
- 每案填 `card.hero.hero_type`，從 14 類選一：overwork、fall、machine、traffic、chemical、electric、collapse、commute、construction、heat、disease、healthcare、stress、neutral。網站依類型自動配圖。
- **不填 `photo`**。`file` 照舊固定 `"overwork_night_desk.svg"`，`caption`「示意圖」，`origin` 照舊。
- 14 類都對不上時填 `neutral`，回報「待補：待補情境圖」。
- check.js 的 R05 提醒（照片未填或未指定示意圖種類）照列在回報裡，**不擋上架**。

## 2. 版型需要、但第五章沒列的欄位
App 三個版型還會讀下列欄位，漏填會在小卡上印出「undefined」。照士林案的寫法，從同一份分析的對應節次填，不新增分析裡沒有的內容：
- `result.notes`（第 5 節：利息、駁回、訴訟費用等補充說明）
- `result.flow` 的說明欄：`damage_label`、`fault_lines`、`after_label`、`offset_lines`、`final_label`（第 5 節）
- `facts_anchor`（第 2 節：事實時間基準，例如「發病前一個月」）
- `timeline.start`／`timeline.onset` 的 `label` 與 `text`（第 1、2 節）

## 3. 檔名（取代第七章第 2 點）
- **依上架工具現行命名**：`tools/ingest_gpt_replies.py` 產生的「法院代碼_年度_字別_號」，例如 `sldv_110_laosu_72`；`.json` 與 `.md` 同名。
- 已上架的士林案保留原名 `shilin_110_laosu_72`，不改。
- 與現有案例重複時不得覆寫，回報發包人決定。

## 4. 金額四捨五入
第五章 flow 寫「四捨五入到元」；電腦版出圖程式核對時，剛好 .5 元會用另一種進位方式，兩邊可能對不上。遇到剛好 .5 元的案件，回報裡寫明，不自行選邊。

## 5. 一次多件
一次最多 5 件，每件獨立判斷；一件不符合門檻、不適合版型或檢查沒過，只有那一件不上架，其他件照常，回報逐件寫明。

## 6. 上架前檢查的執行方式（第六章）
`node tools/card_check.js <小卡資料.json>`：照原樣載入網站上的 `platform/js/check.js`（不修改），在 Node 執行 `CardCheck.validate`；只補上網頁環境原本就有的網址解析（URL）。
