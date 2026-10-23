"""風格（皮）→ 圖卡顏色角色。

風格檔沿用 AutoDeck 的 skin_*.json（12 個佈景主題色＋背景），圖卡模板只用「角色」取色，
換風格不改模板。skin_original.json 直接列出全部角色（原版顏色），用來證明換成角色寫法後圖面不變。
「尚待確認」橘框與「草稿」標記是警示色，不跟著風格變，不在這裡。
"""
import json
from pathlib import Path

SKIN_DIR = Path(__file__).resolve().parent.parent / "skins"
DEFAULT_SKIN = "original"

# 角色 ← AutoDeck 佈景主題槽位。原則：原告／勞工側用 accent1、被告／雇主側用 accent2（每套皮兩者必不同），
# 黑色標題條、法院節點、頁尾用 dk2，卡片底 lt1、框線 accent4、淡底 lt2。
ROLE_SLOTS = {
    "page": "bg.center", "ink": "dk1", "ink2": "dk2", "muted": "accent3", "card": "lt1",
    "line": "accent4", "line2": "accent4", "dark": "dk2", "on_dark": "lt1", "footer_text": "lt1",
    "plaintiff": "accent1", "defendant": "accent2", "money": "accent1", "money_text": "lt1", "money_sub": "lt1",
    "deduct": "accent2", "pill_text": "accent1", "pill_bg": "lt2", "pill_line": "accent4",
    "adv_bg": "lt2", "adv_line": "accent4", "adv_ink": "dk2", "adv_pill_bg": "lt1", "dot_fill": "lt1",
}

# 文字對比（WCAG）：內文 4.5，大字／強調色 3.0（沿用 AutoDeck check.py 的門檻）
CONTRAST_PAIRS = [
    ("內文字 對 卡片底", "ink", "card", 4.5), ("標題字 對 頁面底", "ink", "page", 4.5),
    ("次要字 對 卡片底", "ink2", "card", 4.5), ("副標 對 頁面底", "ink2", "page", 4.5),
    ("灰標籤 對 卡片底", "muted", "card", 3.0), ("標題條白字 對 標題條", "on_dark", "dark", 4.5),
    ("頁尾字 對 頁尾", "footer_text", "dark", 4.5), ("原告色字 對 卡片底", "plaintiff", "card", 3.0),
    ("扣抵色字 對 卡片底", "deduct", "card", 3.0), ("判賠金額字 對 判賠色塊", "money_text", "money", 3.0),
    ("法院認定標籤", "pill_text", "pill_bg", 3.0), ("顧問區字 對 顧問區底", "adv_ink", "adv_bg", 4.5),
    ("圖示白字 對 原告節點", "on_dark", "plaintiff", 3.0), ("圖示白字 對 被告節點", "on_dark", "defendant", 3.0),
]


def list_skins():
    out = []
    for p in sorted(SKIN_DIR.glob("skin_*.json")):
        s = json.loads(p.read_text(encoding="utf-8"))
        out.append({"id": s["id"], "name": s["name"]})
    out.sort(key=lambda s: (s["id"] != DEFAULT_SKIN, s["id"]))
    return out


def load(skin_id):
    path = SKIN_DIR / f"skin_{skin_id}.json"
    if not skin_id or "/" in skin_id or "\\" in skin_id or not path.is_file():
        raise ValueError(f"找不到風格：{skin_id}")
    return json.loads(path.read_text(encoding="utf-8")), path


def roles(skin):
    if "card_roles" in skin:
        r = dict(skin["card_roles"])
    else:
        col = dict(skin["colors"]); col["bg.center"] = skin["bg"]["center"]
        r = {role: col[slot] for role, slot in ROLE_SLOTS.items()}
    missing = sorted(set(ROLE_SLOTS) - set(r))
    if missing:
        raise ValueError(f"風格 {skin['id']} 缺少顏色角色：{missing}")
    return {k: "#" + v.upper().lstrip("#") for k, v in r.items()}


def page_background(skin, k):
    """頁面背景 CSS：純色、左右邊緣加深（hgrad）、上下漸層（brushed，不加雜紋）。裝飾圖形本版先不畫。"""
    bg = skin.get("bg", {})
    if bg.get("type") == "hgrad":
        e, w = "#" + bg["edge"], bg.get("edge_width", 0.12) * 100
        return f"linear-gradient(90deg, {e} 0%, {k['page']} {w:.1f}%, {k['page']} {100 - w:.1f}%, {e} 100%)"
    if bg.get("type") == "brushed":
        return f"linear-gradient(180deg, #{bg['top']} 0%, #{bg['bottom']} 100%)"
    return k["page"]


