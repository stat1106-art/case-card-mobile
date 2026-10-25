"""路徑檢查：這次推送只准動 cases/。動到其他檔案 → 回傳 1（Actions 標示失敗、不部署）。
用法：python .github/scripts/path_guard.py <推送前 sha> <推送後 sha>
輸出 cases_changed=true|false 到 $GITHUB_OUTPUT（沒有任何 cases/ 變更就不必部署）。"""
import os, subprocess, sys

before, after = sys.argv[1], sys.argv[2]
def git(*a): return subprocess.run(["git", *a], capture_output=True, text=True, check=True).stdout.strip()
if not before or set(before) == {"0"}:
    # 新建分支的第一次推送：和 main 比
    base = git("merge-base", "origin/main", after)
else:
    try: git("cat-file", "-e", before + "^{commit}"); base = before
    except subprocess.CalledProcessError: base = git("merge-base", "origin/main", after)   # 強制推送後舊 sha 不存在
changed = [f for f in git("diff", "--name-only", "--no-renames", base, after).splitlines() if f]
outside = [f for f in changed if not f.startswith("cases/")]
print(f"比較範圍 {base[:10]}..{after[:10]}，變更 {len(changed)} 個檔案")
for f in changed: print(("  ✗ " if f in outside else "  ✓ ") + f)
with open(os.environ.get("GITHUB_OUTPUT", os.devnull), "a") as o:
    o.write(f"cases_changed={'true' if changed and not outside else 'false'}\n")
if outside:
    print(f"::error title=不自動部署::這次推送動到 cases/ 以外的 {len(outside)} 個檔案（{', '.join(outside[:5])}）。自動上架只接受 cases/ 的變更；網站維持原狀。")
    sys.exit(1)
if not changed: print("cases/ 沒有變更，不需要部署。")
