# 手機 App 原始碼

- `fonts/`：手機用字型（woff2 子集），由 `tools/build_fonts.py` 產生。
- `js/engine/`：出圖引擎，照 `casecard/engine/` 的 Python 原始碼逐行改寫成 JavaScript。
  - `card.js`：案例 → 圖卡 HTML（組卡照 `verify_engine.py` 的 `build_card()`）。
  - `template_classic.js`、`template_light.js`、`template_standard.js`：三個版型。
  - `skins.js`：9 種風格的顏色角色、背景、裝飾、文字對比。
  - `icons.js`、`typography.js`、`common.js`：圖示、字型、共用小工具。

## 怎麼證明和電腦版一樣
1. `python tools/check_engine_parity.py`：同一份案例，JS 版和 Python 版產生的 HTML 逐字比對（不需要瀏覽器）。
2. `python tools/render_js_cards.py` 再 `python tools/compare_expected.py verify_out_js`：用 JS 版 HTML＋woff2 字型出圖，和標準答案逐點比對。

以上都在 Linux 的 Chromium 驗證；iPhone Safari 尚未驗證。
