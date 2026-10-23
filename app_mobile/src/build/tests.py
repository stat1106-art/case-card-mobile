"""手機版功能測試（Playwright）。用法：python tests.py <webkit|chromium> <裝置> <輸出資料夾>"""
import base64, hashlib, json, os, sys, time
from playwright.sync_api import sync_playwright
sys.path.insert(0, os.path.dirname(__file__)); from harness import gen
ROOT = '/workspace/case_card_v02'; URL = 'http://127.0.0.1:8811/repo/'
eng, dev, out = sys.argv[1], sys.argv[2], sys.argv[3]; os.makedirs(out, exist_ok=True)
def link(build): 
    tmp = ROOT + '/serve/.repo_tmp'; os.symlink(f'{ROOT}/out/{build}/dist', tmp); os.replace(tmp, ROOT + '/serve/repo')
R = {}; netlog = []
def rec(k, ok, detail=''): R[k] = {'pass': bool(ok), 'detail': detail}; print(('PASS ' if ok else 'FAIL ') + k, str(detail)[:300])
def shot(pg, n): pg.screenshot(path=f'{out}/{n}.png', full_page=True)
def noscroll(pg): return pg.evaluate('()=>({sw:document.documentElement.scrollWidth, cw:document.documentElement.clientWidth})')
SHARE_MOCK = '''window.__shared=null; window.__shareMode='share';
 const _cs=navigator.canShare; Object.defineProperty(navigator,'canShare',{configurable:true,value:(d)=>window.__shareMode==='share'});
 Object.defineProperty(navigator,'share',{configurable:true,value:async(d)=>{const f=d.files[0];const u=new Uint8Array(await f.arrayBuffer());let s='';for(let i=0;i<u.length;i+=32768)s+=String.fromCharCode.apply(null,u.subarray(i,i+32768));window.__shared={name:f.name,type:f.type,b64:btoa(s)};}});'''
import subprocess
SRV = None
def server(on):
    global SRV
    if on and SRV is None: SRV = subprocess.Popen([sys.executable, ROOT + '/build/serve.py', '8811', ROOT + '/serve']); time.sleep(1)
    if not on and SRV is not None: SRV.terminate(); SRV.wait(); SRV = None
def go_offline(ctx):
    # 先試瀏覽器的「離線」模擬；WebKit 測試版在離線模擬下連 Service Worker 也擋住時，改成直接關掉伺服器（等同網站完全連不到）
    server(False)
