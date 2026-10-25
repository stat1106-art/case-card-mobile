/* 案例分析：case.html#檔名（不含 .json） */
(function () {
  'use strict';
  var $ = function (id) { return document.getElementById(id); };
  function show() {
    var raw = location.hash.replace(/^#/, '');
    var name = '';
    try { name = decodeURIComponent(raw); } catch (e) { name = ''; }
    if (!name) {
      $('title').textContent = '案例分析';
      $('body').innerHTML = '<p class="pf-lead">請先到案例庫選一件案例，按「看分析」。</p><div class="pf-actions"><a class="pf-btn primary" href="cases.html">回案例庫</a></div>';
      return;
    }
    if (/[\/\\\x00-\x1f?#%]/.test(name) || name.indexOf('..') >= 0) { bad(name); return; }
    var file = name + '.json';
    $('body').innerHTML = '<p class="pf-lead">讀取中……</p>';
    PF.get('../cases/' + encodeURIComponent(file), 'json').then(function (d) {
      if (!(PF.isObj(d) && d.format === 'case-card-app-case' && PF.isObj(d.source) && PF.isObj(d.card) && typeof d.title === 'string' && d.title.trim())) { bad(name); return; }
      var s = PF.sourceInfo(d), rv = PF.review(d);
      $('title').textContent = d.title;
      document.title = d.title + '｜案例分析';
      var html = '<h2>基本資料</h2><dl class="pf-info"><dt>法院</dt><dd>' + PF.esc(s.court || '尚待確認') + '</dd><dt>案號</dt><dd>' + PF.esc(s.no || '尚待確認') +
        '</dd><dt>判決日期</dt><dd>' + PF.esc(s.date || '尚待確認') + '</dd><dt>來源網址</dt><dd>' +
        (s.url ? '<a href="' + PF.esc(s.url) + '" target="_blank" rel="noopener noreferrer">' + PF.esc(s.url) + '</a>' : '尚待確認') + '</dd></dl>' +
        '<h2>核對狀態</h2>' + (rv.has ? '' : '<p class="pf-notice" id="reviewNotice">本案尚未完成人工核對，內容僅供參考</p>') + PF.reviewHtml(rv) +
        (rv.has && (rv.reviewer || rv.date) ? '<p class="pf-sub">核對人：' + PF.esc(rv.reviewer || '尚待確認') + '｜日期：' + PF.esc(rv.date || '尚待確認') + '</p>' : '') +
        '<div class="pf-actions"><a class="pf-btn primary" id="toCard" href="../index.html#case=' + encodeURIComponent(file) + '">產生這張圖卡</a><a class="pf-btn" href="cases.html">回案例庫</a></div>' +
        '<h2>完整分析</h2><div id="analysis"><p class="pf-lead">讀取中……</p></div>';
      $('body').innerHTML = html;
      PF.get('../cases/' + encodeURIComponent(name) + '.md', 'text').then(function (md) {
        $('analysis').innerHTML = '<div class="md">' + PF.markdown(md) + '</div>';
      }, function () { $('analysis').innerHTML = '<p class="pf-notice">本案尚無完整分析</p>'; });
    }, function () { bad(name); });
  }
  function bad(name) {
    $('title').textContent = '案例分析';
    $('body').innerHTML = '<p class="pf-notice">' + PF.esc(name) + '：' + PF.BROKEN + '</p><div class="pf-actions"><a class="pf-btn" href="cases.html">回案例庫</a></div>';
  }
  window.addEventListener('hashchange', show);
  show();
})();
