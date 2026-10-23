// 風格（皮）→ 圖卡顏色角色、頁面背景、留白處裝飾、文字對比檢查。照 casecard/engine/skins.py。
import { pyFloat, pyRound1 } from "./common.js";

export const DEFAULT_SKIN = "original";

export const ROLE_SLOTS = {
  "page": "bg.center", "ink": "dk1", "ink2": "dk2", "muted": "accent3", "card": "lt1",
  "line": "accent4", "line2": "accent4", "dark": "dk2", "on_dark": "lt1", "footer_text": "lt1",
  "plaintiff": "accent1", "defendant": "accent2", "money": "accent1", "money_text": "lt1", "money_sub": "lt1",
  "deduct": "accent2", "pill_text": "accent1", "pill_bg": "lt2", "pill_line": "accent4",
  "adv_bg": "lt2", "adv_line": "accent4", "adv_ink": "dk2", "adv_pill_bg": "lt1", "dot_fill": "lt1",
};

export const CONTRAST_PAIRS = [
  ["內文字 對 卡片底", "ink", "card", 4.5], ["標題字 對 頁面底", "ink", "page", 4.5],
  ["次要字 對 卡片底", "ink2", "card", 4.5], ["副標 對 頁面底", "ink2", "page", 4.5],
  ["灰標籤 對 卡片底", "muted", "card", 3.0], ["標題條白字 對 標題條", "on_dark", "dark", 4.5],
  ["頁尾字 對 頁尾", "footer_text", "dark", 4.5], ["原告色字 對 卡片底", "plaintiff", "card", 3.0],
  ["扣抵色字 對 卡片底", "deduct", "card", 3.0], ["判賠金額字 對 判賠色塊", "money_text", "money", 3.0],
  ["法院認定標籤", "pill_text", "pill_bg", 3.0], ["顧問區字 對 顧問區底", "adv_ink", "adv_bg", 4.5],
  ["圖示白字 對 原告節點", "on_dark", "plaintiff", 3.0], ["圖示白字 對 被告節點", "on_dark", "defendant", 3.0],
];

// list_skins()：original 排第一，其餘照 id 排序
export function sortSkins(skins) {
  return skins.map((s) => ({ id: s.id, name: s.name }))
    .sort((a, b) => (a.id !== DEFAULT_SKIN) - (b.id !== DEFAULT_SKIN) || (a.id < b.id ? -1 : a.id > b.id ? 1 : 0));
}

