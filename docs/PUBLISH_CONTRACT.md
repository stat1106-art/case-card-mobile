# 自動上架合約（給找案例工具開發用）

需求／裁定：發包人｜整理：Claude（雲端）｜2026-10-25
內容規則以 `ANALYZE_AND_PUBLISH_RULES_v1.md` 與 `ANALYZE_AND_PUBLISH_RULES_v1_SUPPLEMENT.md` 為準；本檔只規定「怎麼推、推什麼、怎麼看結果」。

## 1. 整體流程
1. 工具產生案例檔，發包人在工具裡看過預覽。
2. 工具用發包人的 GitHub 權杖，把檔案推到 `stat1106-art/case-card-mobile` 的 **main** 分支。
3. GitHub Actions「自動上架（cases/）」自動執行：路徑檢查 → 案例資料夾檢查 → 打包 → check.js → 出圖測試 → App 回歸測試。**全部通過才部署**到 gh-pages；任何一關沒過，網站維持原狀。
4. 工具查詢這次推送的 Actions 結果，告訴發包人成功或失敗（第 6 節）。

## 2. 只能推這些檔（其他一律不行）
| 路徑 | 必要 | 說明 |
|---|---|---|
| `cases/<案例名>.json` | 必要 | 小卡資料（第 4 節） |
| `cases/<案例名>.md` | 選用 | 案例分析（第 5 節），平台「案例分析」頁會顯示 |
| `cases/index.json` | 必要 | 案例清單（第 3 節），由**工具**在同一次推送裡更新 |

- **推送只要動到 `cases/` 以外的任何檔案，Actions 會標示失敗、不部署。** 包含圖片（`hero_library/`）、程式、文件。示意圖的新圖要經維護人員走核准流程放上去，不經工具。
- 權杖技術上可以寫整個程式庫，限制靠 Actions 的路徑檢查；工具自己也要擋，只組 `cases/` 的變更。
- 一批案件建議一次提交、一次推送（一次推送只會跑一次檢查）。提交訊息自由寫，建議「上架：案號…」。**不要**在提交訊息寫 `[skip ci]`（會跳過檢查，也就不會部署）。

## 3. 命名與案例清單
- **案例名**：依上架工具現行命名「法院代碼_年度_字別_號」，全部小寫英文、數字、底線。
  - 法院代碼＝`source.jid` 第一段轉小寫（例：`KLDV` → `kldv`）。
  - 字別對照：勞訴 laosu、勞上 laoshang、勞上易 laoshangyi、勞簡 laojian、勞小 laoxiao、重勞訴 zhonglaosu、勞再 laozai、勞抗 laokang、勞簡上 laojianshang、勞訴更 laosugeng；其他字別先問維護人員。
  - 例：基隆地院 115 年度勞訴字第 7 號 → `kldv_115_laosu_7`。已上架的士林案保留舊名 `shilin_110_laosu_72`。
  - `.json` 與 `.md` 同名；不得以 `test`、`fixture`、`sample` 開頭或含這些字段（Actions 會擋）。
- **不得覆寫既有案例**：推送前工具要先確認 `cases/<案例名>.json` 不存在；已存在就停下來讓發包人決定（Actions 不擋「更新既有案例」，所以這一關在工具）。
- **`cases/index.json`** 格式固定：
  ```json
  {"cases": ["kldv_115_laosu_7.json", "shilin_110_laosu_72.json"]}
  ```
  只列 `.json` 檔名、不重複、建議依字母排序。新增案例時加進去，撤回時拿掉。**清單必須和 `cases/` 裡的 .json 完全一致**（多列、漏列都會擋）。

## 4. 小卡資料 `.json`（必填欄位）
以網站上士林案的結構為準；版型三種都會讀這些欄位，漏填會印出「undefined」或檢查不過。

**最外層**：`format`（固定 `"case-card-app-case"`）、`schema_version`（1）、`title`、`source`、`card`
- `source`：`court`、`case_number`、`decision_date`（`YYYY-MM-DD`）、`jid`、`url`（司法院網址，無則空字串）

**card**
- `title`（2 行陣列）、`subtitle`（2 行陣列）、`tags`（2 個）
- `info`：`cause`、`date_pending`（true／false）
- `parties.plaintiff`／`parties.defendant`：`role`、`name`、`natural_person`
  - **自然人 `name` 一律寫遮好的「姓＋○○」**（例：`王○○`、複姓 `歐陽○○`、冠夫姓 `李林○○`）；公司、機關寫全名。
