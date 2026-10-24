import base64, subprocess, sys, time
from pathlib import Path
from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright
serve, out = Path(sys.argv[1]), Path(sys.argv[2])
srv = subprocess.Popen([sys.executable, "-m", "http.server", "8827", "--bind", "127.0.0.1", "-d", str(serve)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1)
B64 = """async()=>{const b=window.__app.current.blob;const u=new Uint8Array(await b.arrayBuffer());let s='';for(let i=0;i<u.length;i+=32768)s+=String.fromCharCode.apply(null,u.subarray(i,i+32768));return btoa(s)}"""
H = serve / "repo/hero_library"
imgs = {k: Image.open(H / f).convert("RGB") for k, f in (("r9", "overwork_night_desk_photo.card.jpg"), ("fall", "type_fall.card.jpg"), ("machine", "type_machine.card.jpg"), ("heat", "type_heat.card.jpg"), ("overwork", "type_overwork.card.jpg"))}
EXPECT = {"shilin_110_laosu_72.json": ("r9", False), "t_fall.json": ("fall", False), "t_machine.json": ("machine", False), "t_heat.json": ("heat", False), "t_none.json": ("overwork", True)}
# 右上圖在各版型的位置：新第一版是內縮的 400×231 圓角小卡（624,18）～（1024,249），淺色與原版是 503×290 貼齊右上（只比資訊列以上 262）
def hero_region(png_img, ref_img, template):
    if template == "classic":
        box = png_img.crop((634, 28, 1014, 239)); ref = ref_img.resize((400, 231), Image.LANCZOS).crop((10, 10, 390, 221))
    else:
        box = png_img.crop((577, 0, 1080, 262)); ref = ref_img.crop((0, 0, 503, 262))
    tol = 25 if template == "classic" else 13   # 新第一版的圖由瀏覽器縮成 400×231，和這裡用 PIL 縮的參考圖有細微色差
    return sum(ImageChops.difference(box, ref).convert("L").histogram()[:tol]) / (box.width * box.height) * 100
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
                im = Image.open(__import__("io").BytesIO(base64.b64decode(pg.evaluate(B64)))).convert("RGB")
                score = {k: hero_region(im, v, t) for k, v in imgs.items()}
                best = max(score, key=score.get)
                second = max(v for k, v in score.items() if k != best)
                passed = res.startswith("檢查全部通過") and best == want and score[best] > 85 and score[best] - second > 30 and (("示意圖尚未配置" in res) == note)
                ok &= passed
                print(("PASS " if passed else "FAIL ") + f"{case:26s} {t:9s} 右上＝{best}（{score[best]:.0f}%，次像 {second:.0f}%）註明尚未配置＝{'是' if '示意圖尚未配置' in res else '否'}")
        b.close()
finally: srv.terminate()
print("全部通過" if ok else "有沒過")
