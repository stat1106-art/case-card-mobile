# 驗收結果 v0.2.0（打包編號 0559495b86，士林案三個版型都用 r9 照片）

## 這一版改了什麼（相對 0625d27372）
- 士林案 `card.hero.image` = `overwork_night_desk_photo.png`：新第一版、淺色、原版右上都用 r9 照片（置中裁成 503×290、JPEG 27KB）。
- r9 照片來源紀錄補齊：作者 GPT、日期 2026-07（發包人 2026-10-23 告知，只到月份）、案例、核准日期 2026-10-23。
- 有情境圖時不再收用不到的舊照片 PNG（200KB），離線快取仍是 47 個檔。

## 測過的項目（Chromium，模擬 iPhone 15）
| 項目 | 結果 |
|---|---|
| 11 張「檢查全部通過」；和標準答案比（右上那格 577–1080 × 0–290 排除）差>32 的像素 0.042%～0.064% | 通過 |
| 11 張右上那格與裁好的照片逐點相同 90.5%～92.1%，其餘是疊在照片上的「示意圖」標籤與草稿標記 | 通過 |
| 離線快取 47 個檔、斷網出圖、216 個請求全是本機 | 通過 |
| 電腦版出圖程式 verify_engine.py | 全部通過 |
| 來源紀錄缺作者與日期時（補齊前），正式打包停止並不留半成品 | 通過 |

**未驗證（NOT VERIFIED）**：iPhone Safari 上三個版型右上的照片與疊放。

---

# 驗收結果 v0.2.0（打包編號 0625d27372，新 App 圖示）

## 這一版改了什麼（相對 b4642fd6fa）
- App 圖示改用發包人選的 `01_silver_gold.png`（素材包 2026-10-23，SHA-256 4a4e4ebb…f039，與 SHA256SUMS.txt 相符）。1024 原檔保留在 `src/build/icon_source/`，不覆蓋；其他 4 款沒有放進程式庫與網站。
- 打包時縮出 apple-touch-icon（180）、icon-192、icon-512；icon-512-maskable 把原圖縮到 74%、外圍補背景色（原圖最外圈中位數色 #E3D5D2），交界 6% 漸層。原檔指紋不符就停止打包。
- maskable 安全範圍核對：最遠的看板下緣兩角在原圖離中心 0.505 倍邊長，縮到 74% 後為 0.374，在安全圓（0.400）內；檢查圖上疊紅色安全圈與模擬圓形裁切，機器人與「職災小卡」字樣都完整。

## 測過的項目（Chromium，模擬 iPhone 15）
離線快取 47 個檔（含 4 個新圖示）、版本號 0625d27372、11 張「檢查全部通過」、斷網出圖、216 個請求全是本機：**全部通過**。

**未驗證（NOT VERIFIED）**：iPhone 主畫面上新圖示的實際樣子。

---

# 驗收結果 v0.2.0（打包編號 b4642fd6fa，每案情境圖）

## 這一版改了什麼（相對 e12ba92000）
- 案例檔 `card.hero.image` 可放每一案自己的情境圖，三個版型都用；沒給就照舊（新第一版、淺色用 SVG 插畫，原版用 r9 照片）。做法、欄位見 `HERO_IMAGES.md`。
- 疊圖沿用 r9 做法：整張畫完後再把圖畫到右上那一格，最後疊回「示意圖」標籤與草稿標記。
- 打包：只收案例有用到的圖；來源紀錄缺 `case`／`author`／`date`／`approved_date`（照片至少要有 `approved_date`）就停止並刪掉半成品。情境圖裁成 503×290、存 JPEG。
- r9 照片的來源紀錄補上 `case`、`approved_date: 2026-10-23`（作者、畫圖日期原紀錄沒有，沒有補）。

## 測過的項目（Chromium，模擬 iPhone 15）
| 項目 | 結果 |
|---|---|
| 測試圖（1600×900 合成圖）× 新第一版、淺色、原版：右上那格與裁好的圖逐點相同的比例 92.0%／92.0%／90.6%，其餘是壓在上面的標籤與草稿標記；三張都「檢查全部通過」 | 通過 |
| 測試圖打包後 10KB（503×290 JPEG） | 通過 |
| 沒給圖的士林案三個版型照舊（插畫／插畫／照片） | 通過 |
| 來源紀錄沒有核准日期、日期格式錯、沒有來源紀錄：打包停止（結束碼 1）、不留輸出資料夾 | 通過 |
| 正式版 11 張「檢查全部通過」，和標準答案差>32 的像素 0.043%～0.064%（與 e12ba92000 相同） | 通過 |
| 離線快取 47 個檔、斷網出圖、216 個請求全是本機 | 通過 |