- `display`：`mask_natural_person_name`（有自然人就 true）；`keep_together`（選用）
- `basics`：4 列 `[標籤, 內容]`，順序固定：職務、時間、月薪或計算基礎、傷病或事故
- `relation`：`claim{label, note}`、`offset{label, amount, note}`、`court{role, name}`、`order{label, amount}`
- `facts`：最多 5 點 `{text, icon}`；`icon` 從 overtime、newhire、event、course、phone、check 選
- `facts_anchor`：事實時間基準（例「發病前一個月」）
- `timeline`：`start{date, label, text}`、`onset{date, label, text}`（日期 `YYYY/MM/DD`，未知寫「尚待確認」）
- `result`：`total`、`lines`（最多 4 行）、`notes`、`pending`、`flow{damage_label, damage_total, fault_op, fault_lines[], after_label, after_fault, offset_op, offset_lines[], final_label}`
  - 無過失相抵：`fault_op` 寫「× 100%（無過失相抵）」；無抵充：`offset_op` 寫「− 0 元」、`offset_lines` 寫「本案無抵充」。
- `sum_checks`（每步 `{parts, total}`）、`immutable_checks`（圖卡上所有數字與日期的原文字串）
- `holdings`：4 點 `{issue, head, body}`；`advisory`：4 點 `{head, body}`；`advisory_icons` 固定 `["search","group","bell","ledger"]`
- `source_card`：`name`「司法院裁判書查詢系統」、`url`、`how`「輸入案號查詢」
- `disclaimer`：固定文字（見規則第五章）
- `hero`：`file` 固定 `"overwork_night_desk.svg"`、**`hero_type` 必填**（overwork、fall、machine、traffic、chemical、electric、collapse、commute、construction、heat、disease、healthcare、stress、neutral 選一；對不上填 neutral）、`caption`「示意圖」、`origin`；**不填 `photo`**；`image` 只能填 `hero_library/` 裡已核准的圖
- `source_refs`、`not_on_card`（依規則第五章）

**Actions 會檢查**：格式、`hero_type`、自然人姓名（`parties` 與全文）、check.js「必須修正」0 項（提醒不擋）、三個版型都「檢查全部通過」（字太多爆框會擋）。

## 5. 案例分析 `.md`
- UTF-8 純文字 Markdown，結構照規則第二章（標題、四行引言、1～16 節、圖卡門檻結論）。
- **所有自然人姓名遮成「姓＋○○」**（原告、被告、證人、家屬、醫師、主管都算；公司、機關、法院不遮；判決原本已匿名的照原樣）。
- 不得放判決全文原稿、找案例工具的交接檔。
- 同一案多位同姓當事人時，用「原告一／被告一／死者」等稱呼區分。
- Actions 會掃描「稱謂＋人名」型態的沒遮姓名；**沒有稱謂在前的人名掃不到**，工具預覽時要請發包人逐份看過。

## 6. 推送後怎麼知道成功或失敗
- 權杖需有 **Actions：唯讀**。推送後用這次提交的 sha 查：
  `GET https://api.github.com/repos/stat1106-art/case-card-mobile/actions/runs?head_sha=<sha>`
  - `status`：`queued`／`in_progress`／`completed`；`conclusion`：`success`／`failure`。
  - 一次完整檢查約 5～10 分鐘；建議每 30 秒查一次，最多等 20 分鐘。
- **成功**：Actions 已把網站推到 gh-pages，GitHub Pages 再花 1～2 分鐘上線。可再讀 `https://stat1106-art.github.io/case-card-mobile/version.json`，`build` 變成新的編號即已上線。
- **失敗**：網站維持原狀。執行紀錄的「打包與完整檢查」步驟會逐關印【通過】／【沒過】與原因（例如「自然人姓名沒遮好：'王小明'」）；工具可把執行頁網址（API 回傳的 `html_url`）給發包人看。修正後再推一次即可，不用撤回。
- 失敗的推送**檔案仍留在 main**（只是沒部署）。下一次推送會連同前次內容一起檢查，所以要先修好。

## 7. 撤回一件已上架的案例
1. 刪除 `cases/<案例名>.json` 與 `cases/<案例名>.md`。
2. 從 `cases/index.json` 拿掉該檔名。
3. 一次推送。Actions 檢查通過後重新部署，網站清單就不再有這一案；同仁的 App 重開後清單會更新（案例清單一律先抓網路上的最新版）。
- 注意：GitHub 的提交歷史仍看得到舊檔；若是個資問題需要從歷史徹底清除，請找維護人員。

## 8. 不要做的事
- 不推 `cases/` 以外的檔案；不改 `.github/`（權杖也不該有 Workflows 權限）。
- 不在提交訊息加 `[skip ci]`。
- 不覆寫既有案例（除非發包人明確決定更新）。
- 不放未遮蔽真名、判決全文原稿、測試假案例。