export function roles(skin) {
  let r;
  if ("card_roles" in skin) {
    r = { ...skin.card_roles };
  } else {
    const col = { ...skin.colors, "bg.center": skin.bg.center };
    r = {};
    for (const [role, slot] of Object.entries(ROLE_SLOTS)) {
      if (!(slot in col)) throw new Error(`風格 ${skin.id} 缺少顏色：${slot}`);
      r[role] = col[slot];
    }
  }
  const missing = Object.keys(ROLE_SLOTS).filter((k) => !(k in r)).sort();
  if (missing.length) throw new Error(`風格 ${skin.id} 缺少顏色角色：${missing.join("、")}`);
  const out = {};
  for (const [k, v] of Object.entries(r)) out[k] = "#" + v.toUpperCase().replace(/^#+/, "");
  return out;
}

export function pageBackground(skin, k) {
  const bg = skin.bg || {};
  if (bg.type === "hgrad") {
    const e = "#" + bg.edge, w = (bg.edge_width ?? 0.12) * 100;
    return `linear-gradient(90deg, ${e} 0%, ${k.page} ${w.toFixed(1)}%, ${k.page} ${(100 - w).toFixed(1)}%, ${e} 100%)`;
  }
  if (bg.type === "brushed") return `linear-gradient(180deg, #${bg.top} 0%, #${bg.bottom} 100%)`;
  return k.page;
}

function lum(h) {
  const c = [0, 2, 4].map((i) => parseInt(h.replace(/^#+/, "").slice(i, i + 2), 16) / 255)
    .map((x) => (x <= 0.03928 ? x / 12.92 : ((x + 0.055) / 1.055) ** 2.4));
  return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
}

export function contrast(a, b) {
  const [hi, lo] = [lum(a), lum(b)].sort((x, y) => y - x);
  return (hi + 0.05) / (lo + 0.05);
}

export function contrastFailures(k) {
  const out = [];
  for (const [label, fg, bg, need] of CONTRAST_PAIRS) {
    const v = contrast(k[fg], k[bg]);
    if (v < need) out.push(`${label} ${k[fg]} / ${k[bg]} = ${v.toFixed(2)}（需 ≥ ${need.toFixed(1)}）`);
  }
  return out;
}

// ───────── 裝飾（只畫在留白處）─────────
// 座標以 [x, y] 存；x、y 若在 Python 是 float，用 {v, f:true} 標記，印出時照 Python 寫法（例 324.0）
const fl = (v) => ({ v, f: true });
const num = (p) => (typeof p === "object" ? pyFloat(p.v) : String(p));
const val = (p) => (typeof p === "object" ? p.v : p);

function circle(cx, cy, r, n = 48, wobble = null) {
  const pts = [];
  for (let i = 0; i < n; i++) {
    const t = 2 * Math.PI * i / n;
    const rr = r * (1 + (wobble !== null ? 0.10 * Math.sin(3 * t + wobble) + 0.06 * Math.sin(5 * t + 2 * wobble) : 0));
    pts.push([fl(pyRound1(cx + rr * Math.cos(t))), fl(pyRound1(cy + rr * Math.sin(t)))]);
  }
  return pts;
}

export function decorations(skin) {
  const bg = skin.bg || {}, dec = skin.decor || {};
  const col = {};
  for (const [kk, v] of Object.entries(skin.colors || {})) col[kk] = "#" + v;
  const out = [];
  const add = (poly, fill) => out.push({ poly, fill });
  if (dec.title_tag) add([[22, 88], [46, 88], [34, 104]], col.accent1);
  if ("slab" in bg) add([[1080, 1060], [1080, 1560], [1032, 1560]], "#" + bg.slab.color);
  if (dec.cover_band) add([[1032, 290], [1080, 290], [1080, 1560], [1032, 1560]], col.accent1);
  if (dec.title_bar) add([[30, 76], [40, 76], [40, 170], [30, 170]], col.accent1);
  if ("rail" in bg) {
    const cs = bg.rail.colors, n = cs.length;
    cs.forEach((c, i) => add([[0, fl(1620 * i / n)], [14, fl(1620 * i / n)], [14, fl(1620 * (i + 1) / n)], [0, fl(1620 * (i + 1) / n)]], "#" + c));
  }
  if (dec.title_dot) add(circle(36, 96, 7, 24), col.accent6);
  if ("blobs" in bg) {
    const b = bg.blobs;
    add(circle(0, 0, 50, 72, b[0].phase ?? 0), "#" + b[0].color);
    add(circle(1080, 1540, 46, 72, b[1].phase ?? 0), "#" + b[1].color);
  }
  if (dec.header_band) {
    add([[0, 0], [14, 0], [14, 1620], [0, 1620]], col.accent2);
    add([[0, 0], [577, 0], [577, 14], [0, 14]], col.accent2);
  }
  if ("corners" in bg) {
    const c = "#" + bg.corners.color;
    add([[0, 0], [64, 0], [0, 38]], c);
    add([[1080, 1566], [1018, 1566], [1080, 1528]], c);
  }
  return out;
}

function b64(s) {
  const bytes = new TextEncoder().encode(s);
  let bin = "";
  for (const b of bytes) bin += String.fromCharCode(b);
  return btoa(bin);
}

export function decorationCss(shapes) {
  if (!shapes.length) return "";
  const body = shapes.map((s) => `<polygon points="${s.poly.map(([x, y]) => `${num(x)},${num(y)}`).join(" ")}" fill="${s.fill}"/>`).join("");
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="1620" viewBox="0 0 1080 1620">${body}</svg>`;
  return "url('data:image/svg+xml;base64," + b64(svg) + "') 0 0 / 1080px 1620px no-repeat";
}

// 裝飾多邊形換成純數字座標（給 L10 檢查用）
export const plainPoly = (poly) => poly.map(([x, y]) => [val(x), val(y)]);

function inside([x, y], poly) {
  let ins = false;
  for (let i = 0; i < poly.length; i++) {
    const [x1, y1] = poly[i], [x2, y2] = poly[(i + 1) % poly.length];
    if ((y1 > y) !== (y2 > y) && x < (x2 - x1) * (y - y1) / (y2 - y1) + x1) ins = !ins;
  }
  return ins;
}

function segCross(a, b, c, d) {
  const o = (p, q, r) => (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0]);
  return (o(a, b, c) * o(a, b, d) < 0) && (o(c, d, a) * o(c, d, b) < 0);
}

// 多邊形是否碰到文字框（外擴 pad px 當安全距離）
export function touches(poly, rect, pad = 2) {
  const l = rect[0] - pad, t = rect[1] - pad, r = rect[2] + pad, b = rect[3] + pad;
  const box = [[l, t], [r, t], [r, b], [l, b]];
  if (poly.some(([x, y]) => l <= x && x <= r && t <= y && y <= b) || box.some((p) => inside(p, poly))) return true;
  const edges = poly.map((p, i) => [p, poly[(i + 1) % poly.length]]);
  const bedges = box.map((p, i) => [p, box[(i + 1) % box.length]]);
  return edges.some(([a, b2]) => bedges.some(([c, d]) => segCross(a, b2, c, d)));
}
