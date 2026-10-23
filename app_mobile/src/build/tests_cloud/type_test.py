import base64, subprocess, sys, time
from pathlib import Path
from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright
serve, out = Path(sys.argv[1]), Path(sys.argv[2])
srv = subprocess.Popen([sys.executable, "-m", "http.server", "8827", "--bind", "127.0.0.1", "-d", str(serve)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1)
B64 = """async()=>{const b=window.__app.current.blob;const u=new Uint8Array(await b.arrayBuffer());let s='';for(let i=0;i<u.length;i+=32768)s+=String.fromCharCode.apply(null,u.subarray(i,i+32768));return btoa(s)}"""
H = serve / "repo/hero_library"
imgs = {k: Image.open(H / f).convert("RGB").crop((0, 0, 503, 262)) for k, f in (("r9", "overwork_night_desk_photo.card.jpg"), ("fall", "type_fall.card.jpg"), ("machine", "type_machine.card.jpg"), ("heat", "type_heat.card.jpg"), ("overwork", "type_overwork.card.jpg"))}
EXPECT = {"shilin_110_laosu_72.json": ("r9", False), "t_fall.json": ("fall", False), "t_machine.json": ("machine", False), "t_heat.json": ("heat", False), "t_none.json": ("overwork", True)}
ok = True
try:
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": 393, "height": 852})
        pg.goto("http://127.0.0.1:8827/repo/"); pg.wait_for_selector("input[name=c]")
        for case, (want, note) in EXPECT.items():
            for t in ("classic", "light", "standard"):
                pg.check(f"input[value='{case}']"); pg.select_option("#tpl", t)
                pg.evaluate("window.__lastResult=null"); pg.click("#go")
                pg.wait_for_function("window.__lastResult && !document.getElementById('go').disabled", timeout=120000)
                res = pg.text_content("#result")
                im = Image.open(__import__("io").BytesIO(base64.b64decode(pg.evaluate(B64)))).convert("RGB").crop((577, 0, 1080, 262))
                score = {k: sum(ImageChops.difference(im, v).convert("L").histogram()[:13]) / (503 * 262) * 100 for k, v in imgs.items()}
                best = max(score, key=score.get)
                passed = res.startswith("檢查全部通過") and best == want and score[best] > 85 and (("示意圖尚未配置" in res) == note)
                ok &= passed
                print(("PASS " if passed else "FAIL ") + f"{case:26s} {t:9s} 右上＝{best}（{score[best]:.0f}%）註明尚未配置＝{'是' if '示意圖尚未配置' in res else '否'}")
        b.close()
finally: srv.terminate()
print("全部通過" if ok else "有沒過")