**未驗證（NOT VERIFIED）**：iPhone Safari 上情境圖、照片與標籤疊放的樣子。

---

# 驗收結果 v0.2.0（打包編號 e12ba92000，原版右上恢復照片）

## 這一版改了什麼（相對 550191349a）
- **照片放回**：r9 深夜辦公桌情境圖 `overwork_night_desk_photo.png`（SHA-256 0cfc7be5…8f18，與來源紀錄一致）由發包人 2026-10-23 同意沿用、可公開；來源紀錄狀態改為「發包人 2026-10-23 同意沿用」。照片與來源紀錄回到 `hero_library/`、網站與離線快取。
- **原版右上照片的畫法**（`js/render.js`）：不再把圖嵌進 SVG（Safari 會漏畫）。存圖時版面上留同大小的空位，整張小卡畫完後再把照片直接畫到畫布右上那一格（照 object-fit: cover 置中裁切），最後把草稿標記單獨疊上去，維持「標記壓在照片上」。
- 新第一版、淺色版維持直接寫進版面的 SVG 插畫，沒有改。
- 標準答案 `standard_original.png` 還原為原始含照片的版本，**不再排除任何區域**。
- 檢查沒過時，結果下方多一個收合的「給維護人員看的詳細資料」（瀏覽器版本、超出的字與超出量），平常不展開。
- 沿用 550191349a 的新 App 圖示。

## 這一版重新測過的項目
| 項目 | 結果 |
|---|---|
| 電腦版出圖程式（Python）11 張，和標準答案逐點比對（含原版照片） | 逐點完全相同 |
| 手機程式（Chromium，模擬 iPhone 15）11 張都「檢查全部通過」 | 通過 |
| 手機程式 11 張和標準答案比，差>32 的像素 | 0.043%～0.064%，無換行不同、無少字 |
| 原版右上那格（照片＋草稿標記，503×290） | 只有 4 個點差>32（標記字邊緣），照片部分完全相同 |
| 離線快取 47 個檔裝好（含照片）、斷網後出圖（原版、新第一版 style3）、216 個請求全是本機 | 通過 |

**未驗證（NOT VERIFIED）**：iPhone Safari 上原版右上照片與草稿標記；550191349a 時真機原版出現的「有文字超出所屬的框」（Chromium 重現不出來，這一版可展開詳細資料查看是哪段字）。

---

# 驗收結果 v0.2.0（打包編號 550191349a）

## 這一版改了什麼（相對 4baa43bd62）
- **原版右上示意圖在 iPhone 存下來的圖裡是空白**（發包人真機回報）。原因判斷：Safari 把小卡轉成圖片時，不畫用 `<img>` 放進來的圖。佐證：88c1d6ba48 的 WebKit 模擬裡，原版那張差>32 的像素有 6.09%（其他 10 張 1～3%），右上那格正好占整張 8.3%，當時照片很可能也沒畫出來。新第一版、淺色版的示意圖是直接寫進版面的 SVG，WebKit 模擬正常。
- 修法（`js/render.js`）：轉成圖片前，把原版右上的 `<img class="hero">` 換成直接寫進版面的 SVG，框的大小、位置照原樣式。Chromium 上改前改後逐點完全相同。
- **App 圖示重畫**（`build/build.py`）：原本四個大字擠在一起；改成深藍底＋白色小卡（黑標題條、內文線、紅色金額條、綠色勾），配色取自原版小卡，不放字（iPhone 會在圖示下方顯示「職災小卡」）。

## 這一版重新測過的項目（Chromium，模擬 iPhone 15，本機子目錄 `/repo/`）
離線快取 45 個檔裝好且無照片、版本號 550191349a、11 張都「檢查全部通過」、斷網出圖（原版、新第一版 style3）、216 個請求全是本機：**全部通過**。

**未驗證（NOT VERIFIED）**：iPhone Safari 上原版右上示意圖是否出現（雲端環境沒有 WebKit）；新圖示在 iPhone 主畫面上的樣子。請發包人真機確認。

