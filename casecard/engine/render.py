"""CASE-CARD PoC renderer（standard）。

用法：python engine/render.py <案件資料夾> [--out 輸出資料夾] [--final]

凍結線規則：本程式不呼叫任何模型、不縮字、不刪字、不換版型。
版面或內容檢查不過 → 狀態「需改文案」並照樣輸出預覽 PNG 供檢視；
--final 模式下任何檢查不過、文案未對照原始分析、或未有正式核准（source.final_approval），一律不產出正式檔（fail closed）。
"""
import argparse, hashlib, io, json, os, platform, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "engine"))
import template as T_STANDARD  # noqa: E402
import template_classic as T_CLASSIC  # noqa: E402
import template_light as T_LIGHT  # noqa: E402
# template_illustrated.py 不再出圖，但 light 版仍借用它的共用函式，檔案保留
TEMPLATES = {"standard": T_STANDARD, "classic": T_CLASSIC, "light": T_LIGHT}

W, H = 1080, 1620
ICC_PATH = ROOT / "assets/icc/sRGB_built-in_588.icc"
ICC_SHA = "ec356e881f5f5cb39fbdcc148b95d03ad8feef761738688ae35e768b77995b45"
FONT_PATH = ROOT / "assets/fonts/NotoSansTC-VF.ttf"
FONT_FAMILY_EXPECTED = "Noto Sans TC"  # 舊名保留；v0.7.0 起 F01 改用 typography.EXPECTED_FAMILIES
import typography  # noqa: E402
import skins  # noqa: E402
MIN_FONT_PX = 18
CHROME_ARGS = ["--force-color-profile=srgb", "--font-render-hinting=none",
               "--disable-lcd-text", "--hide-scrollbars", "--disable-gpu"]

def sha(b: bytes) -> str: return hashlib.sha256(b).hexdigest()
def fsha(p: Path) -> str: return sha(p.read_bytes())

# ─────────────── 內容檢查（渲染前） ───────────────
def content_checks(c: dict):
    out = []
    req = ["tags", "title", "subtitle", "info", "parties", "basics", "relation", "facts",
           "result", "holdings", "advisory", "source_card", "disclaimer"]
    miss = [k for k in req if k not in c]
    out.append(("C01 必要欄位齊全", not miss, f"缺：{miss}" if miss else "齊全"))
    for sc in c.get("sum_checks", []):
        parts = [int(x.replace(",", "")) for x in sc["parts"]]
        tot = int(sc["total"].replace(",", ""))
        out.append(("C02 金額加總一致", sum(parts) == tot, f"{' + '.join(sc['parts'])} = {sum(parts):,}；標示 {sc['total']}"))
    fl = c.get("result", {}).get("flow")
    if fl:
        # 工作台 v0.2.0：比例改從 fault_op（例「× 90%」）讀出，不再寫死 90%；讀不到比例就判失敗，不猜
        import re
        try:
            dmg = int(fl["damage_total"].replace(",", "").replace(" 元", ""))
            aft = int(fl["after_fault"].replace(",", "").replace(" 元", ""))
            m = re.search(r"(\d+(?:\.\d+)?)\s*%", fl.get("fault_op", ""))
            rate = float(m.group(1)) / 100 if m else None
        except (KeyError, ValueError, AttributeError):
            dmg = aft = rate = None
        if rate is None or dmg is None:
            out.append(("C04 損害合計 × 過失比例 等於過失相抵後金額", False, "金額流程格式無法讀取（damage_total／after_fault／fault_op 的百分比）"))
        else:
            out.append(("C04 損害合計 × 過失比例 等於過失相抵後金額", round(dmg * rate) == aft,
                        f"{dmg:,} × {rate:g} = {dmg*rate:,.1f}；標示 {aft:,}"))
    n_src = 1 if isinstance(c.get("source_card"), dict) else 0
    out.append(("C03 單一來源卡", n_src == 1, f"來源卡數 {n_src}"))
    return out

