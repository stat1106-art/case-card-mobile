"""職災小卡 App v0.1.0：本機單頁程式。只開在 127.0.0.1，不連網。
用法：python app.py   （Windows 請雙擊 start_windows.cmd）
"""
from __future__ import annotations
import json
import secrets
import sys
import tempfile
import threading
import webbrowser
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from verify_engine import FRIENDLY, render_one, skins  # 沿用驗收基準的出圖寫法

HOST = "127.0.0.1"
CASES = ROOT / "cases"
TEMPLATES = [("classic", "新第一版"), ("light", "淺色資訊圖"), ("standard", "原版")]
LOCK = threading.Lock()
IMAGES: dict[str, bytes] = {}   # 畫面上的圖；下載直接回傳同一份位元組
DISCLAIMER = "案例內容由 AI 整理，正式使用前請自己對照判決核對。"


def load_cases():
    items = []
    for p in sorted(CASES.glob("*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            if not isinstance(data, dict) or not isinstance(data.get("card"), dict) or not isinstance(data.get("source"), dict):
                raise ValueError
            items.append({"file": p.name, "title": data.get("title") or p.stem, "ok": True})
        except Exception:
            items.append({"file": p.name, "title": p.name, "ok": False, "note": "這個檔讀不出來"})
    return items


def generate(file: str, template: str, skin: str, draft: bool):
    if template not in dict(TEMPLATES):
        return {"error": "版型不正確，請重新選擇。"}
    if template != "classic":
        skin = "original"
    if skin not in {s["id"] for s in skins.list_skins()}:
        return {"error": "風格不正確，請重新選擇。"}
    path = CASES / Path(file).name
    try:
        case = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"error": "這個檔讀不出來，請換一個案例或檢查檔案內容。"}
    with LOCK, tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "card.png"
        try:
            bad, total = render_one(case, template, skin, draft, out)
            data = out.read_bytes()
        except Exception:
            return {"error": "這個案例產生不出小卡，請檢查案例內容是否完整（法院、案號、判決日期、圖卡內容）。"}
    token = secrets.token_hex(8)
    IMAGES.clear()
    IMAGES[token] = data
    problems = []
    for b in bad:
        text = FRIENDLY.get(b[:3], "其他檢查沒過")
        if text not in problems:
            problems.append(text)
    return {"image": token, "total": total, "failed": problems,
            "name": f"{Path(file).stem}_{template}_{skin}{'_草稿' if draft else ''}.png"}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send(self, code, body: bytes, ctype, extra=None):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def json(self, obj):
        self.send(200, json.dumps(obj, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

    def do_GET(self):
        u = urlparse(self.path)
        q = parse_qs(u.query)
        if u.path == "/":
            self.send(200, (ROOT / "app_page.html").read_bytes(), "text/html; charset=utf-8")
        elif u.path == "/api/options":
            self.json({"cases": load_cases(), "templates": [{"id": i, "name": n} for i, n in TEMPLATES],
                       "skins": skins.list_skins(), "disclaimer": DISCLAIMER})
        elif u.path.startswith("/image/"):
            data = IMAGES.get(u.path.split("/")[-1])
            if data is None:
                return self.send(404, "找不到這張圖，請重新產生。".encode("utf-8"), "text/plain; charset=utf-8")
            extra = {}
            if "dl" in q:
                from urllib.parse import quote
                extra["Content-Disposition"] = "attachment; filename*=UTF-8''" + quote(q.get("name", ["card.png"])[0])
            self.send(200, data, "image/png", extra)
        else:
            self.send(404, b"", "text/plain")

    def do_POST(self):
        if urlparse(self.path).path != "/api/generate":
            return self.send(404, b"", "text/plain")
        try:
            req = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            self.json(generate(str(req.get("file", "")), str(req.get("template", "")), str(req.get("skin", "")), bool(req.get("draft", True))))
        except Exception:
            self.json({"error": "發生問題，請再試一次。"})


def main():
    nums = [a for a in sys.argv[1:] if a.isdigit()]
    port = int(nums[0]) if nums else 8765
    srv = ThreadingHTTPServer((HOST, port), Handler)
    url = f"http://{HOST}:{srv.server_address[1]}/"
    print(f"職災小卡已開啟：{url}\n要結束時，直接關掉這個黑色視窗。")
    if "--no-browser" not in sys.argv:
        webbrowser.open(url)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
