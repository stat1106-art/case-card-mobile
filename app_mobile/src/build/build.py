"""組出 dist/：python build/build.py  （不用 Node）"""
import datetime as _dt, hashlib, json, re as _re, shutil, sys, os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ROOT = Path(__file__).resolve().parent.parent
KIT = ROOT / 'src2/case_card_app_kit'
if not KIT.exists(): KIT = ROOT.parent.parent   # 沒有 src2 捷徑時（例如 GitHub Actions），套件就是程式庫根目錄
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
# 企業職災平台（platform/）：原樣放進網站 platform/，不進離線預先快取（sw.js 的 FRESH 對它採網路優先）。
# sw.js 的快取名稱＝casecard-<打包編號>-platform-<平台版本>，平台版本從 platform/js/common.js 讀出，平台改版也會換快取。
PLATFORM = ROOT / 'platform'
if not (PLATFORM / 'js/common.js').is_file(): raise SystemExit('缺少 platform/（企業職災平台）')
for p in sorted(PLATFORM.rglob('*')):
    if p.is_file(): cp(p, 'platform/' + p.relative_to(PLATFORM).as_posix())
_pv = _re.search(r"VERSION\s*=\s*'([0-9][0-9.]*)'", (PLATFORM / 'js/common.js').read_text(encoding='utf-8'))
if not _pv: raise SystemExit('platform/js/common.js 讀不到平台版本')
PLATFORM_VERSION = _pv.group(1)
for p in sorted((KIT / 'casecard/skins').glob('skin_*.json')): cp(p, 'skins/' + p.name)
cp(KIT / 'casecard/design/standard.css', 'design/standard.css')
# 案例來源資料夾：預設用本包的 cases/；要加案例就把檔案和 index.json 放進去再重新打包（也可用 --cases 指定別的資料夾）
CASES = Path(sys.argv[sys.argv.index('--cases') + 1]) if '--cases' in sys.argv else KIT / 'cases'
for p in sorted(CASES.glob('*.json')): cp(p, 'cases/' + p.name)
# 案例分析 .md（平台頁讀 cases/<案例檔名>.md）：自然人姓名要先遮成「王○○」，用 tools/mask_analysis_md.py 同一套規則檢查，沒遮就停止
sys.path.insert(0, str(KIT / 'tools'))
from mask_analysis_md import candidates as _md_names
for p in sorted(CASES.glob('*.md')):
    _t = p.read_text(encoding='utf-8'); _left = _md_names(_t)
    if _left: raise SystemExit(f'{p.name} 還有自然人姓名沒遮：' + '、'.join(sorted({n for n, _ in _left})) + '（先跑 tools/mask_analysis_md.py）')
    cp(p, 'cases/' + p.name)
# 放上網站的案例檔，自然人姓名一律先遮成「姓＋○○」（例如「羅○○」、複姓「歐陽○○」）再存；沒遮就停止打包
import re as _re
for p in sorted(CASES.glob('*.json')):
    try: parties = (json.loads(p.read_text(encoding='utf-8')).get('card') or {}).get('parties') or {}
    except Exception: continue   # 壞掉的案例檔由 App 標示「讀不出來」
    for who in parties.values():
        if isinstance(who, dict) and who.get('natural_person') and not _re.fullmatch(r'[^○〇]{1,2}[○〇]{1,3}', str(who.get('name', ''))):
            raise SystemExit(f'{p.name} 的自然人姓名沒有遮好：{who.get("name")!r}（要寫成「羅○○」這種格式）')

# ── 右上角的圖 ──
# SVG 插畫照舊全收；每案專屬圖（card.hero.image）只收案例有用到的，事故類型圖（type_*）全收，預設照片一定收；
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
    if miss: raise SystemExit(f'{pv.name} 缺：{"、".join(miss)}（來源紀錄不完整、或沒有發包人核准日期的圖，不准放進網站）')
    try: _dt.date.fromisoformat(str(d['approved_date']))
    except ValueError: raise SystemExit(f'{pv.name} 的核准日期格式要寫成 2026-10-23：{d["approved_date"]!r}')
    return pv