---

# 驗收結果 v0.2.0（打包編號 4baa43bd62，示意圖暫換）

## 這一版改了什麼（相對打包編號 88c1d6ba48）
- **示意圖暫換**：照片 `overwork_night_desk_photo.png` 與 `overwork_night_desk_photo.provenance.json` 使用權尚未確認，已從 `dist/`、離線快取清單（`sw.js`）拿掉；`case-card-mobile` 程式庫的任何一次提交裡都沒有這兩個檔。
- 原版（standard）右上改用 `overwork_night_desk.svg`（`js/app.js`）；存圖時依副檔名用正確的圖片格式嵌入（`js/render.js`）。
- `build/build.py`：`hero_library` 只收 `.svg`；打包時若 `dist/` 或快取清單出現任何含 photo 的檔名就停止。
- 其餘檔案（版型、檢查、字型、圖示、風格、案例）與 88c1d6ba48 逐位元組相同。

## 標準答案比對方式
- `standard_original.png` 右上那格（x 577–1080、y 0–290，草稿標記也在這格裡）**比對時排除**，標準答案圖該格已蓋上「示意圖暫換／此格不比對」。其他 10 張照常全張比對。
- 遮罩定義在程式庫的 `reference/expected_png/compare_mask.json`。

## 這一版重新測過的項目（Chromium，模擬 iPhone 15 尺寸、像素比 3，本機子目錄 `/repo/`）
| 項目 | 結果 |
|---|---|
| 離線快取裝好 45 個檔、快取裡沒有照片、版本號顯示 4baa43bd62 | 通過 |
| 11 張出圖都「檢查全部通過」（新第一版 original 19 項、其他風格 20 項、淺色 18 項、原版 18 項） | 通過 |
| 11 張和標準答案比較，差>32 的像素 0.04%～0.06%（原版已排除示意圖那格），沒有換行不同、沒有少字 | 通過 |
| 斷網後重開、出圖（原版、新第一版 style3） | 通過 |
| 216 個請求全是本機，沒有任何照片請求 | 通過 |

**WebKit（Safari 核心）這一版沒有重測**：這裡的雲端環境沒有安裝 WebKit。下面 88c1d6ba48 的 WebKit 結果，除了原版右上那格以外的部分仍可參考；原版右上換成 SVG 後在 Safari 上的樣子**未驗證（NOT VERIFIED）**。真 iPhone 與真的 GitHub Pages 一樣沒測。

---

以下是上一版（打包編號 88c1d6ba48，含照片）的驗收紀錄，保留作對照。

## 驗收結果 v0.2.0（打包編號 88c1d6ba48）

測試方式：`dist/` 放在本機 `http://127.0.0.1:8811/repo/`（模擬 GitHub Pages 的子目錄），用 Playwright 1.56.0 的 WebKit（Safari 26.0 核心）模擬 iPhone SE、iPhone 15，另用 Chromium 對照。**沒有用真的 iPhone，也沒有真的部署到 GitHub Pages。** 證據都在 `/workspace/case_card_v02/evidence/`（下表簡稱 `evidence/`）。

