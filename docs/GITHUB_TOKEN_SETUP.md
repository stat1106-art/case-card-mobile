# 找案例工具用的 GitHub 權杖：怎麼建（只給這個程式庫、最小權限）

這把權杖就像一張「只能開 case-card-mobile 這一個信箱、只能投遞、不能改郵局規則」的鑰匙。請你自己建、自己保管，**不要傳給任何人（包括我）**。

## 建立步驟（約 3 分鐘）
1. 登入 GitHub，右上角頭像 → **Settings**（設定）。
2. 左邊選單最下面 → **Developer settings**（開發人員設定）。
3. **Personal access tokens** → **Fine-grained tokens** → 右上 **Generate new token**（產生新權杖）。
   - 請用 **Fine-grained**（細分權限）那種，不要用 Tokens (classic)：classic 只能「全部程式庫一起開」。
4. 填寫：
   - **Token name**：`case-card-publisher`
   - **Expiration**（到期）：**90 days**（到期後再建一把新的，舊的自動失效）
   - **Resource owner**：`stat1106-art`
   - **Repository access**：選 **Only select repositories** → 只勾 **`case-card-mobile`**
5. **Repository permissions**（程式庫權限）只開這三個，其他全部保持 **No access**：

| 權限 | 設定 | 為什麼要 |
|---|---|---|
| **Contents** | **Read and write** | 把案例檔推到 main |
| **Actions** | **Read-only** | 推送後查自動上架成功或失敗 |
| **Metadata** | Read-only | GitHub 規定必開（會自動勾） |

6. 按最下面 **Generate token**，畫面會顯示一串 `github_pat_...` 開頭的字，**只顯示這一次**，馬上複製貼進找案例工具的設定裡。

## 一定不要開的權限
- **Workflows**：不開。沒有這個權限，權杖就**改不了自動上架的檢查規則**（`.github/workflows/`），GitHub 會直接拒絕。
- **Administration**、**Secrets**、**Pages**、**Environments**、**Pull requests**、**Issues** 等：都用不到，不開。

## 要知道的限制
- GitHub 的權杖沒辦法限制「只能寫 `cases/` 資料夾」：開了 Contents 寫入，就能寫整個程式庫的檔案（Workflows 除外）。所以另外有兩道防線：
  1. **自動上架的路徑檢查**：推送只要動到 `cases/` 以外的檔案，一律不部署、標示失敗，網站維持原狀。
  2. **找案例工具自己**只組 `cases/` 的變更。
- 即使沒部署，推上去的檔案還是會留在 main，維護人員要清掉。

## 保管與停用
- 權杖只存在你電腦的找案例工具設定裡；不要貼進對話、文件、截圖或 LINE。
- 懷疑外流、或電腦遺失：立刻到同一頁（Fine-grained tokens）按 **Delete**（刪除），再建一把新的。
- 到期前 GitHub 會寄信提醒；到期後工具推送會失敗，照上面步驟重建即可。
