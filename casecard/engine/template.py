"""card_content.json → HTML。只做排版，不改寫、不刪減文字。"""
import html, json
from pathlib import Path
from icons import icon
import typography

_esc = html.escape
_KEEP = []

def E(s):
    """跳脫 HTML；並把 display.keep_together 列出的詞包成不斷行（僅排版提示，不改文字）。"""
    out = _esc(str(s))
    for w in _KEEP:
        ew = _esc(w)
        out = out.replace(ew, f'<span class="nb">{ew}</span>')
    return out

def _join(parts):
    """把分行的短句接成一行：全形括號前不加空白，其餘以一個空白相接（與資料中「40 個月」的寫法一致）。"""
    out = ""
    for x in parts:
        out += x if (not out or x.startswith("（")) else " " + x
    return out

def mask_name(name: str) -> str:
    # 自然人姓名遮蔽：保留首尾字，中間以 ○ 取代（兩字名遮第二字）
    if len(name) <= 1: return name
    if len(name) == 2: return name[0] + "○"
    return name[0] + "○" * (len(name) - 2) + name[-1]

def party_name(p, display):
    if p.get("natural_person") and display.get("mask_natural_person_name"):
        return mask_name(p["name"])
    return p["name"]

def sec_head(ic, text, extra=""):
    # r9 規則：黑底標題條貼合圖示＋文字，左右 8px、上下 5px
    return (f'<div class="sh-row"><span class="sh" data-chk="chip">{icon(ic, 20, 2.2)}'
            f'<span class="sh-t">{E(text)}</span></span>{extra}</div>')

def label(kind):
    # 文字標示，不只靠顏色
    if kind == "court":
        return '<span class="lab lab-court">法院認定</span>'
    return '<span class="lab lab-adv">顧問分析｜非法院見解</span>'

