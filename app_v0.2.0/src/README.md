# 原始檔與打包方式（只用 Python，不用 Node）

- `app_src/`：手機版畫面與程式（`index.html`、`app.css`、`js/engine.js` 版型與檢查、`js/render.js` 出圖、`js/app.js` 畫面流程、`sw.js` 離線快取、`manifest.webmanifest`）。
- `build/charset.py`：整理要放進字型的字（教育部常用字＋次常用字、全形標點、英數、所有案例與說明文件用到的字）。
- `build/build_fonts.py`：用 fontTools 把思源黑體／宋體做成各粗細的 woff2 子集（每個粗細拆成常用字、其他兩檔），Barlow 只留英數。
- `build/build.py 輸出資料夾 [--cases 案例資料夾]`：組出 `dist/`，並依內容換新的版本編號。路徑預設以本包上一層的 `src2/case_card_app_kit` 為原始套件，請依實際位置調整 `KIT`。
- `build/parity_html.py`：比對 JS 產生的 HTML 和 Python 原程式產生的 HTML（11 張逐字相同）。
- `build/evidence_cards.py`、`build/tests.py`：Playwright 對照與功能測試（需 `pip install playwright pillow fonttools brotli` 和 `playwright install webkit chromium`）。
- 第三方程式庫：無。

## 放進 case-card-mobile 程式庫後
- 打包好的網站（`dist/`）放在 **gh-pages** 分支的最上層，GitHub Pages 從那裡發布。
- 重新打包時：`build/build.py` 的 `KIT` 指向本程式庫根目錄（例如建一個 `src2/case_card_app_kit` 捷徑指到程式庫），`build/fonts_out/` 放 gh-pages 分支 `fonts/` 裡的 woff2 與 `fonts.json`。
- 示意圖暫換：`hero_library` 只收 `.svg`，照片不進網站（見 `../ACCEPTANCE.md`）。
