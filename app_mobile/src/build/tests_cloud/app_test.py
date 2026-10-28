import base64, json, subprocess, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright
serve, out = Path(sys.argv[1]), Path(sys.argv[2])
URL = "http://127.0.0.1:8822/repo/"
# 打包編號與預先快取檔數從被測的網站讀（不寫死）
BUILD = json.loads((serve / "repo/version.json").read_text(encoding="utf-8"))["build"]
_sw = (serve / "repo/sw.js").read_text(encoding="utf-8")
PRECACHE_N = len(json.loads(_sw.split("const PRECACHE = ", 1)[1].split(";\n", 1)[0]))
srv = subprocess.Popen([sys.executable, "-m", "http.server", "8822", "--bind", "127.0.0.1", "-d", str(serve)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1)
R = {}; net = []
def rec(k, ok, d=""): R[k] = ok; print(("PASS " if ok else "FAIL ") + k, str(d)[:200])
JOBS = [("classic", s) for s in ["original","style1","style1_print","style2","style3","style4","style5","style6","style7"]]  # 0.5.0：只留新第一版
def gen(pg, t, s, name):
    pg.select_option("#tpl", t)
    if t == "classic": pg.select_option("#skin", s)
    pg.evaluate("window.__lastResult=null")
    pg.click("#go")
    pg.wait_for_function("window.__lastResult && !document.getElementById('go').disabled", timeout=120000)
    res = pg.text_content("#result")
    b64 = pg.evaluate("""async()=>{const b=window.__app.current.blob;const u=new Uint8Array(await b.arrayBuffer());let s='';for(let i=0;i<u.length;i+=32768)s+=String.fromCharCode.apply(null,u.subarray(i,i+32768));return btoa(s)}""")
    (out / name).write_bytes(base64.b64decode(b64))
    return res
try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={"width": 393, "height": 852}, device_scale_factor=3, is_mobile=True, has_touch=True)
        ctx.on("request", lambda r: net.append(r.url))
        pg = ctx.new_page(); pg.goto(URL); pg.wait_for_selector("input[name=c]")
        pg.evaluate("navigator.serviceWorker.ready"); pg.reload(); pg.wait_for_selector("input[name=c]")
        rec("離線快取接管頁面", pg.evaluate("!!navigator.serviceWorker.controller"))
        n = pg.evaluate("async()=>{const ks=await caches.keys();let n=0;for(const k of ks){n+=(await (await caches.open(k)).keys()).length}return [ks,n]}")
        rec(f"快取清單全部裝好（{PRECACHE_N} 個）", n[1] >= PRECACHE_N, n)
        rec("照片在離線快取裡", pg.evaluate("async()=>{for(const k of await caches.keys()){for(const r of await (await caches.open(k)).keys()){if(/photo/i.test(r.url))return true}}return false}"))
        rec("版本號", BUILD in pg.text_content("#ver"), pg.text_content("#ver"))
        for t, s in JOBS:
            res = gen(pg, t, s, f"{t}_{s}.png")
            rec(f"出圖 {t}/{s}", res.startswith("檢查全部通過"), res)
        ctx.set_offline(True)
        pg.reload(); pg.wait_for_selector("input[name=c]")
        res = gen(pg, "classic", "original", "offline_classic_original.png")
        rec("斷網後出圖（新第一版 original）", res.startswith("檢查全部通過"), res)
        res = gen(pg, "classic", "style3", "offline_classic_style3.png")
        rec("斷網後出圖（新第一版 style3）", res.startswith("檢查全部通過"), res)
        pg.screenshot(path=str(out / "screen_offline.png"), full_page=True)
        b.close()
finally:
    srv.terminate()
ext = sorted({u for u in net if not u.startswith(("http://127.0.0.1:8822/", "data:", "blob:"))})
rec("沒有連到外部網址", not ext, ext or f"共 {len(net)} 個請求，全部是本機")
(out / "network_log.txt").write_text("\n".join(net))
print("全部通過" if all(R.values()) else f"{sum(not v for v in R.values())} 項沒過")
