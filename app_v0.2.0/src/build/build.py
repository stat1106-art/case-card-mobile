"""組出 dist/：python build/build.py  （不用 Node）"""
import datetime as _dt, hashlib, json, shutil, sys, os
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
# 中途停下來（例如圖沒有核准日期）就把半成品整個刪掉，避免被拿去部署
import atexit
_done = []
atexit.register(lambda: _done or shutil.rmtree(out, ignore_errors=True))
def cp(a, b):
    b = out / b; b.parent.mkdir(parents=True, exist_ok=True); shutil.copyfile(a, b)
for p in APP.rglob('*'):
    if p.is_file(): cp(p, p.relative_to(APP))
for p in sorted((KIT / 'casecard/skins').glob('skin_*.json')): cp(p, 'skins/' + p.name)
cp(KIT / 'casecard/design/standard.css', 'design/standard.css')
# 案例來源資料夾：預設用本包的 cases/；要加案例就把檔案和 index.json 放進去再重新打包（也可用 --cases 指定別的資料夾）
CASES = Path(sys.argv[sys.argv.index('--cases') + 1]) if '--cases' in sys.argv else KIT / 'cases'
for p in sorted(CASES.glob('*.json')): cp(p, 'cases/' + p.name)

# ── 右上角的圖 ──
# SVG 插畫照舊全收；照片（card.hero.photo，原版用）與每案情境圖（card.hero.image，三個版型都用）只收案例有用到的，
# 而且每張都要有同名 .provenance.json 且寫了發包人核准日期，否則停止打包（不准放進網站）。
# 情境圖先置中裁成右上那一格的比例（503×290）、存成 JPEG（檔名＝原檔名主檔名＋.card.jpg，app.js 用同一規則找檔）。
HERO_W, HERO_H = 503, 290
HERO_MAX_BYTES = 150_000
HERO_DIRS = [CASES / 'hero', KIT / 'hero_library']   # 先找案例資料夾旁的 hero/，再找 hero_library/
for p in sorted((KIT / 'hero_library').glob('*.svg')): cp(p, 'hero_library/' + p.name)
def hero_src(name):
    if not name or '/' in name or '\\' in name: raise SystemExit(f'圖檔名不正確：{name!r}')
    for d in HERO_DIRS:
        if (d / name).is_file(): return d / name
    raise SystemExit(f'找不到圖：{name}（放在 hero_library/）')
def provenance(src, need):
    pv = src.with_name(src.name.rsplit('.', 1)[0] + '.provenance.json')
    if not pv.is_file(): raise SystemExit(f'{src.name} 沒有同名的來源紀錄 {pv.name}，不准放進網站')
    d = json.loads(pv.read_text(encoding='utf-8'))
    miss = [k for k in need if not str(d.get(k) or '').strip()]
    if miss: raise SystemExit(f'{pv.name} 缺：{"、".join(miss)}（沒有發包人核准日期的圖不准放進網站）')
    try: _dt.date.fromisoformat(str(d['approved_date']))
    except ValueError: raise SystemExit(f'{pv.name} 的核准日期格式要寫成 2026-10-23：{d["approved_date"]!r}')
    return pv
def card_name(name): return name.rsplit('.', 1)[0] + '.card.jpg'
used = {}
for p in sorted(CASES.glob('*.json')):
    try: hero = (json.loads(p.read_text(encoding='utf-8')).get('card') or {}).get('hero') or {}
    except Exception: continue   # 壞掉的案例檔由 App 標示「讀不出來」
    if hero.get('photo'): used[('photo', hero['photo'])] = p.name
    if hero.get('image'): used[('image', hero['image'])] = p.name