# ─────────────── 版面量測（瀏覽器內） ───────────────
JS_MEASURE = r"""
(args) => {
  const {minFont, immutable} = args;
  const R = e => e.getBoundingClientRect();
  const res = {overflow:[], clipped:[], small:[], chips:[], sections:[], missing:[], outside:[], textRects:[]};
  // 1. 容器溢出
  document.querySelectorAll('.box,.row,.hc,.ac,.head-l,.finding,.pending,.disc,.draftbar').forEach(e=>{
    if (e.scrollHeight > e.clientHeight + 1 || e.scrollWidth > e.clientWidth + 1)
      res.overflow.push({cls:e.className, id:e.id, sh:e.scrollHeight, ch:e.clientHeight, sw:e.scrollWidth, cw:e.clientWidth});
  });
  // 2. 文字節點：字級、是否超出所屬容器或畫布
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let n; let textNodes = 0;
  while ((n = walker.nextNode())) {
    if (!n.textContent.trim()) continue;
    const el = n.parentElement; textNodes++;
    const fs = parseFloat(getComputedStyle(el).fontSize);
    if (fs < minFont) res.small.push({t:n.textContent.trim().slice(0,20), fs});
    const rg = document.createRange(); rg.selectNodeContents(n);
    const host = el.closest('.hc,.ac,.finding,.pending,.box,.disc,.draftbar,.head-l,.tag,.sh') || document.body;
    const hr = R(host);
    for (const r of rg.getClientRects()) {
      res.textRects.push([r.left, r.top, r.right, r.bottom, n.textContent.trim().slice(0,12)]);
      if (r.left < hr.left - 0.5 || r.right > hr.right + 0.5 || r.top < hr.top - 0.5 || r.bottom > hr.bottom + 0.5)
        res.clipped.push({t:n.textContent.trim().slice(0,20), host:host.className});
      if (r.left < 0 || r.top < 0 || r.right > 1080 || r.bottom > 1620)
        res.outside.push({t:n.textContent.trim().slice(0,20)});
    }
  }
  res.textNodes = textNodes;
  // 3. r9 標題條貼合：左右 8px、上下 5px
  document.querySelectorAll('.sh, .chip').forEach(ch=>{
    const kind = ch.classList.contains('sh') ? 'r9' : 'classic';
    const tx = kind === 'r9' ? ch.querySelector('.sh-t') : ch;
    const c = R(ch), sv = ch.querySelector('svg');
    const rg = document.createRange(); rg.selectNodeContents(tx); const t = rg.getBoundingClientRect();
    const ic = sv ? R(sv) : t;
    res.chips.push({kind, t:tx.textContent, padL:+(ic.left-c.left).toFixed(2), padR:+(c.right-t.right).toFixed(2),
                    padT:+(Math.min(ic.top,t.top)-c.top).toFixed(2), padB:+(c.bottom-Math.max(ic.bottom,t.bottom)).toFixed(2)});
  });
  // 4. 區塊順序與間距
  document.querySelectorAll('#card > *').forEach(e=>{const r=R(e); res.sections.push({id:e.id||e.className, top:r.top, bottom:r.bottom, ov:e.dataset.overlap||''});});
  // 5. 不可變字串存在
  const txt = document.body.innerText.replace(/\s+/g,'');
  immutable.forEach(s=>{ if (!txt.includes(s.replace(/\s+/g,''))) res.missing.push(s); });
  res.srcCount = document.querySelectorAll('#s-src').length;
  res.lastId = [...document.querySelectorAll('#card > *')].pop().id;
  res.fontStatus = [...document.fonts].map(f=>f.family+':'+f.status);
  return res;
}
"""

