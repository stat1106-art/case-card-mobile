"""card_content.json → HTML｜illustrated 版型（第三輪設計 I：色塊標題＋三角法律關係圖＋金額流程＋事實時間軸）。

只排版，不改寫、不刪減文字。版面數值照 Claude Design 畫布上使用者選定的 I 版。
"""
import html
from pathlib import Path
from icons import P as ICONS

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
    band = d.get("band_color", "#12434A")
    info, rel, r = c["info"], c["relation"], c["result"]
    pl, df = c["parties"]["plaintiff"], c["parties"]["defendant"]
    pl_name = mask_name(pl["name"]) if pl.get("natural_person") and d.get("mask_natural_person_name") else pl["name"]
    df_name = df["name"]
    df_lines = [df_name[:5], df_name[5:]] if len(df_name) > 6 else [df_name]
    fl = r["flow"]
    font_url = ref(root / "assets/fonts/NotoSansTC-VF.ttf")
    hero_path = root / c["_case_dir"] / c["hero"]["file"]
    hero_svg = hero_path.read_text(encoding="utf-8") if hero_path.exists() else ""

    tags = (f'<span style="font-size: 18px; line-height: 26px; font-weight: 700; color: {band}; background: #FFFFFF; border-radius: 6px; padding: 0 10px">{E(c["tags"][0])}</span>'
            f'<span style="font-size: 18px; line-height: 26px; font-weight: 700; color: #FFFFFF; border: 1.5px solid #FFFFFF; border-radius: 6px; padding: 0 10px">{E(c["tags"][1])}</span>')
    title = "".join(f'<span style="display: block">{E(t)}</span>' for t in c["title"])
    sub = "<br>".join(E(t) for t in c["subtitle"])
    draft_badge = ('<span id="draftbadge" style="position: absolute; left: 14px; top: 14px; font-size: 18px; line-height: 24px; font-weight: 700; '
                   'color: #8A3B12; background: #FDF1E6; border: 1.5px solid #E3A36F; border-radius: 8px; padding: 4px 10px">草稿｜法院內容尚未對照原始分析</span>'
                   if draft else "")

    def info_cell(k, v, first=False):
        bl = "" if first else " border-left: 1px solid #E1E8E6;"
        return (f'<div style="padding: 9px 16px 10px;{bl}"><div style="font-size: 18px; line-height: 26px; color: #5A6B6D">{k}</div>'
                f'<div style="font-size: 20px; line-height: 30px; font-weight: 700">{E(v)}</div></div>')
    infobar = (info_cell("法院", info["court"], True) + info_cell("案號", info["case_no"]) +
               info_cell("裁判日期", info["date"]) + info_cell("案由", info["cause"]))

    def node(left, top, color, icon):
        return (f'<div style="position: absolute; left: {left}px; top: {top}px; width: 56px; height: 56px; border-radius: 50%; background: {color}; '
                f'color: #FFFFFF; display: flex; align-items: center; justify-content: center">{svg(icon, 30, stroke=2)}</div>')
    def arrow(left, top, width, color, rot=None, head="right"):
        tr = f" transform-origin: 0 50%; transform: rotate({rot}deg);" if rot is not None else ""
        if head == "right":
            hd = f'<span style="position: absolute; right: -2px; top: -6px; width: 0; height: 0; border-top: 7.5px solid transparent; border-bottom: 7.5px solid transparent; border-left: 13px solid {color}"></span>'
        else:
            hd = f'<span style="position: absolute; left: -2px; top: -6px; width: 0; height: 0; border-top: 7.5px solid transparent; border-bottom: 7.5px solid transparent; border-right: 13px solid {color}"></span>'
        return f'<div style="position: absolute; left: {left}px; top: {top}px; width: {width}px; height: 3px; background: {color};{tr}">{hd}</div>'

    relation = f'''
    <div class="box" style="position: relative; margin-top: 6px; height: 240px; background: #FFFFFF; border-radius: 16px">
      <div style="position: absolute; left: 334px; top: 8px; width: 300px; text-align: center; font-size: 20px; line-height: 28px"><span style="font-size: 18px; color: #5A6B6D">{E(rel["court"]["role"])}　</span><b>{E(rel["court"]["name"])}</b></div>
      {node(456, 42, "#2B3A3D", "scale")}
      {node(178, 158, "#1D8A6E", "person")}
      <div style="position: absolute; left: 24px; top: 158px; width: 140px; text-align: right"><div style="font-size: 18px; line-height: 26px; color: #5A6B6D">{E(pl["role"])}</div><div style="font-size: 20px; line-height: 28px; font-weight: 700">{E(pl_name)}</div></div>
      {node(734, 158, "#3D5A80", "building")}
      <div style="position: absolute; left: 802px; top: 143px; width: 150px"><div style="font-size: 18px; line-height: 26px; color: #5A6B6D">{E(df["role"])}</div><div style="font-size: 20px; line-height: 28px; font-weight: 700">{"<br>".join(E(x) for x in df_lines)}</div></div>
      {arrow(234.6, 172.6, 237, "#1D8A6E", -22.65)}
      <div style="position: absolute; left: 60px; top: 66px; width: 250px; text-align: right"><div style="font-size: 18px; line-height: 26px; font-weight: 700; color: #167058">{E(rel["claim"]["label"])}</div><div style="font-size: 18px; line-height: 26px; color: #4C5D5F">{E("（" + rel["claim"]["note"] + "）")}</div></div>
      {arrow(514.5, 81.2, 237, "#2B3A3D", 22.65)}
      <div style="position: absolute; left: 658px; top: 66px; width: 250px"><div style="font-size: 18px; line-height: 26px; font-weight: 700">{E(rel["order"]["label"])}</div><div style="font-size: 20px; line-height: 26px; font-weight: 900">{E(rel["order"]["amount"])}</div></div>
      {arrow(240, 182, 490, "#D0603E", None, "left")}
      <div style="position: absolute; left: 284px; top: 188px; width: 400px; text-align: center"><div style="font-size: 18px; line-height: 26px; font-weight: 700; color: #B44E2F">{E(rel["offset"]["label"] + " " + rel["offset"]["amount"])}</div><div style="font-size: 18px; line-height: 26px; color: #4C5D5F">{E("（" + rel["offset"]["note"] + "）")}</div></div>
    </div>'''

    def op(main, lines, size):
        ls = "".join(f'<div style="font-size: 18px; line-height: 24px; color: #4C5D5F">{E(x)}</div>' for x in lines)
        return (f'<div style="display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 0 6px">'
                f'<div style="font-size: {size}px; line-height: 28px; font-weight: 900; color: #B44E2F">{E(main)}</div>'
                f'<div style="width: 120px; height: 3px; background: #D0603E; position: relative; margin: 3px 0 4px"><span style="position: absolute; right: -2px; top: -6px; width: 0; height: 0; border-top: 7.5px solid transparent; border-bottom: 7.5px solid transparent; border-left: 12px solid #D0603E"></span></div>{ls}</div>')
    def valbox(label, val, final=False):
        if final:
            return (f'<div style="background: #D0603E; color: #FFFFFF; border-radius: 12px; padding: 10px 16px; display: flex; flex-direction: column; justify-content: center">'
                    f'<div style="font-size: 18px; line-height: 26px; color: #FBE3DA">{E(label)}</div><div style="font-size: 27px; line-height: 34px; font-weight: 900">{E(val)}</div></div>')
        return (f'<div style="background: #FFFFFF; border-radius: 12px; padding: 10px 16px; display: flex; flex-direction: column; justify-content: center">'
                f'<div style="font-size: 18px; line-height: 26px; color: #5A6B6D">{E(label)}</div><div style="font-size: 22px; line-height: 30px; font-weight: 900">{E(val)}</div></div>')
    flow = (valbox(fl["damage_label"], fl["damage_total"]) + op(fl["fault_op"], fl["fault_lines"], 21) +
            valbox(fl["after_label"], fl["after_fault"]) + op(fl["offset_op"], fl["offset_lines"], 20) +
            valbox(fl["final_label"], r["total"], True))

    def fact(f):
        t, ic = (f["text"], f.get("icon", "check")) if isinstance(f, dict) else (f, "check")
        return (f'<div style="display: flex; gap: 10px; align-items: flex-start"><span style="flex: none; width: 38px; height: 38px; border-radius: 50%; background: #1D8A6E; color: #FFFFFF; display: flex; align-items: center; justify-content: center">{svg(ic, 22)}</span>'
                f'<span style="font-size: 18px; line-height: 27px">{E(t)}</span></div>')
    facts = "".join(fact(f) for f in c["facts"])
    tl = c["timeline"]
    dot_open = f'<span style="width: 16px; height: 16px; margin-top: 6px; border-radius: 50%; background: #FFFFFF; border: 3px solid {band}; box-sizing: border-box"></span>'
    row = 'position: relative; display: grid; grid-template-columns: 34px minmax(0, 1fr); font-size: 18px; line-height: 28px'

    holds = "".join(
        f'<div class="hc" style="background: #FFFFFF; border-radius: 14px; padding: 9px 10px 10px; border-top: 4px solid {band}">'
        f'<div style="font-size: 18px; line-height: 26px; font-weight: 900">{E(h["head"])}</div>'
        f'<div style="margin-top: 4px; font-size: 18px; line-height: 27px; color: #4C5D5F">{E(h["body"])}</div></div>' for h in c["holdings"])
    advs = "".join(
        f'<div class="ac"><div style="display: flex; gap: 6px; align-items: center">{svg(ic, 22, "#8A5A10")}<span style="font-size: 18px; line-height: 26px; font-weight: 900">{E(a["head"])}</span></div>'
        f'<div style="margin-top: 2px; font-size: 18px; line-height: 27px; color: #4A3F30">{E(a["body"])}</div></div>'
        for a, ic in zip(c["advisory"], c.get("advisory_icons", ["search", "group", "bell", "ledger"])))
    s = c["source_card"]
    pill_court = f'<span style="font-size: 18px; line-height: 26px; font-weight: 700; color: #FFFFFF; background: {band}; border-radius: 6px; padding: 0 12px">法院認定</span>'
    h2 = f'margin: 0; font-size: 21px; line-height: 30px; font-weight: 900; color: {band}'

    return f'''<!doctype html><html lang="zh-Hant-TW"><head><meta charset="utf-8">
<style>@font-face{{font-family:"CardSans";src:url("{font_url}") format("truetype");font-weight:100 900;font-display:block;}}
html,body{{margin:0;width:1080px;height:1620px;overflow:hidden;background:#EDF1F0}}</style></head><body>
<main id="card" style="position: relative; width: 1080px; height: 1620px; overflow: hidden; background: #EDF1F0; color: #172426; font-family: CardSans, sans-serif; display: flex; flex-direction: column; gap: 8px">
  <header id="s-head" style="position: relative; flex: none; height: 290px; background: {band}">
    <div style="position: absolute; left: 56px; top: 30px; width: 500px; color: #FFFFFF">
      <div style="display: flex; gap: 8px">{tags}</div>
      <h1 style="margin: 14px 0 0; font-size: 40px; line-height: 52px; font-weight: 900">{title}</h1>
      <p style="margin: 10px 0 0; font-size: 19px; line-height: 29px; font-weight: 500; color: #D3E6E3">{sub}</p>
    </div>
    <div style="position: absolute; right: 0; top: 0; width: 503px; height: 290px; overflow: hidden; background: #DCE6F0">
      {hero_svg}
      <span style="position: absolute; right: 14px; top: 14px; font-size: 18px; line-height: 26px; font-weight: 700; color: #172426; background: #FFFFFF; border-radius: 13px; padding: 0 10px">{E(c["hero"]["caption"])}</span>
      {draft_badge}
    </div>
  </header>

  <section id="s-info" class="box" data-overlap="ok" style="position: relative; flex: none; margin: -36px 56px 0; display: grid; grid-template-columns: minmax(0, 0.92fr) minmax(0, 1.16fr) minmax(0, 0.92fr) minmax(0, 1fr); background: #FFFFFF; border-radius: 14px; box-shadow: 0 0 0 1px #D5DEDC">{infobar}</section>

  <section id="s-rel" style="flex: none; margin: 0 56px"><h2 style="{h2}">法律關係圖</h2>{relation}</section>

  <section id="s-result" style="flex: none; margin: 0 56px">
    <h2 style="{h2}; display: flex; justify-content: space-between; align-items: center">判決結果{pill_court}</h2>
    <div style="margin-top: 6px; display: grid; grid-template-columns: minmax(0, 1fr) 170px minmax(0, 1fr) 170px minmax(0, 1.2fr); align-items: stretch">{flow}</div>
    <div style="margin-top: 8px; font-size: 18px; line-height: 27px; color: #2F3E40">{E(r["notes"])}</div>
    <div class="pending" style="margin-top: 6px; background: #F8E9D2; border-radius: 10px; padding: 5px 14px; font-size: 18px; line-height: 27px; color: #6B3E0C"><b style="color: #9A5B0F">尚待確認｜</b>{E(r["pending"])}</div>
  </section>

  <section id="s-facts" style="flex: none; margin: 0 56px">
    <h2 style="{h2}">事實經過<span style="font-size: 18px; font-weight: 500; color: #5A6B6D">（工作負荷重點）</span></h2>
    <div class="box" style="position: relative; margin-top: 6px; background: #FFFFFF; border-radius: 16px; padding: 8px 20px 8px 20px">
      <div style="position: absolute; left: 31px; top: 26px; bottom: 30px; width: 3px; background: #9DB9B5"></div>
      <div style="{row}">{dot_open}<div><b style="color: {band}">{E(tl["start"]["date"])}　{E(tl["start"]["label"])}</b><span style="margin-left: 12px">{E(tl["start"]["text"])}</span></div></div>
      <div style="{row}; margin-top: 5px">{dot_open}<div><b style="color: {band}">{E(c["facts_anchor"])}</b>
        <div style="margin-top: 6px; display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); column-gap: 18px; row-gap: 8px">{facts}</div></div></div>
      <div style="{row}; margin-top: 5px"><span style="width: 16px; height: 16px; margin-top: 6px; border-radius: 50%; background: #D0603E"></span><div><b style="color: #B44E2F">{E(tl["onset"]["date"])}　{E(tl["onset"]["label"])}</b><span style="margin-left: 12px">{E(tl["onset"]["text"])}</span></div></div>
    </div>
  </section>

  <section id="s-hold" style="flex: none; margin: 0 56px">
    <h2 style="{h2}; display: flex; justify-content: space-between; align-items: center">法院核心見解{pill_court}</h2>
    <div style="margin-top: 6px; display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px">{holds}</div>
  </section>

  <section id="s-adv" class="box" style="flex: none; margin: 0 56px; background: #F5EEDF; border-radius: 14px; padding: 7px 18px 9px">
    <h2 style="margin: 0; font-size: 21px; line-height: 30px; font-weight: 900; color: #6E460C; display: flex; justify-content: space-between; align-items: center">主管必看重點<span style="font-size: 18px; line-height: 26px; font-weight: 700; color: #6E460C; background: #FFFFFF; border: 1.5px solid #D9BE8E; border-radius: 6px; padding: 0 12px">顧問分析｜非法院見解</span></h2>
    <div style="margin-top: 6px; display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px">{advs}</div>
  </section>

  <section id="s-src" style="flex: none; margin: 0 56px; display: flex; gap: 14px; align-items: baseline; font-size: 18px; line-height: 26px">
    <span style="font-weight: 700; color: {band}">原始判決來源</span><span>{E(s["name"])}</span><span style="color: #4C5D5F">{E(s["url"])}｜{E(s["how"])}</span>
  </section>

  <footer id="s-disc" class="disc" style="margin-top: auto; flex: none; background: {band}; padding: 13px 40px 14px; text-align: center; font-size: 18px; line-height: 26px; color: #DDEBE9">{E(c["disclaimer"])}</footer>
</main></body></html>'''
