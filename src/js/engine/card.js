// 案例 → 圖卡 HTML。組卡照 verify_engine.py 的 build_card()，風格與裝飾準備照 casecard/engine/render.py。
import * as skins from "./skins.js";
import * as classic from "./template_classic.js";
import * as light from "./template_light.js";
import * as standard from "./template_standard.js";

export const TEMPLATES = { classic, light, standard };
export const W = 1080, H = 1620;

function parseIsoDate(s) {
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(s));
  const day = m && new Date(Date.UTC(+m[1], +m[2] - 1, +m[3]));
  if (!m || day.getUTCFullYear() !== +m[1] || day.getUTCMonth() !== +m[2] - 1 || day.getUTCDate() !== +m[3]) {
    throw new Error(`判決日期格式不對：${s}`);
  }
  return { year: +m[1], month: +m[2], day: +m[3] };
}

// 把案例檔組成出圖要的 card。法院、案號、日期一律從 source 帶入。
export function buildCard(caseObj, template, skin, draft) {
  const src = caseObj.source;
  const card = structuredClone(caseObj.card);
  const day = parseIsoDate(src.decision_date);
  const info = { ...(card.info || {}) };
  Object.assign(info, { court: src.court, case_no: src.case_number, date: `${day.year} 年 ${day.month} 月 ${day.day} 日` });
  if (!("date_pending" in info)) info.date_pending = false;
  card.info = info;
  card.template = template;
  card.skin = skin;
  card.source = { verified_against_analysis: !draft };
  const immutable = [...(card.immutable_checks || [])];
  for (const v of [info.court, info.case_no, info.date]) if (!immutable.includes(v)) immutable.push(v);
  card.immutable_checks = immutable;
  return card;
}

// render.py 出圖前的準備：事實統一成 {text, icon}、風格角色、裝飾、頁面背景
export function prepare(card, skinFiles) {
  const c = card;
  c.facts = (c.facts || []).map((f) => (typeof f === "object" && f !== null ? f : { text: f, icon: "check" }));
  const tmpl = c.template || "standard";
  if (!(tmpl in TEMPLATES)) throw new Error(`沒有這個版型：${tmpl}`);
  const skinId = c.skin || skins.DEFAULT_SKIN;
  if (tmpl !== "classic" && skinId !== skins.DEFAULT_SKIN) throw new Error(`版型 ${tmpl} 尚未支援換風格（目前只有 classic）`);
  const skin = skinFiles[skinId];
  if (!skin) throw new Error(`找不到風格：${skinId}`);
  c._skin_roles = skins.roles(skin);
  const deco = tmpl === "classic" ? skins.decorations(skin) : [];
  const decoCss = skins.decorationCss(deco);
  const baseBg = skins.pageBackground(skin, c._skin_roles);
  c._page_bg = decoCss ? `${decoCss}, ${baseBg}` : baseBg;
  return { template: tmpl, skinId, deco: deco.map((s) => ({ poly: skins.plainPoly(s.poly), fill: s.fill })) };
}

// assets = { fonts, skins: {id: skinJson}, heroSvg, heroUrl, standardCss }
export function cardHtml(caseObj, template, skinId, draft, assets) {
  const card = buildCard(caseObj, template, skinId, draft);
  const meta = prepare(card, assets.skins);
  const html = TEMPLATES[meta.template].buildHtml(card, assets, draft);
  return { html, card, ...meta };
}
