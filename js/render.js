/* 在瀏覽器裡出圖：小卡 HTML → 隱藏的 1080×1620 頁框量測與檢查 → SVG foreignObject → canvas → PNG。 */
(function (G) {
'use strict';
const EN = G.CardEngine;
let FONTS = null, COVERED = null;
const dataUrlCache = new Map();

async function init(base) {
  FONTS = await (await fetch(base + 'fonts/fonts.json')).json();
  COVERED = new Set(Array.from(FONTS.covered));
}
// 原程式的字型宣告（可變字型 ttf）→ 隨包的 woff2 靜態子集（每個粗細一份，分常用字／其他兩塊）
function fontFaces(urlOf) {
  let css = '';
  for (const f of FONTS.faces) {
    const [a, b] = f.files;
    css += `@font-face{font-family:"${f.family}";src:url("${urlOf(a)}") format("woff2");font-weight:${f.weight};font-display:block;unicode-range:${FONTS.range_a};}`;
    css += `@font-face{font-family:"${f.family}";src:url("${urlOf(b)}") format("woff2");font-weight:${f.weight};font-display:block;unicode-range:${FONTS.range_b};}`;
  }
  css += `@font-face{font-family:"CardNum";src:url("${urlOf('BarlowCondensed-Bold.woff2')}") format("woff2");font-weight:100 800;font-display:block;unicode-range:U+0030-0039,U+002C,U+002E,U+0025;}`;
  css += `@font-face{font-family:"CardNum";src:url("${urlOf('BarlowCondensed-ExtraBold.woff2')}") format("woff2");font-weight:801 900;font-display:block;unicode-range:U+0030-0039,U+002C,U+002E,U+0025;}`;
  return css;
}
function swapFonts(html, urlOf, extraCss) {
  const SANS = '@font-face{font-family:"CardSans";src:url("@@NotoSansTC-VF.ttf") format("truetype");font-weight:100 900;font-display:block;}';
  const TITLE = '@font-face{font-family:"CardTitle";src:url("@@NotoSerifTC-VF.ttf") format("truetype");font-weight:100 900;font-display:block;}';
  const N1 = '@font-face{font-family:"CardNum";src:url("@@BarlowCondensed-Bold.ttf") format("truetype");font-weight:100 800;font-display:block;unicode-range:U+0030-0039,U+002C,U+002E,U+0025;}';
  const N2 = '@font-face{font-family:"CardNum";src:url("@@BarlowCondensed-ExtraBold.ttf") format("truetype");font-weight:801 900;font-display:block;unicode-range:U+0030-0039,U+002C,U+002E,U+0025;}';
  for (const s of [SANS, TITLE, N1, N2]) if (!html.includes(s)) throw new Error('字型宣告與預期不同');
  html = html.replace(SANS, fontFaces(urlOf) + (extraCss || '')).replace(TITLE, '').replace(N1, '').replace(N2, '');
  if (html.includes('@@')) throw new Error('字型路徑沒有換完');
  return html;
}
// 電腦版（Chromium、裝置像素比 1）會把 1.5px 這類小數框線畫成整數 px（1.5→1、7.5→7）。
// iPhone 螢幕像素比是 2 或 3，同樣的 1.5px 會真的變成 1.5px，整張圖往下長幾 px、底部被擠出去。
// 所以出圖前先把框線寬度換成電腦版實際畫出來的整數值，版面才會和標準答案一樣。只動框線粗細，不動任何文字。
function desktopBorders(html) {
  return html.replace(/(border(?:-(?:top|right|bottom|left))?(?:-width)?\s*:\s*)(\d+\.\d+)px/g, (m, k, v) => k + Math.floor(parseFloat(v)) + 'px');
}
function textNodes(doc) {
  const out = [], w = doc.createTreeWalker(doc.body, NodeFilter.SHOW_TEXT); let n;
  while ((n = w.nextNode())) if (n.textContent.trim()) out.push(n);
  return out;
}
// 需要的字型（字族＋粗細）與用到的字
function usage(doc) {
  const win = doc.defaultView, map = new Map();
  for (const n of textNodes(doc)) {
    const cs = win.getComputedStyle(n.parentElement);
    const fams = cs.fontFamily.split(',').map(s => s.trim().replace(/^["']|["']$/g, '')).filter(f => /^Card/.test(f));
    if (!fams.includes('CardSans')) fams.push('CardSans');
    for (const f of fams) { const k = f + '|' + cs.fontWeight; map.set(k, (map.get(k) || '') + n.textContent); }
  }
  return map;
}
function missingGlyphs(doc) {
  const miss = new Set();
  for (const n of textNodes(doc)) for (const ch of n.textContent) if (!/\s/.test(ch) && !COVERED.has(ch)) miss.add(ch);
  return [...miss];
}
function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }
function frameLoad(iframe, html) {
  return new Promise((res, rej) => { iframe.onload = () => res(); iframe.onerror = rej; iframe.srcdoc = html; });
}
async function toB64(url) {
  if (dataUrlCache.has(url)) return dataUrlCache.get(url);
  const buf = new Uint8Array(await (await fetch(url)).arrayBuffer());
  let bin = ''; for (let i = 0; i < buf.length; i += 0x8000) bin += String.fromCharCode.apply(null, buf.subarray(i, i + 0x8000));
  const v = btoa(bin); dataUrlCache.set(url, v); return v;
}
// 給維護人員看：「文字超出所屬的框」是哪幾個字、超出哪一邊幾 px（判斷規則同 JS_MEASURE 的 L02，只多記超出量，不影響檢查結果）
function clipDiag(doc) {
  const out = [], w = doc.createTreeWalker(doc.body, NodeFilter.SHOW_TEXT); let n;
  while ((n = w.nextNode())) {
    if (!n.textContent.trim()) continue;
    const host = n.parentElement.closest('.hc,.ac,.finding,.pending,.box,.disc,.draftbar,.head-l,.tag,.sh') || doc.body;
    const h = host.getBoundingClientRect(), rg = doc.createRange(); rg.selectNodeContents(n);
    for (const r of rg.getClientRects()) {
      const d = { 左: h.left - r.left, 右: r.right - h.right, 上: h.top - r.top, 下: r.bottom - h.bottom };
      const over = Object.entries(d).filter(([, v]) => v > 0.5).map(([k, v]) => `${k} ${v.toFixed(2)}px`);
      if (over.length) out.push(`「${n.textContent.trim().slice(0, 20)}」超出 ${host === doc.body ? "整張圖" : (host.id || host.className)}：${over.join('、')}`);
    }
  }
  return out;
}
// 小卡 HTML → SVG（foreignObject）圖片
async function svgImage(html, tweak) {
  const pdoc = new DOMParser().parseFromString(html, 'text/html');
  if (tweak) tweak(pdoc);
  const xhtml = new XMLSerializer().serializeToString(pdoc.documentElement);
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="${EN.W}" height="${EN.H}" viewBox="0 0 ${EN.W} ${EN.H}"><foreignObject x="0" y="0" width="${EN.W}" height="${EN.H}">${xhtml}</foreignObject></svg>`;
  // 用 data: 網址（blob: 網址的 SVG 在部分瀏覽器會讓畫布無法輸出）
  const img = new Image(); img.decoding = 'sync';
  await new Promise((res, rej) => { img.onload = res; img.onerror = () => rej(new Error('圖片轉換失敗')); img.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svg); });
  try { await img.decode(); } catch (e) { /* 部分瀏覽器不支援 */ }
  return img;
}
async function loadImage(url) {
  const img = new Image();
  await new Promise((res, rej) => { img.onload = res; img.onerror = () => rej(new Error('右上的圖讀不出來')); img.src = url; });
  try { await img.decode(); } catch (e) { /* 部分瀏覽器不支援 */ }
  return img;
}
// 照 CSS object-fit: cover（置中裁切）畫進框裡
function drawCover(ctx, { img, x, y, w, h }) {
  const iw = img.naturalWidth || img.width, ih = img.naturalHeight || img.height;
  const s = Math.max(w / iw, h / ih), sw = w / s, sh = h / s;
  ctx.drawImage(img, (iw - sw) / 2, (ih - sh) / 2, sw, sh, x, y, w, h);
}
async function sha256(blob) {
  if (!(G.crypto && crypto.subtle)) return '';
  const h = await crypto.subtle.digest('SHA-256', await blob.arrayBuffer());
  return [...new Uint8Array(h)].map(b => b.toString(16).padStart(2, '0')).join('');
}

/* 主流程。回傳 {checks, failedIds, blob(可能 null), ...} */
async function renderCard(opts) {
  const { kase, template, skin, draft, skinsById, assets, base, host } = opts;
  const prep = EN.prepare(kase, template, skin, draft, skinsById, assets, n => '@@' + n);
  prep.html = desktopBorders(prep.html);
  const checks = prep.checks.slice();
  const fontUrl = f => base + 'fonts/' + f;
  const html = swapFonts(prep.html, fontUrl, 'html{-webkit-text-size-adjust:100%;text-size-adjust:100%}');
  // 1. 放進隱藏的 1080×1620 頁框排版
  host.innerHTML = '';
  const iframe = document.createElement('iframe');
  iframe.setAttribute('aria-hidden', 'true'); iframe.tabIndex = -1;
  iframe.style.cssText = 'width:1080px;height:1620px;border:0;display:block';
  host.appendChild(iframe);
  await frameLoad(iframe, html);
  const doc = iframe.contentDocument, win = iframe.contentWindow;
  // 2. 缺字檢查：有缺字就不出圖，避免手機自己換成別的字型
  const miss = missingGlyphs(doc);
  checks.push(['G01 每個字都在隨包字型裡', !miss.length, miss.length ? miss : '全部都有']);
  if (miss.length) { host.innerHTML = ''; return { checks, missing: miss, blob: null }; }
  // 3. 等字型真的載入：document.fonts.ready＋逐一 load（只載這張圖用到的字族、粗細與字）
  await doc.fonts.ready;
  const use = usage(doc), loaded = [];
  for (const [k, text] of use) { const [fam, w] = k.split('|'); loaded.push(...await doc.fonts.load(`${w} 20px "${fam}"`, text)); }
  await doc.fonts.ready;
  const needFaces = [...new Set(loaded)];
  const allLoaded = needFaces.length > 0 && needFaces.every(f => f.status === 'loaded');
  // 4. 版面量測（原程式 JS_MEASURE 原樣執行）
  const measure = win.eval('(' + EN.JS_MEASURE + ')');
  const m = measure({ minFont: EN.MIN_FONT_PX, immutable: prep.card.immutable_checks || [] });
  checks.push(...EN.layoutChecks(m, prep.card, prep.deco));
  const diag = m.clipped.length ? clipDiag(doc) : [];
  checks.push(['F01 用到的字型都是隨包字型且已載入', allLoaded, needFaces.map(f => f.family + ' ' + f.weight + '：' + f.status)]);
  checks.push(['F02 字型檔 hash 已記錄', !!FONTS.sha256, FONTS.sha256 || '無']);
  // 5. 轉成 PNG：把用到的字型塊嵌進 SVG（圖片裡不能再去讀外部檔）
  const usedFiles = new Set();
  for (const f of needFaces) { const u = (f.__url) || ''; void u; }
  const usedChars = {}; for (const [k, t] of use) usedChars[k] = t;
  const rangeA = new Set(); // 判斷字在 a 塊或 b 塊
  for (const face of FONTS.faces) {
    for (const k of Object.keys(usedChars)) {
      const [fam, w] = k.split('|');
      if (fam === face.family && String(face.weight) === String(w)) {
        for (const ch of usedChars[k]) { if (/\s/.test(ch)) continue; usedFiles.add(FONTS.charsA.includes(ch) ? face.files[0] : face.files[1]); }
      }
    }
  }
  usedFiles.add('BarlowCondensed-Bold.woff2'); usedFiles.add('BarlowCondensed-ExtraBold.woff2');
  const b64 = {}; for (const f of usedFiles) b64[f] = await toB64(fontUrl(f));
  let svgHtml = swapFonts(prep.html, f => b64[f] ? 'data:font/woff2;base64,' + b64[f] : 'data:font/woff2;base64,', '');
  // 右上角的圖（原版的照片／插畫、各版型的每案情境圖）不嵌進 SVG：Safari 存圖時不畫 SVG 裡用 <img> 放進來的圖。
  // 改成版面上留同大小的空位，整張畫完後再把圖直接畫到畫布的那一格；原本壓在圖上的東西（草稿標記、「示意圖」標籤）最後再單獨疊一次。
  let hero = null, topImg = null;
  if (assets.heroImageUrl) {                       // 新第一版、淺色版：空位 #hero-slot 填滿右上那一格
    const slot = doc.getElementById('hero-slot');
    if (!slot) throw new Error('找不到右上的圖的位置');
    const rc = slot.getBoundingClientRect();
    hero = { img: await loadImage(assets.heroImageUrl), x: rc.left, y: rc.top, w: rc.width, h: rc.height };
  } else if (assets.heroPhotoUrl && !assets.heroPhotoUrl.startsWith('data:')) {   // 原版：img.hero
    const tag = `<img class="hero" src="${assets.heroPhotoUrl}" alt="">`;
    if (!svgHtml.includes(tag)) throw new Error('找不到右上的圖的位置');
    const rc = doc.querySelector('img.hero').getBoundingClientRect();
    hero = { img: await loadImage(assets.heroPhotoUrl), x: rc.left, y: rc.top, w: rc.width, h: rc.height };
    svgHtml = svgHtml.split(tag).join('<div class="hero"></div>');
  }
  if (hero) {
    // 那一格裡原本壓在圖上面的東西（新第一版往上疊的資訊列、「示意圖」標籤、草稿標記……）都要回到圖上面：
    // 把整張小卡再畫一層，只拿掉「圖下面」的東西（頁面、頁首、圖框的底色與空位），畫的時候限制在那一格裡。
    const clear = '<style>html,body,#card,header,.head{background:transparent!important;box-shadow:none!important}</style>';
    topImg = await svgImage(svgHtml.replace('</head>', clear + '</head>'), d => {
      const slot = d.getElementById('hero-slot');
      if (slot) { slot.parentElement.style.background = 'transparent'; slot.remove(); }
    });
  }
  const img = await svgImage(svgHtml);
  const cv = document.createElement('canvas'); cv.width = EN.W; cv.height = EN.H;
  const ctx = cv.getContext('2d', { willReadFrequently: true });
  // Safari 第一次畫可能字型還沒套上：重畫到連續兩次結果一樣為止
  let prev = null;
  for (let i = 0; i < 8; i++) {
    ctx.clearRect(0, 0, EN.W, EN.H); ctx.drawImage(img, 0, 0, EN.W, EN.H);
    if (hero) drawCover(ctx, hero);
    if (topImg) { ctx.save(); ctx.beginPath(); ctx.rect(hero.x, hero.y, hero.w, hero.h); ctx.clip(); ctx.drawImage(topImg, 0, 0, EN.W, EN.H); ctx.restore(); }
    const d = ctx.getImageData(0, 0, EN.W, EN.H).data;
    let h = 0; for (let j = 0; j < d.length; j += 397) h = (h * 31 + d[j]) | 0;
    if (prev !== null && h === prev && i >= 2) break;
    prev = h; await sleep(120);
  }
  const blob = await new Promise(r => cv.toBlob(r, 'image/png'));
  let ok = false, dims = '';
  if (blob) { const bm = await createImageBitmap(blob); ok = bm.width === EN.W && bm.height === EN.H; dims = `${bm.width}×${bm.height}`; bm.close && bm.close(); }
  checks.push(['P01 PNG 1080×1620', ok, dims || '沒有產生']);
  host.innerHTML = '';
  return { checks, blob, sha256: blob ? await sha256(blob) : '', measure: m, diag };
}

function friendly(checks, missing) {
  const problems = [];
  for (const [id, pass] of checks) {
    if (pass) continue;
    let t;
    if (id.startsWith('G01')) t = '這幾個字字型裡沒有：' + (missing || []).join('');
    else t = EN.FRIENDLY[id.slice(0, 3)] || '其他檢查沒過';
    if (!problems.includes(t)) problems.push(t);
  }
  return problems;
}
G.CardRender = { init, renderCard, friendly, swapFonts, desktopBorders };
})(window);
