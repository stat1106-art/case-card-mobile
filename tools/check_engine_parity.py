"""比對：同一份案例，JavaScript 版引擎（src/js/engine）和 Python 原版（casecard/engine）產生的圖卡 HTML 是否一字不差。

用法：python tools/check_engine_parity.py [案例檔 ...]（預設 cases/ 全部＋docs 的兩個範例）
字型網址、示意圖網址兩邊都換成同一個代號再比，其餘每個字都要相同。不需要瀏覽器。
"""
import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "casecard" / "engine"))
sys.path.insert(0, str(ROOT))
import skins  # noqa: E402
import render as engine  # noqa: E402
from verify_engine import build_card  # noqa: E402


def py_html(case: dict, template: str, skin_id: str, draft: bool, case_dir: Path) -> str:
    """照 render.py 出圖前的準備步驟產生 HTML（不開瀏覽器）。"""
    c = build_card(case, template, skin_id, draft)
    c["_case_dir"] = str(case_dir)
    c["facts"] = [f if isinstance(f, dict) else {"text": f, "icon": "check"} for f in c.get("facts", [])]
    skin, _ = skins.load(c.get("skin") or skins.DEFAULT_SKIN)
    c["_skin_roles"] = skins.roles(skin)
    deco = skins.decorations(skin, c["_skin_roles"]) if c.get("template") == "classic" else []
    deco_css = skins.decoration_css(deco)
    base_bg = skins.page_background(skin, c["_skin_roles"])
    c["_page_bg"] = f"{deco_css}, {base_bg}" if deco_css else base_bg
    ref = lambda p: "@hero.png" if p.name == "hero.png" else "@fonts/" + p.name
    return engine.TEMPLATES[template].build_html(c, engine.ROOT, draft, ref)


def check(case_path: Path) -> int:
    case = json.loads(case_path.read_text(encoding="utf-8"))
    jobs = [("classic", s["id"]) for s in skins.list_skins()] + [("light", "original"), ("standard", "original")]
    bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        case_dir = Path(tmp)
        hero = case["card"].get("hero") or {}
        if hero.get("file"):
            (case_dir / hero["file"]).write_bytes((ROOT / "hero_library" / hero["file"]).read_bytes())
        (case_dir / "hero.png").write_bytes(b"")  # 只要存在；standard 版只引用網址
        for draft in (True, False):
            js = json.loads(subprocess.run(
                ["node", str(ROOT / "tools" / "js_card_html.mjs"), str(case_path), "1" if draft else "0"] + [f"{t}:{s}" for t, s in jobs],
                check=True, capture_output=True, text=True, encoding="utf-8").stdout)
            for t, s in jobs:
                a = py_html(copy.deepcopy(case), t, s, draft, case_dir)
                b = js[f"{t}:{s}"]
                if a == b:
                    print(f"一致 {case_path.name} {t}/{s} 草稿={'是' if draft else '否'}（{len(a):,} 字）")
                    continue
                bad += 1
                i = next((k for k in range(min(len(a), len(b))) if a[k] != b[k]), min(len(a), len(b)))
                print(f"不同 {case_path.name} {t}/{s} 草稿={'是' if draft else '否'}：第 {i} 字起\n  Python：{a[max(0, i - 60):i + 80]!r}\n  JS    ：{b[max(0, i - 60):i + 80]!r}")
    return bad


def main():
    paths = [Path(p) for p in sys.argv[1:]] or sorted((ROOT / "cases").glob("*.json"))
    paths = [p for p in paths if p.name != "index.json"]
    bad = sum(check(p) for p in paths)
    print("全部一致" if not bad else f"{bad} 組不一致")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
