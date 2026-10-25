/* 案例庫 */
(function () {
  'use strict';
  var $ = function (id) { return document.getElementById(id); };
  var ALL = [];
  var CAND_NOTE = '這是自動節錄，尚未經 GPT 深入分析與核對';

  function year(d) { var s = PF.sourceInfo(d).date; return /^\d{4}/.test(s) ? s.slice(0, 4) : ''; }
  function tags(d) { return PF.list(d.card && d.card.tags); }
  function subtitle(d) { return PF.list(d.card && d.card.subtitle).join('，'); }
  function haystack(c) {
    var s = PF.sourceInfo(c.data);
    return [c.data.title, s.court, s.no, tags(c.data).join(' '), subtitle(c.data)].join(' ').toLowerCase();
  }
  function filtered() {
    var words = $('q').value.trim().toLowerCase().split(/\s+/).filter(Boolean);
    var tg = $('tag').value, yr = $('year').value;
    return ALL.filter(function (c) {
      if (!c.ok) return !words.length && !tg && !yr;
      if (tg && tags(c.data).indexOf(tg) < 0) return false;
      if (yr && year(c.data) !== yr) return false;
      var h = haystack(c);
      return words.every(function (w) { return h.indexOf(w) >= 0; });
    });
  }
  function card(c) {
    if (!c.ok) return '<article class="pf-card bad"><h3>' + '案例「' + PF.esc(String(c.file).replace(/\.json$/i, '')) + '」' + '</h3><p>' + PF.BROKEN + '</p></article>';
    var d = c.data, s = PF.sourceInfo(d), rv = PF.review(d);
    return '<article class="pf-card"><h3>' + PF.esc(d.title) + '</h3>' +
      '<div class="pf-meta"><span>' + PF.esc(s.court || '法院尚待確認') + '</span><span>' + PF.esc(s.no || '案號尚待確認') + '</span><span>判決日期 ' + PF.esc(s.date || '尚待確認') + '</span></div>' +
      (tags(d).length ? '<div class="pf-tags">' + tags(d).map(function (t) { return '<span>' + PF.esc(t) + '</span>'; }).join('') + '</div>' : '') +
      (subtitle(d) ? '<p class="pf-sub">' + PF.esc(subtitle(d)) + '</p>' : '') +
      '<div><strong>核對狀態：</strong>' + PF.esc(rv.summary) + '</div>' + PF.reviewHtml(rv) +
      '<div class="pf-actions"><a class="pf-btn primary" href="case.html#' + encodeURIComponent(c.stem) + '">看分析</a>' +
      '<a class="pf-btn" href="../index.html#case=' + encodeURIComponent(c.file) + '">產生圖卡</a>' +
      '<button type="button" class="pf-btn" data-report="' + PF.esc(c.file) + '">下載本案重點</button></div></article>';
  }
  function draw() {
    var list = filtered();
    var good = list.filter(function (c) { return c.ok; }).length;
    $('count').textContent = '共 ' + ALL.filter(function (c) { return c.ok; }).length + ' 件案例，目前顯示 ' + good + ' 件' + (list.length > good ? '（另有 ' + (list.length - good) + ' 個檔案讀不出來）' : '') + '。';
    $('list').innerHTML = list.map(card).join('') || '<p class="pf-lead">沒有符合條件的案例。</p>';
  }
  function fillFilters() {
    var ts = {}, ys = {};
    ALL.forEach(function (c) { if (!c.ok) return; tags(c.data).forEach(function (t) { ts[t] = 1; }); var y = year(c.data); if (y) ys[y] = 1; });
    Object.keys(ts).sort().forEach(function (t) { $('tag').add(new Option(t, t)); });
    Object.keys(ys).sort().reverse().forEach(function (y) { $('year').add(new Option(y + ' 年', y)); });
  }
  function csvCell(v) { var s = String(v == null ? '' : v); if (/^[=+\-@]/.test(s)) s = "'" + s; return '"' + s.replace(/"/g, '""') + '"'; }
  function csv() {
    var rows = filtered().filter(function (c) { return c.ok; }).map(function (c) {
      var d = c.data, s = PF.sourceInfo(d);
      return [c.stem, d.title, [s.court, s.no].filter(Boolean).join(' '), s.date, tags(d).join('、'), subtitle(d), s.url, PF.review(d).summary];
    });
    var head = ['編號', '案件短題', '法院／完整案號', '判決日期', '標籤', '一句摘要', '來源網址', '核對狀態'];
    PF.download('\ufeff' + [head].concat(rows).map(function (r) { return r.map(csvCell).join(','); }).join('\r\n') + '\r\n',
      '職災案例索引_' + PF.today().replace(/-/g, '') + '.csv', 'text/csv;charset=utf-8');
  }
  var REPORT_CSS = 'body{margin:0;background:#fff;color:#222;font-family:-apple-system,"PingFang TC","Noto Sans TC","Microsoft JhengHei",sans-serif}main{max-width:860px;margin:auto;padding:24px 16px;line-height:1.8}h1{font-size:24px;line-height:1.4}dl{display:grid;grid-template-columns:max-content 1fr;gap:4px 12px}dt{font-weight:700}dd{margin:0;overflow-wrap:anywhere}table{border-collapse:collapse;width:100%}th,td{border:1px solid #bbb;padding:5px 7px;text-align:left;vertical-align:top}th{background:#eee}blockquote{margin:8px 0;padding:6px 12px;border-left:4px solid #999;background:#f5f5f5}.note{background:#fff3d9;padding:8px 12px;border-radius:8px}.disc{color:#555;font-size:13px;border-top:1px solid #ccc;margin-top:24px;padding-top:10px}';
  function report(file) {
    var c = ALL.filter(function (x) { return x.ok && x.file === file; })[0];
    if (!c) return;
    var d = c.data, s = PF.sourceInfo(d), rv = PF.review(d);
    function build(md) {
      var html = '<!DOCTYPE html><html lang="zh-Hant-TW"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">' +
        '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'">' +
        '<title>' + PF.esc(d.title) + '｜本案重點</title><style>' + REPORT_CSS + '</style></head><body><main>' +
        '<h1>' + PF.esc(d.title) + '</h1><h2>基本資料</h2><dl><dt>法院</dt><dd>' + PF.esc(s.court || '尚待確認') + '</dd><dt>案號</dt><dd>' + PF.esc(s.no || '尚待確認') +
        '</dd><dt>判決日期</dt><dd>' + PF.esc(s.date || '尚待確認') + '</dd><dt>來源網址</dt><dd>' + PF.esc(s.url || '尚待確認') + '</dd><dt>核對狀態</dt><dd>' +
        rv.items.map(function (i) { return PF.esc(i.label) + '：' + (i.ok ? '已核對' : '尚待核對'); }).join('、') + '</dd></dl>' +
        (rv.has ? '' : '<p class="note">本案尚未完成人工核對，內容僅供參考</p>') +
        '<h2>完整分析</h2>' + (md === null ? '<p>本案尚無完整分析</p>' : PF.markdown(md)) +
        '<p class="disc">本平台為案例摘要與風險溝通參考，個案仍應以正式判決書全文及最終裁判結果為準；不構成法律意見，也不保證理賠。可用瀏覽器的列印功能存成 PDF。下載日期：' + PF.today() + '</p></main></body></html>';
      PF.download(html, c.stem + '_本案重點.html', 'text/html;charset=utf-8');
    }
    PF.get('../cases/' + encodeURIComponent(c.stem) + '.md', 'text').then(build, function () { build(null); });
  }
  function candidates() {
    PF.get('data/case_library_original5_masked.json', 'json').then(function (lib) {
      var recs = PF.isObj(lib) && Array.isArray(lib.records) ? lib.records : [];
      var html = recs.map(function (raw, i) {
        try {
          var h = clCaseHtml(clValidateRow(raw), i, false);
          return h.replace('<article class="cl-card"', '<article class="cl-card"').replace(/(<article class="cl-card"[^>]*>)/, '$1<p class="cl-warning">' + CAND_NOTE + '</p>');
        } catch (e) { return '<div class="cl-card"><p class="cl-warning">' + PF.BROKEN + '</p></div>'; }
      }).join('');
      $('cand').innerHTML = html || '<p class="pf-lead">目前沒有候選判決。</p>';
    }, function () { $('cand').innerHTML = '<p class="pf-lead">候選判決資料讀不出來，請重新整理頁面。</p>'; });
  }
  $('q').addEventListener('input', draw);
  $('tag').addEventListener('change', draw);
  $('year').addEventListener('change', draw);
  $('csv').addEventListener('click', csv);
  $('list').addEventListener('click', function (e) { var b = e.target.closest('button[data-report]'); if (b) report(b.getAttribute('data-report')); });
  PF.loadCases().then(function (all) {
    ALL = all.sort(function (a, b) { return a.file < b.file ? -1 : a.file > b.file ? 1 : 0; });
    fillFilters(); draw();
  }, function () { $('count').textContent = '案例清單讀不出來，請重新整理頁面再試一次。'; });
  candidates();
})();
