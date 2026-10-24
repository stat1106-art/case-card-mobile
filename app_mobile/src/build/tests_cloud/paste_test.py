"""v0.3.0「貼上案例」驗收（Chromium，模擬 iPhone）。用法：python paste_test.py <serve 資料夾> <輸出資料夾> <士林案 json> <標準答案資料夾>"""
import base64, json, subprocess, sys, time
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw
from playwright.sync_api import sync_playwright
serve, out, case_path, ref = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4])
URL = "http://127.0.0.1:8825/repo/"
srv = subprocess.Popen([sys.executable, "-m", "http.server", "8825", "--bind", "127.0.0.1", "-d", str(serve)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1)
R, net = {}, []
def rec(k, ok, d=""): R[k] = bool(ok); print(("PASS " if ok else "FAIL ") + k, str(d)[:220])
B64 = """async()=>{const b=window.__app.current.blob;const u=new Uint8Array(await b.arrayBuffer());let s='';for(let i=0;i<u.length;i+=32768)s+=String.fromCharCode.apply(null,u.subarray(i,i+32768));return btoa(s)}"""
shilin = case_path.read_text(encoding="utf-8")
WRAPPED = "幫你整理好了，請貼到 App：\n```json\n" + shilin + "\n```\n以上，有問題再跟我說 {備註}"
def paste(pg, text):
    pg.fill("#paste", text); pg.click("#addpaste"); return pg.text_content("#pastemsg")
def labels(pg): return pg.eval_on_selector_all("#cases label", "els=>els.map(e=>e.textContent)")
def pick_pasted(pg, idx=0):
    vals = pg.eval_on_selector_all("input[name=c]", "els=>els.map(e=>e.value)")
    v = [x for x in vals if x.startswith("pasted_")][idx]; pg.check(f"input[value='{v}']"); return v
def gen(pg, t, s="original", name=None):
    pg.select_option("#tpl", t)
    if t == "classic": pg.select_option("#skin", s)
    pg.evaluate("window.__lastResult=null"); pg.click("#go")
    pg.wait_for_function("window.__lastResult && !document.getElementById('go').disabled", timeout=120000)
    res = pg.text_content("#result")
    if name: (out / name).write_bytes(base64.b64decode(pg.evaluate(B64)))
    return res
# 右上圖在各版型的位置：新第一版是內縮的 400×231 圓角小卡（624,18）～（1024,249），淺色與原版是 503×290 貼齊右上（只比資訊列以上 262）
def hero_region(png_img, ref_img, template):
    if template == "classic":
        box = png_img.crop((634, 28, 1014, 239)); ref = ref_img.resize((400, 231), Image.LANCZOS).crop((10, 10, 390, 221))
    else:
        box = png_img.crop((577, 0, 1080, 262)); ref = ref_img.crop((0, 0, 503, 262))
    tol = 25 if template == "classic" else 13   # 新第一版的圖由瀏覽器縮成 400×231，和這裡用 PIL 縮的參考圖有細微色差
    return sum(ImageChops.difference(box, ref).convert("L").histogram()[:tol]) / (box.width * box.height) * 100
def hero_same(png, ref_img, template):
    return hero_region(Image.open(png).convert("RGB"), ref_img, template)
try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={"width": 393, "height": 852}, device_scale_factor=3, is_mobile=True, has_touch=True)
        ctx.on("request", lambda r: net.append(r.url))
        pg = ctx.new_page(); pg.goto(URL); pg.wait_for_selector("input[name=c]")
        pg.evaluate("navigator.serviceWorker.ready"); pg.reload(); pg.wait_for_selector("input[name=c]")
        rec("版本 0.3.0", "版本 0.3.0" in pg.text_content("#ver"), pg.text_content("#ver"))
        # (b) 不是 JSON／不是小卡資料
        m = paste(pg, "這是一段說明文字，不是小卡資料 {沒有引號: 1}")
        rec("(b) 貼不是 JSON 的字 → 提示", m == "貼上的內容不是小卡資料", m)
        m2 = paste(pg, '```json\n{"format": "something-else", "source": {}, "card": {}}\n```')
        rec("(b) 貼 JSON 但不是小卡格式 → 提示", m2 == "貼上的內容不是小卡資料", m2)
        rec("(b) 都沒有加入清單", not any("（貼上）" in x for x in labels(pg)), labels(pg))
        # (a) 帶圍欄與前後文字的士林案
        m = paste(pg, WRAPPED)
        rec("(a) 抽出 JSON 並加入", m.startswith("已加入："), m)
        rec("(a) 清單出現（貼上）", any(x.endswith("（貼上）") for x in labels(pg)), labels(pg))
        pick_pasted(pg)
        jobs = [("classic", s) for s in ["original","style1","style1_print","style2","style3","style4","style5","style6","style7"]] + [("light","original"),("standard","original")]
        worst = 0
        for t, s in jobs:
            res = gen(pg, t, s, f"{t}_{s}.png")
            a = Image.open(ref / f"{t}_{s}.png").convert("RGB"); bb = Image.open(out / f"{t}_{s}.png").convert("RGB")
            for im in (a, bb): ImageDraw.Draw(im).rectangle([577, 0, 1079, 289], fill=0)
            n = sum(ImageChops.difference(a, bb).convert("L").histogram()[33:]) / 1080 / 1620 * 100; worst = max(worst, n)
            rec(f"(a) 貼上案例出圖 {t}/{s}", res.startswith("檢查全部通過") and n < 0.2, f"{res[:16]}｜和標準答案差>32 {n:.3f}%（右上那格排除）")
        jpg = Image.open(serve / "repo/hero_library/overwork_night_desk_photo.card.jpg").convert("RGB")
        rec("(a) 貼上案例右上是照片（三個版型）", min(hero_same(out / f"{t}_original.png", jpg, t) for t in ("classic", "light", "standard")) > 85)
        # 4. 缺圖改用預設圖
        d = json.loads(shilin); d["title"] = "測試：圖檔都不存在"
        d["card"]["hero"].pop("image", None); d["card"]["hero"]["photo"] = "no_such_photo.png"; d["card"]["hero"]["file"] = "no_such.svg"
        m = paste(pg, json.dumps(d, ensure_ascii=False)); rec("缺圖案例加入", m.startswith("已加入："), m)
        pick_pasted(pg, 1)
        # 圖檔都不存在、沒寫類型：三個版型都改用 overwork 類型圖，並註明「示意圖尚未配置」
        ow = Image.open(serve / "repo/hero_library/type_overwork.card.jpg").convert("RGB")
        for t in ("standard", "classic", "light"):
            res = gen(pg, t, name=f"missing_{t}.png")
            rec(f"缺圖：{t} 用 overwork 類型圖＋註明、照樣出圖", res.startswith("檢查全部通過") and "示意圖尚未配置" in res and hero_same(out / f"missing_{t}.png", ow, t) > 85, res[:16])
        # (c) 重開還在
        pg.reload(); pg.wait_for_selector("input[name=c]")
        n_p = sum(x.endswith("（貼上）") for x in labels(pg))
        rec("(c) 重開 App 貼上的案例還在（2 筆）", n_p == 2, labels(pg))
        # 刪除
        pg.click(".caserow button >> nth=1"); m = pg.text_content("#pastemsg")
        pg.reload(); pg.wait_for_selector("input[name=c]")
        rec("刪除後重開也不見（剩 1 筆）", m.startswith("已刪除：") and sum(x.endswith("（貼上）") for x in labels(pg)) == 1, m)
        # 12. iPhone SE 寬度不用左右捲動
        pg.set_viewport_size({"width": 320, "height": 568})
        sw = pg.evaluate("()=>[document.documentElement.scrollWidth, document.documentElement.clientWidth]")
        rec("iPhone SE 寬度不用左右捲動", sw[0] <= sw[1], sw)
        pg.set_viewport_size({"width": 393, "height": 852})
        # (d) 飛航模式：照樣能貼、能出圖
        ctx.set_offline(True); pg.reload(); pg.wait_for_selector("input[name=c]")
        m = paste(pg, WRAPPED); pick_pasted(pg, 1)
        res = gen(pg, "standard", name="offline_standard.png")
        rec("(d) 斷網貼上＋出圖", m.startswith("已加入：") and res.startswith("檢查全部通過"), f"{m[:20]}｜{res[:16]}")
        res = gen(pg, "classic", "style3")
        rec("(d) 斷網出圖（新第一版 style3）", res.startswith("檢查全部通過"), res[:16])
        ctx.set_offline(False)
        # localStorage 存不住
        ctx2 = b.new_context(viewport={"width": 393, "height": 852})
        ctx2.add_init_script("Storage.prototype.setItem=function(){throw new DOMException('QuotaExceededError','QuotaExceededError')};Storage.prototype.getItem=function(){throw new DOMException('SecurityError','SecurityError')};")
        ctx2.on("request", lambda r: net.append(r.url))
        pg2 = ctx2.new_page(); pg2.goto(URL); pg2.wait_for_selector("input[name=c]")
        m = paste(pg2, WRAPPED)
        rec("存不住：提示「這台手機存不住，關掉就不見」且清單有", "這台手機存不住，關掉就不見" in m and any(x.endswith("（貼上）") for x in labels(pg2)), m)
        pick_pasted(pg2); res = gen(pg2, "light")
        rec("存不住：照樣能出圖", res.startswith("檢查全部通過"), res[:16])
        b.close()
finally:
    srv.terminate()
ext = sorted({u for u in net if not u.startswith(("http://127.0.0.1:8825/", "data:", "blob:"))})
rec("(e) 沒有連到外部網址", not ext, ext or f"共 {len(net)} 個請求，全部是本機")
(out / "network_log.txt").write_text("\n".join(net))
print("全部通過" if all(R.values()) else f"{sum(not v for v in R.values())} 項沒過")
