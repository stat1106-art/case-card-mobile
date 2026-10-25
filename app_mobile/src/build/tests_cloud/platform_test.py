import subprocess, sys, time
from playwright.sync_api import sync_playwright
srv = subprocess.Popen([sys.executable, "-m", "http.server", "8829", "--bind", "127.0.0.1", "-d", sys.argv[1]], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1)
B = "http://127.0.0.1:8829/repo/"; ok = True; net = []
WANT = sys.argv[2] if len(sys.argv) > 2 else "0.1.4"
try:
    with sync_playwright() as p:
        b = p.chromium.launch(); ctx = b.new_context(viewport={"width": 393, "height": 852}); ctx.on("request", lambda r: net.append(r.url))
        for page in ("index.html", "cases.html", "case.html", "check.html"):
            pg = ctx.new_page(); errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.goto(B + "platform/" + page); pg.wait_for_load_state("networkidle")
            v = pg.text_content("#pfVersion")
            good = v == f"平台版本 {WANT}" and not errs; ok &= good
            print(("PASS " if good else "FAIL ") + f"platform/{page} 頁尾「{v}」 程式錯誤 {errs or '無'}"); pg.close()
        # 案例庫的「查職安署重大職災」按鈕：網址、新分頁、說明小字（外部網站在測試裡擋掉，只看開到哪裡）
        pg = ctx.new_page(); pg.goto(B + "platform/cases.html"); pg.wait_for_load_state("networkidle")
        before = len(net)
        a = pg.locator("a.pf-btn", has_text="查職安署重大職災")
        info = {"n": a.count(), "href": a.get_attribute("href"), "target": a.get_attribute("target"), "rel": a.get_attribute("rel"),
                "note": pg.text_content(".pf-source"), "first": pg.evaluate("document.querySelector('main').children[1].textContent.trim()")}
        good = (info["n"] == 1 and info["href"] == "https://pacs.osha.gov.tw/2875/" and info["target"] == "_blank" and "noopener" in (info["rel"] or "")
                and info["note"] == "資料來源：勞動部職業安全衛生署 重大職業災害公開網" and info["first"] == "查職安署重大職災")
        print(("PASS " if good else "FAIL ") + f"案例庫上方按鈕與說明：{info}"); ok &= good
        ctx.route("https://pacs.osha.gov.tw/**", lambda r: r.abort())
        with ctx.expect_page() as newp: a.click()
        popup = newp.value; time.sleep(0.5)
        good = popup.url.startswith("https://pacs.osha.gov.tw/2875") or any(u.startswith("https://pacs.osha.gov.tw/2875") for u in net[before:])
        print(("PASS " if good else "FAIL ") + f"點按鈕開新分頁：{popup.url}"); ok &= good
        popup.close(); pg.close()
        clicked = [u for u in net if u.startswith("https://pacs.osha.gov.tw/")]
        for u in clicked: net.remove(u)
        pg = ctx.new_page(); pg.goto(B); pg.wait_for_selector("input[name=c]")
        pg.evaluate("navigator.serviceWorker.ready"); pg.reload(); pg.wait_for_selector("input[name=c]")
        keys = pg.evaluate("caches.keys()"); print("App 快取名稱：", keys); ok &= any(k.endswith(f"-platform-{WANT}") for k in keys)
        pg.click("#go"); pg.wait_for_function("window.__lastResult && !document.getElementById('go').disabled", timeout=120000)
        r = pg.text_content("#result"); print(("PASS " if r.startswith("檢查全部通過") else "FAIL ") + "App 出圖：" + r[:16]); ok &= r.startswith("檢查全部通過")
        print("App 版本：", pg.text_content("#ver"))
        b.close()
finally: srv.terminate()
ext = sorted({u for u in net if not u.startswith(("http://127.0.0.1:8829/", "data:", "blob:"))})
print(("PASS " if not ext else "FAIL ") + f"外部連線：{ext or '無'}"); ok &= not ext
print("全部通過" if ok else "有沒過")
