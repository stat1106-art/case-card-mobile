"""用 JavaScript 版引擎產生的 HTML＋手機用 woff2 字型出圖（Chromium），存成 PNG，給 compare_expected.py 比對。

用法：python tools/render_js_cards.py [輸出資料夾]（預設 verify_out_js）
這支只是在電腦上驗證版面；手機上的出圖（轉 PNG）在 App 裡做。
"""
import json
import subprocess
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "casecard" / "engine"))
import render as engine  # noqa: E402
import skins  # noqa: E402


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "verify_out_js"
    out.mkdir(parents=True, exist_ok=True)
    case_path = ROOT / "cases" / "shilin_110_laosu_72.json"
    jobs = [("classic", s["id"]) for s in skins.list_skins()] + [("light", "original"), ("standard", "original")]
    htmls = json.loads(subprocess.run(
        ["node", str(ROOT / "tools" / "js_card_html.mjs"), "--real", str(case_path), "1"] + [f"{t}:{s}" for t, s in jobs],
        check=True, capture_output=True, text=True, encoding="utf-8").stdout)
    with sync_playwright() as p:
        br = p.chromium.launch(args=engine.CHROME_ARGS)
        ctx = br.new_context(viewport={"width": engine.W, "height": engine.H}, device_scale_factor=1,
                             color_scheme="light", reduced_motion="reduce", locale="zh-TW")
        for t, s in jobs:
            html = htmls[f"{t}:{s}"]
            if html.startswith("ERROR"):
                raise SystemExit(f"{t}/{s}：{html}")
            page_file = out / f"{t}_{s}.html"
            page_file.write_text(html, encoding="utf-8")
            page = ctx.new_page()
            page.goto(page_file.resolve().as_uri(), wait_until="load")
            page.evaluate("Promise.all([...document.fonts].map(f=>f.load()))")
            page.wait_for_function("[...document.fonts].every(f=>f.status==='loaded')", timeout=15000)
            page.screenshot(path=str(out / f"{t}_{s}.png"), clip={"x": 0, "y": 0, "width": engine.W, "height": engine.H},
                            animations="disabled", caret="hide", scale="css")
            page.close()
            page_file.unlink()
            print(f"出圖 {t}/{s}")
        br.close()


if __name__ == "__main__":
    main()
