"""v0.4.0 驗收：同仁畫面／管理頁貼上 GPT 回覆（Chromium，模擬 iPhone）。
用法：python admin_test.py <serve 資料夾> <輸出資料夾> <士林案 json> <reference/expected_png>"""
import base64, json, subprocess, sys, time
from pathlib import Path
from PIL import Image, ImageChops, ImageDraw
from playwright.sync_api import sync_playwright
serve, out, case_path, ref = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4])
URL = "http://127.0.0.1:8828/repo/"
srv = subprocess.Popen([sys.executable, "-m", "http.server", "8828", "--bind", "127.0.0.1", "-d", str(serve)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1)
R, net = {}, []
def rec(k, ok, d=""): R[k] = bool(ok); print(("PASS " if ok else "FAIL ") + k, str(d)[:220])
B64 = """async()=>{const b=window.__app.current.blob;const u=new Uint8Array(await b.arrayBuffer());let s='';for(let i=0;i<u.length;i+=32768)s+=String.fromCharCode.apply(null,u.subarray(i,i+32768));return btoa(s)}"""
shilin = case_path.read_text(encoding="utf-8")
second = json.loads(shilin); second["title"] = "測試：第二案（同一段回覆）"; second["card"]["hero"].pop("image", None); second["card"]["hero"]["hero_type"] = "fall"
GPT_ONE = ("好的，以下是本案整理結果。\n圖卡門檻：可供圖卡使用\n情境圖：overwork（深夜辦公室、過勞）\n\n```json\n" + shilin +
           "\n```\n\n如果要調整標題或白話說明，請告訴我。")
GPT_TWO = ("本次整理兩案。\n\n第一案\n情境圖：overwork\n```json\n" + shilin + "\n```\n\n第二案\n情境圖：fall\n```json\n" +
           json.dumps(second, ensure_ascii=False, indent=1) + "\n```\n以上。")
GPT_NONE = ("圖卡門檻：本案不適合現有版型\n說明：本案為程序裁定，沒有損害計算與金額流程，不產生圖卡資料。\n"
            "```json\n{\"verdict\": \"not_suitable\", \"reason\": \"程序裁定\"}\n```")
FORBIDDEN = ["JSON", "json", "貼上", "format", "case-card", "localStorage", "程式"]
def open_admin(pg): pg.click("#adminlink"); pg.wait_for_selector("#paste", state="visible")
def close_admin(pg): pg.click("#closeadmin"); pg.wait_for_selector("#go", state="visible")
def paste(pg, text): pg.fill("#paste", text); pg.click("#addpaste"); return pg.text_content("#pastemsg")
def labels(pg): return pg.eval_on_selector_all("#cases label", "els=>els.map(e=>e.textContent)")
def pick_local(pg, idx=0):
    vals = pg.eval_on_selector_all("input[name=c]", "els=>els.map(e=>e.value)")
    v = [x for x in vals if x.startswith("local_")][idx]; pg.check(f"input[value='{v}']")
def gen(pg, t, s="original", name=None):
    pg.select_option("#tpl", t)
    if t == "classic": pg.select_option("#skin", s)
    pg.evaluate("window.__lastResult=null"); pg.click("#go")
    pg.wait_for_function("window.__lastResult && !document.getElementById('go').disabled", timeout=120000)
    res = pg.text_content("#result")
    if name: (out / name).write_bytes(base64.b64decode(pg.evaluate(B64)))
    return res
def user_view_ok(pg):
    txt = pg.evaluate("document.getElementById('userview').innerText + document.querySelector('.ver').innerText")
    hits = [w for w in FORBIDDEN if w in txt]
    paste_visible = pg.evaluate("(()=>{const e=document.getElementById('paste');return !!(e&&e.offsetParent)})()")
    return (not hits and not paste_visible), hits
try:
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={"width": 393, "height": 852}, device_scale_factor=3, is_mobile=True, has_touch=True)
        ctx.on("request", lambda r: net.append(r.url))
        pg = ctx.new_page(); pg.goto(URL); pg.wait_for_selector("input[name=c]")
        pg.evaluate("navigator.serviceWorker.ready"); pg.reload(); pg.wait_for_selector("input[name=c]")
        rec("版本 0.4.0", "版本 0.4.0" in pg.text_content("#ver"), pg.text_content("#ver"))
        # (a) 同仁畫面
        ok, hits = user_view_ok(pg); rec("(a) 同仁畫面看不到貼上框、沒有程式字眼", ok, hits)
        pg.screenshot(path=str(out / "a_user_view_iphone15.png"), full_page=True)
        rec("(a) 「管理」入口在版本號旁", pg.evaluate("document.getElementById('adminlink').parentElement.querySelector('#ver')!==null"))
        # (c) 沒有小卡資料的回覆
        open_admin(pg)
        m = paste(pg, GPT_NONE)
        rec("(c) 沒有小卡資料 → 指定提示", m == "這段回覆裡沒有小卡資料，請確認 GPT 的圖卡門檻是『可供圖卡使用』", m)
        m2 = paste(pg, "謝謝，我再整理一下。")
        rec("(c) 純文字回覆 → 同一句提示", m2 == "這段回覆裡沒有小卡資料，請確認 GPT 的圖卡門檻是『可供圖卡使用』", m2)
        pg.screenshot(path=str(out / "c_no_card.png"), full_page=True)
        # (b) 整段 GPT 回覆
        m = paste(pg, GPT_ONE); rec("(b) 整段 GPT 回覆（前後文字＋情境圖行＋圍欄）→ 加入", m.startswith("已加入：1 案"), m)
        m = paste(pg, GPT_TWO); rec("(b) 一段回覆裡兩案 → 兩案都加入", m.startswith("已加入：2 案"), m)
        pg.screenshot(path=str(out / "b_admin_added.png"), full_page=True)
        rec("管理頁列出 3 案（僅本機）", pg.eval_on_selector_all("#localcases .case", "e=>e.length") == 3)
        close_admin(pg)
        rec("清單標「（僅本機）」", sum(x.endswith("（僅本機）") for x in labels(pg)) == 3, labels(pg))
        ok, hits = user_view_ok(pg); rec("回到同仁畫面仍看不到貼上框", ok, hits)
        # 僅本機案例出圖：11 張和標準答案比（右上那格排除）
        pick_local(pg)
        jobs = [("classic", s) for s in ["original","style1","style1_print","style2","style3","style4","style5","style6","style7"]] + [("light","original"),("standard","original")]
        for t, s in jobs:
            res = gen(pg, t, s, f"{t}_{s}.png")
            a = Image.open(ref / f"{t}_{s}.png").convert("RGB"); bb = Image.open(out / f"{t}_{s}.png").convert("RGB")
            for im in (a, bb): ImageDraw.Draw(im).rectangle([577, 0, 1079, 289], fill=0)
            n = sum(ImageChops.difference(a, bb).convert("L").histogram()[33:]) / 1080 / 1620 * 100
            rec(f"(b) 僅本機案例出圖 {t}/{s}", res.startswith("檢查全部通過") and n < 0.2, f"{res[:16]}｜差>32 {n:.3f}%")
        pg.screenshot(path=str(out / "b_user_after_generate.png"), full_page=True)
        # 重開還在、管理頁刪除
        pg.reload(); pg.wait_for_selector("input[name=c]")
        rec("重開 App 僅本機案例還在", sum(x.endswith("（僅本機）") for x in labels(pg)) == 3)
        open_admin(pg); pg.click("#localcases button >> nth=2"); m = pg.text_content("#pastemsg"); close_admin(pg)
        pg.reload(); pg.wait_for_selector("input[name=c]")
        rec("管理頁刪除後重開也不見", m.startswith("已刪除：") and sum(x.endswith("（僅本機）") for x in labels(pg)) == 2, m)
        # iPhone SE 寬度
        pg.set_viewport_size({"width": 320, "height": 568})
        sw = pg.evaluate("()=>[document.documentElement.scrollWidth, document.documentElement.clientWidth]")
        rec("iPhone SE 寬度不用左右捲動（同仁畫面）", sw[0] <= sw[1], sw)
        pg.screenshot(path=str(out / "a_user_view_iphoneSE.png"), full_page=True)
        open_admin(pg)
        sw = pg.evaluate("()=>[document.documentElement.scrollWidth, document.documentElement.clientWidth]")
        rec("iPhone SE 寬度不用左右捲動（管理頁）", sw[0] <= sw[1], sw); close_admin(pg)
        pg.set_viewport_size({"width": 393, "height": 852})
        # (d) 飛航模式：清單、出圖
        ctx.set_offline(True); pg.reload(); pg.wait_for_selector("input[name=c]")
        rec("(d) 斷網清單照常（內建＋僅本機）", len(labels(pg)) == 3, labels(pg))
        pg.check("input[value='shilin_110_laosu_72.json']")
        res = gen(pg, "classic", "style3", "d_offline_classic_style3.png"); rec("(d) 斷網出圖（內建案例 新第一版 style3）", res.startswith("檢查全部通過"), res[:16])
        pick_local(pg, 1); res = gen(pg, "standard", name="d_offline_local_standard.png"); rec("(d) 斷網出圖（僅本機案例 原版）", res.startswith("檢查全部通過"), res[:16])
        open_admin(pg); m = paste(pg, GPT_ONE); close_admin(pg); rec("(d) 斷網也能在管理頁加入", m.startswith("已加入：1 案"), m)
        ctx.set_offline(False)
        # 存不住
        ctx2 = b.new_context(viewport={"width": 393, "height": 852})
        ctx2.add_init_script("Storage.prototype.setItem=function(){throw new DOMException('QuotaExceededError','QuotaExceededError')};Storage.prototype.getItem=function(){throw new DOMException('SecurityError','SecurityError')};")
        ctx2.on("request", lambda r: net.append(r.url))
        pg2 = ctx2.new_page(); pg2.goto(URL); pg2.wait_for_selector("input[name=c]"); open_admin(pg2)
        m = paste(pg2, GPT_ONE); rec("存不住：提示「這台手機存不住，關掉就不見」", "這台手機存不住，關掉就不見" in m, m)
        b.close()
finally:
    srv.terminate()
ext = sorted({u for u in net if not u.startswith(("http://127.0.0.1:8828/", "data:", "blob:"))})
rec("不連外部網址", not ext, ext or f"共 {len(net)} 個請求，全部是本機")
print("全部通過" if all(R.values()) else f"{sum(not v for v in R.values())} 項沒過")
