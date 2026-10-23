"""11 張並排對照＋像素差＋換行比對。用法：python evidence_cards.py <engine> <device或none> <outdir>"""
import base64, json, os, sys, time
from PIL import Image, ImageChops, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright
sys.path.insert(0, os.path.dirname(__file__)); from harness import gen, URL
E = '/workspace/case_card_v02/src2/case_card_app_kit/reference/expected_png/'
PY = '/workspace/case_card_v02/build/py_html/'
eng, dev, out = sys.argv[1], sys.argv[2], sys.argv[3]; os.makedirs(out, exist_ok=True)
JOBS = [('classic', s) for s in ['original','style1','style1_print','style2','style3','style4','style5','style6','style7']] + [('light','original'),('standard','original')]
JSM = open('/workspace/case_card_v02/app_src/js/engine.js', encoding='utf-8').read()
FNT = ImageFont.truetype('/workspace/case_card_v02/src2/case_card_app_kit/casecard/assets/fonts/NotoSansTC-VF.ttf', 34)
def lines(rects):
    d = {}
    for l, t, r, b, s in rects: d.setdefault(s, []).append(round(t))
    return d
rows = []
with sync_playwright() as p:
    b = getattr(p, eng).launch()
    ctx = b.new_context(**(p.devices[dev] if dev != 'none' else {}))
    pg = ctx.new_page(); pg.goto(URL); pg.wait_for_selector('input[name=c]')
    # 參考：電腦版 HTML 用原字型在 Chromium 量出的文字位置
    rb = p.chromium.launch(); rp = rb.new_page(viewport={'width':1080,'height':1620}); rp.goto('http://127.0.0.1:8811/repo/version.json')  # 同源，字型才載得到
    for tpl, skin in JOBS:
        t0 = time.time(); r = gen(pg, tpl, skin); sec = time.time() - t0
        png = base64.b64decode(r['b64']); fn = f'{out}/{tpl}_{skin}_mobile.png'; open(fn, 'wb').write(png)
        a = Image.open(fn).convert('RGB'); e = Image.open(E + f'{tpl}_{skin}.png').convert('RGB')
        d = ImageChops.difference(a, e).convert('L'); h = d.histogram(); tot = 1080 * 1620
        gt32 = sum(h[33:]); gt96 = sum(h[97:]); mean = sum(i * v for i, v in enumerate(h)) / tot
        html = open(PY + f'{tpl}_{skin}.html', encoding='utf-8').read().replace('REF:', 'http://127.0.0.1:8811/kitref/')
        rp.set_content(html, wait_until='load'); rp.evaluate('document.fonts.ready'); rp.wait_for_timeout(300); assert rp.evaluate('[...document.fonts].every(f=>f.status!=="error")')
        rp.add_script_tag(content=JSM)
        ref = rp.evaluate('(imm)=>{const f=eval("("+CardEngine.JS_MEASURE+")"); return f({minFont:18, immutable:imm}).textRects}', [])
        A, B = lines(r['res']['rects']), lines(ref)
        brk = [k for k in set(A) | set(B) if len(A.get(k, [])) != len(B.get(k, []))]
        shift = max([abs(x - y) for k in A if k in B and len(A[k]) == len(B[k]) for x, y in zip(sorted(A[k]), sorted(B[k]))] or [0])
        heat = Image.eval(d, lambda v: 255 if v > 32 else 0).convert('RGB'); heat = Image.blend(e, Image.merge('RGB', (heat.split()[0], Image.new('L', heat.size), Image.new('L', heat.size))), 0.6)
        sbs = Image.new('RGB', (1080 * 3 + 40, 1620 + 60), 'white'); dr = ImageDraw.Draw(sbs)
        for i, (im, lab) in enumerate([(e, '電腦版標準答案'), (a, f'手機版（{eng} {dev}）'), (heat, '差異（紅＝差 >32）')]):
            sbs.paste(im, (i * 1100, 60)); dr.text((i * 1100 + 10, 10), lab, font=FNT, fill='black')
        sbs.save(f'{out}/{tpl}_{skin}_sidebyside.png')
        checks = r['res']['checks']; ok = all(c[1] for c in checks)
        row = dict(job=f'{tpl}_{skin}', sec=round(sec, 1), checks=len(checks), all_pass=ok, ui=r['result'].strip(), shown_bytes=r['shownBytes'], png_bytes=len(png), size=a.size,
                   px_diff_gt32=gt32, pct_gt32=round(gt32 * 100 / tot, 2), px_diff_gt96=gt96, mean_abs=round(mean, 2), text_nodes=len(A), line_count_mismatch=brk, max_line_top_shift_px=shift, sha256=r['res']['sha256'])
        print(json.dumps(row, ensure_ascii=False)); rows.append(row)
    b.close(); rb.close()
json.dump(rows, open(f'{out}/summary.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
