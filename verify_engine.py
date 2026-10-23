"""驗收基準：用 cases/ 裡的士林案，透過出圖程式（casecard/engine）出圖，確認這台電腦能正常產生小卡。

用法：python verify_engine.py
成功：最後一行「全部通過」，並在 verify_out/ 產生 9 張新第一版（每種風格一張）＋淺色、原版各一張。
這支只示範「怎麼呼叫出圖程式」，App 畫面請另外寫；呼叫方式照這裡就不會出錯。
"""
from __future__ import annotations
import copy
import datetime as dt
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "casecard" / "engine"))
import render as engine  # noqa: E402
import skins  # noqa: E402

FRIENDLY = {
    "C01": "圖卡內容缺少必要欄位", "C02": "金額加總對不上", "C03": "來源卡必須剛好一張",
    "C04": "過失相抵計算對不上", "C05": "這個風格的文字顏色太淡", "L01": "某個區塊內容太多、超出框線",
    "L02": "有文字超出所屬的框", "L03": "文字太多，整張圖放不下", "L04": "有文字小於 18px",
    "L05": "黑色標題條尺寸不符", "L06": "區塊互相重疊", "L07": "最底下的免責說明被擠出畫面",
    "L08": "來源卡必須剛好一張", "L09": "案號、金額等必須出現的字沒有出現在圖上",
    "L10": "風格的裝飾壓到文字", "F01": "用到隨包以外的字型", "F02": "字型檔沒有記錄到", "P01": "PNG 格式異常",
}


def build_card(case: dict, template: str, skin: str, draft: bool) -> dict:
    """把案例檔組成出圖程式要的 card_content。法院、案號、日期一律從 source 帶入。"""
    src = case["source"]
    card = copy.deepcopy(case["card"])
    day = dt.date.fromisoformat(src["decision_date"])
    info = dict(card.get("info") or {})
    info.update({"court": src["court"], "case_no": src["case_number"], "date": f"{day.year} 年 {day.month} 月 {day.day} 日"})
    info.setdefault("date_pending", False)
    card["info"] = info
    card["template"] = template
    card["skin"] = skin                                   # 非 classic 版型只能用 "original"
    card["source"] = {"verified_against_analysis": not draft}   # False＝右上角出現「草稿」
    immutable = list(card.get("immutable_checks") or [])
    for value in (info["court"], info["case_no"], info["date"]):
        if value not in immutable:
            immutable.append(value)
    card["immutable_checks"] = immutable
    return card


def svg_to_png(svg: Path, out_png: Path, w: int, h: int):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        br = p.chromium.launch(args=engine.CHROME_ARGS)
        page = br.new_context(viewport={"width": w, "height": h}, device_scale_factor=1).new_page()
        page.set_content(f'<html><body style="margin:0">{svg.read_text(encoding="utf-8")}</body></html>')
        page.screenshot(path=str(out_png), clip={"x": 0, "y": 0, "width": w, "height": h})
        br.close()


def render_one(case: dict, template: str, skin: str, draft: bool, out_png: Path):
    work = ROOT / "casecard" / "_work" / f"{template}_{skin}"
    shutil.rmtree(work, ignore_errors=True)
    (work / "case").mkdir(parents=True)
    (work / "case" / "card_content.json").write_text(json.dumps(build_card(case, template, skin, draft), ensure_ascii=False), encoding="utf-8")
    hero = case["card"].get("hero") or {}
    for key, target in (("file", None), ("photo", "hero.png")):
        if hero.get(key) and (ROOT / "hero_library" / hero[key]).exists():
            shutil.copyfile(ROOT / "hero_library" / hero[key], work / "case" / (target or hero[key]))
    # 示意圖暫換：照片沒進公開程式庫，原版右上改用 hero.file 的 SVG（轉成 503×290 的 hero.png）
    if hero.get("file") and not (work / "case" / "hero.png").exists():
        svg_to_png(ROOT / "hero_library" / hero["file"], work / "case" / "hero.png", 503, 290)
    report = engine.render(work / "case", work / "out", False, template)
    shutil.copyfile(work / "out" / "card_preview.png", out_png)
    shutil.rmtree(work, ignore_errors=True)
    bad = [c["id"] for c in report["checks"] if not c["pass"]]
    return bad, len(report["checks"])


def main():
    case = json.loads((ROOT / "cases" / "shilin_110_laosu_72.json").read_text(encoding="utf-8"))
    out = ROOT / "verify_out"
    out.mkdir(exist_ok=True)
    jobs = [("classic", s["id"]) for s in skins.list_skins()] + [("light", "original"), ("standard", "original")]
    failed = 0
    for template, skin in jobs:
        bad, total = render_one(case, template, skin, True, out / f"{template}_{skin}.png")
        if bad:
            failed += 1
            print(f"未過 {template}/{skin}：" + "；".join(FRIENDLY.get(b[:3], b) for b in bad))
        else:
            print(f"通過 {template}/{skin}（{total} 項檢查）")
    print("全部通過" if not failed else f"{failed} 張沒過")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