def cdp_font_check(page):
    """以 CDP CSS.getPlatformFontsForNode 查每個含文字元素實際使用的字型。"""
    s = page.context.new_cdp_session(page)
    s.send("DOM.enable"); s.send("CSS.enable")
    root = s.send("DOM.getDocument", {"depth": -1})["root"]["nodeId"]
    ids = s.send("DOM.querySelectorAll", {"nodeId": root, "selector": "body *"})["nodeIds"]
    fams, glyphs, nodes = {}, 0, 0
    for nid in ids:
        try:
            fonts = s.send("CSS.getPlatformFontsForNode", {"nodeId": nid})["fonts"]
        except Exception:
            continue
        if fonts: nodes += 1
        for f in fonts:
            key = f"{f['familyName']}|custom={f.get('isCustomFont')}"
            fams[key] = fams.get(key, 0) + f["glyphCount"]; glyphs += f["glyphCount"]
    s.detach()
    return {"families": fams, "glyphs": glyphs, "nodes_with_text": nodes}

def render(case_dir: Path, out_dir: Path, final: bool, template: str = None):
    from playwright.sync_api import sync_playwright
    from PIL import Image
    import PIL, playwright

    c = json.loads((case_dir / "card_content.json").read_text(encoding="utf-8"))
    c["_case_dir"] = os.path.relpath(case_dir, ROOT)
    if template:
        c["template"] = template
    # 舊格式（純文字事實）統一轉成 {text, icon}，各版型只處理一種格式
    c["facts"] = [f if isinstance(f, dict) else {"text": f, "icon": "check"} for f in c.get("facts", [])]
    verified = bool(c.get("source", {}).get("verified_against_analysis"))
    draft = not verified
    # v0.6.1：施工者自查只能讓預覽去掉草稿徽章；正式檔另需正式核准（GPT 事實審查＋主視覺沿用核准），缺就拒絕
    fa = c.get("source", {}).get("final_approval") or {}
    approved = fa.get("approved") is True and bool(str(fa.get("by", "")).strip())

    out_dir.mkdir(parents=True, exist_ok=True)
    build = out_dir / "card.html"
    ref = lambda p: os.path.relpath(p, out_dir).replace(os.sep, "/")
    tmpl = TEMPLATES[c.get("template", "standard")]
    # v0.8.0：風格（皮）。只有 classic 用角色取色；其他版型固定原色，指定別的風格就停止，不悄悄忽略
    skin_id = c.get("skin") or skins.DEFAULT_SKIN
    if c.get("template") != "classic" and skin_id != skins.DEFAULT_SKIN:
        raise ValueError(f"版型 {c.get('template')} 尚未支援換風格（目前只有 classic）")
    skin, skin_path = skins.load(skin_id)
    c["_skin_roles"] = skins.roles(skin)
    deco = skins.decorations(skin, c["_skin_roles"]) if c.get("template") == "classic" else []
    deco_css = skins.decoration_css(deco)
    base_bg = skins.page_background(skin, c["_skin_roles"])
    c["_page_bg"] = f"{deco_css}, {base_bg}" if deco_css else base_bg
    html = tmpl.build_html(c, ROOT, draft, ref)
    build.write_text(html, encoding="utf-8")

    icc = ICC_PATH.read_bytes()
    assert sha(icc) == ICC_SHA, "固定 ICC 檔被更動"

    checks = content_checks(c)
    if c.get("template") == "classic":
        bad_contrast = skins.contrast_failures(c["_skin_roles"])
        checks.append(("C05 文字對比（內文 4.5、強調 3.0）", not bad_contrast,
                       bad_contrast or f"風格 {skin_id}：{len(skins.CONTRAST_PAIRS)} 組全部達標"))
    with sync_playwright() as p:
        br = p.chromium.launch(args=CHROME_ARGS)
        ctx = br.new_context(viewport={"width": W, "height": H}, device_scale_factor=1,
                             color_scheme="light", reduced_motion="reduce", locale="zh-TW")
        page = ctx.new_page()
        page.goto(build.resolve().as_uri(), wait_until="load")
        page.evaluate("document.fonts.ready")
        # v0.7.0：有些字型（例如只接管數字的窄體某一粗細）在本張圖可能沒用到，瀏覽器不會自動載入；主動全部載入再等
        page.evaluate("Promise.all([...document.fonts].map(f=>f.load()))")
        page.wait_for_function("[...document.fonts].every(f=>f.status==='loaded')", timeout=15000)
        m = page.evaluate(JS_MEASURE, {"minFont": MIN_FONT_PX, "immutable": c.get("immutable_checks", [])})
        fonts = cdp_font_check(page)
        png = page.screenshot(clip={"x": 0, "y": 0, "width": W, "height": H}, type="png",
                              animations="disabled", caret="hide", scale="css")
        browser_version = br.version
        br.close()

    # ── 版面檢查結果 ──
    checks.append(("L01 容器無溢出", not m["overflow"], m["overflow"] or "無"))
    checks.append(("L02 文字未超出所屬框（字形裁切）", not m["clipped"], m["clipped"] or f"檢查 {m['textNodes']} 個文字節點"))
    checks.append(("L03 文字未超出畫布", not m["outside"], m["outside"] or "無"))
    checks.append((f"L04 最小字級 ≥ {MIN_FONT_PX}px", not m["small"], m["small"] or "全部符合"))
    # r9（原版，含圖示）：左右 8、上下 5；classic（無圖示）：左右 10±1 且左右對稱、字不超出條框上下（容差 1px）
    def chip_ok(x):
        if x.get("kind") == "classic":
            return 9 <= x["padL"] <= 11 and 9 <= x["padR"] <= 11 and abs(x["padL"] - x["padR"]) <= 1 and x["padT"] >= -1 and x["padB"] >= -1
        return 7 <= x["padL"] <= 9 and 7 <= x["padR"] <= 9 and 3 <= x["padT"] <= 7 and 3 <= x["padB"] <= 7
    bad_chip = [x for x in m["chips"] if not chip_ok(x)]
    kinds = sorted({x.get("kind", "r9") for x in m["chips"]})
    checks.append(("L05 標題條貼合（r9：左右8／上下5；classic：左右10且對稱、字不出框）", not bad_chip,
                   bad_chip or (f"{len(m['chips'])} 條全數符合（{'、'.join(kinds)} 規格）" if m['chips'] else "不適用（此版型無黑底標題條）")))
    secs = m["sections"]
    overlap = [(a["id"], b["id"]) for a, b in zip(secs, secs[1:]) if b["top"] < a["bottom"] - 0.5 and b.get("ov") != "ok"]
    checks.append(("L06 區塊不重疊", not overlap, overlap or "無"))
    checks.append(("L07 免責聲明為最後區塊且貼齊底部", m["lastId"] == "s-disc" and abs(secs[-1]["bottom"] - H) < 0.5,
                   f"最後區塊 {m['lastId']}，底 {secs[-1]['bottom']}"))
    checks.append(("L08 來源卡唯一", m["srcCount"] == 1, f"{m['srcCount']}"))
    checks.append(("L09 不可變字串全數出現在圖面", not m["missing"], m["missing"] or f"{len(c.get('immutable_checks', []))} 項全部出現"))
    if deco:
        hits = sorted({tr[4] for shp in deco for tr in m["textRects"] if skins.touches(shp["poly"], tr[:4])})
        checks.append(("L10 裝飾不壓字", not hits, hits or f"{len(deco)} 個裝飾圖形，未碰到任何文字"))
    fam_ok = all(k.startswith(typography.EXPECTED_FAMILIES) and k.endswith("|custom=True") for k in fonts["families"])
    checks.append(("F01 實際字形無系統字型 fallback（CDP）", fam_ok and fonts["glyphs"] > 0, fonts["families"]))
    font_hashes = {n: fsha(ROOT / "assets/fonts" / n) for n in sorted((ROOT / "assets/fonts").glob("*.ttf")) and [q.name for q in sorted((ROOT / "assets/fonts").glob("*.ttf"))]}
    checks.append(("F02 字型檔 hash 已記錄", True, font_hashes))

    # ── PNG：固定 ICC、無時間戳 ──
    im = Image.open(io.BytesIO(png)).convert("RGB")
    assert im.size == (W, H)
    buf = io.BytesIO()
    im.save(buf, format="PNG", icc_profile=icc, compress_level=9, optimize=False)
    png_bytes = buf.getvalue()
    checks.append(("P01 PNG 1080×1620 RGB＋固定 sRGB ICC", True, f"ICC {len(icc)} bytes, sha {ICC_SHA[:12]}…"))

    layout_ok = all(ok for _, ok, _ in checks)
    if not layout_ok:
        status = "需改文案"
    elif draft:
        status = "草稿可預覽（文案未對照原始分析）"
    else:
        status = "成功可預覽"

    name = "card_preview.png"
    if final:
        if not layout_ok or draft or not approved:
            status = "拒絕正式輸出：" + ("版面檢查未過" if not layout_ok else "文案未對照原始深入分析" if draft
                                     else "尚未完成正式核准（source.final_approval：GPT 案件事實審查、主視覺沿用核准）")
            name = None
        else:
            name = "card_final.png"
    if name:
        (out_dir / name).write_bytes(png_bytes)

    free = secs[-1]["top"] - secs[-2]["bottom"] if len(secs) > 1 else None
    report = {
        "status": status,
        "output": name,
        "png_file_sha256": sha(png_bytes),
        "png_pixel_sha256": sha(im.tobytes()),
        "png_size_bytes": len(png_bytes),
        "checks": [{"id": k, "pass": ok, "detail": d} for k, ok, d in checks],
        "observations": {"free_px_above_disclaimer": free, "chips": m["chips"], "font_status": m["fontStatus"],
                         "cdp_fonts": fonts},
        "inputs": {
            "card_content.json": fsha(case_dir / "card_content.json"),
            "hero": fsha(case_dir / c["hero"]["file"]) if c.get("hero") else (fsha(case_dir / "hero.png") if (case_dir / "hero.png").exists() else None),
            "standard.css": fsha(ROOT / "design/standard.css"),
            "template": fsha(Path(tmpl.__file__)), "template_name": c.get("template"),
            "skin": skin_id, "skin_file": fsha(skin_path), "skins.py": fsha(Path(skins.__file__)),
            "icons.py": fsha(ROOT / "engine/icons.py"),
            "render.py": fsha(Path(__file__)),
            "font": fsha(FONT_PATH), "fonts": {q.name: fsha(q) for q in sorted((ROOT / "assets/fonts").glob("*.ttf"))}, "icc": ICC_SHA, "card.html": sha(html.encode("utf-8")),
        },
        "environment": {"os": platform.platform(), "python": platform.python_version(),
                        "playwright": playwright.__version__ if hasattr(playwright, "__version__") else _pw_ver(),
                        "chromium": browser_version, "pillow": PIL.__version__, "chrome_args": CHROME_ARGS},
    }
    (out_dir / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return report

def _pw_ver():
    try:
        from importlib.metadata import version
        return version("playwright")
    except Exception:
        return "unknown"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("case_dir"); ap.add_argument("--out"); ap.add_argument("--final", action="store_true")
    ap.add_argument("--template", choices=sorted(TEMPLATES), help="覆寫 JSON 的 template 欄位")
    a = ap.parse_args()
    case_dir = Path(a.case_dir).resolve()
    out = Path(a.out).resolve() if a.out else ROOT / "out" / case_dir.name
    r = render(case_dir, out, a.final, a.template)
    print(f"狀態：{r['status']}")
    for ch in r["checks"]:
        print(("  PASS " if ch["pass"] else "  FAIL ") + ch["id"] + ("" if ch["pass"] else f"  → {ch['detail']}"))
    print(f"PNG sha256：{r['png_file_sha256']}\n像素 sha256：{r['png_pixel_sha256']}\n輸出：{out}")
    sys.exit(0 if all(c["pass"] for c in r["checks"]) else 2)

if __name__ == "__main__":
    main()
