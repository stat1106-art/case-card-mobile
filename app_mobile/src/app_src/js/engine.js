/* 職災小卡 出圖程式（瀏覽器版）。照 casecard/engine/*.py 逐行改寫成 JavaScript，產生同樣的 HTML。
   只排版，不改寫、不刪減、不縮小文字。 */
(function (G) {
'use strict';
const ICONS = {
 "court":   '<path d="M3 9.5 12 4l9 5.5"/><path d="M4 20h16"/><path d="M6 10.5v7M10 10.5v7M14 10.5v7M18 10.5v7"/>',
 "doc":     '<path d="M6 3h8l4 4v14H6z"/><path d="M14 3v4h4"/><path d="M9 12h6M9 16h6"/>',
 "cal":     '<rect x="3.5" y="5" width="17" height="15" rx="2"/><path d="M3.5 10h17M8 3v4M16 3v4"/>',
 "scale":   '<path d="M12 4v16M7 20h10M5 7h14"/><path d="M5 7l-3 6a3 3 0 0 0 6 0zM19 7l-3 6a3 3 0 0 0 6 0z"/>',
 "person":  '<circle cx="12" cy="8" r="4"/><path d="M4.5 20.5c1-4 4-6 7.5-6s6.5 2 7.5 6"/>',
 "building":'<rect x="5" y="3.5" width="14" height="17" rx="1.5"/><path d="M9 8h2M13 8h2M9 12h2M13 12h2M10.5 20.5v-4h3v4"/>',
 "group":   '<circle cx="9" cy="8.5" r="3.2"/><circle cx="17" cy="9.5" r="2.5"/><path d="M3 19.5c.8-3.3 3.2-5 6-5s5.2 1.7 6 5M15.5 14.6c2.6-.2 4.6 1.4 5.2 4.4"/>',
 "clip":    '<rect x="5" y="4.5" width="14" height="16.5" rx="2"/><path d="M9 3h6v3H9zM8.5 11h7M8.5 15h5"/>',
 "gavel":   '<path d="M13.5 4.5l6 6M11 7l6 6M12.3 5.8l-4 4 6 6 4-4"/><path d="M10.3 11.8 3.5 18.6l1.9 1.9 6.8-6.8"/>',
 "bulb":    '<path d="M9 18h6M10 21h4"/><path d="M12 3a6 6 0 0 0-3.5 10.9c.6.5 1 1.3 1 2.1h5c0-.8.4-1.6 1-2.1A6 6 0 0 0 12 3z"/>',
 "link":    '<path d="M10 14a4 4 0 0 0 5.7 0l3-3a4 4 0 0 0-5.7-5.7l-1 1"/><path d="M14 10a4 4 0 0 0-5.7 0l-3 3a4 4 0 0 0 5.7 5.7l1-1"/>',
 "check":   '<circle cx="12" cy="12" r="9"/><path d="M7.8 12.3l2.8 2.8 5.6-5.8"/>',
 "alert":   '<circle cx="12" cy="12" r="9"/><path d="M12 7.5v5.5M12 16.3v.2"/>',
 "clock":   '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.5 2"/>',
 "chat":    '<path d="M4 5h16v11H9l-5 4z"/><path d="M8 9.5h8M8 12.5h5"/>',
 "shield":  '<path d="M12 3l7.5 3v5.5c0 4.5-3.2 8-7.5 9.5-4.3-1.5-7.5-5-7.5-9.5V6z"/>',
 "coins":   '<ellipse cx="12" cy="6.5" rx="7" ry="2.8"/><path d="M5 6.5v5c0 1.5 3.1 2.8 7 2.8s7-1.3 7-2.8v-5M5 11.5v5c0 1.5 3.1 2.8 7 2.8s7-1.3 7-2.8v-5"/>',
 "search":  '<circle cx="10.5" cy="10.5" r="6"/><path d="M15 15l5.5 5.5"/>',
 "heart":   '<path d="M12 20s-7.5-4.6-7.5-10.2A4.3 4.3 0 0 1 12 7.3a4.3 4.3 0 0 1 7.5 2.5C19.5 15.4 12 20 12 20z"/>',
 "pulse":   '<path d="M3 12h4l2-5 4 10 2-5h6"/>',
 "overtime": '<circle cx="11" cy="13" r="8"/><path d="M11 9v4l2.5 1.6"/><path d="M20.5 4.8a3.4 3.4 0 0 1-4.3 4.3 3.4 3.4 0 1 0 4.3-4.3z"/>',
 "newhire":  '<rect x="3.5" y="5" width="17" height="15" rx="2"/><path d="M3.5 10h17M8 3v4M16 3v4"/><path d="M11 13.5h2v4"/>',
 "event":    '<path d="M5 3h7l-.4 4.5a3.1 3.1 0 0 1-6.2 0z"/><path d="M8.5 10.6V18M6 18h5"/><path d="M14 9.5h7v6h-2.5L16 18v-2.5h-2z"/>',
 "course":   '<path d="M2.5 9 12 4.5 21.5 9 12 13.5z"/><path d="M6.5 11v4.5c1.5 1.6 3.4 2.4 5.5 2.4s4-.8 5.5-2.4V11"/><path d="M21.5 9v5"/>',
 "phone":    '<rect x="6.5" y="2.5" width="11" height="19" rx="2.5"/><path d="M9.5 8h5M9.5 11.5h3.5"/><path d="M11 18.5h2"/>',
 "bell":     '<path d="M6 16v-5a6 6 0 0 1 12 0v5l1.5 2h-15z"/><path d="M10 20.5a2 2 0 0 0 4 0"/>',
 "ledger":   '<rect x="4" y="5" width="16" height="14" rx="1.5"/><path d="M12 5v14M4 10h16"/>',
 "gauge":    '<path d="M3.5 16a8.5 8.5 0 1 1 17 0"/><path d="M12 16l4.5-5"/><path d="M3.5 16h2.5M18 16h2.5"/>',
 "shieldalert": '<path d="M12 3l7.5 3v5.5c0 4.5-3.2 8-7.5 9.5-4.3-1.5-7.5-5-7.5-9.5V6z"/><path d="M12 8v4.5M12 15.5v.2"/>',
};
function iconStd(name, size, stroke, cls) {
  size = size == null ? 24 : size; stroke = stroke == null ? 2.0 : stroke; cls = cls || 'ic';
  if (!(name in ICONS)) throw new Error('KeyError ' + name);
  return `<svg class="${cls}" width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" ` +
    `stroke="currentColor" stroke-width="${pyNum(stroke)}" stroke-linecap="round" stroke-linejoin="round" ` +
    `aria-hidden="true">${ICONS[name]}</svg>`;
}
// Python str(float)：整數值的浮點數印成 "2.0"
function pyNum(x) { return (typeof x === 'object' && x && 'f' in x) ? pyFloat(x.f) : String(x); }
function F(v) { return { f: v }; }
function pyFloat(v) {
  if (Object.is(v, -0)) return '-0.0';
  if (Number.isInteger(v)) return v.toFixed(1);
  return String(v);
}
function esc(s) {
  return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#x27;');
}
const plen = s => Array.from(s).length;
function makeE(keep, wrap) {
  const K = [...keep].sort((a, b) => plen(b) - plen(a)); // Python sorted(key=len, reverse=True) 穩定排序
  return s => { let out = esc(s); for (const w of K) { const ew = esc(w); out = out.split(ew).join(wrap(ew)); } return out; };
}
function svg(name, size, color, stroke) {
  color = color || 'currentColor'; stroke = stroke == null ? 2.2 : stroke;
  if (!(name in ICONS)) throw new Error('KeyError ' + name);
  return `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="${color}" ` +
    `stroke-width="${stroke}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${ICONS[name]}</svg>`;
}
function maskName(name) {
  const a = Array.from(name);
  if (a.length <= 1) return name;
  if (a.length === 2) return a[0] + '○';
  return a[0] + '○'.repeat(a.length - 2) + a[a.length - 1];
}
function zip(a, b) { const n = Math.min(a.length, b.length), o = []; for (let i = 0; i < n; i++) o.push([a[i], b[i]]); return o; }

/* typography.py */
const NUMS = 'unicode-range:U+0030-0039,U+002C,U+002E,U+0025;';
function typoCss(ref, titleSel, amountSel) {
  const face = (fam, file, w, extra) => `@font-face{font-family:"${fam}";src:url("${ref(file)}") format("truetype");font-weight:${w};font-display:block;${extra || ''}}`;
  return '<style>' + face('CardTitle', 'NotoSerifTC-VF.ttf', '100 900') + face('CardNum', 'BarlowCondensed-Bold.ttf', '100 800', NUMS)
    + face('CardNum', 'BarlowCondensed-ExtraBold.ttf', '801 900', NUMS)
    + titleSel + '{font-family:"CardTitle","CardSans",serif}' + amountSel + '{font-family:"CardNum","CardSans",sans-serif}' + '</style>';
}

/* template_classic.py */
function buildClassic(c, draft, ref, A) {
  const d = c.display || {};
  const E = makeE(d.keep_together || [], ew => `<span style="white-space: nowrap">${ew}</span>`);
  const K = c._skin_roles, band = K.dark;
  const info = c.info, rel = c.relation, r = c.result;
  const pl = c.parties.plaintiff, df = c.parties.defendant;
  const pl_name = (pl.natural_person && d.mask_natural_person_name) ? maskName(pl.name) : pl.name;
  const df_name = df.name, dfa = Array.from(df_name);
  const df_lines = dfa.length > 6 ? [dfa.slice(0, 5).join(''), dfa.slice(5).join('')] : [df_name];
  const fl = r.flow;
  const font_url = ref('NotoSansTC-VF.ttf');
  const hero_svg = A.heroSvg || '';
  const tags = `<span style="font-size: 18px; line-height: 26px; font-weight: 700; color: ${K.on_dark}; background: ${K.dark}; border-radius: 6px; padding: 0 10px">${E(c.tags[0])}</span>`
    + `<span style="font-size: 18px; line-height: 26px; font-weight: 700; color: ${K.on_dark}; background: ${K.dark}; border: 1.5px solid ${K.dark}; border-radius: 6px; padding: 0 10px">${E(c.tags[1])}</span>`;
  const title = c.title.map(t => `<span style="display: block">${E(t)}</span>`).join('');
  const sub = c.subtitle.map(t => E(t)).join('<br>');
  const draft_badge = draft ? '<span id="draftbadge" style="position: absolute; left: 14px; top: 14px; font-size: 18px; line-height: 24px; font-weight: 700; '
    + 'color: #8A3B12; background: #FDF1E6; border: 1.5px solid #E3A36F; border-radius: 8px; padding: 4px 10px">草稿｜法院內容尚未對照原始分析</span>' : '';
  const info_cell = (k, v, first) => {
    const bl = first ? '' : ` border-left: 1px solid ${K.line};`;
    return `<div style="padding: 9px 16px 10px;${bl}"><div style="font-size: 18px; line-height: 26px; color: ${K.muted}">${k}</div>`
      + `<div style="font-size: 20px; line-height: 30px; font-weight: 700">${E(v)}</div></div>`;
  };
  const infobar = info_cell('法院', info.court, true) + info_cell('案號', info.case_no) + info_cell('裁判日期', info.date) + info_cell('案由', info.cause);
  const node = (left, top, color, icon) => `<div style="position: absolute; left: ${left}px; top: ${top}px; width: 56px; height: 56px; border-radius: 50%; background: ${color}; `
    + `color: ${K.on_dark}; display: flex; align-items: center; justify-content: center">${svg(icon, 30, null, 2)}</div>`;
  const arrow = (left, top, width, color, rot, head) => {
    head = head || 'right';
    const tr = rot != null ? ` transform-origin: 0 50%; transform: rotate(${rot}deg);` : '';
    const hd = head === 'right'
      ? `<span style="position: absolute; right: -2px; top: -6px; width: 0; height: 0; border-top: 7.5px solid transparent; border-bottom: 7.5px solid transparent; border-left: 13px solid ${color}"></span>`
      : `<span style="position: absolute; left: -2px; top: -6px; width: 0; height: 0; border-top: 7.5px solid transparent; border-bottom: 7.5px solid transparent; border-right: 13px solid ${color}"></span>`;
    return `<div style="position: absolute; left: ${left}px; top: ${top}px; width: ${width}px; height: 3px; background: ${color};${tr}">${hd}</div>`;
  };
  const relation = `
    <div class="box" style="position: relative; margin-top: 6px; height: 240px; background: ${K.card}; box-shadow: inset 0 0 0 1.5px ${K.line}; border-radius: 16px">
      <div style="position: absolute; left: 334px; top: 8px; width: 300px; text-align: center; font-size: 20px; line-height: 28px"><span style="font-size: 18px; color: ${K.muted}">${E(rel.court.role)}　</span><b>${E(rel.court.name)}</b></div>
      ${node(456, 42, K.dark, 'scale')}
      ${node(178, 158, K.plaintiff, 'person')}
      <div style="position: absolute; left: 24px; top: 158px; width: 140px; text-align: right"><div style="font-size: 18px; line-height: 26px; color: ${K.muted}">${E(pl.role)}</div><div style="font-size: 20px; line-height: 28px; font-weight: 700">${E(pl_name)}</div></div>
      ${node(734, 158, K.defendant, 'building')}
      <div style="position: absolute; left: 802px; top: 143px; width: 150px"><div style="font-size: 18px; line-height: 26px; color: ${K.muted}">${E(df.role)}</div><div style="font-size: 20px; line-height: 28px; font-weight: 700">${df_lines.map(x => E(x)).join('<br>')}</div></div>
      ${arrow(234.6, 172.6, 237, K.plaintiff, -22.65)}
      <div style="position: absolute; left: 60px; top: 66px; width: 250px; text-align: right"><div style="font-size: 18px; line-height: 26px; font-weight: 700; color: ${K.plaintiff}">${E(rel.claim.label)}</div><div style="font-size: 18px; line-height: 26px; color: ${K.ink2}">${E('（' + rel.claim.note + '）')}</div></div>
      ${arrow(514.5, 81.2, 237, K.dark, 22.65)}
      <div style="position: absolute; left: 658px; top: 66px; width: 250px"><div style="font-size: 18px; line-height: 26px; font-weight: 700">${E(rel.order.label)}</div><div class="amt" style="font-size: 20px; line-height: 26px; font-weight: 900">${E(rel.order.amount)}</div></div>
      ${arrow(240, 182, 490, K.deduct, null, 'left')}
      <div style="position: absolute; left: 284px; top: 188px; width: 400px; text-align: center"><div style="font-size: 18px; line-height: 26px; font-weight: 700; color: ${K.deduct}">${E(rel.offset.label + ' ' + rel.offset.amount)}</div><div style="font-size: 18px; line-height: 26px; color: ${K.ink2}">${E('（' + rel.offset.note + '）')}</div></div>
    </div>`;
  const op = (main, lines, size) => {
    const ls = lines.map(x => `<div style="font-size: 18px; line-height: 24px; color: ${K.ink2}">${E(x)}</div>`).join('');
    return `<div style="display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 0 6px">`
      + `<div style="font-size: ${size}px; line-height: 28px; font-weight: 900; color: ${K.deduct}">${E(main)}</div>`
      + `<div style="width: 120px; height: 3px; background: ${K.deduct}; position: relative; margin: 3px 0 4px"><span style="position: absolute; right: -2px; top: -6px; width: 0; height: 0; border-top: 7.5px solid transparent; border-bottom: 7.5px solid transparent; border-left: 12px solid ${K.deduct}"></span></div>${ls}</div>`;
  };
  const valbox = (label, val, fin) => fin
    ? `<div style="background: ${K.money}; color: ${K.money_text}; border-radius: 12px; padding: 10px 16px; display: flex; flex-direction: column; justify-content: center">`
      + `<div style="font-size: 18px; line-height: 26px; color: ${K.money_sub}">${E(label)}</div><div class="amt" style="font-size: 27px; line-height: 34px; font-weight: 900">${E(val)}</div></div>`
    : `<div style="background: ${K.card}; box-shadow: inset 0 0 0 1.5px ${K.line}; border-radius: 12px; padding: 10px 16px; display: flex; flex-direction: column; justify-content: center">`
      + `<div style="font-size: 18px; line-height: 26px; color: ${K.muted}">${E(label)}</div><div class="amt" style="font-size: 22px; line-height: 30px; font-weight: 900">${E(val)}</div></div>`;
  const flow = valbox(fl.damage_label, fl.damage_total) + op(fl.fault_op, fl.fault_lines, 21) + valbox(fl.after_label, fl.after_fault) + op(fl.offset_op, fl.offset_lines, 20) + valbox(fl.final_label, r.total, true);
  const fact = f => {
    const [t, ic] = (f && typeof f === 'object') ? [f.text, f.icon || 'check'] : [f, 'check'];
    return `<div style="display: flex; gap: 10px; align-items: flex-start"><span style="flex: none; width: 38px; height: 38px; border-radius: 50%; background: ${K.dark}; color: ${K.on_dark}; display: flex; align-items: center; justify-content: center">${svg(ic, 22)}</span>`
      + `<span style="font-size: 18px; line-height: 27px">${E(t)}</span></div>`;
  };
  const facts = c.facts.map(fact).join('');
  const tl = c.timeline;
  const dot_open = `<span style="width: 16px; height: 16px; margin-top: 6px; border-radius: 50%; background: ${K.dot_fill}; border: 3px solid ${band}; box-sizing: border-box"></span>`;
  const row = 'position: relative; display: grid; grid-template-columns: 34px minmax(0, 1fr); font-size: 18px; line-height: 28px';
  const holds = c.holdings.map(h => `<div class="hc" style="background: ${K.card}; box-shadow: inset 0 0 0 1.5px ${K.line}; border-radius: 14px; padding: 9px 10px 10px; border-top: 4px solid ${K.plaintiff}">`
    + `<div style="font-size: 18px; line-height: 26px; font-weight: 900">${E(h.head)}</div>`
    + `<div style="margin-top: 4px; font-size: 18px; line-height: 27px; color: ${K.ink2}">${E(h.body)}</div></div>`).join('');
  const advs = zip(c.advisory, c.advisory_icons || ['search', 'group', 'bell', 'ledger']).map(([a, ic]) =>
    `<div class="ac"><div style="display: flex; gap: 6px; align-items: center">${svg(ic, 22, K.adv_ink)}<span style="font-size: 18px; line-height: 26px; font-weight: 900">${E(a.head)}</span></div>`
    + `<div style="margin-top: 2px; font-size: 18px; line-height: 27px; color: ${K.ink2}">${E(a.body)}</div></div>`).join('');
  const s = c.source_card;
  const pill_court = `<span style="font-size: 18px; line-height: 26px; font-weight: 700; color: ${K.pill_text}; background: ${K.pill_bg}; box-shadow: inset 0 0 0 1.5px ${K.pill_line}; border-radius: 6px; padding: 0 12px">法院認定</span>`;
  const h2 = `margin: 0; font-size: 21px; line-height: 30px; font-weight: 900; color: ${K.ink}`;
  return `<!doctype html><html lang="zh-Hant-TW"><head><meta charset="utf-8">
<style>@font-face{font-family:"CardSans";src:url("${font_url}") format("truetype");font-weight:100 900;font-display:block;}
html,body{margin:0;width:1080px;height:1620px;overflow:hidden;background:${K.page}}</style>${typoCss(ref, 'h1, h2, .hc > div:first-child, .ac > div:first-child', '.amt')}</head><body>
<main id="card" style="position: relative; width: 1080px; height: 1620px; overflow: hidden; background: ${c._page_bg}; color: ${K.ink}; font-family: CardSans, sans-serif; display: flex; flex-direction: column; gap: 8px">
  <header id="s-head" style="position: relative; flex: none; height: 290px; background: transparent">
    <div style="position: absolute; left: 56px; top: 30px; width: 500px; color: ${K.ink}">
      <div style="display: flex; gap: 8px">${tags}</div>
      <h1 style="margin: 14px 0 0; font-size: 40px; line-height: 52px; font-weight: 900">${title}</h1>
      <p style="margin: 10px 0 0; font-size: 19px; line-height: 29px; font-weight: 500; color: ${K.ink2}">${sub}</p>
    </div>
    <div style="position: absolute; right: 0; top: 0; width: 503px; height: 290px; overflow: hidden; background: #DCE6F0">
      ${hero_svg}
      <span style="position: absolute; right: 14px; top: 14px; font-size: 18px; line-height: 26px; font-weight: 700; color: #1D1B18; background: #FFFFFF; border-radius: 13px; padding: 0 10px">${E(c.hero.caption)}</span>
      ${draft_badge}
    </div>
  </header>

  <section id="s-info" class="box" data-overlap="ok" style="position: relative; flex: none; margin: -36px 56px 0; display: grid; grid-template-columns: minmax(0, 0.92fr) minmax(0, 1.16fr) minmax(0, 0.92fr) minmax(0, 1fr); background: ${K.card}; border-radius: 14px; box-shadow: 0 0 0 1.5px ${K.line}">${infobar}</section>

  <section id="s-rel" style="flex: none; margin: 0 56px"><h2 style="${h2}"><span class="chip" style="display: inline-block; background: ${K.dark}; color: ${K.on_dark}; border-radius: 6px; padding: 0 10px">法律關係圖</span></h2>${relation}</section>

  <section id="s-result" style="flex: none; margin: 0 56px">
    <h2 style="${h2}; display: flex; justify-content: space-between; align-items: center"><span class="chip" style="display: inline-block; background: ${K.dark}; color: ${K.on_dark}; border-radius: 6px; padding: 0 10px">判決結果</span>${pill_court}</h2>
    <div style="margin-top: 6px; display: grid; grid-template-columns: minmax(0, 1fr) 170px minmax(0, 1fr) 170px minmax(0, 1.2fr); align-items: stretch">${flow}</div>
    <div style="margin-top: 8px; font-size: 18px; line-height: 27px; color: ${K.ink2}">${E(r.notes)}</div>
    <div class="pending" style="margin-top: 6px; background: #FDF1E6; box-shadow: inset 0 0 0 1.5px #EFC7A5; border-radius: 10px; padding: 5px 14px; font-size: 18px; line-height: 27px; color: #6B3A12"><b style="color: #B8540F">尚待確認｜</b>${E(r.pending)}</div>
  </section>

  <section id="s-facts" style="flex: none; margin: 0 56px">
    <h2 style="${h2}"><span class="chip" style="display: inline-block; background: ${K.dark}; color: ${K.on_dark}; border-radius: 6px; padding: 0 10px">事實經過</span><span style="font-size: 18px; font-weight: 500; color: ${K.muted}">（工作負荷重點）</span></h2>
    <div class="box" style="position: relative; margin-top: 6px; background: ${K.card}; box-shadow: inset 0 0 0 1.5px ${K.line}; border-radius: 16px; padding: 8px 20px 8px 20px">
      <div style="position: absolute; left: 31px; top: 26px; bottom: 30px; width: 3px; background: ${K.line2}"></div>
      <div style="${row}">${dot_open}<div><b style="color: ${band}">${E(tl.start.date)}　${E(tl.start.label)}</b><span style="margin-left: 12px">${E(tl.start.text)}</span></div></div>
      <div style="${row}; margin-top: 5px">${dot_open}<div><b style="color: ${band}">${E(c.facts_anchor)}</b>
        <div style="margin-top: 6px; display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); column-gap: 18px; row-gap: 8px">${facts}</div></div></div>
      <div style="${row}; margin-top: 5px"><span style="width: 16px; height: 16px; margin-top: 6px; border-radius: 50%; background: ${K.money}"></span><div><b style="color: ${K.money}">${E(tl.onset.date)}　${E(tl.onset.label)}</b><span style="margin-left: 12px">${E(tl.onset.text)}</span></div></div>
    </div>
  </section>

  <section id="s-hold" style="flex: none; margin: 0 56px">
    <h2 style="${h2}; display: flex; justify-content: space-between; align-items: center"><span class="chip" style="display: inline-block; background: ${K.dark}; color: ${K.on_dark}; border-radius: 6px; padding: 0 10px">法院核心見解</span>${pill_court}</h2>
    <div style="margin-top: 6px; display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px">${holds}</div>
  </section>

  <section id="s-adv" class="box" style="flex: none; margin: 0 56px; background: ${K.adv_bg}; box-shadow: inset 0 0 0 1.5px ${K.adv_line}; border-radius: 14px; padding: 7px 18px 9px">
    <h2 style="margin: 0; font-size: 21px; line-height: 30px; font-weight: 900; color: ${K.adv_ink}; display: flex; justify-content: space-between; align-items: center">主管必看重點<span style="font-size: 18px; line-height: 26px; font-weight: 700; color: ${K.adv_ink}; background: ${K.adv_pill_bg}; border: 1.5px solid ${K.adv_line}; border-radius: 6px; padding: 0 12px">顧問分析｜非法院見解</span></h2>
    <div style="margin-top: 6px; display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px">${advs}</div>
  </section>

  <section id="s-src" style="flex: none; margin: 0 56px; display: flex; gap: 14px; align-items: baseline; font-size: 18px; line-height: 26px">
    <span style="font-weight: 700; color: ${band}">原始判決來源</span><span>${E(s.name)}</span><span style="color: ${K.ink2}">${E(s.url)}｜${E(s.how)}</span>
  </section>

  <footer id="s-disc" class="disc" style="margin-top: auto; flex: none; background: ${band}; padding: 13px 40px 14px; text-align: center; font-size: 18px; line-height: 26px; color: ${K.footer_text}">${E(c.disclaimer)}</footer>
</main></body></html>`;
}

/* template_light.py */
function buildLight(c, draft, ref, A) {
  const d = c.display || {};
  const E = makeE(d.keep_together || [], ew => `<span style="white-space: nowrap">${ew}</span>`);
  const NAVY = '#23466E', TEAL = '#0F8070', SLATE = '#4F5D6B', AMBER = '#C47A12', PLUM = '#6A4B95';
  const info = c.info, rel = c.relation, r = c.result, fl = c.result.flow;
  const pl = c.parties.plaintiff, df = c.parties.defendant;
  const pl_name = (pl.natural_person && d.mask_natural_person_name) ? maskName(pl.name) : pl.name;
  const font_url = ref('NotoSansTC-VF.ttf');
  const hero_svg = A.heroSvg || '';
  const draft_badge = draft ? '<span id="draftbadge" style="position: absolute; left: 14px; top: 14px; font-size: 18px; line-height: 24px; font-weight: 700; color: #8A3B12; background: #FDF1E6; border: 1.5px solid #E3A36F; border-radius: 8px; padding: 4px 10px">草稿｜法院內容尚未對照原始分析</span>' : '';
  const tags = `<span style="font-size: 18px; line-height: 26px; font-weight: 700; color: #FFFFFF; background: ${NAVY}; border-radius: 13px; padding: 0 12px">${E(c.tags[0])}</span>`
    + `<span style="font-size: 18px; line-height: 26px; font-weight: 700; color: ${NAVY}; border: 1.5px solid ${NAVY}; border-radius: 13px; padding: 0 12px">${E(c.tags[1])}</span>`;
  const title = c.title.map(t => `<span style="display: block">${E(t)}</span>`).join('');
  const sub = c.subtitle.map(t => E(t)).join('<br>');
  const cell = (ic, k, v, first) => {
    const bl = first ? '' : ' border-left: 1px solid #E1E7ED;';
    return `<div style="padding: 9px 16px 10px;${bl}"><div style="display: flex; align-items: center; gap: 6px; font-size: 18px; line-height: 26px; color: #5B6B7B">${svg(ic, 20, NAVY)}${k}</div>`
      + `<div style="font-size: 20px; line-height: 30px; font-weight: 700">${E(v)}</div></div>`;
  };
  const infobar = cell('court', '法院', info.court, true) + cell('doc', '案號', info.case_no) + cell('cal', '裁判日期', info.date) + cell('scale', '案由', info.cause);
  const node = (left, width, color, icon, role, name) => `<div style="position: absolute; left: ${left}px; top: 14px; width: ${width}px; text-align: center">`
    + `<div style="width: 56px; height: 56px; margin: 0 auto; border-radius: 50%; background: ${color}; color: #FFFFFF; display: flex; align-items: center; justify-content: center">${svg(icon, 30, null, 2)}</div>`
    + `<div style="margin-top: 6px; font-size: 18px; line-height: 26px; color: #5B6B7B">${E(role)}</div><div style="font-size: 20px; line-height: 28px; font-weight: 700">${E(name)}</div></div>`;
  const harrow = (left, color, top_txt, top_style, bot_txt, bot_style) =>
    `<div style="position: absolute; left: ${left}px; width: 296px; top: 41px; height: 3px; background: ${color}"><span style="position: absolute; right: -2px; top: -6px; width: 0; height: 0; border-top: 7.5px solid transparent; border-bottom: 7.5px solid transparent; border-left: 13px solid ${color}"></span></div>`
    + `<div style="position: absolute; left: ${left}px; width: 296px; top: 12px; text-align: center; ${top_style}">${top_txt}</div>`
    + `<div style="position: absolute; left: ${left}px; width: 296px; top: 50px; text-align: center; ${bot_style}">${bot_txt}</div>`;
  const relation = `<div class="box" style="position: relative; margin-top: 6px; height: 188px; background: #FFFFFF; border-radius: 14px">
      ${node(25, 170, TEAL, 'person', pl.role, pl_name)}
      ${node(399, 170, NAVY, 'court', rel.court.role, rel.court.name)}
      ${node(758, 200, SLATE, 'building', df.role, df.name)}
      ${harrow(150, TEAL, E(rel.claim.label), `font-size: 18px; line-height: 26px; font-weight: 700; color: ${TEAL}`, E('（' + rel.claim.note + '）'), 'font-size: 18px; line-height: 26px; color: #4A5A6A')}
      ${harrow(522, NAVY, E(rel.order.label), `font-size: 18px; line-height: 26px; font-weight: 700; color: ${NAVY}`, '<span class="amt">' + E(rel.order.amount) + '</span>', `font-size: 20px; line-height: 26px; font-weight: 900; color: ${NAVY}`)}
      <div style="position: absolute; left: 110px; width: 748px; top: 136px; height: 30px; border: 3px solid ${AMBER}; border-top: none; border-radius: 0 0 12px 12px; box-sizing: border-box"></div>
      <span style="position: absolute; left: 103px; top: 124px; width: 0; height: 0; border-left: 7.5px solid transparent; border-right: 7.5px solid transparent; border-bottom: 13px solid ${AMBER}"></span>
      <div style="position: absolute; left: 484px; top: 150px; transform: translateX(-50%); white-space: nowrap; background: #FFFFFF; padding: 0 12px; font-size: 18px; line-height: 28px"><b style="color: #A86508">${E(rel.offset.label + ' ' + rel.offset.amount)}</b><span style="color: #4A5A6A">${E('（' + rel.offset.note + '）')}</span></div>
    </div>`;
  const op = (main, lines, size) => {
    const ls = lines.map(x => `<div style="font-size: 18px; line-height: 24px; color: #4A5A6A">${E(x)}</div>`).join('');
    return `<div style="display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; padding: 0 6px"><div style="font-size: ${size}px; line-height: 28px; font-weight: 900; color: #A86508">${E(main)}</div>`
      + `<div style="width: 120px; height: 3px; background: ${AMBER}; position: relative; margin: 3px 0 4px"><span style="position: absolute; right: -2px; top: -6px; width: 0; height: 0; border-top: 7.5px solid transparent; border-bottom: 7.5px solid transparent; border-left: 12px solid ${AMBER}"></span></div>${ls}</div>`;
  };
  const vbox = (label, val, fin) => fin
    ? `<div style="background: ${NAVY}; color: #FFFFFF; border-radius: 12px; padding: 10px 16px; display: flex; flex-direction: column; justify-content: center"><div style="font-size: 18px; line-height: 26px; color: #C9D6E6">${E(label)}</div><div class="amt" style="font-size: 27px; line-height: 34px; font-weight: 900">${E(val)}</div></div>`
    : `<div style="background: #FFFFFF; border-radius: 12px; padding: 10px 16px; display: flex; flex-direction: column; justify-content: center"><div style="font-size: 18px; line-height: 26px; color: #5B6B7B">${E(label)}</div><div class="amt" style="font-size: 22px; line-height: 30px; font-weight: 900">${E(val)}</div></div>`;
  const flow = vbox(fl.damage_label, fl.damage_total) + op(fl.fault_op, fl.fault_lines, 21) + vbox(fl.after_label, fl.after_fault) + op(fl.offset_op, fl.offset_lines, 20) + vbox(fl.final_label, r.total, true);
  const tiles = c.facts.map(f => `<div class="hc" style="background: #FFFFFF; border-radius: 14px; padding: 10px 10px 10px"><div style="width: 44px; height: 44px; border-radius: 50%; background: #E0F1EE; color: ${TEAL}; display: flex; align-items: center; justify-content: center">${svg(f.icon || 'check', 26, null, 2)}</div>`
    + `<div style="margin-top: 8px; font-size: 18px; line-height: 27px">${E(f.text)}</div></div>`).join('');
  const b = Array.isArray(c.basics) ? Object.fromEntries(c.basics) : Object.assign({}, c.basics);
  for (const k of ['職務', '時間', '月薪', '疾病']) if (!(k in b)) throw new Error('KeyError ' + k);
  const basics = `<div style="display: flex; gap: 8px"><b style="flex: none; color: #5B6B7B">職務</b><span>${E(b['職務'])}</span></div>`
    + `<div style="display: flex; gap: 8px"><b style="flex: none; color: #5B6B7B">時間</b><span>${E(b['時間'])}</span></div>`
    + `<div style="display: flex; gap: 8px"><b style="flex: none; color: #5B6B7B">月薪</b><span>${E(b['月薪'])}</span></div>`
    + `<div style="grid-column: 1 / -1; display: flex; gap: 8px"><b style="flex: none; color: #5B6B7B">疾病</b><span>${E(b['疾病'])}</span></div>`;
  const hold_ic = ['gauge', 'clip', 'shieldalert', 'coins'];
  const holds = zip(c.holdings, hold_ic).map(([h, ic]) => `<div class="hc" style="background: #FFFFFF; border-radius: 14px; padding: 9px 10px 10px"><div style="display: flex; gap: 6px; align-items: center">${svg(ic, 22, NAVY)}<span style="font-size: 18px; line-height: 26px; font-weight: 900">${E(h.head)}</span></div>`
    + `<div style="margin-top: 4px; font-size: 18px; line-height: 27px; color: #4A5A6A">${E(h.body)}</div></div>`).join('');
  const advs = zip(c.advisory, c.advisory_icons || ['search', 'group', 'bell', 'ledger']).map(([a, ic]) =>
    `<div class="ac"><div style="display: flex; gap: 8px; align-items: center">${svg(ic, 24, PLUM)}<span style="font-size: 19px; line-height: 27px; font-weight: 900">${E(a.head)}</span></div>`
    + `<div style="margin-top: 2px; font-size: 18px; line-height: 27px; color: #3E3550">${E(a.body)}</div></div>`).join('');
  const s = c.source_card;
  const pill = `<span style="font-size: 18px; line-height: 26px; font-weight: 700; color: #FFFFFF; background: ${NAVY}; border-radius: 13px; padding: 0 12px">法院認定</span>`;
  const h2 = 'margin: 0; font-size: 21px; line-height: 30px; font-weight: 900';
  return `<!doctype html><html lang="zh-Hant-TW"><head><meta charset="utf-8">
<style>@font-face{font-family:"CardSans";src:url("${font_url}") format("truetype");font-weight:100 900;font-display:block;}
html,body{margin:0;width:1080px;height:1620px;overflow:hidden;background:#F2F5F8}</style>${typoCss(ref, 'h1, h2, .hc > div:first-child, .ac > div:first-child', '.amt')}</head><body>
<main id="card" style="position: relative; width: 1080px; height: 1620px; overflow: hidden; background: #F2F5F8; color: #1B2A3A; font-family: CardSans, sans-serif; display: flex; flex-direction: column; gap: 12px">
  <header id="s-head" style="position: relative; flex: none; height: 290px">
    <div style="position: absolute; left: 56px; top: 34px; width: 500px">
      <div style="display: flex; gap: 8px">${tags}</div>
      <h1 style="margin: 14px 0 0; font-size: 40px; line-height: 52px; font-weight: 900">${title}</h1>
      <p style="margin: 12px 0 0; font-size: 19px; line-height: 29px; font-weight: 500; color: #4A5A6A">${sub}</p>
    </div>
    <div style="position: absolute; right: 0; top: 0; width: 503px; height: 290px; overflow: hidden; background: #DCE6F0">${hero_svg}
      <span style="position: absolute; left: 14px; bottom: 14px; font-size: 18px; line-height: 26px; font-weight: 700; color: #1B2A3A; background: #FFFFFF; border-radius: 13px; padding: 0 10px">${E(c.hero.caption)}</span>${draft_badge}</div>
  </header>
  <section id="s-info" class="box" style="flex: none; margin: 0 56px; display: grid; grid-template-columns: minmax(0, 0.92fr) minmax(0, 1.16fr) minmax(0, 0.92fr) minmax(0, 1fr); background: #FFFFFF; border-radius: 14px">${infobar}</section>
  <section id="s-rel" style="flex: none; margin: 0 56px"><h2 style="${h2}">法律關係圖</h2>${relation}</section>
  <section id="s-result" style="flex: none; margin: 0 56px">
    <h2 style="${h2}; display: flex; justify-content: space-between; align-items: center">判決結果${pill}</h2>
    <div style="margin-top: 6px; display: grid; grid-template-columns: minmax(0, 1fr) 170px minmax(0, 1fr) 170px minmax(0, 1.2fr); align-items: stretch">${flow}</div>
    <div style="margin-top: 8px; font-size: 18px; line-height: 27px; color: #33424F">${E(r.notes)}</div>
    <div class="pending" style="margin-top: 6px; display: flex; gap: 8px; align-items: center; background: #FBEBD3; border-radius: 10px; padding: 5px 14px; font-size: 18px; line-height: 27px; color: #6E4206">${svg('alert', 20, '#A86508')}<span><b style="color: #A86508">尚待確認｜</b>${E(r.pending)}</span></div>
  </section>
  <section id="s-facts" style="flex: none; margin: 0 56px">
    <h2 style="${h2}">事實經過<span style="font-size: 18px; font-weight: 500; color: #5B6B7B">（工作負荷重點）</span></h2>
    <div style="margin-top: 6px; display: grid; grid-template-columns: minmax(0, 1.02fr) minmax(0, 0.92fr) minmax(0, 1.16fr) minmax(0, 1fr) minmax(0, 0.9fr); gap: 10px">${tiles}</div>
  </section>
  <section id="s-basic" class="box" style="flex: none; margin: 0 56px; background: #FFFFFF; border-radius: 14px; padding: 10px 18px 12px; display: grid; grid-template-columns: minmax(0, 0.8fr) minmax(0, 1.25fr) minmax(0, 1.15fr); column-gap: 20px; row-gap: 6px; font-size: 18px; line-height: 27px">${basics}</section>
  <section id="s-hold" style="flex: none; margin: 0 56px">
    <h2 style="${h2}; display: flex; justify-content: space-between; align-items: center">法院核心見解${pill}</h2>
    <div style="margin-top: 6px; display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px">${holds}</div>
  </section>
  <section id="s-adv" class="box" style="flex: none; margin: 0 56px; background: #EEE8F6; border-radius: 14px; padding: 8px 18px 10px">
    <h2 style="${h2}; color: #4E3473; display: flex; justify-content: space-between; align-items: center">主管必看重點<span style="font-size: 18px; line-height: 26px; font-weight: 700; color: #4E3473; background: #FFFFFF; border: 1.5px solid #B9A6D6; border-radius: 13px; padding: 0 12px">顧問分析｜非法院見解</span></h2>
    <div style="margin-top: 6px; display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 16px">${advs}</div>
  </section>
  <section id="s-src" style="flex: none; margin: 0 56px; display: flex; gap: 14px; align-items: baseline; font-size: 18px; line-height: 26px">
    <span style="font-weight: 700; color: ${NAVY}">原始判決來源</span><span>${E(s.name)}</span><span style="color: #4A5A6A">${E(s.url)}｜${E(s.how)}</span>
  </section>
  <footer id="s-disc" class="disc" style="margin-top: auto; flex: none; background: #1B2A3A; padding: 13px 40px 14px; text-align: center; font-size: 18px; line-height: 26px; color: #DCE4EC">${E(c.disclaimer)}</footer>
</main></body></html>`;
}

/* template.py（standard／原版） */
function buildStandard(c, draft, ref, A) {
  const d = c.display || {};
  const E = makeE(d.keep_together || [], ew => `<span class="nb">${ew}</span>`);
  const join = parts => { let out = ''; for (const x of parts) out += (!out || x.startsWith('（')) ? x : ' ' + x; return out; };
  const party_name = p => (p.natural_person && d.mask_natural_person_name) ? maskName(p.name) : p.name;
  const sec_head = (ic, text, extra) => `<div class="sh-row"><span class="sh" data-chk="chip">${iconStd(ic, 20, 2.2)}`
    + `<span class="sh-t">${E(text)}</span></span>${extra || ''}</div>`;
  const label = kind => kind === 'court' ? '<span class="lab lab-court">法院認定</span>' : '<span class="lab lab-adv">顧問分析｜非法院見解</span>';
  const info = c.info, pl = c.parties.plaintiff, df = c.parties.defendant;
  const pl_name = party_name(pl), df_name = party_name(df);
  const tags = zip(['court', 'pulse'], c.tags).map(([i, t]) => `<span class="tag" data-chk="chip">${iconStd(i, 22, 2.2)}<span>${E(t)}</span></span>`).join('');
  const title = c.title.map(t => `<span class="tl">${E(t)}</span>`).join('');
  const sub = c.subtitle.map(t => `<span class="sl">${E(t)}</span>`).join('');
  const date_html = E(info.date) + (info.date_pending ? '<span class="pend-chip">待核</span>' : '');
  const infobar = [['court', '法院', E(info.court)], ['doc', '案號', E(info.case_no)], ['cal', '裁判日期', date_html], ['scale', '案由', E(info.cause)]]
    .map(([i, k, v]) => `<div class="ib"><div class="ib-k">${iconStd(i, 20, 2.2)}<span>${k}</span></div><div class="ib-v">${v}</div></div>`).join('');
  const basicsList = Array.isArray(c.basics) ? c.basics : Object.keys(c.basics); // Python 迭代 dict 會得到鍵
  const basics = basicsList.map(([k, v]) => `<div class="kv"><div class="k">${E(k)}</div><div class="v">${E(v)}</div></div>`).join('');
  const rel = c.relation;
  const relation = `
      <div class="rel">
        <div class="node"><div class="bub bub-g">${iconStd('person', 44, 2)}</div>
          <div class="nr">${E(pl.role)}</div><div class="nn">${E(pl_name)}</div></div>
        <div class="mid">
          <div class="arrow-lab"><b>${E(rel.claim.label)}</b><span>${E('（' + rel.claim.note + '）')}</span></div>
          <div class="arr arr-l"></div>
          <div class="arr arr-r"></div>
          <div class="arrow-lab"><b class="red">${E(rel.offset.label)}</b><b class="red">${E(rel.offset.amount != null ? rel.offset.amount : '')}</b><span>${E('（' + rel.offset.note + '）')}</span></div>
        </div>
        <div class="node"><div class="bub bub-n">${iconStd('building', 44, 2)}</div>
          <div class="nr">${E(df.role)}</div><div class="nn">${E(df_name)}</div></div>
      </div>
      `;
  const facts = c.facts.map((t, i) => `<li><span class="num">${i + 1}</span><span class="ft">${E(t && typeof t === 'object' ? t.text : t)}</span></li>`).join('');
  const r = c.result, fl = r.flow;
  let res_body;
  if (fl) {
    res_body = '<div class="ledger">'
      + `<div class="lg-row"><span class="lg-k">${E(fl.damage_label)}</span><span class="lg-v">${E(fl.damage_total)}</span></div>`
      + `<div class="lg-op"><b>${E(fl.fault_op)}</b><span>${E(join(fl.fault_lines))}</span></div>`
      + `<div class="lg-row"><span class="lg-k">${E(fl.after_label)}</span><span class="lg-v">${E(fl.after_fault)}</span></div>`
      + `<div class="lg-op"><b class="red">${E(fl.offset_op)}</b><span>${E(join(fl.offset_lines))}</span></div>`
      + '</div>' + `<p class="res-note">${E(r.notes)}</p>`;
  } else {
    res_body = '<ul class="res">' + r.lines.map(t => `<li>${E(t)}</li>`).join('') + '</ul>';
  }
  const hold_icons = ['clock', 'chat', 'shield', 'coins'];
  const show_issues = d.show_issues !== undefined ? d.show_issues : true;
  const issue_html = h => show_issues ? `<div class="hq">爭點｜${E(h.issue)}</div>` : '';
  const holds = zip(c.holdings, hold_icons).map(([h]) => `<div class="hc">${issue_html(h)}<div class="hh"><span>${E(h.head)}</span></div><div class="hb">${E(h.body)}</div></div>`).join('');
  const advs = zip(c.advisory, ['search', 'group', 'heart', 'doc']).map(([a]) => `<div class="ac"><div class="ah"><span>${E(a.head)}</span></div><div class="ab">${E(a.body)}</div></div>`).join('');
  const s = c.source_card;
  const draft_bar = draft ? '<div class="draftbadge" id="draftbadge">草稿｜法院內容尚未對照<br>原始深入分析，不得外流</div>' : '';
  const font_url = ref('NotoSansTC-VF.ttf');
  const css = A.standardCss;
  const hero_html = A.heroPhotoUrl ? `<img class="hero" src="${A.heroPhotoUrl}" alt="">` : '<div class="hero hero-ph">主視覺預留區<br>（尚無獨立素材）</div>';
  return `<!doctype html><html lang="zh-Hant-TW"><head><meta charset="utf-8">
<style>@font-face{font-family:"CardSans";src:url("${font_url}") format("truetype");font-weight:100 900;font-display:block;}</style>
<style>${css}</style>${typoCss(ref, 'h1, .sh-t, .hh, .ah', '.rt-v, .lg-v')}</head><body>
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
    <section class="box col" id="s-basic">${sec_head('person', '案件基本資料')}<div class="kvs">${basics}</div></section>
    <section class="box col" id="s-rel">${sec_head('group', '法律關係圖')}${relation}</section>
  </div>

  <div class="row rb">
    <section class="box col" id="s-facts">${sec_head('clip', '事實經過（工作負荷重點）')}
      <ol class="facts">${facts}</ol>
    </section>
    <section class="box col" id="s-result">${sec_head('gavel', '判決結果', '<div class="res-total"><span class="rt-k">被告應給付</span><span class="rt-v">' + E(r.total) + '</span></div>')}
      ${res_body}
      <div class="pending">${iconStd('alert', 22, 2.2)}<div><b>尚待確認｜</b>${E(r.pending)}</div></div>
    </section>
  </div>

  <section class="box" id="s-hold">${sec_head('scale', '法院核心見解', label('court'))}
    <div class="grid4">${holds}</div></section>

  <section class="box adv" id="s-adv">${sec_head('bulb', '主管必看重點', label('adv'))}
    <div class="grid4">${advs}</div></section>

  <section class="box src" id="s-src"><div class="src-row">${sec_head('link', '原始判決來源')}
    <div class="src-b"><b>${E(s.name)}</b><span class="url">${E(s.url)}</span><span class="sep">｜</span><span>${E(s.how)}</span></div></div>
  </section>

  <footer class="disc" id="s-disc">${E(c.disclaimer)}</footer>
</main></body></html>`;
}

/* skins.py */
const DEFAULT_SKIN = 'original';
const ROLE_SLOTS = {
  page: 'bg.center', ink: 'dk1', ink2: 'dk2', muted: 'accent3', card: 'lt1', line: 'accent4', line2: 'accent4', dark: 'dk2', on_dark: 'lt1', footer_text: 'lt1',
  plaintiff: 'accent1', defendant: 'accent2', money: 'accent1', money_text: 'lt1', money_sub: 'lt1', deduct: 'accent2', pill_text: 'accent1', pill_bg: 'lt2', pill_line: 'accent4',
  adv_bg: 'lt2', adv_line: 'accent4', adv_ink: 'dk2', adv_pill_bg: 'lt1', dot_fill: 'lt1',
};
const CONTRAST_PAIRS = [
  ['內文字 對 卡片底', 'ink', 'card', 4.5], ['標題字 對 頁面底', 'ink', 'page', 4.5],
  ['次要字 對 卡片底', 'ink2', 'card', 4.5], ['副標 對 頁面底', 'ink2', 'page', 4.5],
  ['灰標籤 對 卡片底', 'muted', 'card', 3.0], ['標題條白字 對 標題條', 'on_dark', 'dark', 4.5],
  ['頁尾字 對 頁尾', 'footer_text', 'dark', 4.5], ['原告色字 對 卡片底', 'plaintiff', 'card', 3.0],
  ['扣抵色字 對 卡片底', 'deduct', 'card', 3.0], ['判賠金額字 對 判賠色塊', 'money_text', 'money', 3.0],
  ['法院認定標籤', 'pill_text', 'pill_bg', 3.0], ['顧問區字 對 顧問區底', 'adv_ink', 'adv_bg', 4.5],
  ['圖示白字 對 原告節點', 'on_dark', 'plaintiff', 3.0], ['圖示白字 對 被告節點', 'on_dark', 'defendant', 3.0],
];
function skinRoles(skin) {
  let r;
  if ('card_roles' in skin) r = Object.assign({}, skin.card_roles);
  else { const col = Object.assign({}, skin.colors); col['bg.center'] = skin.bg.center; r = {}; for (const [role, slot] of Object.entries(ROLE_SLOTS)) { if (!(slot in col)) throw new Error('KeyError ' + slot); r[role] = col[slot]; } }
  const missing = Object.keys(ROLE_SLOTS).filter(k => !(k in r)).sort();
  if (missing.length) throw new Error(`風格 ${skin.id} 缺少顏色角色：${missing}`);
  const o = {}; for (const [k, v] of Object.entries(r)) o[k] = '#' + String(v).toUpperCase().replace(/^#+/, ''); return o;
}
function pageBackground(skin, k) {
  const bg = skin.bg || {};
  if (bg.type === 'hgrad') { const e = '#' + bg.edge, w = (bg.edge_width != null ? bg.edge_width : 0.12) * 100; return `linear-gradient(90deg, ${e} 0%, ${k.page} ${w.toFixed(1)}%, ${k.page} ${(100 - w).toFixed(1)}%, ${e} 100%)`; }
  if (bg.type === 'brushed') return `linear-gradient(180deg, #${bg.top} 0%, #${bg.bottom} 100%)`;
  return k.page;
}
function lum(h) { const c = [0, 2, 4].map(i => parseInt(h.replace(/^#+/, '').slice(i, i + 2), 16) / 255).map(x => x <= 0.03928 ? x / 12.92 : Math.pow((x + 0.055) / 1.055, 2.4)); return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]; }
function contrast(a, b) { const [hi, lo] = [lum(a), lum(b)].sort((x, y) => y - x); return (hi + 0.05) / (lo + 0.05); }
function contrastFailures(k) {
  const out = [];
  for (const [label, fg, bg, need] of CONTRAST_PAIRS) { const v = contrast(k[fg], k[bg]); if (v < need) out.push(`${label} ${k[fg]} / ${k[bg]} = ${v.toFixed(2)}（需 ≥ ${need.toFixed(1)}）`); }
  return out;
}
// Python round(x, 1)：以精確十進位值做四捨六入五成雙
function pyRound1(x) {
  const s = x * 10, fl = Math.floor(s), diff = s - fl;
  let r;
  if (Math.abs(diff - 0.5) < 1e-9) {
    // 接近 .5 時用精確字串判斷
    const exact = Number(x.toPrecision(17)); const t = exact.toFixed(20);
    r = (fl % 2 === 0) ? fl : fl + 1; // 真正的平手才會走到這裡（很少）
    void t;
  } else r = diff < 0.5 ? fl : fl + 1;
  const v = r / 10; return v === 0 && (x < 0) ? -0 : v;
}
function circle(cx, cy, rad, n, wobble) {
  n = n || 48; const pts = [];
  for (let i = 0; i < n; i++) {
    const t = 2 * Math.PI * i / n;
    const rr = rad * (1 + (wobble != null ? 0.10 * Math.sin(3 * t + wobble) + 0.06 * Math.sin(5 * t + 2 * wobble) : 0));
    pts.push([F(pyRound1(cx + rr * Math.cos(t))), F(pyRound1(cy + rr * Math.sin(t)))]);
  }
  return pts;
}
function decorations(skin) {
  const bg = skin.bg || {}, dec = skin.decor || {};
  const col = {}; for (const [kk, v] of Object.entries(skin.colors || {})) col[kk] = '#' + v;
  const out = []; const add = (poly, fill) => out.push({ poly, fill });
  if (dec.title_tag) add([[22, 88], [46, 88], [34, 104]], col.accent1);
  if ('slab' in bg) add([[1080, 1060], [1080, 1560], [1032, 1560]], '#' + bg.slab.color);
  if (dec.cover_band) add([[1032, 290], [1080, 290], [1080, 1560], [1032, 1560]], col.accent1);
  if (dec.title_bar) add([[30, 76], [40, 76], [40, 170], [30, 170]], col.accent1);
  if ('rail' in bg) { const cs = bg.rail.colors, n = cs.length; cs.forEach((c, i) => add([[0, F(1620 * i / n)], [14, F(1620 * i / n)], [14, F(1620 * (i + 1) / n)], [0, F(1620 * (i + 1) / n)]], '#' + c)); }
  if (dec.title_dot) add(circle(36, 96, 7, 24), col.accent6);
  if ('blobs' in bg) { const b = bg.blobs; add(circle(0, 0, 50, 72, b[0].phase != null ? b[0].phase : 0), '#' + b[0].color); add(circle(1080, 1540, 46, 72, b[1].phase != null ? b[1].phase : 0), '#' + b[1].color); }
  if (dec.header_band) { add([[0, 0], [14, 0], [14, 1620], [0, 1620]], col.accent2); add([[0, 0], [577, 0], [577, 14], [0, 14]], col.accent2); }
  if ('corners' in bg) { const c = '#' + bg.corners.color; add([[0, 0], [64, 0], [0, 38]], c); add([[1080, 1566], [1018, 1566], [1080, 1528]], c); }
  return out;
}
const num = v => (typeof v === 'object' ? v.f : v);
function b64utf8(s) { const bytes = new TextEncoder().encode(s); let bin = ''; for (let i = 0; i < bytes.length; i += 0x8000) bin += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000)); return btoa(bin); }
function decorationCss(shapes) {
  if (!shapes.length) return '';
  const body = shapes.map(s => `<polygon points="${s.poly.map(([x, y]) => `${pyNum(x)},${pyNum(y)}`).join(' ')}" fill="${s.fill}"/>`).join('');
  const sv = `<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1620" viewBox="0 0 1080 1620">${body}</svg>`;
  return "url('data:image/svg+xml;base64," + b64utf8(sv) + "') 0 0 / 1080px 1620px no-repeat";
}
function inside(pt, poly) {
  const [x, y] = pt; let ins = false;
  for (let i = 0; i < poly.length; i++) { const [x1, y1] = poly[i], [x2, y2] = poly[(i + 1) % poly.length]; if ((y1 > y) !== (y2 > y) && x < (x2 - x1) * (y - y1) / (y2 - y1) + x1) ins = !ins; }
  return ins;
}
function segCross(a, b, c, d) { const o = (p, q, r) => (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0]); return (o(a, b, c) * o(a, b, d) < 0) && (o(c, d, a) * o(c, d, b) < 0); }
function touches(polyRaw, rect, pad) {
  pad = pad == null ? 2 : pad; const poly = polyRaw.map(([x, y]) => [num(x), num(y)]);
  const l = rect[0] - pad, t = rect[1] - pad, r = rect[2] + pad, b = rect[3] + pad;
  const box = [[l, t], [r, t], [r, b], [l, b]];
  if (poly.some(([x, y]) => l <= x && x <= r && t <= y && y <= b) || box.some(p => inside(p, poly))) return true;
  for (let i = 0; i < poly.length; i++) for (let j = 0; j < 4; j++) if (segCross(poly[i], poly[(i + 1) % poly.length], box[j], box[(j + 1) % 4])) return true;
  return false;
}

/* render.py：內容檢查 */
const fmtInt = n => (n < 0 ? '-' : '') + Math.abs(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
function pyInt(s) { s = String(s).trim().replace(/_/g, ''); if (!/^[+-]?\d+$/.test(s)) throw new Error('ValueError'); return parseInt(s, 10); }
function fmtG(x) { let s = Number(x.toPrecision(6)).toString(); return s; }
function contentChecks(c) {
  const out = [];
  const req = ['tags', 'title', 'subtitle', 'info', 'parties', 'basics', 'relation', 'facts', 'result', 'holdings', 'advisory', 'source_card', 'disclaimer'];
  const miss = req.filter(k => !(k in c));
  out.push(['C01 必要欄位齊全', !miss.length, miss.length ? `缺：${JSON.stringify(miss)}` : '齊全']);
  for (const sc of (c.sum_checks || [])) {
    const parts = sc.parts.map(x => pyInt(x.replace(/,/g, ''))), tot = pyInt(sc.total.replace(/,/g, ''));
    const sum = parts.reduce((a, b) => a + b, 0);
    out.push(['C02 金額加總一致', sum === tot, `${sc.parts.join(' + ')} = ${fmtInt(sum)}；標示 ${sc.total}`]);
  }
  const fl = (c.result || {}).flow;
  if (fl) {
    let dmg = null, aft = null, rate = null;
    try {
      dmg = pyInt(fl.damage_total.replace(/,/g, '').replace(/ 元/g, ''));
      aft = pyInt(fl.after_fault.replace(/,/g, '').replace(/ 元/g, ''));
      const m = /(\d+(?:\.\d+)?)\s*%/.exec(fl.fault_op || '');
      rate = m ? parseFloat(m[1]) / 100 : null;
    } catch (e) { dmg = aft = rate = null; }
    if (rate === null || dmg === null) out.push(['C04 損害合計 × 過失比例 等於過失相抵後金額', false, '金額流程格式無法讀取（damage_total／after_fault／fault_op 的百分比）']);
    else out.push(['C04 損害合計 × 過失比例 等於過失相抵後金額', Math.round(dmg * rate) === aft, `${fmtInt(dmg)} × ${fmtG(rate)} = ${(dmg * rate).toLocaleString('en-US', { minimumFractionDigits: 1, maximumFractionDigits: 1 })}；標示 ${fmtInt(aft)}`]);
  }
  const n_src = (c.source_card && typeof c.source_card === 'object' && !Array.isArray(c.source_card)) ? 1 : 0;
  out.push(['C03 單一來源卡', n_src === 1, `來源卡數 ${n_src}`]);
  return out;
}

/* render.py：JS_MEASURE（原樣沿用，在小卡頁面裡執行） */
const JS_MEASURE = `(args) => {
  const {minFont, immutable} = args;
  const R = e => e.getBoundingClientRect();
  const res = {overflow:[], clipped:[], small:[], chips:[], sections:[], missing:[], outside:[], textRects:[]};
  document.querySelectorAll('.box,.row,.hc,.ac,.head-l,.finding,.pending,.disc,.draftbar').forEach(e=>{
    if (e.scrollHeight > e.clientHeight + 1 || e.scrollWidth > e.clientWidth + 1)
      res.overflow.push({cls:e.className, id:e.id, sh:e.scrollHeight, ch:e.clientHeight, sw:e.scrollWidth, cw:e.clientWidth});
  });
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
  document.querySelectorAll('.sh, .chip').forEach(ch=>{
    const kind = ch.classList.contains('sh') ? 'r9' : 'classic';
    const tx = kind === 'r9' ? ch.querySelector('.sh-t') : ch;
    const c = R(ch), sv = ch.querySelector('svg');
    const rg = document.createRange(); rg.selectNodeContents(tx); const t = rg.getBoundingClientRect();
    const ic = sv ? R(sv) : t;
    res.chips.push({kind, t:tx.textContent, padL:+(ic.left-c.left).toFixed(2), padR:+(c.right-t.right).toFixed(2),
                    padT:+(Math.min(ic.top,t.top)-c.top).toFixed(2), padB:+(c.bottom-Math.max(ic.bottom,t.bottom)).toFixed(2)});
  });
  document.querySelectorAll('#card > *').forEach(e=>{const r=R(e); res.sections.push({id:e.id||e.className, top:r.top, bottom:r.bottom, ov:e.dataset.overlap||''});});
  const txt = document.body.innerText.replace(/\\s+/g,'');
  immutable.forEach(s=>{ if (!txt.includes(s.replace(/\\s+/g,''))) res.missing.push(s); });
  res.srcCount = document.querySelectorAll('#s-src').length;
  res.lastId = [...document.querySelectorAll('#card > *')].pop().id;
  res.fontStatus = [...document.fonts].map(f=>f.family+':'+f.status);
  return res;
}`;
const MIN_FONT_PX = 18, W = 1080, H = 1620;
function layoutChecks(m, c, deco) {
  const checks = [];
  checks.push(['L01 容器無溢出', !m.overflow.length, m.overflow.length ? m.overflow : '無']);
  checks.push(['L02 文字未超出所屬框（字形裁切）', !m.clipped.length, m.clipped.length ? m.clipped : `檢查 ${m.textNodes} 個文字節點`]);
  checks.push(['L03 文字未超出畫布', !m.outside.length, m.outside.length ? m.outside : '無']);
  checks.push([`L04 最小字級 ≥ ${MIN_FONT_PX}px`, !m.small.length, m.small.length ? m.small : '全部符合']);
  const chipOk = x => x.kind === 'classic'
    ? (9 <= x.padL && x.padL <= 11 && 9 <= x.padR && x.padR <= 11 && Math.abs(x.padL - x.padR) <= 1 && x.padT >= -1 && x.padB >= -1)
    : (7 <= x.padL && x.padL <= 9 && 7 <= x.padR && x.padR <= 9 && 3 <= x.padT && x.padT <= 7 && 3 <= x.padB && x.padB <= 7);
  const bad = m.chips.filter(x => !chipOk(x));
  const kinds = [...new Set(m.chips.map(x => x.kind || 'r9'))].sort();
  checks.push(['L05 標題條貼合（r9：左右8／上下5；classic：左右10且對稱、字不出框）', !bad.length, bad.length ? bad : (m.chips.length ? `${m.chips.length} 條全數符合（${kinds.join('、')} 規格）` : '不適用（此版型無黑底標題條）')]);
  const secs = m.sections, overlap = [];
  for (let i = 0; i + 1 < secs.length; i++) { const a = secs[i], b = secs[i + 1]; if (b.top < a.bottom - 0.5 && b.ov !== 'ok') overlap.push([a.id, b.id]); }
  checks.push(['L06 區塊不重疊', !overlap.length, overlap.length ? overlap : '無']);
  checks.push(['L07 免責聲明為最後區塊且貼齊底部', m.lastId === 's-disc' && Math.abs(secs[secs.length - 1].bottom - H) < 0.5, `最後區塊 ${m.lastId}，底 ${secs[secs.length - 1].bottom}`]);
  checks.push(['L08 來源卡唯一', m.srcCount === 1, `${m.srcCount}`]);
  checks.push(['L09 不可變字串全數出現在圖面', !m.missing.length, m.missing.length ? m.missing : `${(c.immutable_checks || []).length} 項全部出現`]);
  if (deco.length) {
    const hits = [...new Set(deco.flatMap(shp => m.textRects.filter(tr => touches(shp.poly, tr.slice(0, 4))).map(tr => tr[4])))].sort();
    checks.push(['L10 裝飾不壓字', !hits.length, hits.length ? hits : `${deco.length} 個裝飾圖形，未碰到任何文字`]);
  }
  return checks;
}

/* verify_engine.py：build_card() 與 FRIENDLY */
const FRIENDLY = {
  C01: '圖卡內容缺少必要欄位', C02: '金額加總對不上', C03: '來源卡必須剛好一張',
  C04: '過失相抵計算對不上', C05: '這個風格的文字顏色太淡', L01: '某個區塊內容太多、超出框線',
  L02: '有文字超出所屬的框', L03: '文字太多，整張圖放不下', L04: '有文字小於 18px',
  L05: '黑色標題條尺寸不符', L06: '區塊互相重疊', L07: '最底下的免責說明被擠出畫面',
  L08: '來源卡必須剛好一張', L09: '案號、金額等必須出現的字沒有出現在圖上',
  L10: '風格的裝飾壓到文字', F01: '用到隨包以外的字型', F02: '字型檔沒有記錄到', P01: 'PNG 格式異常',
};
function buildCard(kase, template, skin, draft) {
  const src = kase.source;
  const card = JSON.parse(JSON.stringify(kase.card));
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(src.decision_date || '');
  if (!m) throw new Error('decision_date');
  const y = +m[1], mo = +m[2], da = +m[3]; const dt = new Date(Date.UTC(y, mo - 1, da));
  if (dt.getUTCMonth() !== mo - 1 || dt.getUTCDate() !== da) throw new Error('decision_date');
  const info = Object.assign({}, card.info || {});
  if (src.court == null || src.case_number == null) throw new Error('source');
  Object.assign(info, { court: src.court, case_no: src.case_number, date: `${y} 年 ${mo} 月 ${da} 日` });
  if (!('date_pending' in info)) info.date_pending = false;
  card.info = info; card.template = template; card.skin = skin;
  card.source = { verified_against_analysis: !draft };
  const immutable = [...(card.immutable_checks || [])];
  for (const v of [info.court, info.case_no, info.date]) if (!immutable.includes(v)) immutable.push(v);
  card.immutable_checks = immutable;
  return card;
}

/* 對應 render.py render() 的前置步驟：回傳小卡 HTML（字型路徑用 ref 決定）與檢查需要的資料 */
function prepare(kase, template, skinId, draft, skinsById, assets, ref) {
  const c = buildCard(kase, template, skinId, draft);
  c.template = template;
  c.facts = (c.facts || []).map(f => (f && typeof f === 'object') ? f : { text: f, icon: 'check' });
  const isDraft = !(c.source || {}).verified_against_analysis;
  if (template !== 'classic' && skinId !== DEFAULT_SKIN) throw new Error(`版型 ${template} 尚未支援換風格（目前只有 classic）`);
  const skin = skinsById[skinId]; if (!skin) throw new Error(`找不到風格：${skinId}`);
  c._skin_roles = skinRoles(skin);
  const deco = template === 'classic' ? decorations(skin) : [];
  const dc = decorationCss(deco), base = pageBackground(skin, c._skin_roles);
  c._page_bg = dc ? `${dc}, ${base}` : base;
  const builder = { classic: buildClassic, light: buildLight, standard: buildStandard }[template];
  if (!builder) throw new Error('template');
  const html = builder(c, isDraft, ref, assets);
  const checks = contentChecks(c);
  if (template === 'classic') {
    const bad = contrastFailures(c._skin_roles);
    checks.push(['C05 文字對比（內文 4.5、強調 3.0）', !bad.length, bad.length ? bad : `風格 ${skinId}：${CONTRAST_PAIRS.length} 組全部達標`]);
  }
  return { card: c, html, checks, deco };
}

G.CardEngine = { prepare, buildCard, layoutChecks, contentChecks, contrastFailures, decorations, decorationCss, JS_MEASURE, FRIENDLY, MIN_FONT_PX, W, H, DEFAULT_SKIN };
})(typeof window !== 'undefined' ? window : globalThis);
