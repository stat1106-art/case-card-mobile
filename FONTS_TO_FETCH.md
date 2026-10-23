# 這包少了兩個字型檔（太大，附檔放不下）

缺的檔案要放回 `casecard/assets/fonts/`，檔名和檔案指紋（SHA-256）必須完全一樣：

| 檔名 | SHA-256 | 大小 |
|---|---|---|
| NotoSansTC-VF.ttf | 864727d210d54f2537bbe23b3a839436c3992af72de9322af5270897246bd44f | 11,941,968 bytes |
| NotoSerifTC-VF.ttf | 0077e18f57c6908f4a000969880940bdb0dad057c0e8d98b49dc364c3d1b09c6 | 16,851,596 bytes |

來源：Google／Adobe 的 Noto CJK 公開字型（SIL OFL 1.1，可自由散布），GitHub 上的 notofonts/noto-cjk 程式庫，Variable TTF 的繁中子集（Subset）版本。

做法：
1. 從公開來源下載，算 SHA-256，**一字不差**才能用。
2. 找不到一模一樣的檔案時，**停下來回報發包人**，不要換別的版本將就：字型版本不同，換行位置就可能不同，和標準答案圖對不上。發包人會另外把原檔上傳給你。
3. 放回去之後跑 `python verify_engine.py`，最後一行必須是「全部通過」。
