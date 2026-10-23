"""工作台 ↔ 出圖程式（casecard 0.8.0）的橋接。

工作台的案件案件資料是唯一正本：法院、案號、裁判日期一律從 source 帶入圖卡，不在圖卡內容另外維護。
出圖程式只負責排版與檢查；正式與否由工作台的人工核對＋看圖確認決定，不使用出圖程式自己的 final 旗標。
"""
from __future__ import annotations
import copy
import datetime as dt
import json
import shutil
import sys
import threading
import uuid
from pathlib import Path

from .validation import AppError, CARD_TEMPLATES, fail

APP_ROOT = Path(__file__).resolve().parent.parent
ENGINE_ROOT = APP_ROOT / "casecard"
HERO_LIBRARY = APP_ROOT / "hero_library"
# 暫存資料夾放在出圖程式資料夾內：Windows 上若放在別顆磁碟，出圖程式計算相對路徑會失敗
WORK_ROOT = ENGINE_ROOT / "_work"
_LOCK = threading.Lock()
_STATUS = None


def engine_status(refresh=False):
    """回傳 {available, message}。缺套件或缺瀏覽器元件時講清楚怎麼補，不自動安裝。"""
    global _STATUS
    if _STATUS is not None and not refresh:
        return _STATUS
    try:
        import PIL  # noqa: F401
        from playwright.sync_api import sync_playwright
    except ImportError:
        _STATUS = {"available": False, "message": "出圖程式尚未安裝：請關閉本視窗，雙擊 setup_first_time.cmd 安裝一次（需要網路），再重新啟動。"}
        return _STATUS
    try:
        with sync_playwright() as p:
            path = Path(p.chromium.executable_path)
        ok = path.exists()
    except Exception:
        ok = False
    _STATUS = ({"available": True, "message": "出圖程式可用"} if ok else
               {"available": False, "message": "出圖程式缺少瀏覽器元件：請雙擊 setup_first_time.cmd 安裝一次（需要網路），再重新啟動。"})
    return _STATUS


def format_date(value):
    """2026-06-12 → 2026 年 6 月 12 日（出圖程式與既有圖卡的寫法）。"""
    day = dt.date.fromisoformat(value)
    return f"{day.year} 年 {day.month} 月 {day.day} 日"


def build_card(case, template, mode, skin="original"):
    """把工作台案件組成出圖程式要的 card_content。缺必要來源資料就停止，不猜。"""
    if template not in CARD_TEMPLATES:
        fail("不支援此版型。", "unsupported_template")
    if mode not in ("draft", "final"):
        fail("出圖模式須為 draft 或 final。")
    if not isinstance(case.get("card"), dict):
        fail("此案件還沒有圖卡內容。請先匯入圖卡內容，或用「交給 AI 整理」補上，再按儲存。", "card_missing", 409)
    src = case["source"]
    missing = [label for key, label in (("court", "法院"), ("case_number", "完整案號"), ("decision_date", "判決日期")) if not src.get(key, "").strip()]
    if missing:
        fail("出圖前請先在「判決來源」填好：" + "、".join(missing) + "。圖卡上的法院、案號、日期都從這裡帶入。", "source_incomplete", 409, missing)
    card = copy.deepcopy(case["card"])
    info = dict(card.get("info") or {})
    info.update({"court": src["court"].strip(), "case_no": src["case_number"].strip(), "date": format_date(src["decision_date"])})
    info.setdefault("date_pending", False)
    card["info"] = info
    card["template"] = template
    if template != "classic" and skin != "original":
        fail("目前只有「新第一版」可以換風格；其他版型請用原版配色。", "skin_unsupported")
    if skin not in skin_ids():
        fail("找不到這個風格。", "unsupported_skin")
    card["skin"] = skin
    # 草稿一律帶「草稿」徽章；正式版預覽不帶。正式與否由工作台核對決定。
    card["source"] = {"verified_against_analysis": mode == "final"}
    immutable = list(card.get("immutable_checks") or [])
    for value in (info["court"], info["case_no"], info["date"]):
        if value not in immutable:
            immutable.append(value)
    card["immutable_checks"] = immutable
    card["case_id"] = case["id"]
    return card


