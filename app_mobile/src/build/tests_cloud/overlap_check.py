"""右上圖疊上去後，原本壓在圖上的東西有沒有被蓋掉：新第一版的資訊列壓在那一格下緣（x 577–1024、y 262–290），
這一條要和標準答案一樣。用法：python overlap_check.py <app_test 輸出資料夾> <reference/expected_png>"""
import os, sys
from pathlib import Path
from PIL import Image, ImageChops
out, ref = Path(sys.argv[1]), Path(sys.argv[2])
STRIP = (577, 262, 1024, 290)
LIMIT = int(os.environ.get("OVERLAP_LIMIT", "200"))   # 容許字邊緣反鋸齒的少數點；CI 主機渲染不同，用環境變數放寬
bad = 0
for e in sorted(ref.glob("classic_*.png")):
    a, b = Image.open(e).convert("RGB").crop(STRIP), Image.open(out / e.name).convert("RGB").crop(STRIP)
    n = sum(ImageChops.difference(a, b).convert("L").histogram()[33:])
    print(("通過 " if n <= LIMIT else "沒過 ") + f"{e.name}：資訊列那一條差>32 {n} 點")
    bad += n > LIMIT
print("全部通過" if not bad else f"{bad} 張沒過")
sys.exit(1 if bad else 0)
