import base64, json, sys, time
from playwright.sync_api import sync_playwright
URL = 'http://127.0.0.1:8811/repo/'
def gen(pg, tpl, skin, draft=True, case=None):
    if case: pg.check(f'input[name=c][value="{case}"]')
    pg.select_option('#tpl', tpl)
    if tpl == 'classic': pg.select_option('#skin', skin)
    pg.set_checked('#draft', draft)
    pg.evaluate('window.__lastResult=null')
    pg.click('#go')
    pg.wait_for_function('window.__lastResult!==null || /產生不出|發生問題|讀不出來/.test(document.getElementById("msg").textContent)', timeout=120000)
    r = pg.evaluate('''async()=>{const c=window.__app.current; let b64=null;
      if(c){const u=new Uint8Array(await c.blob.arrayBuffer()); let s=''; for(let i=0;i<u.length;i+=32768) s+=String.fromCharCode.apply(null,u.subarray(i,i+32768)); b64=btoa(s);}
      const shown = c ? await (await fetch(document.getElementById('pic').src)).arrayBuffer().then(a=>a.byteLength) : 0;
      return {res:window.__lastResult, b64, shownBytes:shown, msg:document.getElementById('msg').textContent, result:document.getElementById('result').innerText}}''')
    return r
if __name__ == '__main__':
    eng = sys.argv[1]
    with sync_playwright() as p:
        b = getattr(p, eng).launch()
        ctx = b.new_context(**p.devices['iPhone 15'] if eng == 'webkit' else {})
        pg = ctx.new_page(); pg.on('console', lambda m: print('console', m.text))
        pg.goto(URL); pg.wait_for_selector('input[name=c]')
        t=time.time(); r = gen(pg, sys.argv[2], sys.argv[3]); print('sec', round(time.time()-t,1))
        print(r['msg'], r['result'])
        print([c[:2] for c in r['res']['checks']] if r['res'] else None)
        if r['b64']: open(f'/tmp/t_{eng}.png','wb').write(base64.b64decode(r['b64']))
        b.close()
