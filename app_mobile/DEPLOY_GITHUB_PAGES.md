# 把職災小卡放到 GitHub Pages（第一次做也看得懂）

> `stat1106-art/case-card-mobile` 程式庫已經放好了：網站在 **gh-pages** 分支的最上層。打開 GitHub Pages 時，第三節第 4 步的 Branch 請選 **gh-pages**、資料夾 **/(root)**。下面一、二節是自己另開存放區時才要做。

要放上網的只有 `dist` 資料夾裡的東西，不用安裝任何程式、不用打指令。

## 一、建一個存放區（第一次才要做）
1. 用瀏覽器打開 https://github.com ，登入。
2. 右上角按 **＋** → **New repository**。
3. **Repository name** 填一個英文名字，例如 `casecard`。
4. 選 **Public**（免費帳號的 GitHub Pages 要公開；內容只能放合成或公開判決資料）。
5. 按綠色的 **Create repository**。

## 二、上傳檔案
1. 在剛建好的存放區頁面，按 **uploading an existing file** 這幾個字（或 **Add file** → **Upload files**）。
2. 打開電腦裡解壓縮後的 `dist` 資料夾，**把資料夾裡面的全部東西**（`index.html`、`sw.js`、`fonts`、`cases` 等）一起拖進網頁的框裡。
   - 要拖「裡面的東西」，不是拖 `dist` 這個資料夾本身。拖完後，存放區最上層要看得到 `index.html`。
3. 等下面的檔案清單都跑完，按綠色的 **Commit changes**。

## 三、打開 GitHub Pages
1. 存放區上方按 **Settings**（齒輪）。
2. 左邊選單按 **Pages**。
3. **Source** 選 **Deploy from a branch**。
4. **Branch** 選 **main**，旁邊資料夾選 **/(root)**，按 **Save**。
5. 等 1～3 分鐘，重新整理這一頁，上面會出現 **Visit site** 和網址，例如 `https://你的帳號.github.io/casecard/`。

## 四、在 iPhone 加到主畫面
1. 用 **Safari** 打開上面的網址（要用 Safari，不要用 LINE 裡面的瀏覽器）。
2. 等清單出現（第一次會下載約 17MB 字型，請用 Wi-Fi）。
3. 按下方的 **分享**（方框加向上箭頭）→ **加入主畫面** → 右上角 **加入**。
4. 之後從桌面的「職災小卡」圖示打開。

## 五、新增案例、重新部署
1. 把新的案例檔（`.json`）放進電腦裡 `src` 的案例資料夾，並把檔名加到 `cases/index.json` 的清單裡。
2. 在電腦上重新打包：`python build/build.py 新的輸出位置 --cases 你的案例資料夾`（只需要 Python，不用 Node）。打包時會換新的版本編號。
3. 回到 GitHub 存放區 → **Add file** → **Upload files**，把新的 `dist` 裡面的全部東西再拖一次（同名檔案會被取代）→ **Commit changes**。
4. 同仁把 App 關掉再打開（必要時再開一次），畫面最下方的「版本」編號會變新，新案例就會出現在清單裡。

只想加案例、不想重新打包也可以：直接上傳新的案例檔和改好的 `cases/index.json`。案例清單每次都會先問網路，所以同仁重開就看得到；但這樣不會換版本編號，飛航模式下要先在有網路時打開過一次新案例。
