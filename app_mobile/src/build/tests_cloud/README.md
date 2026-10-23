# 雲端施工時用的測試（Chromium，模擬 iPhone）

把打包好的網站放在 `<serve>/repo/`（模擬 GitHub Pages 子目錄）後執行：
- `app_test.py <serve> <輸出>`：離線快取、11 張出圖與檢查、斷網出圖、外部連線紀錄。檔內的打包編號要改成要測的那一版。
- `paste_test.py <serve> <輸出> <士林案 json> <reference/expected_png>`：v0.3.0「貼上案例」驗收 (a)～(e)＋缺圖預設圖、存不住提示、刪除、iPhone SE 寬度。
- `overlap_check.py <app_test 輸出> <reference/expected_png>`：新第一版資訊列壓在右上圖上的那一條沒被圖蓋掉。
- `hero_test.py <serve> <輸出>`：每案情境圖在三個版型的位置（搭配 `testcases_v3` 打包）。

需要 `pip install playwright==1.56.0 pillow`；沒有 WebKit，iPhone Safari 的結果要真機確認。