def card_name(name): return name.rsplit('.', 1)[0] + '.card.jpg'
used = {}
for p in sorted(CASES.glob('*.json')):
    try: hero = (json.loads(p.read_text(encoding='utf-8')).get('card') or {}).get('hero') or {}
    except Exception: continue   # 壞掉的案例檔由 App 標示「讀不出來」
    # 舊的 hero.photo 欄位不再收：沒有專屬圖時改用事故類型圖，最後一層是一定會放的預設照片（app.js 的 DEFAULT_PHOTO）
    if hero.get('image'): used[('image', hero['image'])] = p.name
# 事故類型圖庫：hero_library/hero_<類型>_<a|b|…>.png｜.jpg｜.webp（案例 card.hero.hero_type 選類型）。
# 每類只放「使用中」那一張進網站（預設 _a，其他留在 hero_library 備用），網站檔名一律 type_<類型>.card.jpg（app.js 用同一規則找檔）。
# 只認下列類型；檔名是 hero_<英文>_<字母> 卻不是這些類型就停止。來源紀錄要有 type、author、date、approved_date。
HERO_TYPES = ['overwork', 'fall', 'machine', 'traffic', 'chemical', 'electric', 'collapse', 'commute',
              'construction', 'heat', 'disease', 'healthcare', 'stress', 'neutral']
ACTIVE_VARIANT = 'a'
import re as _re2
type_src = {}
for src in sorted((KIT / 'hero_library').iterdir()):
    m = _re2.fullmatch(r'hero_([a-z]+)_([a-z])\.(png|jpe?g|webp)', src.name)
    if not m: continue
    t, v = m.group(1), m.group(2)
    if t not in HERO_TYPES: raise SystemExit(f'類型圖 {src.name} 的類型不在清單裡：{"、".join(HERO_TYPES)}')
    if v == ACTIVE_VARIANT: type_src[t] = src.name
for t, name in type_src.items(): used[('type', name)] = t
# App 找不到案例的圖時（例如貼上的案例）原版改用這張預設照片（app.js 的 DEFAULT_PHOTO），所以一定要放
used.setdefault(('image', 'overwork_night_desk_photo.png'), '（預設圖）')
for (kind, name), case_file in sorted(used.items()):
    src = hero_src(name)
    if src.suffix.lower() not in ('.png', '.jpg', '.jpeg', '.webp'): raise SystemExit(f'情境圖只收 png／jpg／webp：{name}')
    pv = provenance(src, ['type', 'author', 'date', 'approved_date'] if kind == 'type' else ['case', 'author', 'date', 'approved_date'])
    if kind == 'type' and json.loads(pv.read_text(encoding='utf-8')).get('type') != case_file:
        raise SystemExit(f'{pv.name} 的 type 要寫 {case_file}')
    im = Image.open(src).convert('RGB')
    r = HERO_W / HERO_H
    # 來源紀錄可寫 crop_focus_x／crop_focus_y（0＝保留左／上緣、0.5＝置中〔預設〕、1＝保留右／下緣）調整裁切位置
    pvd = json.loads(pv.read_text(encoding='utf-8'))
    fx, fy = (min(1.0, max(0.0, float(pvd.get(k, 0.5)))) for k in ('crop_focus_x', 'crop_focus_y'))
    if im.width / im.height > r: w = round(im.height * r); x0 = round((im.width - w) * fx); im = im.crop((x0, 0, x0 + w, im.height))
    else: h = round(im.width / r); y0 = round((im.height - h) * fy); im = im.crop((0, y0, im.width, y0 + h))
    im = im.resize((HERO_W, HERO_H), Image.LANCZOS)
    dst = out / 'hero_library' / (f'type_{case_file}.card.jpg' if kind == 'type' else card_name(name)); dst.parent.mkdir(parents=True, exist_ok=True)
    for q in (85, 75, 65):
        im.save(dst, 'JPEG', quality=q, optimize=True, progressive=False)
        if dst.stat().st_size <= HERO_MAX_BYTES: break
    else: raise SystemExit(f'{name} 壓到品質 65 仍超過 {HERO_MAX_BYTES // 1000}KB')
    print(f'情境圖 {name} → {dst.name}（{dst.stat().st_size // 1000}KB，{case_file}）')
    cp(pv, 'hero_library/' + pv.name)
