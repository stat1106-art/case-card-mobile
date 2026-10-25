/* 職災小卡 手機版：畫面流程沿用 v0.1 電腦版，只把出圖改成在瀏覽器裡做。 */
(function () {
'use strict';
const APP_VERSION = '0.4.0';
const BUILD = '83e866a029';
// 壞檔在清單上的標示（驗收第 10 條的用字）；要換字只改這裡
const BROKEN_LABEL = '這個案例讀不出來';
const DISCLAIMER = '案例內容由 AI 整理，正式使用前請自己對照判決核對。';
const TEMPLATES = [['classic', '新第一版'], ['light', '淺色資訊圖'], ['standard', '原版']];
const SKIN_FILES = ['original', 'style1', 'style1_print', 'style2', 'style3', 'style4', 'style5', 'style6', 'style7'];
const MSG = {
  start: '請先在上面選案例，再按「產生小卡」。',
  loaded: '案例清單已讀取。',
  none: 'cases 資料夾裡沒有可以用的案例。',
  pick: '請先選一個案例。',
  busy: '產生中，請稍候……',
  badFile: BROKEN_LABEL + '，請換一個案例或檢查檔案內容。',
  cannot: '這個案例產生不出小卡，請檢查案例內容是否完整（法院、案號、判決日期、圖卡內容）。',
  badTpl: '版型不正確，請重新選擇。',
  badSkin: '風格不正確，請重新選擇。',
  oops: '發生問題，請再試一次。',
  listFail: '案例清單讀不出來，請按「重新讀取」再試一次。',
  pasteEmpty: '請先把 GPT 的回覆貼進上面的框。',
  pasteBad: '這段回覆裡沒有小卡資料，請確認 GPT 的圖卡門檻是『可供圖卡使用』',
  pasteIncomplete: '段小卡資料缺少判決來源或圖卡內容，沒有加入',
  localNone: '這支手機目前沒有自己加入的案例。',
  pasteOk: '已加入：',
  pasteMemOnly: '這台手機存不住，關掉就不見',
  pasteDeleted: '已刪除：',
};
const PASTE_KEY = 'pastedCases';
const PASTE_TAG = '（僅本機）';
// 找不到圖時的預設圖：原版用 r9 照片（打包時一定會放、已裁好），新第一版與淺色用 SVG 插畫
const DEFAULT_PHOTO = 'hero_library/overwork_night_desk_photo.card.jpg';
const DEFAULT_SVG = 'hero_library/overwork_night_desk.svg';
// 事故類型圖庫（案例 card.hero.hero_type）；沒有對應的類型圖時用 overwork，並在畫面註明
const HERO_TYPES = ['overwork', 'fall', 'machine', 'traffic', 'chemical', 'electric', 'collapse', 'commute',
  'construction', 'heat', 'disease', 'healthcare', 'stress', 'neutral'];
const HERO_FALLBACK_TYPE = 'overwork';
const HERO_NOT_SET = '示意圖尚未配置';
// 新第一版、淺色版放情境圖時，SVG 插畫的位置換成這個空位（填滿右上那一格），存圖時再把圖疊上去
const HERO_SLOT = '<div id="hero-slot" style="position: absolute; left: 0; top: 0; width: 100%; height: 100%"></div>';
// 新第一版放示意圖時，右上那一格改成內縮的圓角小卡（寬 400×高 231，和原本 503×290 同比例）：
// 右緣對齊下面各區塊（距右 56px）、下緣停在資訊列上方，圖不再被資訊列蓋住；其他區塊位置不變。
const HERO_INSET_CLASSIC = { from: 'right: 0; top: 0; width: 503px; height: 290px; overflow: hidden; background: #DCE6F0',
  to: 'right: 56px; top: 18px; width: 400px; height: 231px; overflow: hidden; background: #DCE6F0; border-radius: 14px' };
const $ = id => document.getElementById(id);
const BASE = new URL('./', location.href).href;   // 相對路徑：放在 GitHub Pages 子目錄也能用
let SKINS = {}, CASES = [], current = null;       // current = {blob, url, name}
let PASTED = [], pasteMemOnly = false;            // 管理頁貼上的案例（僅本機） [{id, data}]
let adminSeen = false;                            // 這次打開 App 有沒有進過管理頁（進過才顯示給維護人員看的詳細資料）

async function getJSON(path) {
  const r = await fetch(BASE + path, { cache: 'no-cache' });
  if (!r.ok) throw new Error(r.status);
  return r.json();
}
async function getText(path) {
  const r = await fetch(BASE + path);
  if (!r.ok) throw new Error(r.status);
  return r.text();
}
// 從貼上的 GPT 回覆找出所有小卡資料（format 為 case-card-app-case 的物件）：
// 從每個「{」開始，照括號深度找到對應的「}」（字串裡的括號不算），能解析就收下並跳到它後面；
// 收下的東西如果是外層包裝（例如一次好幾案），往裡面找 format 對的物件。前後說明文字、圍欄、「情境圖：」那一行都會被略過。
function extractCases(text) {
  const s = String(text || ''), found = [];
  const walk = v => {
    if (Array.isArray(v)) { v.forEach(walk); return; }
    if (!v || typeof v !== 'object') return;
    if (v.format === 'case-card-app-case') { found.push(v); return; }
    Object.values(v).forEach(walk);
  };
  let i = s.indexOf('{');
  while (i !== -1) {
    let depth = 0, inStr = false, bs = false, end = -1;
    for (let j = i; j < s.length; j++) {
      const ch = s[j];
      if (inStr) { if (bs) bs = false; else if (ch === '\\') bs = true; else if (ch === '"') inStr = false; continue; }
      if (ch === '"') inStr = true;
      else if (ch === '{') depth++;
      else if (ch === '}' && --depth === 0) { end = j; break; }
    }
    let parsed = null;
    if (end !== -1) { try { parsed = JSON.parse(s.slice(i, end + 1)); } catch (e) { /* 換下一個「{」 */ } }
    if (parsed !== null) { walk(parsed); i = s.indexOf('{', end + 1); } else i = s.indexOf('{', i + 1);
  }
  return found;
}
function okCase(d) { return d && typeof d === 'object' && !Array.isArray(d) && d.card && typeof d.card === 'object' && !Array.isArray(d.card) && d.source && typeof d.source === 'object' && !Array.isArray(d.source); }
// 圖檔名只取檔名本身（貼上的資料可能寫了路徑或奇怪字元）
function safeName(n) { return encodeURIComponent(String(n).split(/[\\/]/).pop()); }
// 依序試，回傳第一個抓得到的路徑；都抓不到就回傳最後一個（預設圖）；strict 時都抓不到回傳空字串
async function firstOk(paths, strict) {
  const list = paths.filter(Boolean);
  for (const p of list) {
    try { const r = await fetch(BASE + p); if (r.ok) return p; } catch (e) { /* 沒網路又不在快取裡 */ }
  }
  return strict ? '' : list[list.length - 1] || '';
}
function stem(f) { return f.replace(/\.json$/i, ''); }

async function loadSkins() {
  const list = await Promise.all(SKIN_FILES.map(id => getJSON('skins/skin_' + id + '.json')));
  SKINS = {}; list.forEach(s => { SKINS[s.id] = s; });
  const ids = Object.keys(SKINS).sort((a, b) => (a !== 'original') - (b !== 'original') || (a < b ? -1 : a > b ? 1 : 0));
  return ids.map(id => ({ id, name: SKINS[id].name || id }));
}
async function loadCases() {
  const idx = await getJSON('cases/index.json');
  const files = (idx && Array.isArray(idx.cases)) ? idx.cases.filter(f => typeof f === 'string') : [];
  return Promise.all(files.slice().sort().map(async file => {
    try {
      const data = await getJSON('cases/' + encodeURIComponent(file));
      if (!okCase(data)) throw new Error('bad');
      return { file, title: data.title || stem(file), ok: true, data };
    } catch (e) { return { file, title: file, ok: false, note: BROKEN_LABEL }; }
  }));
}
// ── 貼上的案例：存在這台手機的瀏覽器（localStorage），讀寫失敗就只放在記憶體 ──
function readPasted() {
  try {
    const v = JSON.parse(localStorage.getItem(PASTE_KEY) || '[]');
    return Array.isArray(v) ? v.filter(x => x && typeof x.id === 'string' && x.data && typeof x.data === 'object') : [];
  } catch (e) { pasteMemOnly = true; return []; }
}
function writePasted() {
  try { localStorage.setItem(PASTE_KEY, JSON.stringify(PASTED)); pasteMemOnly = false; return true; }
  catch (e) { pasteMemOnly = true; return false; }
}
function pasteTitle(d) { return String(d.title || (d.source && d.source.case_number) || '貼上的案例'); }
function addPasted() {
  const text = $('paste').value;
  if (!text.trim()) { $('pastemsg').textContent = MSG.pasteEmpty; return; }
  const found = extractCases(text);
  if (!found.length) { $('pastemsg').textContent = MSG.pasteBad; return; }
  const good = found.filter(okCase), bad = found.length - good.length;
  if (!good.length) { $('pastemsg').textContent = `${bad} ${MSG.pasteIncomplete}`; return; }
  let last = '';
  good.forEach((d, k) => { last = 'local_' + Date.now().toString(36) + '_' + k; PASTED.push({ id: last, data: d }); });
  const saved = writePasted();
  $('paste').value = '';
  $('pastemsg').textContent = `${MSG.pasteOk}${good.length} 案：${good.map(pasteTitle).join('、')}`
    + (bad ? `。另有 ${bad} ${MSG.pasteIncomplete}` : '') + (saved ? '' : '。' + MSG.pasteMemOnly);
  renderList(last); renderLocal();
}
function deletePasted(id) {
  const item = PASTED.find(x => x.id === id);
  PASTED = PASTED.filter(x => x.id !== id);
  const saved = writePasted();
  $('pastemsg').textContent = (item ? MSG.pasteDeleted + pasteTitle(item.data) : '') + (saved ? '' : '。' + MSG.pasteMemOnly);
  renderList(); renderLocal();
}
// 管理頁：這支手機加入的案例＋刪除
function renderLocal() {
  $('localcases').innerHTML = '';
  if (!PASTED.length) { const p = document.createElement('p'); p.className = 'note'; p.textContent = MSG.localNone; $('localcases').append(p); return; }
  PASTED.forEach(x => {
    const row = document.createElement('div'); row.className = 'caserow';
    const t = document.createElement('span'); t.className = 'case'; t.textContent = pasteTitle(x.data) + PASTE_TAG;
    const del = document.createElement('button'); del.type = 'button'; del.textContent = '刪除';
    del.setAttribute('aria-label', '刪除 ' + pasteTitle(x.data)); del.onclick = () => deletePasted(x.id);
    row.append(t, del); $('localcases').append(row);
  });
}
function showAdmin(on) {
  if (on) { adminSeen = true; renderLocal(); }
  $('userview').hidden = on; $('adminview').hidden = !on; $('adminlink').hidden = on;
  window.scrollTo(0, 0);
}
function allCases() {
  return CASES.concat(PASTED.map(x => ({ file: x.id, title: pasteTitle(x.data), ok: true, data: x.data, pasted: true })));
}
function renderList(select) {
  const keep = select || (document.querySelector('input[name=c]:checked') || {}).value;
  $('cases').innerHTML = '';
  allCases().forEach(c => {
    const l = document.createElement('label'); l.className = 'case' + (c.ok ? '' : ' bad');
    if (c.ok) { const r = document.createElement('input'); r.type = 'radio'; r.name = 'c'; r.value = c.file; l.append(r); }
    l.append(c.ok ? c.title + (c.pasted ? PASTE_TAG : '') : `${c.file}（${c.note}）`);
    $('cases').append(l);
  });
  const r = [...document.querySelectorAll('input[name=c]')];
  (r.find(x => x.value === keep) || r[0] || {}).checked = true;
  return r.length;
}
// 平台入口只可選取清單中已讀取成功的網站案例，不拿網址片段組檔案路徑。
function caseFromHash(hash) {
  const match = /^#case=(.+)$/.exec(hash);
  let want = '';
  try { want = match ? decodeURIComponent(match[1]) : ''; } catch (e) { return ''; }
  return (CASES.find(c => c.ok === true && c.file === want) || {}).file || '';
}
async function load(fromNavigation) {
  const keep = (document.querySelector('input[name=c]:checked') || {}).value;
  try {
    if (!$('tpl').options.length) {
      TEMPLATES.forEach(([id, n]) => $('tpl').add(new Option(n, id)));
      (await loadSkins()).forEach(s => $('skin').add(new Option(s.name, s.id)));
    }
    CASES = await loadCases();
  } catch (e) { CASES = []; $('msg').textContent = MSG.listFail; renderList(keep); return; }
  const n = renderList((fromNavigation === true && caseFromHash(location.hash)) || keep);
  $('disc').textContent = DISCLAIMER; tplChange();
  $('msg').textContent = n ? MSG.loaded : MSG.none;
}
function tplChange() {
  const c = $('tpl').value === 'classic'; $('skin').disabled = !c;
  if (!c) $('skin').value = 'original';
  $('skinnote').textContent = c ? '' : '只有新第一版可以換風格';
}
function clearResult() {
  $('result').innerHTML = ''; $('picwrap').hidden = true;
  if (current) { URL.revokeObjectURL(current.url); current = null; }
  $('pic').removeAttribute('src');
}
function esc(s) { return String(s).replace(/[&<>"]/g, ch => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[ch])); }

async function generate() {
  const sel = document.querySelector('input[name=c]:checked');
  if (!sel) { $('msg').textContent = MSG.pick; return; }
  const template = $('tpl').value; let skin = $('skin').value; const draft = $('draft').checked;
  if (!TEMPLATES.some(t => t[0] === template)) { $('msg').textContent = MSG.badTpl; return; }
  if (template !== 'classic') skin = 'original';
  if (!SKINS[skin]) { $('msg').textContent = MSG.badSkin; return; }
  const c = allCases().find(x => x.file === sel.value);
  if (!c || !c.ok) { $('msg').textContent = MSG.badFile; return; }
  $('msg').textContent = MSG.busy; clearResult(); $('go').disabled = true;
  let heroNote = '';
  try {
    let res;
    try {
      const hero = (c.data.card && c.data.card.hero) || {};
      const assets = { standardCss: await getText('design/standard.css') };
      // 右上角的圖（三個版型都一樣）：該案專屬圖 → 事故類型圖 → overwork 類型圖 → 預設圖（原版 r9 照片、新第一版與淺色 SVG 插畫）。
      // 圖打包時已裁好、存成「主檔名.card.jpg」（build.py 的 card_name）。缺圖不能讓小卡出不來。
      // 順序：該案專屬圖（hero.image）→ 事故類型圖（hero.hero_type）→ overwork 類型圖（註明「示意圖尚未配置」）→ 舊的預設圖（同上註明）
      const own = hero.image ? await firstOk(['hero_library/' + safeName(hero.image).replace(/\.[^.]+$/, '') + '.card.jpg'], true) : '';
      const type = HERO_TYPES.includes(hero.hero_type) ? hero.hero_type : '';
      const typed = !own && type ? await firstOk(['hero_library/type_' + type + '.card.jpg'], true) : '';
      const fallback = !own && !typed ? await firstOk(['hero_library/type_' + HERO_FALLBACK_TYPE + '.card.jpg'], true) : '';
      const image = own || typed || fallback;
      heroNote = own || typed ? '' : HERO_NOT_SET;
      if (template === 'standard') {
        assets.heroPhotoUrl = BASE + (image || DEFAULT_PHOTO);
      } else if (image) {
        assets.heroSvg = HERO_SLOT; assets.heroImageUrl = BASE + image;
        if (template === 'classic') assets.heroInset = HERO_INSET_CLASSIC;   // 新第一版：圖縮小內縮，不被資訊列蓋住
      }
      else {
        const svg = await firstOk([hero.file && /\.svg$/i.test(hero.file) && 'hero_library/' + safeName(hero.file), DEFAULT_SVG]);
        assets.heroSvg = await getText(svg);
      }
      res = await CardRender.renderCard({ kase: c.data, template, skin, draft, skinsById: SKINS, assets, base: BASE, host: $('stage') });
    } catch (e) { console.error(e); $('msg').textContent = MSG.cannot; return; }
    $('msg').textContent = '';
    const failed = res.checks.filter(x => !x[1]);
    const problems = CardRender.friendly(res.checks, res.missing);
    if (failed.length) {
      $('result').innerHTML = `<div class="warn"><b>檢查沒過（${failed.length} 項），請修改案例內容：</b><ul>${problems.map(f => '<li>' + esc(f) + '</li>').join('')}</ul>` +
        (res.blob ? '下面的圖照原樣產生，讓你看哪裡超出；文字沒有被縮小或刪減。' : '') +
        (adminSeen ? `<details class="diag"><summary>給維護人員看的詳細資料</summary><pre>${esc([navigator.userAgent, ...(res.diag || []), ...failed.map(x => x[0] + '：' + JSON.stringify(x[2]))].join('\n'))}</pre></details>` : '') + '</div>';
    } else {
      $('result').innerHTML = `<div class="okmsg">檢查全部通過（${res.checks.length} 項）</div>`;
    }
    if (heroNote) $('result').insertAdjacentHTML('beforeend', `<p class="note heronote">右上角：${esc(heroNote)}</p>`);
    if (res.blob) {
      const name = `${stem(c.file)}_${template}_${skin}${draft ? '_草稿' : ''}.png`;
      current = { blob: res.blob, url: URL.createObjectURL(res.blob), name, sha256: res.sha256 };
      $('pic').src = current.url; $('picwrap').hidden = false;
    }
    window.__lastResult = { checks: res.checks, rects: res.measure ? res.measure.textRects : null, sha256: res.sha256, name: current && current.name };
  } catch (e) { console.error(e); $('msg').textContent = MSG.oops; }
  finally { $('go').disabled = false; }
}
function showFull() {
  $('fullpic').src = current.url; $('full').hidden = false;
}
async function save() {
  if (!current) return;
  // 存的就是畫面上這一份 PNG（不重畫）
  const file = new File([current.blob], current.name, { type: 'image/png' });
  if (navigator.canShare && navigator.share && navigator.canShare({ files: [file] })) {
    try { await navigator.share({ files: [file] }); return; }
    catch (e) { if (e && e.name === 'AbortError') return; }
  }
  showFull();
}
$('tpl').onchange = tplChange; $('reload').onclick = load; $('addpaste').onclick = addPasted; $('adminlink').onclick = () => showAdmin(true); $('closeadmin').onclick = () => showAdmin(false); $('go').onclick = generate; $('save').onclick = save;
$('closefull').onclick = () => { $('full').hidden = true; };
$('ver').textContent = `版本 ${APP_VERSION}（${BUILD}）`;

if ('serviceWorker' in navigator && location.protocol !== 'file:') {
  let reloaded = false;
  const hadController = !!navigator.serviceWorker.controller;
  navigator.serviceWorker.addEventListener('controllerchange', () => { if (hadController && !reloaded) { reloaded = true; location.reload(); } });
  navigator.serviceWorker.register('sw.js').then(reg => reg.update()).catch(() => {});
}
window.__app = { BROKEN_LABEL, APP_VERSION, BUILD, extractCases, get current() { return current; } };
PASTED = readPasted();
window.addEventListener('hashchange', () => load(true));
CardRender.init(BASE).then(() => load(true)).catch(() => { $('msg').textContent = MSG.listFail; });
})();

