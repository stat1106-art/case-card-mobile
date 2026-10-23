"""card_content.json → HTML｜light 版型（第三輪設計 H：淺色圖解卡、橫向法律關係圖、事實五格圖示）。
只排版，不改寫、不刪減文字。與 illustrated 共用同一份 JSON。"""
from pathlib import Path
import template_illustrated as TI
import typography
from template_illustrated import E, svg, mask_name

def build_html(c: dict, root: Path, draft: bool, ref) -> str:
    d = c.get("display", {})
    TI._KEEP[:] = sorted(d.get("keep_together", []), key=len, reverse=True)
    NAVY, TEAL, SLATE, AMBER, PLUM = "#23466E", "#0F8070", "#4F5D6B", "#C47A12", "#6A4B95"
    info, rel, r, fl = c["info"], c["relation"], c["result"], c["result"]["flow"]
    pl, df = c["parties"]["plaintiff"], c["parties"]["defendant"]
    pl_name = mask_name(pl["name"]) if pl.get("natural_person") and d.get("mask_natural_person_name") else pl["name"]
    font_url = ref(root / "assets/fonts/NotoSansTC-VF.ttf")
    hp = root / c["_case_dir"] / c["hero"]["file"]
    hero_svg = hp.read_text(encoding="utf-8") if hp.exists() else ""
    draft_badge = ('<span id="draftbadge" style="position: absolute; left: 14px; top: 14px; font-size: 18px; line-height: 24px; font-weight: 700; color: #8A3B12; background: #FDF1E6; border: 1.5px solid #E3A36F; border-radius: 8px; padding: 4px 10px">草稿｜法院內容尚未對照原始分析</span>' if draft else "")

    tags = (f'<span style="font-size: 18px; line-height: 26px; font-weight: 700; color: #FFFFFF; background: {NAVY}; border-radius: 13px; padding: 0 12px">{E(c["tags"][0])}</span>'
            f'<span style="font-size: 18px; line-height: 26px; font-weight: 700; color: {NAVY}; border: 1.5px solid {NAVY}; border-radius: 13px; padding: 0 12px">{E(c["tags"][1])}</span>')
    title = "".join(f'<span style="display: block">{E(t)}</span>' for t in c["title"])
    sub = "<br>".join(E(t) for t in c["subtitle"])

    def cell(ic, k, v, first=False):
        bl = "" if first else " border-left: 1px solid #E1E7ED;"
        return (f'<div style="padding: 9px 16px 10px;{bl}"><div style="display: flex; align-items: center; gap: 6px; font-size: 18px; line-height: 26px; color: #5B6B7B">{svg(ic, 20, NAVY)}{k}</div>'
                f'<div style="font-size: 20px; line-height: 30px; font-weight: 700">{E(v)}</div></div>')
    infobar = cell("court", "法院", info["court"], True) + cell("doc", "案號", info["case_no"]) + cell("cal", "裁判日期", info["date"]) + cell("scale", "案由", info["cause"])

    def node(left, width, color, icon, role, name):
        return (f'<div style="position: absolute; left: {left}px; top: 14px; width: {width}px; text-align: center">'
                f'<div style="width: 56px; height: 56px; margin: 0 auto; border-radius: 50%; background: {color}; color: #FFFFFF; display: flex; align-items: center; justify-content: center">{svg(icon, 30, stroke=2)}</div>'
                f'<div style="margin-top: 6px; font-size: 18px; line-height: 26px; color: #5B6B7B">{E(role)}</div><div style="font-size: 20px; line-height: 28px; font-weight: 700">{E(name)}</div></div>')
    def harrow(left, color, top_txt, top_style, bot_txt, bot_style):
        return (f'<div style="position: absolute; left: {left}px; width: 296px; top: 41px; height: 3px; background: {color}"><span style="position: absolute; right: -2px; top: -6px; width: 0; height: 0; border-top: 7.5px solid transparent; border-bottom: 7.5px solid transparent; border-left: 13px solid {color}"></span></div>'
                f'<div style="position: absolute; left: {left}px; width: 296px; top: 12px; text-align: center; {top_style}">{top_txt}</div>'
                f'<div style="position: absolute; left: {left}px; width: 296px; top: 50px; text-align: center; {bot_style}">{bot_txt}</div>')
    relation = f'''<div class="box" style="position: relative; margin-top: 6px; height: 188px; background: #FFFFFF; border-radius: 14px">
      {node(25, 170, TEAL, "person", pl["role"], pl_name)}
      {node(399, 170, NAVY, "court", rel["court"]["role"], rel["court"]["name"])}
      {node(758, 200, SLATE, "building", df["role"], df["name"])}
      {harrow(150, TEAL, E(rel["claim"]["label"]), f"font-size: 18px; line-height: 26px; font-weight: 700; color: {TEAL}", E("（" + rel["claim"]["note"] + "）"), "font-size: 18px; line-height: 26px; color: #4A5A6A")}
      {harrow(522, NAVY, E(rel["order"]["label"]), f"font-size: 18px; line-height: 26px; font-weight: 700; color: {NAVY}", '<span class="amt">' + E(rel["order"]["amount"]) + '</span>', f"font-size: 20px; line-height: 26px; font-weight: 900; color: {NAVY}")}
      <div style="position: absolute; left: 110px; width: 748px; top: 136px; height: 30px; border: 3px solid {AMBER}; border-top: none; border-radius: 0 0 12px 12px; box-sizing: border-box"></div>
      <span style="position: absolute; left: 103px; top: 124px; width: 0; height: 0; border-left: 7.5px solid transparent; border-right: 7.5px solid transparent; border-bottom: 13px solid {AMBER}"></span>
      <div style="position: absolute; left: 484px; top: 150px; transform: translateX(-50%); white-space: nowrap; background: #FFFFFF; padding: 0 12px; font-size: 18px; line-height: 28px"><b style="color: #A86508">{E(rel["offset"]["label"] + " " + rel["offset"]["amount"])}</b><span style="color: #4A5A6A">{E("（" + rel["offset"]["note"] + "）")}</span></div>
    </div>'''

    def op(main, lines, size):
        ls = "".join(f'<div style="font-size: 18px; line-height: 24px; color: #4A5A6A">{E(x)}</div>' for x in lines)
        return (f'<div style="display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 0 6px"><div style="font-size: {size}px; line-height: 28px; font-weight: 900; color: #A86508">{E(main)}</div>'
                f'<div style="width: 120px; height: 3px; background: {AMBER}; position: relative; margin: 3px 0 4px"><span style="position: absolute; right: -2px; top: -6px; width: 0; height: 0; border-top: 7.5px solid transparent; border-bottom: 7.5px solid transparent; border-left: 12px solid {AMBER}"></span></div>{ls}</div>')
    def vbox(label, val, final=False):
        if final:
            return (f'<div style="background: {NAVY}; color: #FFFFFF; border-radius: 12px; padding: 10px 16px; display: flex; flex-direction: column; justify-content: center"><div style="font-size: 18px; line-height: 26px; color: #C9D6E6">{E(label)}</div><div class="amt" style="font-size: 27px; line-height: 34px; font-weight: 900">{E(val)}</div></div>')
        return (f'<div style="background: #FFFFFF; border-radius: 12px; padding: 10px 16px; display: flex; flex-direction: column; justify-content: center"><div style="font-size: 18px; line-height: 26px; color: #5B6B7B">{E(label)}</div><div class="amt" style="font-size: 22px; line-height: 30px; font-weight: 900">{E(val)}</div></div>')
    flow = vbox(fl["damage_label"], fl["damage_total"]) + op(fl["fault_op"], fl["fault_lines"], 21) + vbox(fl["after_label"], fl["after_fault"]) + op(fl["offset_op"], fl["offset_lines"], 20) + vbox(fl["final_label"], r["total"], True)

    tiles = "".join(
        f'<div class="hc" style="background: #FFFFFF; border-radius: 14px; padding: 10px 10px 10px"><div style="width: 44px; height: 44px; border-radius: 50%; background: #E0F1EE; color: {TEAL}; display: flex; align-items: center; justify-content: center">{svg(f.get("icon", "check"), 26, stroke=2)}</div>'
        f'<div style="margin-top: 8px; font-size: 18px; line-height: 27px">{E(f["text"])}</div></div>' for f in c["facts"])
    b = dict(c["basics"])
    basics = (f'<div style="display: flex; gap: 8px"><b style="flex: none; color: #5B6B7B">職務</b><span>{E(b["職務"])}</span></div>'
              f'<div style="display: flex; gap: 8px"><b style="flex: none; color: #5B6B7B">時間</b><span>{E(b["時間"])}</span></div>'
              f'<div style="display: flex; gap: 8px"><b style="flex: none; color: #5B6B7B">月薪</b><span>{E(b["月薪"])}</span></div>'
              f'<div style="grid-column: 1 / -1; display: flex; gap: 8px"><b style="flex: none; color: #5B6B7B">疾病</b><span>{E(b["疾病"])}</span></div>')
    hold_ic = ["gauge", "clip", "shieldalert", "coins"]
    holds = "".join(
        f'<div class="hc" style="background: #FFFFFF; border-radius: 14px; padding: 9px 10px 10px"><div style="display: flex; gap: 6px; align-items: center">{svg(ic, 22, NAVY)}<span style="font-size: 18px; line-height: 26px; font-weight: 900">{E(h["head"])}</span></div>'
        f'<div style="margin-top: 4px; font-size: 18px; line-height: 27px; color: #4A5A6A">{E(h["body"])}</div></div>' for h, ic in zip(c["holdings"], hold_ic))
    advs = "".join(
        f'<div class="ac"><div style="display: flex; gap: 8px; align-items: center">{svg(ic, 24, PLUM)}<span style="font-size: 19px; line-height: 27px; font-weight: 900">{E(a["head"])}</span></div>'
        f'<div style="margin-top: 2px; font-size: 18px; line-height: 27px; color: #3E3550">{E(a["body"])}</div></div>'
        for a, ic in zip(c["advisory"], c.get("advisory_icons", ["search", "group", "bell", "ledger"])))
    s = c["source_card"]
    pill = f'<span style="font-size: 18px; line-height: 26px; font-weight: 700; color: #FFFFFF; background: {NAVY}; border-radius: 13px; padding: 0 12px">法院認定</span>'
    h2 = "margin: 0; font-size: 21px; line-height: 30px; font-weight: 900"

    return f'''<!doctype html><html lang="zh-Hant-TW"><head><meta charset="utf-8">
<style>@font-face{{font-family:"CardSans";src:url("{font_url}") format("truetype");font-weight:100 900;font-display:block;}}
html,body{{margin:0;width:1080px;height:1620px;overflow:hidden;background:#F2F5F8}}</style>{typography.css(ref, root, 'h1, h2, .hc > div:first-child, .ac > div:first-child', '.amt')}</head><body>
<main id="card" style="position: relative; width: 1080px; height: 1620px; overflow: hidden; background: #F2F5F8; color: #1B2A3A; font-family: CardSans, sans-serif; display: flex; flex-direction: column; gap: 12px">
  <header id="s-head" style="position: relative; flex: none; height: 290px">
    <div style="position: absolute; left: 56px; top: 34px; width: 500px">
      <div style="display: flex; gap: 8px">{tags}</div>
      <h1 style="margin: 14px 0 0; font-size: 40px; line-height: 52px; font-weight: 900">{title}</h1>
      <p style="margin: 12px 0 0; font-size: 19px; line-height: 29px; font-weight: 500; color: #4A5A6A">{sub}</p>
    </div>
    <div style="position: absolute; right: 0; top: 0; width: 503px; height: 290px; overflow: hidden; background: #DCE6F0">{hero_svg}
      <span style="position: absolute; left: 14px; bottom: 14px; font-size: 18px; line-height: 26px; font-weight: 700; color: #1B2A3A; background: #FFFFFF; border-radius: 13px; padding: 0 10px">{E(c["hero"]["caption"])}</span>{draft_badge}</div>
  </header>
  <section id="s-info" class="box" style="flex: none; margin: 0 56px; display: grid; grid-template-columns: minmax(0, 0.92fr) minmax(0, 1.16fr) minmax(0, 0.92fr) minmax(0, 1fr); background: #FFFFFF; border-radius: 14px">{infobar}</section>
  <section id="s-rel" style="flex: none; margin: 0 56px"><h2 style="{h2}">法律關係圖</h2>{relation}</section>
  <section id="s-result" style="flex: none; margin: 0 56px">
    <h2 style="{h2}; display: flex; justify-content: space-between; align-items: center">判決結果{pill}</h2>
    <div style="margin-top: 6px; display: grid; grid-template-columns: minmax(0, 1fr) 170px minmax(0, 1fr) 170px minmax(0, 1.2fr); align-items: stretch">{flow}</div>
    <div style="margin-top: 8px; font-size: 18px; line-height: 27px; color: #33424F">{E(r["notes"])}</div>
    <div class="pending" style="margin-top: 6px; display: flex; gap: 8px; align-items: center; background: #FBEBD3; border-radius: 10px; padding: 5px 14px; font-size: 18px; line-height: 27px; color: #6E4206">{svg("alert", 20, "#A86508")}<span><b style="color: #A86508">尚待確認｜</b>{E(r["pending"])}</span></div>
  </section>
  <section id="s-facts" style="flex: none; margin: 0 56px">
    <h2 style="{h2}">事實經過<span style="font-size: 18px; font-weight: 500; color: #5B6B7B">（工作負荷重點）</span></h2>
    <div style="margin-top: 6px; display: grid; grid-template-columns: minmax(0, 1.02fr) minmax(0, 0.92fr) minmax(0, 1.16fr) minmax(0, 1fr) minmax(0, 0.9fr); gap: 10px">{tiles}</div>
  </section>
  <section id="s-basic" class="box" style="flex: none; margin: 0 56px; background: #FFFFFF; border-radius: 14px; padding: 10px 18px 12px; display: grid; grid-template-columns: minmax(0, 0.8fr) minmax(0, 1.25fr) minmax(0, 1.15fr); column-gap: 20px; row-gap: 6px; font-size: 18px; line-height: 27px">{basics}</section>
  <section id="s-hold" style="flex: none; margin: 0 56px">
    <h2 style="{h2}; display: flex; justify-content: space-between; align-items: center">法院核心見解{pill}</h2>
    <div style="margin-top: 6px; display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px">{holds}</div>
  </section>
  <section id="s-adv" class="box" style="flex: none; margin: 0 56px; background: #EEE8F6; border-radius: 14px; padding: 8px 18px 10px">
    <h2 style="{h2}; color: #4E3473; display: flex; justify-content: space-between; align-items: center">主管必看重點<span style="font-size: 18px; line-height: 26px; font-weight: 700; color: #4E3473; background: #FFFFFF; border: 1.5px solid #B9A6D6; border-radius: 13px; padding: 0 12px">顧問分析｜非法院見解</span></h2>
    <div style="margin-top: 6px; display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px">{advs}</div>
  </section>
  <section id="s-src" style="flex: none; margin: 0 56px; display: flex; gap: 14px; align-items: baseline; font-size: 18px; line-height: 26px">
    <span style="font-weight: 700; color: {NAVY}">原始判決來源</span><span>{E(s["name"])}</span><span style="color: #4A5A6A">{E(s["url"])}｜{E(s["how"])}</span>
  </section>
  <footer id="s-disc" class="disc" style="margin-top: auto; flex: none; background: #1B2A3A; padding: 13px 40px 14px; text-align: center; font-size: 18px; line-height: 26px; color: #DCE4EC">{E(c["disclaimer"])}</footer>
</main></body></html>'''