| # | 項目 | 結果 | 證據 |
|---|---|---|---|
| 1 | 加入主畫面、全螢幕、有名稱和圖示 | **沒測**（要真的 iPhone＋GitHub Pages）。模擬只確認：manifest `display: standalone`、`start_url ./`、名稱「職災小卡」、圖示 192/512/maskable/apple-touch-icon 都在、Service Worker 有接管頁面 | `dist/manifest.webmanifest`、`dist/icons/`、`evidence/tests_*/results.json` 的 sw_controls_page |
| 2 | 飛航模式下清單、出圖、存照片 | **真機沒測**。模擬通過：WebKit（SE、15）第一次打開後把伺服器關掉，再重開 App → 清單、出圖（原版）、存照片都正常；Chromium 用離線模擬也通過。WebKit 測試工具的「離線模擬」會連 Service Worker 一起擋住、頁面打不開，所以 WebKit 改用關伺服器的方式 | `evidence/tests_*/02_offline.png`、`results.json` |
| 3 | 11 張和標準答案一致 | **模擬通過，真機沒測**。三種引擎 11 張都沒有換行不同、沒有少字；區塊位置、字型、顏色、裝飾一致，差異是字的反鋸齒和最多 5px 的位移（見下表） | `evidence/cards_*/*_sidebyside.png`、`summary.json` |
| 4 | 每張都跑完檢查、寫「檢查全部通過（○ 項）」，有 C05、L10 | **模擬通過**。新第一版 original 19 項、其他 8 種風格 20 項、淺色 18 項、原版 18 項（＝電腦版的項目＋規格要求的缺字檢查 G01） | `evidence/cards_*/summary.json`、`evidence/tests_*/04_result_classic_style3.png` |
| 5 | 爆框案例：檢查沒過＋白話說明，圖照樣顯示 | **模擬通過**：「檢查沒過（3 項）」：有文字超出所屬的框／文字太多，整張圖放不下／最底下的免責說明被擠出畫面；圖照原樣產生，沒有縮字刪字 | `evidence/tests_*/05_overflow.png`、`05_overflow_card.png` |
| 6 | 草稿預設打勾、免責文字 | **模擬通過**；取消勾選時檔名沒有「_草稿」、圖不同 | `evidence/tests_*/01_start.png` |
| 7 | 淺色／原版時風格選單變灰、固定原版、寫提示 | **模擬通過** | `evidence/tests_*/07_light_skin_greyed.png` |
| 8 | 存到照片的圖 1080×1620、和畫面上同一張 | **模擬通過**：分享出去的檔案和畫面上的圖 sha256 相同、1080×1620。iPhone 真正的分享選單（「儲存影像」）**沒測**；分享選單是用測試程式代替的。不支援分享時的全螢幕＋「長按圖片 → 加入照片」也測過 | `evidence/tests_*/08_shared.png`、`08_fallback_fullscreen.png` |
| 9 | index.json 加案例並重新部署，重開看得到；顯示版本號 | **GitHub Pages 沒測**。本機模擬通過：換成加了新案例、重新打包的版本後，重開 App 約 1.3 秒內版本號從 8c62725017 變成 19100e17df、新案例出現，之後離線也看得到 | `evidence/tests_*/09_after_update.png`、`results.json` |
| 10 | 壞檔標「這個案例讀不出來」，其他照常 | **模擬通過** | `evidence/tests_*/01_start.png` |
| 11 | 用到字型外字元：檢查沒過並列出缺的字 | **模擬通過**：「這幾個字字型裡沒有：𪚥䲜」，不出圖 | `evidence/tests_*/11_missing_glyph.png` |
| 12 | SE 和一般 iPhone 不用左右捲動、按鈕點得到 | **模擬通過**（SE 寬 320、15 寬 393 都沒有左右捲動；可點的地方高度都 ≥44px）。真機**沒測** | `evidence/tests_webkit_iphoneSE/`、`tests_webkit_iphone15/` |
| 13 | 台灣繁體、無大陸用語和工程術語 | **自己檢查過**（沒有找別人看） | `dist/index.html`、`dist/js/app.js` |
| 14 | 不連外部網址 | **本機通過**：整個測試流程 239 個請求全是 127.0.0.1。部署到 GitHub Pages 後的紀錄**沒測** | `evidence/14_network_log_webkit_iphone15.png`、`evidence/tests_*/network_log.txt` |

