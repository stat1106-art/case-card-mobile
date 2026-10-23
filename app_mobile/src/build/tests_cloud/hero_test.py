import base64, subprocess, sys, time
from pathlib import Path
from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright
serve, out = Path(sys.argv[1]), Path(sys.argv[2])
srv = subprocess.Popen([sys.executable, "-m", "http.server", "8824", "--bind", "127.0.0.1", "-d", str(serve)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1)
B64 = """async()=>{const b=window.__app.current.blob;const u=new Uint8Array(await b.arrayBuffer());let s='';for(let i=0;i<u.length;i+=32768)s+=String.fromCharCode.apply(null,u.subarray(i,i+32768));return btoa(s)}"""
ok = True
try:
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": 393, "height": 852}, device_scale_factor=3)
        pg.goto("http://127.0.0.1:8824/repo/"); pg.wait_for_selector("input[name=c]")
        jpg = Image.open(serve / "repo/hero_library/test_scene.card.jpg").convert("RGB")
        for case in ("test_hero_image.json", "shilin_110_laosu_72.json"):
            for t in ("classic", "light", "standard"):
                pg.check(f"input[value='{case}']"); pg.select_option("#tpl", t)
                pg.evaluate("window.__lastResult=null"); pg.click("#go")
                pg.wait_for_function("window.__lastResult && !document.getElementById('go').disabled", timeout=120000)
                res = pg.text_content("#result")
                png = out / f"{case[:-5]}_{t}.png"; png.write_bytes(base64.b64decode(pg.evaluate(B64)))
                im = Image.open(png).convert("RGB"); assert im.size == (1080, 1620)
                box = im.crop((577, 0, 1080, 290))
                d = ImageChops.difference(box, jpg).convert("L")
                same = sum(d.histogram()[:13]) / (503 * 290) * 100
                passed = res.startswith("檢查全部通過")
                print(f"{case:28s} {t:9s} {res[:16]:16s} 右上那格和情境圖相同的比例 {same:5.1f}%")
                ok &= passed
        b.close()
finally: srv.terminate()
print("全部檢查通過" if ok else "有檢查沒過")