for (kind, name), case_file in sorted(used.items()):
    src = hero_src(name)
    if kind == 'photo':
        pv = provenance(src, ['approved_date'])
        cp(src, 'hero_library/' + name)
    else:
        if src.suffix.lower() not in ('.png', '.jpg', '.jpeg', '.webp'): raise SystemExit(f'情境圖只收 png／jpg／webp：{name}')
        pv = provenance(src, ['case', 'author', 'date', 'approved_date'])
        im = Image.open(src).convert('RGB')
        r = HERO_W / HERO_H
        if im.width / im.height > r: w = round(im.height * r); im = im.crop(((im.width - w) // 2, 0, (im.width - w) // 2 + w, im.height))
        else: h = round(im.width / r); im = im.crop((0, (im.height - h) // 2, im.width, (im.height - h) // 2 + h))
        im = im.resize((HERO_W, HERO_H), Image.LANCZOS)
        dst = out / 'hero_library' / card_name(name); dst.parent.mkdir(parents=True, exist_ok=True)
        for q in (85, 75, 65):
            im.save(dst, 'JPEG', quality=q, optimize=True, progressive=False)
            if dst.stat().st_size <= HERO_MAX_BYTES: break
        else: raise SystemExit(f'{name} 壓到品質 65 仍超過 {HERO_MAX_BYTES // 1000}KB')
        print(f'情境圖 {name} → {dst.name}（{dst.stat().st_size // 1000}KB，{case_file}）')
    cp(pv, 'hero_library/' + pv.name)
for p in sorted(FONTS.iterdir()): cp(p, 'fonts/' + p.name)
for n in ('OFL.txt', 'FONTS_LICENSE.md'): cp(KIT / 'casecard/assets/fonts' / n, 'fonts/' + n)
# 圖示：深藍底＋一張白色小卡（黑標題條、內文線、紅色金額條、綠色勾），配色取自原版小卡；不放字（iPhone 會在圖示下方顯示名稱）
NAVY, CARD, BAND, LINE, RED, GREEN, WHITE = "#1E4B78", "#FFFDF8", "#171614", "#D9D2C3", "#B3342B", "#1D7A4A", "#FFFFFF"
def icon(size, safe=1.0):
    k = 4; S = size * k
    im = Image.new('RGB', (S, S), NAVY); d = ImageDraw.Draw(im)
    def box(x0, y0, x1, y1):
        f = lambda v: (0.5 + (v - 0.5) * safe) * S
        return [f(x0), f(y0), f(x1), f(y1)]
    r = lambda v: v * safe * S
    d.rounded_rectangle(box(0.22, 0.16, 0.78, 0.84), radius=r(0.06), fill=CARD)
    d.rounded_rectangle(box(0.22, 0.16, 0.78, 0.34), radius=r(0.06), fill=BAND)
    d.rectangle(box(0.22, 0.28, 0.78, 0.34), fill=BAND)
    d.rounded_rectangle(box(0.29, 0.22, 0.56, 0.28), radius=r(0.02), fill=WHITE)
    for y in (0.42, 0.52):
        d.rounded_rectangle(box(0.29, y, 0.71, y + 0.045), radius=r(0.022), fill=LINE)
    d.rounded_rectangle(box(0.29, 0.62, 0.55, 0.74), radius=r(0.03), fill=RED)
    cx, cy, cr = 0.655, 0.68, 0.085
    d.ellipse(box(cx - cr, cy - cr, cx + cr, cy + cr), fill=GREEN)
    pts = [box(x, y, x, y)[:2] for x, y in ((0.615, 0.68), (0.645, 0.71), (0.70, 0.645))]
    d.line(pts, fill=WHITE, width=int(r(0.028)), joint='curve')
    for p in (pts[0], pts[2]):
        w = r(0.014); d.ellipse([p[0] - w, p[1] - w, p[0] + w, p[1] + w], fill=WHITE)
    return im.resize((size, size), Image.LANCZOS)
(out / 'icons').mkdir()
icon(192).save(out / 'icons/icon-192.png'); icon(512).save(out / 'icons/icon-512.png')
icon(512, 0.8).save(out / 'icons/icon-512-maskable.png'); icon(180).save(out / 'icons/apple-touch-icon.png')
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
_done.append(True)
print('build', build, len(pre), 'files')