for p in sorted(FONTS.iterdir()): cp(p, 'fonts/' + p.name)
for n in ('OFL.txt', 'FONTS_LICENSE.md'): cp(KIT / 'casecard/assets/fonts' / n, 'fonts/' + n)
# 圖示：發包人選用的 1024 原檔（build/icon_source/robot_black_starry.png，2026-10-23 改選黑色星空款，不覆蓋）縮出各尺寸
ICON_SRC = Path(__file__).resolve().parent / 'icon_source' / 'robot_black_starry.png'
ICON_SHA = '5c42b32d86d37c1b47d6253bac7bc956483edd409bb5fe61d511b0456b66e43c'
if hashlib.sha256(ICON_SRC.read_bytes()).hexdigest() != ICON_SHA: raise SystemExit('App 圖示原檔被改過，和發包人選的不同')
icon_src = Image.open(ICON_SRC).convert('RGB')
def icon(size):
    return icon_src.resize((size, size), Image.LANCZOS)
# maskable：原圖縮到 74%、外圍補背景色（原圖最外圈的中位數色），交界 6% 漸層（不碰到離邊最近約 7% 的手），內容都在中心半徑 40% 的安全圓內
MASK_SCALE = 0.74
def icon_maskable(size):
    n = icon_src.width
    edge = [icon_src.getpixel((x, y)) for x in range(n) for y in (0, n - 1)] + [icon_src.getpixel((x, y)) for y in range(n) for x in (0, n - 1)]
    bg = tuple(sorted(c[i] for c in edge)[len(edge) // 2] for i in range(3))
    inner = round(size * MASK_SCALE)
    im = Image.new('RGB', (size, size), bg)
    fg = icon_src.resize((inner, inner), Image.LANCZOS)
    feather = max(2, round(inner * 0.06))
    mask = Image.new('L', (inner, inner), 0); md = ImageDraw.Draw(mask)
    for k in range(feather): md.rectangle([k, k, inner - 1 - k, inner - 1 - k], outline=round(255 * (k + 1) / feather))
    md.rectangle([feather, feather, inner - 1 - feather, inner - 1 - feather], fill=255)
    off = (size - inner) // 2
    im.paste(fg, (off, off), mask)
    return im
(out / 'icons').mkdir()
icon(192).save(out / 'icons/icon-192.png'); icon(512).save(out / 'icons/icon-512.png')
icon_maskable(512).save(out / 'icons/icon-512-maskable.png'); icon(180).save(out / 'icons/apple-touch-icon.png')
# 版本編號＝所有檔案內容的雜湊（內容一變就換）
files = sorted(p for p in out.rglob('*') if p.is_file() and p.name != 'sw.js')
h = hashlib.sha256()
for p in files: h.update(str(p.relative_to(out)).encode()); h.update(p.read_bytes())
build = h.hexdigest()[:10]
pre = ['./'] + [p.relative_to(out).as_posix() for p in files if (not p.name.endswith(('.md', '.txt')) or p.parent.name == 'fonts') and not p.relative_to(out).as_posix().startswith('platform/')]
sw = (out / 'sw.js').read_text(encoding='utf-8').replace('__BUILD__', build).replace('__PRECACHE__', json.dumps(pre, ensure_ascii=False)).replace('__PLATFORM__', PLATFORM_VERSION)
(out / 'sw.js').write_text(sw, encoding='utf-8')
a = (out / 'js/app.js').read_text(encoding='utf-8').replace('__BUILD__', build); (out / 'js/app.js').write_text(a, encoding='utf-8')
(out / 'version.json').write_text(json.dumps({'version': '0.4.0', 'build': build}), encoding='utf-8')
# 測試用的假案例（fixtures、test_ 開頭、testcases）與夾 <script> 的資料不得進網站
for p in sorted(out.rglob('*')):
    rel = p.relative_to(out).as_posix()
    if not p.is_file(): continue
    if _re.search(r'(^|/)(fixtures?|testcases?[^/]*|tests?)(/|$)|(^|/)test_[^/]*$', rel, _re.I):
        raise SystemExit(f'測試用檔案不得放進網站：{rel}')
    if rel.startswith(('cases/', 'platform/data/')) and p.suffix in ('.json', '.md') and '<script' in p.read_text(encoding='utf-8', errors='ignore').lower():
        raise SystemExit(f'資料檔裡有 <script>，不得放進網站：{rel}')
_done.append(True)
print('build', build, len(pre), 'files')