def _lum(h):
    c = [int(h.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contrast(a, b):
    hi, lo = sorted([_lum(a), _lum(b)], reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def contrast_failures(k):
    out = []
    for label, fg, bg, need in CONTRAST_PAIRS:
        v = contrast(k[fg], k[bg])
        if v < need:
            out.append(f"{label} {k[fg]} / {k[bg]} = {v:.2f}（需 ≥ {need}）")
    return out


# ───────── 裝飾（只畫在留白處：左右約 50px 邊、頂端角落、標題左側）─────────
# 圖卡座標 1080×1620。卡片從 x=56 到 1024；標題第一行約 y=70–122、兩行到 y=174；頁尾約 y≥1568。
# 每個圖形都是多邊形，render.py 會逐一檢查不碰到任何文字（L10）。
import base64
import math


def _circle(cx, cy, r, n=48, wobble=None):
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        rr = r * (1 + (0.10 * math.sin(3 * t + wobble) + 0.06 * math.sin(5 * t + 2 * wobble) if wobble is not None else 0))
        pts.append((round(cx + rr * math.cos(t), 1), round(cy + rr * math.sin(t), 1)))
    return pts


def decorations(skin, k):
    """回傳 [{'poly': [(x, y), ...], 'fill': '#RRGGBB'}]。只用風格檔裡已有的顏色，不新增主色。"""
    sid, bg, dec = skin.get("id"), skin.get("bg", {}), skin.get("decor", {})
    col = {kk: "#" + v for kk, v in skin.get("colors", {}).items()}
    out = []
    add = lambda poly, fill: out.append({"poly": poly, "fill": fill})
    if dec.get("title_tag"):                       # style1：標題左側金色倒三角
        add([(22, 88), (46, 88), (34, 104)], col["accent1"])
    if "slab" in bg:                               # style1：右下斜切色塊，只在右側留白
        add([(1080, 1060), (1080, 1560), (1032, 1560)], "#" + bg["slab"]["color"])
    if dec.get("cover_band"):                      # style2：右側留白深藍直條
        add([(1032, 290), (1080, 290), (1080, 1560), (1032, 1560)], col["accent1"])
    if dec.get("title_bar"):                       # style3：標題左側黑色直條
        add([(30, 76), (40, 76), (40, 170), (30, 170)], col["accent1"])
    if "rail" in bg:                               # style4：左緣五色直條（裝飾色，不放字）
        cs, n = bg["rail"]["colors"], len(bg["rail"]["colors"])
        for i, c in enumerate(cs):
            add([(0, 1620 * i / n), (14, 1620 * i / n), (14, 1620 * (i + 1) / n), (0, 1620 * (i + 1) / n)], "#" + c)
    if dec.get("title_dot"):                       # style4：標題左側珊瑚紅圓點
        add(_circle(36, 96, 7, 24), col["accent6"])
    if "blobs" in bg:                              # style5：角落流體色塊（左上、右下）
        b = bg["blobs"]
        add(_circle(0, 0, 50, 72, b[0].get("phase", 0)), "#" + b[0]["color"])
        add(_circle(1080, 1540, 46, 72, b[1].get("phase", 0)), "#" + b[1]["color"])
    if dec.get("header_band"):                     # style6：左側深藍紫直條＋頂端色帶（標題區左半）
        add([(0, 0), (14, 0), (14, 1620), (0, 1620)], col["accent2"])
        add([(0, 0), (577, 0), (577, 14), (0, 14)], col["accent2"])
    if "corners" in bg:                            # style7：左上、右下深色斜角三角形
        c = "#" + bg["corners"]["color"]
        add([(0, 0), (64, 0), (0, 38)], c)
        add([(1080, 1566), (1018, 1566), (1080, 1528)], c)
    return out


def decoration_css(shapes):
    if not shapes:
        return ""
    body = "".join(f'<polygon points="{" ".join(f"{x},{y}" for x, y in s["poly"])}" fill="{s["fill"]}"/>' for s in shapes)
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1620" viewBox="0 0 1080 1620">{body}</svg>'
    return "url('data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode("ascii") + "') 0 0 / 1080px 1620px no-repeat"


def _inside(pt, poly):
    x, y, inside = pt[0], pt[1], False
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            inside = not inside
    return inside


def _seg_cross(a, b, c, d):
    o = lambda p, q, r: (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    return (o(a, b, c) * o(a, b, d) < 0) and (o(c, d, a) * o(c, d, b) < 0)


def touches(poly, rect, pad=2):
    """多邊形是否碰到文字框（外擴 pad px 當安全距離）。"""
    l, t, r, b = rect[0] - pad, rect[1] - pad, rect[2] + pad, rect[3] + pad
    box = [(l, t), (r, t), (r, b), (l, b)]
    if any(l <= x <= r and t <= y <= b for x, y in poly) or any(_inside(p, poly) for p in box):
        return True
    edges = list(zip(poly, poly[1:] + poly[:1]))
    return any(_seg_cross(a, b2, c, d) for a, b2 in edges for c, d in zip(box, box[1:] + box[:1]))
