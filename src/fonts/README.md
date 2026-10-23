# 手機用字型（自動產生，不要手改）

由 `python tools/build_fonts.py` 從 `casecard/assets/fonts/` 的原字型裁成子集、轉 woff2。

| 檔案 | 大小 | 字數 |
|---|---|---|
| NotoSansTC-VF.woff2 | 3.30 MB | 11,800 |
| NotoSerifTC-VF.woff2 | 4.68 MB | 11,800 |
| BarlowCondensed-Bold.woff2 | 0.04 MB | 全收 |
| BarlowCondensed-ExtraBold.woff2 | 0.04 MB | 全收 |

- 收字：教育部常用字＋次常用字、全形標點、CJK 符號、注音、英數與常用符號，以及案例、版型、畫面文字實際用到的字（清單見 `charset.txt`）。
- 教育部表內有、但原字型本身就沒有的 4 個字：㚷㮣叄嬎（出圖前的缺字檢查會擋下）。
- 驗證：把出圖程式改指向這些 woff2 跑士林案 11 張，和標準答案逐點完全相同（示意圖暫換那格除外）。
- 授權：SIL Open Font License 1.1（`OFL.txt`），裁子集屬授權允許的修改版。
