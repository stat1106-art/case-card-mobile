# App 圖示原檔

- `01_silver_gold.png`：發包人 2026-10-23 選用的 App 圖示（銀金款），1024×1024 原檔，不覆蓋、不修改。
  SHA-256 4a4e4ebb31f3bc98b5958f4619d737505dd3f080d32db56132299e967f5ff039（與素材包 SHA256SUMS.txt 相同）。
- 同一素材包的其他 4 款沒有放進程式庫與網站。
- `build/build.py` 打包時從這張縮出 apple-touch-icon（180）、192、512；512 maskable 把原圖縮到 74%、外圍補背景色，
  讓機器人與「職災小卡」字樣都在 maskable 安全範圍（中心半徑 40% 的圓）內。
