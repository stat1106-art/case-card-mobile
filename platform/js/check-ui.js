/* 檢查頁面：不儲存、不送出內容，所有回覆文字均以純文字顯示。 */
(function () {
  'use strict';
  var current = null;
  function el(id) { return document.getElementById(id); }
  function reset() {
    current = null;
    el('checkResult').hidden = true;
    el('manualCopy').hidden = true;
    el('copyText').value = '';
    el('copyStatus').textContent = '';
    el('copyCard').hidden = true;
    el('requiredList').replaceChildren();
    el('warningsList').replaceChildren();
    el('resultTitle').textContent = '';
    el('resultMessage').textContent = '';
  }
  function renderList(id, items, empty) {
    var list = el(id);
    list.replaceChildren();
    if (!items.length) {
      var none = document.createElement('li');
      none.className = 'check-empty';
      none.textContent = empty;
      list.appendChild(none);
      return;
    }
    items.forEach(function (item) {
      var row = document.createElement('li');
      if (item.code) {
        var code = document.createElement('span');
        code.className = 'check-code';
        code.textContent = item.code;
        row.appendChild(code);
      }
      row.appendChild(document.createTextNode(item.message));
      list.appendChild(row);
    });
  }
  function inspect() {
    reset();
    el('inputStatus').textContent = '';
    var result;
    try { result = CardCheck.inspect(el('reply').value); }
    catch (error) {
      result = { status: 'missing', message: '這段內容目前無法讀取。請重新貼上 GPT 02 的完整回覆，再試一次。', errors: [], warnings: [], canPublish: false };
    }
    current = result;
    var found = result.status === 'found';
    el('checkResult').hidden = false;
    el('findings').hidden = !found;
    el('copyActions').hidden = !found;
    el('copyCorrections').hidden = !found || !result.errors.length;
    el('copyCard').hidden = !found || !result.canPublish;
    el('resultBanner').className = 'check-banner ' + (found ? (result.canPublish ? 'pass' : 'fail') : 'hold');
    if (found) {
      el('resultTitle').textContent = result.canPublish ? '可以上架' : '有 ' + result.errors.length + ' 項必修，請 GPT 修改';
      el('resultMessage').textContent = result.canPublish ? '未發現必修項目。請看完下方提醒，再複製小卡資料。' : '請把修改要求貼回 GPT 02，收到完整回覆後再檢查一次。';
      el('requiredCount').textContent = String(result.errors.length);
      el('warningsCount').textContent = String(result.warnings.length);
      renderList('requiredList', result.errors, '沒有必修項目。');
      renderList('warningsList', result.warnings, '沒有提醒事項。');
    } else {
      el('resultTitle').textContent = result.status === 'refused' ? '這案目前不能做成小卡' : '沒有找到小卡資料';
      el('resultMessage').textContent = (result.status === 'refused' ? (result.refusal || result.message) : result.message) || '這段回覆裡沒有小卡資料。請確認 GPT 的圖卡門檻是「可供圖卡使用」。';
    }
    el('resultTitle').focus({ preventScroll: true });
    el('checkResult').scrollIntoView({ behavior: 'auto', block: 'start' });
  }
  function correctionText() {
    if (!current || !current.errors.length) return '';
    return '請修正小卡資料：\n' + current.errors.map(function (item, index) {
      return (index + 1) + '. ' + item.message;
    }).join('\n') + '\n請保留判決原文的數字、日期、單位與意思；修完重新附上整段小卡資料，讓我再次檢查。';
  }
  function legacyCopy(text) {
    var area = document.createElement('textarea');
    area.className = 'check-copy-buffer';
    area.value = text;
    area.setAttribute('readonly', '');
    area.setAttribute('aria-hidden', 'true');
    document.body.appendChild(area);
    area.select();
    area.setSelectionRange(0, area.value.length);
    var copied = false;
    try { copied = document.execCommand('copy'); } catch (error) { copied = false; }
    area.remove();
    return copied;
  }
  async function copy(text, label) {
    if (!text) return;
    var sourceResult = current;
    el('copyStatus').textContent = '';
    el('manualCopy').hidden = true;
    var copied = false;
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(text);
        copied = true;
      }
    } catch (error) { copied = false; }
    if (current !== sourceResult) return;
    if (!copied) copied = legacyCopy(text);
    if (copied) {
      el('copyStatus').textContent = '已複製' + label + '。';
    } else {
      el('copyText').value = text;
      el('manualCopy').hidden = false;
      el('copyText').focus();
      el('copyText').select();
      el('copyStatus').textContent = '請手動複製下方已選取的內容。';
    }
  }
  el('startCheck').addEventListener('click', inspect);
  el('reply').addEventListener('input', function () {
    var hadResult = !!current;
    reset();
    el('inputStatus').textContent = hadResult ? '內容已變更，請重新開始檢查。' : '';
  });
  el('clearInput').addEventListener('click', function () {
    el('reply').value = '';
    reset();
    el('inputStatus').textContent = '已清空貼上的內容。';
    el('reply').focus();
  });
  el('copyCorrections').addEventListener('click', function () { copy(correctionText(), '給 GPT 的修改要求'); });
  el('copyCard').addEventListener('click', function () {
    if (current && current.canPublish) copy(current.json || JSON.stringify(current.data, null, 2), '小卡資料');
  });
})();
