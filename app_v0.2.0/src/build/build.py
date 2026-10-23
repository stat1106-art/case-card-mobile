"""組出 dist/：python build/build.py  （不用 Node）"""
import hashlib, json, shutil, sys, os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ROOT = Path(__file__).resolve().parent.parent
KIT = ROOT / 'src2/case_card_app_kit'
APP = ROOT / 'app_src'
FONTS = ROOT / 'build/fonts_out'
args = [a for i, a in enumerate(sys.argv[1:], 1) if a != '--cases' and sys.argv[i - 1] != '--cases']
out = Path(args[0]) if args else ROOT / 'dist'
if out.exists(): raise SystemExit(f'{out} 已存在，請換一個輸出位置')
out.mkdir(parents=True)
def cp(a, b):
    b = out / b; b.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(a, b)
for p in APP.rglob('*'):
    if p.is_file(): cp(p, p.relative_to(APP))
for p in sorted((KIT / 'casecard/skins').glob('skin_*.json')): cp(p, 'skins/' + p.name)
cp(KIT / 'casecard/design/standard.css', 'design/standard.css')
# 示意圖只收 SVG：照片（*_photo.png 與其來源紀錄）使用權未確認，不得進網站與離線快取
for p in sorted((KIT / 'hero_library').glob('*.svg')): cp(p, 'hero_library/' + p.name)
# 案例來源資料夾：預設用本包的 cases/；要加案例就把檔案和 index.json 放進去再重新打包（也可用 --cases 指定別的資料夾）
CASES = Path(sys.argv[sys.argv.index('--cases') + 1]) if '--cases' in sys.argv else KIT / 'cases'
for p in sorted(CASES.glob('*.json')): cp(p, 'cases/' + p.name)
for p in sorted(FONTS.iterdir()): cp(p, 'fonts/' + p.name)
for n in ('OFL.txt', 'FONTS_LICENSE.md'): cp(KIT / 'casecard/assets/fonts' / n, 'fonts/' + n)
# 圖示
f = ImageFont.truetype(str(KIT / 'casecard/assets/fonts/NotoSansTC-VF.ttf'), 10)
def icon(size, pad):
    im = Image.new('RGB', (size, size), '#1f5fbf'); d = ImageDraw.Draw(im)
    fnt = ImageFont.truetype(str(KIT / 'casecard/assets/fonts/NotoSansTC-VF.ttf'), int(size * (0.30 if pad else 0.36)))
    try: fnt.set_variation_by_axes([900])
    except Exception: pass
    for i, t in enumerate(('職災', '小卡')):
        d.text((size / 2, size * (0.36 + 0.30 * i) if not pad else size * (0.38 + 0.26 * i)), t, font=fnt, fill='white', anchor='mm')
    return im
(out / 'icons').mkdir()
icon(192, False).save(out / 'icons/icon-192.png'); icon(512, False).save(out / 'icons/icon-512.png')
icon(512, True).save(out / 'icons/icon-512-maskable.png'); icon(180, False).save(out / 'icons/apple-touch-icon.png')
# 版本編號＝所有檔案內容的雜湊（內容一變就換）
files = sorted(p for p in out.rglob('*') if p.is_file() and p.name != 'sw.js')
h = hashlib.sha256()
for p in files: h.update(str(p.relative_to(out)).encode()); h.update(p.read_bytes())
build = h.hexdigest()[:10]
pre = ['./'] + [p.relative_to(out).as_posix() for p in files if not p.name.endswith(('.md', '.txt')) or p.parent.name == 'fonts']
sw = (out / 'sw.js').read_text(encoding='utf-8').replace('__BUILD__', build).replace('__PRECACHE__', json.dumps(pre, ensure_ascii=False))
(out / 'sw.js').write_text(sw, encoding='utf-8')
a = (out / 'js/app.js').read_text(encoding='utf-8').replace('__BUILD__', build); (out / 'js/app.js').write_text(a, encoding='utf-8')
(out / 'version.json').write_text(json.dumps({'version': '0.2.0', 'build': build}), encoding='utf-8')
leak = [p for p in out.rglob('*') if 'photo' in p.name.lower()] + (['sw.js 快取清單'] if 'photo' in sw.lower() else [])
if leak: raise SystemExit(f'不得放進網站的照片：{leak}')
print('build', build, len(pre), 'files')
