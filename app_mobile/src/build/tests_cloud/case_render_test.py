"""網站上每一個案例的新第一版都要「檢查全部通過」（0.5.0 起 App 只提供新第一版）；離線快取裝得起來；沒有外部連線。
用法：python case_render_test.py <serve 資料夾（內有 repo/）>  全部通過才回傳 0。"""
import json, subprocess, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright
serve = Path(sys.argv[1]); site = serve / "repo"
cases = json.loads((site / "cases/index.json").read_text(encoding="utf-8"))["cases"]
URL = "http://127.0.0.1:8832/repo/"
srv = subprocess.Popen([sys.executable, "-m", "http.server", "8832", "--bind", "127.0.0.1", "-d", str(serve)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1)
bad, net = 0, []
def rec(name, ok, detail=""):
    global bad
    bad += not ok; print(("PASS " if ok else "FAIL ") + name + (f"：{detail}" if detail else ""))
try:
    with sync_playwright() as p:
        b = p.chromium.launch(); ctx = b.new_context(viewport={"width": 393, "height": 852}); ctx.on("request", lambda r: net.append(r.url))
        pg = ctx.new_page(); pg.goto(URL); pg.wait_for_selector("input[name=c]")
        pg.evaluate("navigator.serviceWorker.ready"); pg.reload(); pg.wait_for_selector("input[name=c]")
        rec("離線快取接管頁面", pg.evaluate("!!navigator.serviceWorker.controller"))
        listed = pg.eval_on_selector_all("input[name=c]", "e=>e.map(x=>x.value)")
        rec(f"清單列出全部 {len(cases)} 案", sorted(listed) == sorted(cases), listed)
        for case in cases:
            for t in ("classic",):
                pg.check(f"input[value='{case}']"); pg.select_option("#tpl", t)
                pg.evaluate("window.__lastResult=null"); pg.click("#go")
                pg.wait_for_function("window.__lastResult && !document.getElementById('go').disabled", timeout=180000)
                res = pg.text_content("#result").strip()
                rec(f"{case} {t}", res.startswith("檢查全部通過"), res[:200])
        b.close()
finally:
    srv.terminate()
ext = sorted({u for u in net if not u.startswith(("http://127.0.0.1:8832/", "data:", "blob:"))})
rec("沒有外部連線", not ext, ext)
print("全部通過" if not bad else f"{bad} 項沒過")
sys.exit(1 if bad else 0)