link('t1b'); server(True)
with sync_playwright() as p:
    b = getattr(p, eng).launch()
    ctx = b.new_context(**p.devices[dev]) if dev != 'none' else b.new_context()
    ctx.add_init_script(SHARE_MOCK)
    ctx.on('request', lambda r: netlog.append(r.url))
    pg = ctx.new_page(); pg.goto(URL); pg.wait_for_selector('input[name=c]')
    pg.wait_for_function('navigator.serviceWorker && navigator.serviceWorker.controller', timeout=60000) if False else None
    pg.evaluate('navigator.serviceWorker.ready'); pg.reload(); pg.wait_for_selector('input[name=c]')
    ctrl = pg.evaluate('!!navigator.serviceWorker.controller'); rec('sw_controls_page', ctrl)
    v1 = pg.text_content('#ver'); rec('version_shown', v1.startswith('版本 0.2.0'), v1)
    shot(pg, '01_start')
    # 6 草稿預設打勾＋免責文字
    rec('06_draft_default_checked', pg.is_checked('#draft'), pg.text_content('#disc'))
    rec('06_disclaimer_text', pg.text_content('#disc') == '案例內容由 AI 整理，正式使用前請自己對照判決核對。')
    # 10 壞檔
    cases = pg.evaluate('[...document.querySelectorAll("#cases .case")].map(l=>({t:l.textContent,bad:l.classList.contains("bad"),radio:!!l.querySelector("input")}))')
    bad = [c for c in cases if c['bad']]
    rec('10_broken_case_label', len(bad) == 1 and bad[0]['t'] == 'test_broken.json（這個案例讀不出來）' and not bad[0]['radio'] and len([c for c in cases if c['radio']]) == 3, cases)
    # 7 風格選單變灰
    st = {}
    for t in ['classic', 'light', 'standard']:
        pg.select_option('#tpl', t)
        st[t] = pg.evaluate('({dis:document.getElementById("skin").disabled, val:document.getElementById("skin").value, note:document.getElementById("skinnote").textContent, bg:getComputedStyle(document.getElementById("skin")).backgroundColor})')
    if True: pg.select_option('#tpl', 'light'); shot(pg, '07_light_skin_greyed')
    rec('07_skin_greyed', not st['classic']['dis'] and st['light']['dis'] and st['standard']['dis'] and st['light']['val'] == 'original' and st['standard']['note'] == '只有新第一版可以換風格', st)
    # 4/8 正常出圖＋分享＝同一份
    r = gen(pg, 'classic', 'style3', True, 'shilin_110_laosu_72.json'); shot(pg, '04_result_classic_style3')
    rec('04_all_checks_pass_text', r['result'].strip().startswith('檢查全部通過（20 項）'), r['result'])
    ids = [c[0][:3] for c in r['res']['checks']]
    rec('04_has_C05_L10', 'C05' in ids and 'L10' in ids, ids)
    shown = pg.evaluate('async()=>{const u=new Uint8Array(await (await fetch(document.getElementById("pic").src)).arrayBuffer());const h=await crypto.subtle.digest("SHA-256",u);return [...new Uint8Array(h)].map(b=>b.toString(16).padStart(2,"0")).join("")}')
    pg.click('#save'); pg.wait_for_function('window.__shared')
    sh = pg.evaluate('window.__shared'); data = base64.b64decode(sh['b64'])
    from PIL import Image; import io
    im = Image.open(io.BytesIO(data))
    rec('08_share_same_bytes_1080x1620', hashlib.sha256(data).hexdigest() == shown == r['res']['sha256'] and im.size == (1080, 1620),
        {'shared_sha': hashlib.sha256(data).hexdigest(), 'shown_sha': shown, 'size': im.size, 'name': sh['name'], 'type': sh['type']})
    open(f'{out}/08_shared.png', 'wb').write(data)
    # 分享不支援時：全螢幕＋提示
    pg.evaluate("window.__shareMode='none'"); pg.click('#save'); pg.wait_for_selector('#full:not([hidden])')
    fsrc = pg.evaluate('document.getElementById("fullpic").src===document.getElementById("pic").src')
    rec('08_fallback_fullscreen_hint', pg.is_visible('#full') and pg.text_content('#full .hint') == '長按圖片 → 加入照片' and fsrc)
    shot(pg, '08_fallback_fullscreen'); pg.click('#closefull'); pg.evaluate("window.__shareMode='share'")
    # 草稿取消
    r2 = gen(pg, 'classic', 'style3', False)
    rec('06_draft_unchecked_name', pg.evaluate('window.__app.current.name') == 'shilin_110_laosu_72_classic_style3.png' and r2['res']['sha256'] != r['res']['sha256'])
    # 5 爆框
    r = gen(pg, 'classic', 'original', True, 'test_overflow.json'); shot(pg, '05_overflow')
    rec('05_overflow_fail_with_image', r['result'].startswith('檢查沒過') and '下面的圖照原樣產生' in r['result'] and r['b64'] is not None, r['result'])
    if r['b64']: open(f'{out}/05_overflow_card.png', 'wb').write(base64.b64decode(r['b64']))
    # 11 缺字
    r = gen(pg, 'classic', 'original', True, 'test_missing_glyph.json'); shot(pg, '11_missing_glyph')
    rec('11_missing_glyph', r['result'].startswith('檢查沒過') and '這幾個字字型裡沒有：𪚥䲜' in r['result'] and r['b64'] is None, r['result'])
    # 12 不用左右捲動、按鈕大小
    sizes = pg.evaluate('[...document.querySelectorAll("button,select,label.case,label.check")].filter(e=>e.offsetParent).map(e=>{const r=e.getBoundingClientRect();return [e.id||e.className,Math.round(r.width),Math.round(r.height)]})')
    ns = noscroll(pg)
    rec('12_no_horizontal_scroll', ns['sw'] <= ns['cw'], ns)
    rec('12_touch_targets', all(h >= 44 for k, w, h in sizes), sizes)
    # 2 離線（飛航模式）：重開＋出圖＋存照片
    mode = 'set_offline'
    ctx.set_offline(True)
    pg2 = ctx.new_page()
    try: pg2.goto(URL); pg2.wait_for_selector('input[name=c]', timeout=15000)
    except Exception as e:
        R['02_note'] = (f'{eng} 的離線模擬下打不開（{str(e)[:80]}），改用關掉伺服器的方式測'); print('NOTE', R['02_note'])
        ctx.set_offline(False); pg2.close(); go_offline(ctx); mode = 'server_stopped'
        pg2 = ctx.new_page(); pg2.goto(URL); pg2.wait_for_selector('input[name=c]')
    R['02_offline_mode'] = mode
    r = gen(pg2, 'standard', 'original', True, 'shilin_110_laosu_72.json')
    pg2.click('#save'); pg2.wait_for_function('window.__shared')
    rec('02_offline_open_generate_save', r['result'].strip().startswith('檢查全部通過') and r['b64'] is not None and pg2.evaluate('window.__shared.b64.length') > 1000, r['result'])
    shot(pg2, '02_offline'); pg2.close(); pg.close()
    ctx.set_offline(False); server(True)
    # 9 加一筆新案例並重新部署 → 重開看得到、版本號更新
    link('t2b')
    pg3 = ctx.new_page(); pg3.goto(URL); pg3.wait_for_selector('input[name=c]')
    time.sleep(3); pg3.wait_for_load_state()
    t9 = time.time(); upd = None
    for i in range(30):  # 每 2 秒重開一次，最多 60 秒，記錄多久看得到新版本
        pg3.close(); pg3 = ctx.new_page(); pg3.goto(URL); pg3.wait_for_selector('input[name=c]'); time.sleep(1)
        if '19100e17df' in pg3.text_content('#ver'): upd = round(time.time() - t9, 1); break
        time.sleep(1)
    pg4 = pg3; R['09_seconds_until_new_version'] = upd
    titles = pg4.evaluate('[...document.querySelectorAll("#cases .case")].map(l=>l.textContent)'); v2 = pg4.text_content('#ver')
    sw_build = pg4.evaluate('caches.keys()')
    rec('09_new_case_after_reopen', '（測試）新增的案例' in titles and v2 != v1 and '19100e17df' in v2, {'before': v1, 'after': v2, 'titles': titles, 'caches': sw_build})
    shot(pg4, '09_after_update')
    if R['02_offline_mode'] == 'set_offline': ctx.set_offline(True)
    else: server(False)
    pg5 = ctx.new_page(); pg5.goto(URL); pg5.wait_for_selector('input[name=c]')
    rec('09_offline_after_update', '（測試）新增的案例' in pg5.evaluate('document.getElementById("cases").textContent'))
    ctx.set_offline(False); server(True)
    # 14 網路紀錄
    ext = sorted({u for u in netlog if not (u.startswith('http://127.0.0.1:8811/') or u.startswith('data:') or u.startswith('blob:') or u == 'about:srcdoc')})
    rec('14_no_external_urls', not ext, {'total_requests': len(netlog), 'external': ext})
    b.close()
link('b1'); server(False)
json.dump(R, open(f'{out}/results.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
open(f'{out}/network_log.txt', 'w', encoding='utf-8').write('\n'.join(netlog))
