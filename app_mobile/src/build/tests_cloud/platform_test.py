import subprocess, sys, time
from playwright.sync_api import sync_playwright
srv = subprocess.Popen([sys.executable, "-m", "http.server", "8829", "--bind", "127.0.0.1", "-d", sys.argv[1]], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1)
B = "http://127.0.0.1:8829/repo/"; ok = True; net = []
try:
    with sync_playwright() as p:
        b = p.chromium.launch(); ctx = b.new_context(viewport={"width": 393, "height": 852}); ctx.on("request", lambda r: net.append(r.url))
        for page in ("index.html", "cases.html", "case.html", "check.html"):
            pg = ctx.new_page(); errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.goto(B + "platform/" + page); pg.wait_for_load_state("networkidle")
            v = pg.text_content("#pfVersion")
            good = v == "平台版本 0.1.4" and not errs; ok &= good
            print(("PASS " if good else "FAIL ") + f"platform/{page} 頁尾「{v}」 程式錯誤 {errs or '無'}"); pg.close()
        pg = ctx.new_page(); pg.goto(B); pg.wait_for_selector("input[name=c]")
        pg.evaluate("navigator.serviceWorker.ready"); pg.reload(); pg.wait_for_selector("input[name=c]")
        keys = pg.evaluate("caches.keys()"); print("App 快取名稱：", keys); ok &= any(k.endswith("-platform-0.1.4") for k in keys)
        pg.click("#go"); pg.wait_for_function("window.__lastResult && !document.getElementById('go').disabled", timeout=120000)
        r = pg.text_content("#result"); print(("PASS " if r.startswith("檢查全部通過") else "FAIL ") + "App 出圖：" + r[:16]); ok &= r.startswith("檢查全部通過")
        print("App 版本：", pg.text_content("#ver"))
        b.close()
finally: srv.terminate()
ext = sorted({u for u in net if not u.startswith(("http://127.0.0.1:8829/", "data:", "blob:"))})
print(("PASS " if not ext else "FAIL ") + f"外部連線：{ext or '無'}"); ok &= not ext
print("全部通過" if ok else "有沒過")
