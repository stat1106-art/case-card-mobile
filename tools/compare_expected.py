"""把出圖結果和 reference/expected_png 的標準答案逐點比對。

用法：python tools/compare_expected.py <出圖資料夾>（預設 verify_out）
compare_mask.json 列出的區域不比對（例如「示意圖暫換」那一格）。
"""
import json
import sys
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
REF = ROOT / "reference" / "expected_png"


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "verify_out"
    masks = json.loads((REF / "compare_mask.json").read_text(encoding="utf-8"))
    failed = 0
    for exp in sorted(REF.glob("*.png")):
        got = out / exp.name
        if not got.exists():
            failed += 1
            print(f"缺圖 {exp.name}")
            continue
        a, b = Image.open(exp).convert("RGB"), Image.open(got).convert("RGB")
        if a.size != b.size:
            failed += 1
            print(f"尺寸不同 {exp.name}：{a.size} vs {b.size}")
            continue
        for x, y, w, h, _ in masks.get(exp.name, []):
            for im in (a, b):
                ImageDraw.Draw(im).rectangle([x, y, x + w - 1, y + h - 1], fill=(0, 0, 0))
        diff = ImageChops.difference(a, b).convert("L").point(lambda v: 255 if v > 32 else 0)
        n = diff.histogram()[255]
        note = "（已排除：" + "、".join(m[4] for m in masks[exp.name]) + "）" if exp.name in masks else ""
        if n:
            failed += 1
            print(f"不同 {exp.name}：{n} 點，範圍 {diff.getbbox()}{note}")
        else:
            print(f"一致 {exp.name}{note}")
    print("全部一致" if not failed else f"{failed} 張不一致")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
