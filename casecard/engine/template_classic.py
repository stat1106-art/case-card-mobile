"""card_content.json → HTML｜classic 版型（v0.6.0，取代 I 版出圖；v0.8.0 起顏色改由風格角色決定）。

版面、文字照 I 版（三角法律關係圖＋金額流程＋事實時間軸）；配色換成原版 v0.2：
米白底、黑底標題條、綠（原告／法院認定）、藏青（被告）、紅（扣抵／應給付）、淺藍（顧問分析）。
只排版，不改寫、不刪減文字。
"""
import html
from pathlib import Path
from icons import P as ICONS
import typography

_esc = html.escape
_KEEP = []

def E(s):
    out = _esc(str(s))
    for w in _KEEP:
        ew = _esc(w)
        out = out.replace(ew, f'<span style="white-space: nowrap">{ew}</span>')
    return out

def svg(name, size, color="currentColor", stroke=2.2):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" '
            f'stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>')

def mask_name(name):
    if len(name) <= 1: return name
    if len(name) == 2: return name[0] + "○"
    return name[0] + "○" * (len(name) - 2) + name[-1]

def build_html(c: dict, root: Path, draft: bool, ref) -> str:
    d = c.get("display", {})
    _KEEP[:] = sorted(d.get("keep_together", []), key=len, reverse=True)
    # v0.8.0：顏色一律取自風格角色（engine/skins.py）；預設 original 等於 v0.7.0 原色
    K = c["_skin_roles"]
    band = K["dark"]
    info, rel, r = c["info"], c["relation"], c["result"]
    pl, df = c["parties"]["plaintiff"], c["parties"]["defendant"]
    pl_name = mask_name(pl["name"]) if pl.get("natural_person") and d.get("mask_natural_person_name") else pl["name"]
    df_name = df["name"]
    df_lines = [df_name[:5], df_name[5:]] if len(df_name) > 6 else [df_name]
    fl = r["flow"]
    font_url = ref(root / "assets/fonts/NotoSansTC-VF.ttf")
    hero_path = root / c["_case_dir"] / c["hero"]["file"]
    hero_svg = hero_path.read_text(encoding="utf-8") if hero_path.exists() else ""

    tags = (f'<span style="font-size: 18px; line-height: 26px; font-weight: 700; color: {K["on_dark"]}; background: {K["dark"]}; border-radius: 6px; padding: 0 10px">{E(c["tags"][0])}</span>'
            f'<span style="font-size: 18px; line-height: 26px; font-weight: 700; color: {K["on_dark"]}; background: {K["dark"]}; border: 1.5px solid {K["dark"]}; border-radius: 6px; padding: 0 10px">{E(c["tags"][1])}</span>')
    title = "".join(f'<span style="display: block">{E(t)}</span>' for t in c["title"])
    sub = "<br>".join(E(t) for t in c["subtitle"])
    draft_badge = ('<span id="draftbadge" style="position: absolute; left: 14px; top: 14px; font-size: 18px; line-height: 24px; font-weight: 700; '
                   'color: #8A3B12; background: #FDF1E6; border: 1.5px solid #E3A36F; border-radius: 8px; padding: 4px 10px">草稿｜法院內容尚未對照原始分析</span>'
                   if draft else "")

    def info_cell(k, v, first=False):
        bl = "" if first else f" border-left: 1px solid {K['line']};"
        return (f'<div style="padding: 9px 16px 10px;{bl}"><div style="font-size: 18px; line-height: 26px; color: {K["muted"]}">{k}</div>'
                f'<div style="font-size: 20px; line-height: 30px; font-weight: 700">{E(v)}</div></div>')
    infobar = (info_cell("法院", info["court"], True) + info_cell("案號", info["case_no"]) +
               info_cell("裁判日期", info["date"]) + info_cell("案由", info["cause"]))

    def node(left, top, color, icon):
        return (f'<div style="position: absolute; left: {left}px; top: {top}px; width: 56px; height: 56px; border-radius: 50%; background: {color}; '
                f'color: {K["on_dark"]}; display: flex; align-items: center; justify-content: center">{svg(icon, 30, stroke=2)}</div>')
    def arrow(left, top, width, color, rot=None, head="right"):
        tr = f" transform-origin: 0 50%; transform: rotate({rot}deg);" if rot is not None else ""
        if head == "right":
            hd = f'<span style="position: absolute; right: -2px; top: -6px; width: 0; height: 0; border-top: 7.5px solid transparent; border-bottom: 7.5px solid transparent; border-left: 13px solid {color}"></span>'
        else:
            hd = f'<span style="position: absolute; left: -2px; top: -6px; width: 0; height: 0; border-top: 7.5px solid transparent; border-bottom: 7.5px solid transparent; border-right: 13px solid {color}"></span>'
        return f'<div style="position: absolute; left: {left}px; top: {top}px; width: {width}px; height: 3px; background: {color};{tr}">{hd}</div>'

    relation = f'''
    <div class="box" style="position: relative; margin-top: 6px; height: 240px; background: {K["card"]}; box-shadow: inset 0 0 0 1.5px {K["line"]}; border-radius: 16px">
      <div style="position: absolute; left: 334px; top: 8px; width: 300px; text-align: center; font-size: 20px; line-height: 28px"><span style="font-size: 18px; color: {K["muted"]}">{E(rel["court"]["role"])}　</span><b>{E(rel["court"]["name"])}</b></div>
      {node(456, 42, K["dark"], "scale")}
      {node(178, 158, K["plaintiff"], "person")}
      <div style="position: absolute; left: 24px; top: 158px; width: 140px; text-align: right"><div style="font-size: 18px; line-height: 26px; color: {K["muted"]}">{E(pl["role"])}</div><div style="font-size: 20px; line-height: 28px; font-weight: 700">{E(pl_name)}</div></div>
      {node(734, 158, K["defendant"], "building")}
      <div style="position: absolute; left: 802px; top: 143px; width: 150px"><div style="font-size: 18px; line-height: 26px; color: {K["muted"]}">{E(df["role"])}</div><div style="font-size: 20px; line-height: 28px; font-weight: 700">{"<br>".join(E(x) for x in df_lines)}</div></div>
      {arrow(234.6, 172.6, 237, K["plaintiff"], -22.65)}
      <div style="position: absolute; left: 60px; top: 66px; width: 250px; text-align: right"><div style="font-size: 18px; line-height: 26px; font-weight: 700; color: {K["plaintiff"]}">{E(rel["claim"]["label"])}</div><div style="font-size: 18px; line-height: 26px; color: {K["ink2"]}">{E("（" + rel["claim"]["note"] + "）")}</div></div>
      {arrow(514.5, 81.2, 237, K["dark"], 22.65)}
      <div style="position: absolute; left: 658px; top: 66px; width: 250px"><div style="font-size: 18px; line-height: 26px; font-weight: 700">{E(rel["order"]["label"])}</div><div class="amt" style="font-size: 20px; line-height: 26px; font-weight: 900">{E(rel["order"]["amount"])}</div></div>
      {arrow(240, 182, 490, K["deduct"], None, "left")}
      <div style="position: absolute; left: 284px; top: 188px; width: 400px; text-align: center"><div style="font-size: 18px; line-height: 26px; font-weight: 700; color: {K["deduct"]}">{E(rel["offset"]["label"] + " " + rel["offset"]["amount"])}</div><div style="font-size: 18px; line-height: 26px; color: {K["ink2"]}">{E("（" + rel["offset"]["note"] + "）")}</div></div>
    </div>'''

    def op(main, lines, size):
        ls = "".join(f'<div style="font-size: 18px; line-height: 24px; color: {K["ink2"]}">{E(x)}</div>' for x in lines)
        return (f'<div style="display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 0 6px">'
                f'<div style="font-size: {size}px; line-height: 28px; font-weight: 900; color: {K["deduct"]}">{E(main)}</div>'
                f'<div style="width: 120px; height: 3px; background: {K["deduct"]}; position: relative; margin: 3px 0 4px"><span style="position: absolute; right: -2px; top: -6px; width: 0; height: 0; border-top: 7.5px solid transparent; border-bottom: 7.5px solid transparent; border-left: 12px solid {K["deduct"]}"></span></div>{ls}</div>')
    def valbox(label, val, final=False):
        if final:
            return (f'<div style="background: {K["money"]}; color: {K["money_text"]}; border-radius: 12px; padding: 10px 16px; display: flex; flex-direction: column; justify-content: center">'
                    f'<div style="font-size: 18px; line-height: 26px; color: {K["money_sub"]}">{E(label)}</div><div class="amt" style="font-size: 27px; line-height: 34px; font-weight: 900">{E(val)}</div></div>')
        return (f'<div style="background: {K["card"]}; box-shadow: inset 0 0 0 1.5px {K["line"]}; border-radius: 12px; padding: 10px 16px; display: flex; flex-direction: column; justify-content: center">'
                f'<div style="font-size: 18px; line-height: 26px; color: {K["muted"]}">{E(label)}</div><div class="amt" style="font-size: 22px; line-height: 30px; font-weight: 900">{E(val)}</div></div>')
    flow = (valbox(fl["damage_label"], fl["damage_total"]) + op(fl["fault_op"], fl["fault_lines"], 21) +
            valbox(fl["after_label"], fl["after_fault"]) + op(fl["offset_op"], fl["offset_lines"], 20) +
            valbox(fl["final_label"], r["total"], True))

    def fact(f):
        t, ic = (f["text"], f.get("icon", "check")) if isinstance(f, dict) else (f, "check")
        return (f'<div style="display: flex; gap: 10px; align-items: flex-start"><span style="flex: none; width: 38px; height: 38px; border-radius: 50%; background: {K["dark"]}; color: {K["on_dark"]}; display: flex; align-items: center; justify-content: center">{svg(ic, 22)}</span>'
                f'<span style="font-size: 18px; line-height: 27px">{E(t)}</span></div>')
    facts = "".join(fact(f) for f in c["facts"])
    tl = c["timeline"]
    dot_open = f'<span style="width: 16px; height: 16px; margin-top: 6px; border-radius: 50%; background: {K["dot_fill"]}; border: 3px solid {band}; box-sizing: border-box"></span>'
    row = 'position: relative; display: grid; grid-template-columns: 34px minmax(0, 1fr); font-size: 18px; line-height: 28px'

    holds = "".join(
        f'<div class="hc" style="background: {K["card"]}; box-shadow: inset 0 0 0 1.5px {K["line"]}; border-radius: 14px; padding: 9px 10px 10px; border-top: 4px solid {K["plaintiff"]}">'
        f'<div style="font-size: 18px; line-height: 26px; font-weight: 900">{E(h["head"])}</div>'
        f'<div style="margin-top: 4px; font-size: 18px; line-height: 27px; color: {K["ink2"]}">{E(h["body"])}</div></div>' for h in c["holdings"])
    advs = "".join(
        f'<div class="ac"><div style="display: flex; gap: 6px; align-items: center">{svg(ic, 22, K["adv_ink"])}<span style="font-size: 18px; line-height: 26px; font-weight: 900">{E(a["head"])}</span></div>'
        f'<div style="margin-top: 2px; font-size: 18px; line-height: 27px; color: {K["ink2"]}">{E(a["body"])}</div></div>'
        for a, ic in zip(c["advisory"], c.get("advisory_icons", ["search", "group", "bell", "ledger"])))
    s = c["source_card"]
    pill_court = f'<span style="font-size: 18px; line-height: 26px; font-weight: 700; color: {K["pill_text"]}; background: {K["pill_bg"]}; box-shadow: inset 0 0 0 1.5px {K["pill_line"]}; border-radius: 6px; padding: 0 12px">法院認定</span>'
    h2 = f'margin: 0; font-size: 21px; line-height: 30px; font-weight: 900; color: {K["ink"]}'

    return f'''<!doctype html><html lang="zh-Hant-TW"><head><meta charset="utf-8">
<style>@font-face{{font-family:"CardSans";src:url("{font_url}") format("truetype");font-weight:100 900;font-display:block;}}
html,body{{margin:0;width:1080px;height:1620px;overflow:hidden;background:{K["page"]}}}</style>{typography.css(ref, root, 'h1, h2, .hc > div:first-child, .ac > div:first-child', '.amt')}</head><body>
<main id="card" style="position: relative; width: 1080px; height: 1620px; overflow: hidden; background: {c["_page_bg"]}; color: {K["ink"]}; font-family: CardSans, sans-serif; display: flex; flex-direction: column; gap: 8px">
  <header id="s-head" style="position: relative; flex: none; height: 290px; background: transparent">
    <div style="position: absolute; left: 56px; top: 30px; width: 500px; color: {K["ink"]}">
      <div style="display: flex; gap: 8px">{tags}</div>
      <h1 style="margin: 14px 0 0; font-size: 40px; line-height: 52px; font-weight: 900">{title}</h1>
      <p style="margin: 10px 0 0; font-size: 19px; line-height: 29px; font-weight: 500; color: {K["ink2"]}">{sub}</p>
    </div>
    <div style="position: absolute; right: 0; top: 0; width: 503px; height: 290px; overflow: hidden; background: #DCE6F0">
      {hero_svg}
      <span style="position: absolute; right: 14px; top: 14px; font-size: 18px; line-height: 26px; font-weight: 700; color: #1D1B18; background: #FFFFFF; border-radius: 13px; padding: 0 10px">{E(c["hero"]["caption"])}</span>
      {draft_badge}
    </div>
  </header>

  <section id="s-info" class="box" data-overlap="ok" style="position: relative; flex: none; margin: -36px 56px 0; display: grid; grid-template-columns: minmax(0, 0.92fr) minmax(0, 1.16fr) minmax(0, 0.92fr) minmax(0, 1fr); background: {K["card"]}; border-radius: 14px; box-shadow: 0 0 0 1.5px {K["line"]}">{infobar}</section>

  <section id="s-rel" style="flex: none; margin: 0 56px"><h2 style="{h2}"><span class="chip" style="display: inline-block; background: {K["dark"]}; color: {K["on_dark"]}; border-radius: 6px; padding: 0 10px">法律關係圖</span></h2>{relation}</section>

  <section id="s-result" style="flex: none; margin: 0 56px">
    <h2 style="{h2}; display: flex; justify-content: space-between; align-items: center"><span class="chip" style="display: inline-block; background: {K["dark"]}; color: {K["on_dark"]}; border-radius: 6px; padding: 0 10px">判決結果</span>{pill_court}</h2>
    <div style="margin-top: 6px; display: grid; grid-template-columns: minmax(0, 1fr) 170px minmax(0, 1fr) 170px minmax(0, 1.2fr); align-items: stretch">{flow}</div>
    <div style="margin-top: 8px; font-size: 18px; line-height: 27px; color: {K["ink2"]}">{E(r["notes"])}</div>
    <div class="pending" style="margin-top: 6px; background: #FDF1E6; box-shadow: inset 0 0 0 1.5px #EFC7A5; border-radius: 10px; padding: 5px 14px; font-size: 18px; line-height: 27px; color: #6B3A12"><b style="color: #B8540F">尚待確認｜</b>{E(r["pending"])}</div>
  </section>

  <section id="s-facts" style="flex: none; margin: 0 56px">
    <h2 style="{h2}"><span class="chip" style="display: inline-block; background: {K["dark"]}; color: {K["on_dark"]}; border-radius: 6px; padding: 0 10px">事實經過</span><span style="font-size: 18px; font-weight: 500; color: {K["muted"]}">（工作負荷重點）</span></h2>
    <div class="box" style="position: relative; margin-top: 6px; background: {K["card"]}; box-shadow: inset 0 0 0 1.5px {K["line"]}; border-radius: 16px; padding: 8px 20px 8px 20px">
      <div style="position: absolute; left: 31px; top: 26px; bottom: 30px; width: 3px; background: {K["line2"]}"></div>
      <div style="{row}">{dot_open}<div><b style="color: {band}">{E(tl["start"]["date"])}　{E(tl["start"]["label"])}</b><span style="margin-left: 12px">{E(tl["start"]["text"])}</span></div></div>
      <div style="{row}; margin-top: 5px">{dot_open}<div><b style="color: {band}">{E(c["facts_anchor"])}</b>
        <div style="margin-top: 6px; display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); column-gap: 18px; row-gap: 8px">{facts}</div></div></div>
      <div style="{row}; margin-top: 5px"><span style="width: 16px; height: 16px; margin-top: 6px; border-radius: 50%; background: {K["money"]}"></span><div><b style="color: {K["money"]}">{E(tl["onset"]["date"])}　{E(tl["onset"]["label"])}</b><span style="margin-left: 12px">{E(tl["onset"]["text"])}</span></div></div>
    </div>
  </section>

  <section id="s-hold" style="flex: none; margin: 0 56px">
    <h2 style="{h2}; display: flex; justify-content: space-between; align-items: center"><span class="chip" style="display: inline-block; background: {K["dark"]}; color: {K["on_dark"]}; border-radius: 6px; padding: 0 10px">法院核心見解</span>{pill_court}</h2>
    <div style="margin-top: 6px; display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px">{holds}</div>
  </section>

  <section id="s-adv" class="box" style="flex: none; margin: 0 56px; background: {K["adv_bg"]}; box-shadow: inset 0 0 0 1.5px {K["adv_line"]}; border-radius: 14px; padding: 7px 18px 9px">
    <h2 style="margin: 0; font-size: 21px; line-height: 30px; font-weight: 900; color: {K["adv_ink"]}; display: flex; justify-content: space-between; align-items: center">主管必看重點<span style="font-size: 18px; line-height: 26px; font-weight: 700; color: {K["adv_ink"]}; background: {K["adv_pill_bg"]}; border: 1.5px solid {K["adv_line"]}; border-radius: 6px; padding: 0 12px">顧問分析｜非法院見解</span></h2>
    <div style="margin-top: 6px; display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px">{advs}</div>
  </section>

  <section id="s-src" style="flex: none; margin: 0 56px; display: flex; gap: 14px; align-items: baseline; font-size: 18px; line-height: 26px">
    <span style="font-weight: 700; color: {band}">原始判決來源</span><span>{E(s["name"])}</span><span style="color: {K["ink2"]}">{E(s["url"])}｜{E(s["how"])}</span>
  </section>

  <footer id="s-disc" class="disc" style="margin-top: auto; flex: none; background: {band}; padding: 13px 40px 14px; text-align: center; font-size: 18px; line-height: 26px; color: {K["footer_text"]}">{E(c["disclaimer"])}</footer>
</main></body></html>'''
