# 雲端施工時用的測試（Chromium，模擬 iPhone）

把打包好的網站放在 `<serve>/repo/`（模擬 GitHub Pages 子目錄）後執行：
- `app_test.py <serve> <輸出>`：離線快取、11 張出圖與檢查、斷網出圖、外部連線紀錄。檔內的打包編號要改成要測的那一版。
- `admin_test.py <serve> <輸出> <士林案 json> <reference/expected_png>`：v0.4.0 驗收——同仁畫面看不到貼上框、管理頁貼 GPT 回覆（含一段兩案、沒有小卡資料的提示）、僅本機案例 11 張出圖、重開還在、刪除、iPhone SE 寬度、斷網、存不住提示、外部連線。（取代 v0.3.0 的 paste_test.py）
- `overlap_check.py <app_test 輸出> <reference/expected_png>`：新第一版資訊列壓在右上圖上的那一條沒被圖蓋掉。
- `hero_test.py <serve> <輸出>`：每案情境圖在三個版型的位置（搭配 `testcases_v3` 打包）。

需要 `pip install playwright==1.56.0 pillow`；沒有 WebKit，iPhone Safari 的結果要真機確認。