def _hero_files(card):
    hero = card.get("hero") or {}
    files = {}
    for key, target in (("file", None), ("photo", "hero.png")):
        name = hero.get(key)
        if not name:
            continue
        if not isinstance(name, str) or "/" in name or "\\" in name or name.startswith("."):
            fail("示意圖檔名不正確（只能填 hero_library 資料夾裡的檔名）。", "invalid_hero")
        path = HERO_LIBRARY / name
        if not path.is_file():
            fail(f"示意圖檔案找不到：hero_library/{name}", "hero_missing", 409)
        files[target or name] = path
    return files


def friendly(check_id):
    """把檢查代號翻成白話，讓使用者知道要改哪裡。"""
    table = [
        ("C01", "圖卡內容缺少必要欄位，請補齊圖卡內容。"),
        ("C02", "金額加總對不上：分項相加不等於總額，請核對判決金額。"),
        ("C03", "來源卡必須剛好一張。"),
        ("C04", "過失相抵計算對不上：損害合計 × 比例 ≠ 過失相抵後金額，請核對金額流程。"),
        ("C05", "這個風格的文字顏色太淡，看不清楚。請換一個風格，或回報給製作者調色。"),
        ("L01", "某個區塊內容太多、超出框線，請精簡該區文字。"),
        ("L02", "有文字超出所屬的框，請精簡圖卡文字（不會自動縮字）。"),
        ("L03", "文字太多，整張圖放不下，請精簡圖卡文字（不會自動縮字或刪字）。"),
        ("L04", "有文字小於 18px 下限。"),
        ("L05", "黑色標題條尺寸不符規格。"),
        ("L06", "區塊互相重疊，請精簡文字。"),
        ("L07", "最底下的免責說明被擠出畫面，通常是文字太多，請精簡圖卡文字。"),
        ("L08", "來源卡必須剛好一張。"),
        ("L09", "案號、金額等必須出現的字沒有出現在圖上，請檢查圖卡內容。"),
        ("L10", "這個風格的裝飾圖形壓到文字了。請換一個風格，或回報給製作者。"),
        ("F01", "字型異常：圖上用到隨包以外的字型。"),
        ("F02", "字型檔沒有記錄到，請重新安裝或回報給製作者。"),
        ("P01", "PNG 格式異常。"),
    ]
    for prefix, text in table:
        if check_id.startswith(prefix):
            return text
    return "檢查未通過。"


def skin_ids():
    return {p.stem[len("skin_"):] for p in (ENGINE_ROOT / "skins").glob("skin_*.json")}


def skin_list():
    if str(ENGINE_ROOT / "engine") not in sys.path:
        sys.path.insert(0, str(ENGINE_ROOT / "engine"))
    import skins
    return skins.list_skins()


def render_case(case, template, mode, skin="original"):
    """出一張圖。回傳 {ok, status, checks, png}。checks 每項含白話說明。"""
    status = engine_status()
    if not status["available"]:
        raise AppError("engine_unavailable", status["message"], 503)
    card = build_card(case, template, mode, skin)
    heroes = _hero_files(card)
    if str(ENGINE_ROOT / "engine") not in sys.path:
        sys.path.insert(0, str(ENGINE_ROOT / "engine"))
    import render as engine  # casecard/engine/render.py
    with _LOCK:
        WORK_ROOT.mkdir(exist_ok=True)
        work = WORK_ROOT / uuid.uuid4().hex
        case_dir, out_dir = work / "case", work / "out"
        try:
            case_dir.mkdir(parents=True)
            (case_dir / "card_content.json").write_text(json.dumps(card, ensure_ascii=False, indent=2), encoding="utf-8")
            for name, path in heroes.items():
                shutil.copyfile(path, case_dir / name)
            try:
                report = engine.render(case_dir, out_dir, False, template)
            except (KeyError, TypeError, IndexError, ValueError) as error:
                # 圖卡內容格式不合版型需要（缺欄位、型別錯），以白話回報，不當成程式當機
                raise AppError("card_format", f"圖卡內容格式不符合「{CARD_TEMPLATES[template]}」版型：缺少或寫錯欄位 {error!s}。", 422)
            png = (out_dir / "card_preview.png").read_bytes()
        finally:
            shutil.rmtree(work, ignore_errors=True)
    checks = [{"id": c["id"], "pass": c["pass"], "hint": "" if c["pass"] else friendly(c["id"])} for c in report["checks"]]
    ok = all(c["pass"] for c in checks)
    return {"ok": ok, "status": "通過全部檢查" if ok else "要修改內容", "checks": checks, "png": png,
            "png_sha256": report["png_file_sha256"]}
