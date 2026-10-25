/* 平台共用小工具：不連外、不使用第三方程式庫 */
var PF = (function () {
  'use strict';
  var VERSION = '0.1.4';
  var BROKEN = '這個案例讀不出來';
  var REVIEW_ITEMS = [['source', '來源'], ['interpretation', '解讀'], ['amounts', '金額'], ['privacy', '個資遮蔽']];

  function esc(v) {
    return String(v == null ? '' : v).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function get(url, type) {
    return new Promise(function (resolve, reject) {
      var x = new XMLHttpRequest();
      x.open('GET', url, true);
      x.onload = function () {
        if (x.status < 200 || x.status >= 300) { reject(new Error('讀取失敗')); return; }
        if (type === 'json') { try { resolve(JSON.parse(x.responseText)); } catch (e) { reject(e); } }
        else resolve(x.responseText);
      };
      x.onerror = function () { reject(new Error('讀取失敗')); };
      x.send();
    });
  }
  function isObj(v) { return v && typeof v === 'object' && !Array.isArray(v); }
  /* 檔名只接受一般字元，不允許路徑 */
  function safeFile(name) {
    return typeof name === 'string' && /^[^\/\\\x00-\x1f?#%]+\.json$/i.test(name) && name.indexOf('..') < 0;
  }
  function stem(file) { return file.replace(/\.json$/i, ''); }
  function caseOk(d) {
    return isObj(d) && d.format === 'case-card-app-case' && isObj(d.source) && isObj(d.card) && typeof d.title === 'string' && d.title.trim() !== '';
  }
  function list(v) { return Array.isArray(v) ? v.filter(function (x) { return typeof x === 'string'; }) : (typeof v === 'string' && v ? [v] : []); }
  function review(d) {
    var r = isObj(d && d.review) ? d.review : null;
    var items = REVIEW_ITEMS.map(function (it) { return { key: it[0], label: it[1], ok: !!(r && r[it[0]] === true) }; });
    var done = items.filter(function (i) { return i.ok; }).length;
    return { has: !!r, items: items, done: done,
      summary: done === 4 ? '四項已核對' : (done === 0 ? '尚待核對' : '已核對 ' + done + '／4 項'),
      reviewer: r && typeof r.reviewer === 'string' ? r.reviewer : '', date: r && typeof r.date === 'string' ? r.date : '' };
  }
  function reviewHtml(rv) {
    return '<div class="pf-review">' + rv.items.map(function (i) {
      return '<span class="' + (i.ok ? 'ok' : 'wait') + '">' + esc(i.label) + '：' + (i.ok ? '已核對' : '尚待核對') + '</span>';
    }).join('') + '</div>';
  }
  /* 讀 ../cases/index.json 與每一件案例；壞的標示讀不出來，不影響其他 */
  function loadCases() {
    return get('../cases/index.json', 'json').then(function (idx) {
      var files = isObj(idx) && Array.isArray(idx.cases) ? idx.cases : [];
      return Promise.all(files.map(function (file) {
        if (!safeFile(file)) return Promise.resolve({ file: String(file), ok: false });
        return get('../cases/' + encodeURIComponent(file), 'json').then(function (d) {
          return caseOk(d) ? { file: file, stem: stem(file), ok: true, data: d } : { file: file, ok: false };
        }, function () { return { file: file, ok: false }; });
      }));
    });
  }
  function download(text, name, mime) {
    var blob = new Blob([text], { type: mime });
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url; a.download = name; a.rel = 'noopener';
    document.body.appendChild(a); a.click();
    setTimeout(function () { URL.revokeObjectURL(url); if (a.parentNode) a.parentNode.removeChild(a); }, 4000);
  }
  function today() { return new Date(Date.now() + 8 * 3600000).toISOString().slice(0, 10); }

  /* Markdown 轉換：先把整行文字跳脫，再加上標題、粗體、清單、表格、引用。不會放入任何原文 HTML。 */
  function inline(s) {
    var t = esc(s);
    t = t.replace(/\*\*([^*]+?)\*\*/g, '<strong>$1</strong>');
    t = t.replace(/(^|[^*])\*([^*\s][^*]*?)\*(?!\*)/g, '$1<em>$2</em>');
    t = t.replace(/`([^`]+)`/g, '<code>$1</code>');
    return t;
  }
  function cells(line) {
    var s = line.trim();
    if (s.charAt(0) === '|') s = s.slice(1);
    if (s.charAt(s.length - 1) === '|') s = s.slice(0, -1);
    return s.split('|').map(function (c) { return c.trim(); });
  }
  function isSep(line) { return /^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$/.test(line); }
  function markdown(src) {
    var lines = String(src == null ? '' : src).replace(/\r\n?/g, '\n').split('\n');
    var out = [], i = 0, para = [];
    function flush() { if (para.length) { out.push('<p>' + para.map(inline).join('<br>') + '</p>'); para = []; } }
    while (i < lines.length) {
      var line = lines[i], m;
      if (/^\s*$/.test(line)) { flush(); i++; continue; }
      if ((m = /^(#{1,6})\s+(.*)$/.exec(line))) { flush(); var n = m[1].length; out.push('<h' + n + '>' + inline(m[2].replace(/\s+#+\s*$/, '')) + '</h' + n + '>'); i++; continue; }
      if (/^\s*(-{3,}|\*{3,})\s*$/.test(line)) { flush(); out.push('<hr>'); i++; continue; }
      if (/^\s*>/.test(line)) {
        flush(); var q = [];
        while (i < lines.length && /^\s*>/.test(lines[i])) { q.push(lines[i].replace(/^\s*>\s?/, '')); i++; }
        out.push('<blockquote>' + q.map(inline).join('<br>') + '</blockquote>'); continue;
      }
      if (/^\s*\|/.test(line) && i + 1 < lines.length && isSep(lines[i + 1])) {
        flush(); var head = cells(line); i += 2; var rows = [];
        while (i < lines.length && /^\s*\|/.test(lines[i])) { rows.push(cells(lines[i])); i++; }
        out.push('<table><thead><tr>' + head.map(function (c) { return '<th>' + inline(c) + '</th>'; }).join('') + '</tr></thead><tbody>' +
          rows.map(function (r) { return '<tr>' + head.map(function (_, k) { return '<td>' + inline(r[k] || '') + '</td>'; }).join('') + '</tr>'; }).join('') + '</tbody></table>');
        continue;
      }
      if (/^\s*([-*+]|\d+[.)])\s+/.test(line)) {
        flush(); var ordered = /^\s*\d+[.)]\s+/.test(line), items = [];
        while (i < lines.length && (ordered ? /^\s*\d+[.)]\s+/ : /^\s*[-*+]\s+/).test(lines[i])) { items.push(lines[i].replace(/^\s*([-*+]|\d+[.)])\s+/, '')); i++; }
        var tag = ordered ? 'ol' : 'ul';
        out.push('<' + tag + '>' + items.map(function (t) { return '<li>' + inline(t) + '</li>'; }).join('') + '</' + tag + '>'); continue;
      }
      para.push(line); i++;
    }
    flush();
    return out.join('\n');
  }
  function isJudicialUrl(value) {
    if (typeof value !== 'string' || !value.trim()) return false;
    try {
      var url = new URL(value.trim());
      return url.protocol === 'https:' && !url.username && !url.password &&
        (url.hostname === 'judicial.gov.tw' || url.hostname.endsWith('.judicial.gov.tw'));
    } catch (error) { return false; }
  }
  function sourceInfo(d) {
    var s = isObj(d.source) ? d.source : {};
    return { court: typeof s.court === 'string' ? s.court : '', no: typeof s.case_number === 'string' ? s.case_number : '',
      date: typeof s.decision_date === 'string' ? s.decision_date : '', url: isJudicialUrl(s.url) ? s.url.trim() : '' };
  }
  function setVersion() { var v = document.getElementById('pfVersion'); if (v) v.textContent = '平台版本 ' + VERSION; }
  document.addEventListener('DOMContentLoaded', setVersion);
  return { VERSION: VERSION, BROKEN: BROKEN, esc: esc, get: get, loadCases: loadCases, review: review, reviewHtml: reviewHtml,
    markdown: markdown, download: download, today: today, list: list, sourceInfo: sourceInfo, isJudicialUrl: isJudicialUrl, isObj: isObj, stem: stem };
})();