## 11 張對照數字
| 引擎 | 圖 | 畫面結果 | 差>32 的像素 | 平均差 | 換行不同 | 文字位置最大差(px) | 顯示＝存檔 |
|---|---|---|---|---|---|---|---|
| WebKit iPhone 15 | classic_original | 檢查全部通過（19 項） | 1.58% | 1.78 | 無 | 4 | 是 |
| WebKit iPhone 15 | classic_style1 | 檢查全部通過（20 項） | 2.56% | 2.46 | 無 | 4 | 是 |
| WebKit iPhone 15 | classic_style1_print | 檢查全部通過（20 項） | 1.97% | 2.02 | 無 | 4 | 是 |
| WebKit iPhone 15 | classic_style2 | 檢查全部通過（20 項） | 2.28% | 2.19 | 無 | 4 | 是 |
| WebKit iPhone 15 | classic_style3 | 檢查全部通過（20 項） | 3.13% | 2.33 | 無 | 4 | 是 |
| WebKit iPhone 15 | classic_style4 | 檢查全部通過（20 項） | 1.71% | 1.89 | 無 | 4 | 是 |
| WebKit iPhone 15 | classic_style5 | 檢查全部通過（20 項） | 0.87% | 1.48 | 無 | 4 | 是 |
| WebKit iPhone 15 | classic_style6 | 檢查全部通過（20 項） | 1.34% | 1.76 | 無 | 4 | 是 |
| WebKit iPhone 15 | classic_style7 | 檢查全部通過（20 項） | 1.28% | 1.83 | 無 | 4 | 是 |
| WebKit iPhone 15 | light_original | 檢查全部通過（18 項） | 1.29% | 1.54 | 無 | 4 | 是 |
| WebKit iPhone 15 | standard_original | 檢查全部通過（18 項） | 6.09% | 6.59 | 無 | 5 | 是 |
| WebKit iPhone SE | classic_original | 檢查全部通過（19 項） | 1.58% | 1.78 | 無 | 4 | 是 |
| WebKit iPhone SE | classic_style1 | 檢查全部通過（20 項） | 2.56% | 2.46 | 無 | 4 | 是 |
| WebKit iPhone SE | classic_style1_print | 檢查全部通過（20 項） | 1.97% | 2.02 | 無 | 4 | 是 |
| WebKit iPhone SE | classic_style2 | 檢查全部通過（20 項） | 2.28% | 2.19 | 無 | 4 | 是 |
| WebKit iPhone SE | classic_style3 | 檢查全部通過（20 項） | 3.13% | 2.33 | 無 | 4 | 是 |
| WebKit iPhone SE | classic_style4 | 檢查全部通過（20 項） | 1.71% | 1.89 | 無 | 4 | 是 |
| WebKit iPhone SE | classic_style5 | 檢查全部通過（20 項） | 0.87% | 1.48 | 無 | 4 | 是 |
| WebKit iPhone SE | classic_style6 | 檢查全部通過（20 項） | 1.34% | 1.76 | 無 | 4 | 是 |
| WebKit iPhone SE | classic_style7 | 檢查全部通過（20 項） | 1.28% | 1.83 | 無 | 4 | 是 |
| WebKit iPhone SE | light_original | 檢查全部通過（18 項） | 1.29% | 1.54 | 無 | 4 | 是 |
| WebKit iPhone SE | standard_original | 檢查全部通過（18 項） | 6.09% | 6.59 | 無 | 5 | 是 |
| Chromium | classic_original | 檢查全部通過（19 項） | 1.82% | 1.87 | 無 | 0 | 是 |
| Chromium | classic_style1 | 檢查全部通過（20 項） | 1.81% | 1.91 | 無 | 0 | 是 |
| Chromium | classic_style1_print | 檢查全部通過（20 項） | 1.87% | 1.97 | 無 | 0 | 是 |
| Chromium | classic_style2 | 檢查全部通過（20 項） | 1.89% | 2.03 | 無 | 0 | 是 |
| Chromium | classic_style3 | 檢查全部通過（20 項） | 1.93% | 2.05 | 無 | 0 | 是 |
| Chromium | classic_style4 | 檢查全部通過（20 項） | 1.84% | 1.85 | 無 | 0 | 是 |
| Chromium | classic_style5 | 檢查全部通過（20 項） | 1.73% | 1.68 | 無 | 0 | 是 |
| Chromium | classic_style6 | 檢查全部通過（20 項） | 1.84% | 1.86 | 無 | 0 | 是 |
| Chromium | classic_style7 | 檢查全部通過（20 項） | 1.8% | 1.83 | 無 | 0 | 是 |
| Chromium | light_original | 檢查全部通過（18 項） | 1.41% | 1.2 | 無 | 0 | 是 |
| Chromium | standard_original | 檢查全部通過（18 項） | 0.06% | 0.09 | 無 | 0 | 是 |

（「差>32」指 0–255 的顏色差超過 32 的像素占整張圖的比例；「文字位置最大差」是同一行字的上緣和電腦版相差幾 px。）

## 沒驗證的部分
- 真的 iPhone（Safari、加入主畫面、飛航模式、分享選單、照片 App）都沒有測，上面都是模擬。
- 沒有真的部署到 GitHub Pages。
- 模擬器的 WebKit 和 iPhone 上的 Safari 字型繪製可能有細微不同。
