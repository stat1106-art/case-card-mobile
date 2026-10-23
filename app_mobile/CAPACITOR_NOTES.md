# 第二階段：用 Capacitor 包成 iPhone App 的注意事項

`dist/` 已經照可包殼的方式做，原樣放進 Capacitor 的 `webDir` 就能跑。這一版**沒有實際包過**（包殼需要 Mac、Xcode 和 Node，第一階段規定不能用 Node）。

## 已經準備好的地方
- 全部用相對路徑（`./`），沒有寫死網址或子目錄。
- 不靠網址參數存狀態、不開新分頁、不用 `window.open`、沒有登入、沒有分析、不呼叫 AI。
- 沒有後端、沒有 CDN、沒有第三方程式庫；字型、風格、案例、示意圖都在 `dist/` 裡。
- 出圖完全在畫面裡做：HTML → 隱藏的 1080×1620 頁框 → SVG → canvas → PNG。

## 包殼時要處理的事
1. **Service Worker**：Capacitor 的 iOS WebView（`capacitor://localhost`）不支援 Service Worker。`app.js` 只在 `serviceWorker` 存在時才註冊，不支援時會略過；檔案本來就在 App 裡，離線照樣能用。
2. **存到照片**：WKWebView 裡 `navigator.share({files})` 可能不能用。不能用時 App 會改成全螢幕顯示圖片、寫「長按圖片 → 加入照片」。比較好的做法是加 `@capacitor/share` 或相簿外掛，把同一份 PNG（`window.__app.current.blob`）存進相簿，不要重畫。要在 `Info.plist` 加 `NSPhotoLibraryAddUsageDescription`。
3. **新增案例**：包成 App 後，`cases/` 跟著 App 一起發佈，加案例要重新出版 App；或改成從固定網址下載案例清單（這會變成要連網，需另外決定）。
4. **版本號**：畫面最下方顯示 `版本 0.3.0（打包編號）`，App 版本號請和它一致。
5. **字型**：每個粗細兩個檔，合計約 17MB，會讓 App 變大但不影響功能。
6. **貼上的案例**（v0.3.0）：存在 WebView 的 localStorage（key `pastedCases`）。iOS 在儲存空間不足時可能清掉 WebView 資料；包殼後若要保證不見，改存 App 自己的檔案（例如 `@capacitor/preferences` 或 Filesystem）。讀寫失敗時 App 已會改放記憶體並提示「這台手機存不住，關掉就不見」。
