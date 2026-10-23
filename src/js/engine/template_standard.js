// card → HTML｜standard 版型（原版，固定原版配色）。照 casecard/engine/template.py 逐行改寫。
// 只排版，不改寫、不刪減文字。
import { makeE, zip, maskName } from "./common.js";
import { icon } from "./icons.js";
import { typoCss, sansFace } from "./typography.js";

// 把分行的短句接成一行：全形括號前不加空白，其餘以一個空白相接
function join(parts) {
  let out = "";
  for (const x of parts) out += !out || x.startsWith("（") ? x : " " + x;
  return out;
}

const partyName = (p, display) => (p.natural_person && display.mask_natural_person_name ? maskName(p.name) : p.name);

// assets = { fonts, standardCss, heroUrl（右上示意圖；沒有就顯示預留區）}
export function buildHtml(c, assets, draft) {
  const d = c.display || {};
  const E = makeE(d.keep_together || [], (ew) => `<span class="nb">${ew}</span>`);
  const secHead = (ic, text, extra = "") =>
    `<div class="sh-row"><span class="sh" data-chk="chip">${icon(ic, 20, 2.2)}`
    + `<span class="sh-t">${E(text)}</span></span>${extra}</div>`;
  const label = (kind) => (kind === "court"
    ? '<span class="lab lab-court">法院認定</span>'
    : '<span class="lab lab-adv">顧問分析｜非法院見解</span>');

  const info = c.info;
  const pl = c.parties.plaintiff, df = c.parties.defendant;
  const pl_name = partyName(pl, d), df_name = partyName(df, d);

  const tags = zip(["court", "pulse"], c.tags).map(([i, t]) => `<span class="tag" data-chk="chip">${icon(i, 22, 2.2)}<span>${E(t)}</span></span>`).join("");
  const title = c.title.map((t) => `<span class="tl">${E(t)}</span>`).join("");
  const sub = c.subtitle.map((t) => `<span class="sl">${E(t)}</span>`).join("");

  const date_html = E(info.date) + (info.date_pending ? '<span class="pend-chip">待核</span>' : "");
  const infobar = [["court", "法院", E(info.court)], ["doc", "案號", E(info.case_no)],
    ["cal", "裁判日期", date_html], ["scale", "案由", E(info.cause)]]
    .map(([i, k, v]) => `<div class="ib"><div class="ib-k">${icon(i, 20, 2.2)}<span>${k}</span></div><div class="ib-v">${v}</div></div>`).join("");

  const basics = c.basics.map(([k, v]) => `<div class="kv"><div class="k">${E(k)}</div><div class="v">${E(v)}</div></div>`).join("");

  const rel = c.relation;
  const relation = `
      <div class="rel">
        <div class="node"><div class="bub bub-g">${icon("person", 44, 2)}</div>
          <div class="nr">${E(pl.role)}</div><div class="nn">${E(pl_name)}</div></div>
        <div class="mid">
          <div class="arrow-lab"><b>${E(rel.claim.label)}</b><span>${E("（" + rel.claim.note + "）")}</span></div>
          <div class="arr arr-l"></div>
          <div class="arr arr-r"></div>
          <div class="arrow-lab"><b class="red">${E(rel.offset.label)}</b><b class="red">${E(rel.offset.amount ?? "")}</b><span>${E("（" + rel.offset.note + "）")}</span></div>
        </div>
        <div class="node"><div class="bub bub-n">${icon("building", 44, 2)}</div>
          <div class="nr">${E(df.role)}</div><div class="nn">${E(df_name)}</div></div>
      </div>
      `;

  const facts = c.facts.map((t, i) => `<li><span class="num">${i + 1}</span><span class="ft">${E(typeof t === "object" ? t.text : t)}</span></li>`).join("");

  const r = c.result;
  const fl = r.flow;
  let res_body;
  if (fl) {
    res_body = '<div class="ledger">'
      + `<div class="lg-row"><span class="lg-k">${E(fl.damage_label)}</span><span class="lg-v">${E(fl.damage_total)}</span></div>`
      + `<div class="lg-op"><b>${E(fl.fault_op)}</b><span>${E(join(fl.fault_lines))}</span></div>`
      + `<div class="lg-row"><span class="lg-k">${E(fl.after_label)}</span><span class="lg-v">${E(fl.after_fault)}</span></div>`
      + `<div class="lg-op"><b class="red">${E(fl.offset_op)}</b><span>${E(join(fl.offset_lines))}</span></div>`
      + "</div>"
      + `<p class="res-note">${E(r.notes)}</p>`;
  } else {
    res_body = '<ul class="res">' + r.lines.map((t) => `<li>${E(t)}</li>`).join("") + "</ul>";
  }

  const hold_icons = ["clock", "chat", "shield", "coins"];
  const show_issues = d.show_issues ?? true;
  const issue_html = (h) => (show_issues ? `<div class="hq">爭點｜${E(h.issue)}</div>` : "");
  const holds = zip(c.holdings, hold_icons).map(([h]) =>
    `<div class="hc">${issue_html(h)}`
    + `<div class="hh"><span>${E(h.head)}</span></div>`
    + `<div class="hb">${E(h.body)}</div></div>`).join("");

  const adv_icons = ["search", "group", "heart", "doc"];
  const advs = zip(c.advisory, adv_icons).map(([a]) =>
    `<div class="ac"><div class="ah"><span>${E(a.head)}</span></div>`
    + `<div class="ab">${E(a.body)}</div></div>`).join("");

  const s = c.source_card;
  const draft_bar = draft ? '<div class="draftbadge" id="draftbadge">草稿｜法院內容尚未對照<br>原始深入分析，不得外流</div>' : "";

  const hero_html = assets.heroUrl
    ? `<img class="hero" src="${assets.heroUrl}" alt="">`
    : '<div class="hero hero-ph">主視覺預留區<br>（尚無獨立素材）</div>';

  return `<!doctype html><html lang="zh-Hant-TW"><head><meta charset="utf-8">
<style>${sansFace(assets.fonts)}</style>
<style>${assets.standardCss}</style>${typoCss(assets.fonts, "h1, .sh-t, .hh, .ah", ".rt-v, .lg-v")}</head><body>
<main id="card">
  <header class="head">
    ${hero_html}${draft_bar}
    <div class="head-l">
      <div class="tags">${tags}</div>
      <h1>${title}</h1>
      <p class="sub">${sub}</p>
    </div>
  </header>

  <section class="infobar box">${infobar}</section>

  <div class="row">
    <section class="box col" id="s-basic">${secHead("person", "案件基本資料")}<div class="kvs">${basics}</div></section>
    <section class="box col" id="s-rel">${secHead("group", "法律關係圖")}${relation}</section>
  </div>

  <div class="row rb">
    <section class="box col" id="s-facts">${secHead("clip", "事實經過（工作負荷重點）")}
      <ol class="facts">${facts}</ol>
    </section>
    <section class="box col" id="s-result">${secHead("gavel", "判決結果", '<div class="res-total"><span class="rt-k">被告應給付</span><span class="rt-v">' + E(r.total) + "</span></div>")}
      ${res_body}
      <div class="pending">${icon("alert", 22, 2.2)}<div><b>尚待確認｜</b>${E(r.pending)}</div></div>
    </section>
  </div>

  <section class="box" id="s-hold">${secHead("scale", "法院核心見解", label("court"))}
    <div class="grid4">${holds}</div></section>

  <section class="box adv" id="s-adv">${secHead("bulb", "主管必看重點", label("adv"))}
    <div class="grid4">${advs}</div></section>

  <section class="box src" id="s-src"><div class="src-row">${secHead("link", "原始判決來源")}
    <div class="src-b"><b>${E(s.name)}</b><span class="url">${E(s.url)}</span><span class="sep">｜</span><span>${E(s.how)}</span></div></div>
  </section>

  <footer class="disc" id="s-disc">${E(c.disclaimer)}</footer>
</main></body></html>`;
}