def build_html(c: dict, root: Path, draft: bool, ref) -> str:
    d = c.get("display", {})
    _KEEP[:] = sorted(d.get("keep_together", []), key=len, reverse=True)
    info = c["info"]
    pl, df = c["parties"]["plaintiff"], c["parties"]["defendant"]
    pl_name, df_name = party_name(pl, d), party_name(df, d)

    tags = "".join(f'<span class="tag" data-chk="chip">{icon(i, 22, 2.2)}<span>{E(t)}</span></span>'
                   for i, t in zip(["court", "pulse"], c["tags"]))
    title = "".join(f'<span class="tl">{E(t)}</span>' for t in c["title"])
    sub = "".join(f'<span class="sl">{E(t)}</span>' for t in c["subtitle"])

    date_html = E(info["date"]) + ('<span class="pend-chip">待核</span>' if info.get("date_pending") else "")
    infobar = "".join(
        f'<div class="ib"><div class="ib-k">{icon(i, 20, 2.2)}<span>{k}</span></div><div class="ib-v">{v}</div></div>'
        for i, k, v in [("court", "法院", E(info["court"])), ("doc", "案號", E(info["case_no"])),
                        ("cal", "裁判日期", date_html), ("scale", "案由", E(info["cause"]))])

    basics = "".join(f'<div class="kv"><div class="k">{E(k)}</div><div class="v">{E(v)}</div></div>'
                     for k, v in c["basics"])

    rel = c["relation"]
    relation = f'''
      <div class="rel">
        <div class="node"><div class="bub bub-g">{icon("person", 44, 2)}</div>
          <div class="nr">{E(pl["role"])}</div><div class="nn">{E(pl_name)}</div></div>
        <div class="mid">
          <div class="arrow-lab"><b>{E(rel["claim"]["label"])}</b><span>{E("（" + rel["claim"]["note"] + "）")}</span></div>
          <div class="arr arr-l"></div>
          <div class="arr arr-r"></div>
          <div class="arrow-lab"><b class="red">{E(rel["offset"]["label"])}</b><b class="red">{E(rel["offset"].get("amount", ""))}</b><span>{E("（" + rel["offset"]["note"] + "）")}</span></div>
        </div>
        <div class="node"><div class="bub bub-n">{icon("building", 44, 2)}</div>
          <div class="nr">{E(df["role"])}</div><div class="nn">{E(df_name)}</div></div>
      </div>
      '''

    # v0.3 起 facts 為 {text, icon}；相容舊的純字串
    facts = "".join(f'<li><span class="num">{i}</span><span class="ft">{E(t["text"] if isinstance(t, dict) else t)}</span></li>'
                    for i, t in enumerate(c["facts"], 1))

    r = c["result"]
    fl = r.get("flow")
    if fl:
        # 與 illustrated／light 共用同一份 result.flow＋notes；直式算式，只排版不改字
        res_body = (
            '<div class="ledger">'
            f'<div class="lg-row"><span class="lg-k">{E(fl["damage_label"])}</span><span class="lg-v">{E(fl["damage_total"])}</span></div>'
            f'<div class="lg-op"><b>{E(fl["fault_op"])}</b><span>{E(_join(fl["fault_lines"]))}</span></div>'
            f'<div class="lg-row"><span class="lg-k">{E(fl["after_label"])}</span><span class="lg-v">{E(fl["after_fault"])}</span></div>'
            f'<div class="lg-op"><b class="red">{E(fl["offset_op"])}</b><span>{E(_join(fl["offset_lines"]))}</span></div>'
            '</div>'
            f'<p class="res-note">{E(r["notes"])}</p>')
    else:
        res_body = '<ul class="res">' + "".join(f'<li>{E(t)}</li>' for t in r["lines"]) + '</ul>'

    hold_icons = ["clock", "chat", "shield", "coins"]
    show_issues = d.get("show_issues", True)
    issue_html = lambda h: f'<div class="hq">爭點｜{E(h["issue"])}</div>' if show_issues else ""
    holds = "".join(
        f'<div class="hc">{issue_html(h)}'
        f'<div class="hh"><span>{E(h["head"])}</span></div>'
        f'<div class="hb">{E(h["body"])}</div></div>'
        for h, ic in zip(c["holdings"], hold_icons))

    adv_icons = ["search", "group", "heart", "doc"]
    advs = "".join(
        f'<div class="ac"><div class="ah"><span>{E(a["head"])}</span></div>'
        f'<div class="ab">{E(a["body"])}</div></div>'
        for a, ic in zip(c["advisory"], adv_icons))

    s = c["source_card"]
    draft_bar = ('<div class="draftbadge" id="draftbadge">草稿｜法院內容尚未對照<br>原始深入分析，不得外流</div>'
                 if draft else "")

    font_url = ref(root / "assets/fonts/NotoSansTC-VF.ttf")
    css = (root / "design/standard.css").read_text(encoding="utf-8")
    hero = (root / c["_case_dir"] / "hero.png")
    hero_html = (f'<img class="hero" src="{ref(hero)}" alt="">' if hero.exists()
                 else '<div class="hero hero-ph">主視覺預留區<br>（尚無獨立素材）</div>')

    return f'''<!doctype html><html lang="zh-Hant-TW"><head><meta charset="utf-8">
<style>@font-face{{font-family:"CardSans";src:url("{font_url}") format("truetype");font-weight:100 900;font-display:block;}}</style>
<style>{css}</style>{typography.css(ref, root, 'h1, .sh-t, .hh, .ah', '.rt-v, .lg-v')}</head><body>
<main id="card">
  <header class="head">
    {hero_html}{draft_bar}
    <div class="head-l">
      <div class="tags">{tags}</div>
      <h1>{title}</h1>
      <p class="sub">{sub}</p>
    </div>
  </header>

  <section class="infobar box">{infobar}</section>

  <div class="row">
    <section class="box col" id="s-basic">{sec_head("person", "案件基本資料")}<div class="kvs">{basics}</div></section>
    <section class="box col" id="s-rel">{sec_head("group", "法律關係圖")}{relation}</section>
  </div>

  <div class="row rb">
    <section class="box col" id="s-facts">{sec_head("clip", "事實經過（工作負荷重點）")}
      <ol class="facts">{facts}</ol>
    </section>
    <section class="box col" id="s-result">{sec_head("gavel", "判決結果", '<div class="res-total"><span class="rt-k">被告應給付</span><span class="rt-v">' + E(r["total"]) + '</span></div>')}
      {res_body}
      <div class="pending">{icon("alert", 22, 2.2)}<div><b>尚待確認｜</b>{E(r["pending"])}</div></div>
    </section>
  </div>

  <section class="box" id="s-hold">{sec_head("scale", "法院核心見解", label("court"))}
    <div class="grid4">{holds}</div></section>

  <section class="box adv" id="s-adv">{sec_head("bulb", "主管必看重點", label("adv"))}
    <div class="grid4">{advs}</div></section>

  <section class="box src" id="s-src"><div class="src-row">{sec_head("link", "原始判決來源")}
    <div class="src-b"><b>{E(s["name"])}</b><span class="url">{E(s["url"])}</span><span class="sep">｜</span><span>{E(s["how"])}</span></div></div>
  </section>

  <footer class="disc" id="s-disc">{E(c["disclaimer"])}</footer>
</main></body></html>'''
