"""姓名遮蔽掃描（tools/mask_analysis_md.py 的 candidates，打包與自動上架共用）回歸測試。
用法：python mask_rules_test.py；全部符合預期印「全部通過」並回傳 0。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools"))
from mask_analysis_md import candidates  # noqa: E402

# 不是人名，不得判定為未遮（發包人 2026-10-25 回報的誤判，以及先前修過的誤判）
NOT_NAMES = ["原告曾帶男性友人", "被告曾遭勞動部裁處", "被告方提出南華大學函", "原告向家長當面檢討",
             "被告陳述", "勞工向第三人請求", "主管簡報", "原告曾經任職", "原告曾於夜間加班", "被告於同日",
             "原告王○○主張", "原告歐陽○○", "原告李林○○",
             "雇主韋彤企業有限公司", "被告林記工程行負責人", "被告陳氏事務所"]
# 真名沒遮，必須判定為未遮（[句子, 至少要抓到的姓名開頭]）
NAMES = [("原告王小明主張", "王小明"), ("證人余美玲證稱", "余美玲"), ("被告陳大同", "陳大同"), ("原告李林雪嬌", "李林"),
         ("原告曾家豪主張", "曾家豪"), ("證人方志明證稱", "方志明"), ("原告向小華", "向小華"), ("原告歐陽明德", "歐陽明")]

bad = 0
for s in NOT_NAMES:
    got = candidates(s)
    ok = not got; bad += not ok
    print(("通過 " if ok else "FAIL ") + f"不是人名：{s}" + ("" if ok else f"｜誤判為 {[n for n, _ in got]}"))
for s, want in NAMES:
    got = [n for n, _ in candidates(s)]
    ok = any(n.startswith(want) for n in got); bad += not ok
    print(("通過 " if ok else "FAIL ") + f"未遮真名：{s}｜抓到 {got}")
print(f"有 {bad} 項不符" if bad else "全部通過")
sys.exit(1 if bad else 0)
