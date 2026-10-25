/* 上架前檢查：只讀取記憶體中的文字，不連線、不儲存。 */
var CardCheck = (function () {
  'use strict';

  var FORMAT = 'case-card-app-case';
  var DISCLAIMER = '本圖卡為案例摘要，個案仍應以正式判決書全文及最終裁判結果為準；本整理不構成任何法律意見，亦不保證內容正確性。';
  var MISSING = '這段回覆裡沒有小卡資料。請確認 GPT 的圖卡門檻是『可供圖卡使用』。';
  var REQUIRED = ['title', 'subtitle', 'tags', 'info', 'parties', 'basics', 'relation', 'facts', 'result', 'holdings', 'advisory', 'source_card', 'disclaimer', 'hero'];
  var LABELS = {
    format: '資料種類', schema_version: '資料版本', title: '標題', subtitle: '副標題',
    source: '裁判來源', court: '法院', case_number: '案號', decision_date: '判決日期',
    jid: '裁判編號', url: '來源網址', card: '小卡', tags: '分類標籤', info: '基本資訊',
    cause: '案由', date_pending: '日期確認狀態', parties: '當事人', plaintiff: '原告',
    defendant: '被告', role: '角色', name: '名稱', natural_person: '自然人註記',
    basics: '案件資料', relation: '法律關係', claim: '請求事項', offset: '抵充項目',
    order: '判命給付', label: '說明', note: '補充說明', amount: '金額', facts: '事實',
    text: '內容', icon: '圖示', result: '判決結果', total: '總額', lines: '說明',
    pending: '待確認事項', flow: '金額計算', damage_total: '損害合計', damage_label: '損害說明',
    fault_op: '過失相抵比例', fault_lines: '過失相抵說明', after_fault: '過失相抵後金額',
    after_label: '過失相抵後說明', offset_op: '抵充金額', offset_lines: '抵充說明',
    final_label: '最後金額說明', notes: '補充說明', holdings: '法院見解', issue: '爭點',
    head: '小標題', body: '內文', advisory: '顧問建議', source_card: '小卡來源', how: '查詢方式',
    disclaimer: '免責聲明', hero: '示意圖', file: '預設圖', photo: '照片', caption: '圖說',
    origin: '畫面來源', hero_type: '示意圖種類', immutable_checks: '原文核對清單',
    sum_checks: '金額加總清單', parts: '加總項目', source_refs: '段落來源',
    not_on_card: '不放入小卡的內容', result_flow: '計算依據', timeline: '時間軸',
    start: '到職', onset: '事故或發病', date: '日期', facts_anchor: '事實時間基準',
    advisory_icons: '建議圖示', display: '顯示設定', mask_natural_person_name: '姓名遮蔽設定',
    show_issues: '爭點顯示設定', keep_together: '同列文字', band_color: '色帶顏色'
  };
  var own = function (o, k) { return Object.prototype.hasOwnProperty.call(o, k); };
  var object = function (o) { return o !== null && typeof o === 'object' && !Array.isArray(o); };
  var filled = function (v) { return typeof v === 'string' && v.trim().length > 0; };
  var present = function (o, k) { return own(o, k) && o[k] !== null && o[k] !== undefined; };
  var short = function (v) {
    var s = typeof v === 'string' || typeof v === 'number' ? String(v) : '未填或內容不正確';
    return s.length > 100 ? s.slice(0, 100) + '…' : s;
  };

  // 使用主機名稱判斷，避免把 judicial.gov.tw.example.com 或帳號當成司法院。
  function isJudicialUrl(value) {
    if (typeof value !== 'string') return false;
    try {
      var u = new URL(value.trim());
      return u.protocol === 'https:' && !u.username && !u.password &&
        (u.hostname === 'judicial.gov.tw' || u.hostname.endsWith('.judicial.gov.tw'));
    } catch (e) { return false; }
  }

  // 不執行貼上的內容。逐一配對大括號，並跳過字串內的括號與跳脫引號。
  function extract(text) {
    text = typeof text === 'string' ? text : '';
    var starts = [], quoted = false, escaped = false;
    for (var i = 0; i < text.length; i += 1) {
      var c = text[i];
      if (quoted) {
        if (escaped) escaped = false;
        else if (c === '\\') escaped = true;
        else if (c === '"') quoted = false;
        continue;
      }
      if (c === '"' && starts.length) { quoted = true; continue; }
      if (c === '{') { starts.push(i); continue; }
      if (c !== '}' || !starts.length) continue;
      var start = starts.pop(), raw = text.slice(start, i + 1);
      if (raw.indexOf(FORMAT) === -1) continue;
      try {
        var data = JSON.parse(raw);
        if (object(data) && data.format === FORMAT) {
          return { status: 'found', data: data, json: JSON.stringify(data, null, 2), start: start, end: i + 1 };
        }
      } catch (e) { /* 繼續找下一段完整的小卡資料。 */ }
    }
    // 前言也可能含有未配對的括號或引號。主掃描失敗時，從每個可能的
    // 物件起點重新配對，避免前言影響後面的完整資料。
    for (var candidate = text.indexOf('{'); candidate !== -1; candidate = text.indexOf('{', candidate + 1)) {
      if (!/^\{\s*"/.test(text.slice(candidate, candidate + 200))) continue;
      var depth = 0, inString = false, escapeNext = false;
      for (var pos = candidate; pos < text.length; pos += 1) {
        var ch = text[pos];
        if (inString) {
          if (ch === '\n' || ch === '\r') break; // 真正的字串不可含未跳脫換行。
          if (escapeNext) escapeNext = false;
          else if (ch === '\\') escapeNext = true;
          else if (ch === '"') inString = false;
        } else if (ch === '"') inString = true;
        else if (ch === '{') depth += 1;
        else if (ch === '}') {
          depth -= 1;
          if (depth !== 0) continue;
          try {
            var recovered = JSON.parse(text.slice(candidate, pos + 1));
            if (object(recovered) && recovered.format === FORMAT) {
              return { status: 'found', data: recovered, json: JSON.stringify(recovered, null, 2), start: candidate, end: pos + 1 };
            }
          } catch (e) { /* 前言或其他資料，不是要找的小卡。 */ }
          break;
        }
      }
    }
    // 找不到小卡資料時，才看回覆是否寫明不能做成小卡（回覆其他段落提到這些字眼不影響判斷）。
    var refusalLine = text.split(/\r?\n/).find(function (line) {
      return /本案不適合現有版型|核心資料尚待確認/.test(line);
    });
    if (refusalLine !== undefined) {
      return { status: 'refused', refusal: refusalLine.trim(), message: '這案目前不能做成小卡。' };
    }
    return { status: 'missing', message: MISSING };
  }

  function realDate(value) {
    if (typeof value !== 'string' || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
    var y = Number(value.slice(0, 4)), m = Number(value.slice(5, 7)), d = Number(value.slice(8, 10));
    if (y < 1 || m < 1 || m > 12) return false;
    var leap = y % 4 === 0 && (y % 100 !== 0 || y % 400 === 0);
    var days = [31, leap ? 29 : 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
    return d >= 1 && d <= days[m - 1];
  }

  function money(value, signed) {
    if (typeof value === 'number' && (!Number.isSafeInteger(value))) return null;
    if (typeof value !== 'string' && typeof value !== 'number') return null;
    var s = String(value).replace(/[元,，\s]/g, '').replace(/[−－]/g, '-').replace(/＋/g, '+');
    if (!/^[+-]?\d+$/.test(s)) return null;
    var n = BigInt(s);
    return signed || n >= 0n ? n : -n;
  }

  function percentage(value) {
    if (typeof value !== 'string') return null;
    var m = value.trim().match(/^(?:[×xX*]\s*)?(\d+(?:\.\d+)?)\s*[%％](?:\s*[（(]無過失相抵[）)])?$/);
    if (!m) return null;
    var decimals = (m[1].split('.')[1] || '').length;
    var n = BigInt(m[1].replace('.', '')), denominator = 10n ** BigInt(decimals);
    if (n > 100n * denominator) return null;
    return { n: n, denominator: denominator * 100n, text: m[1] + '%' };
  }

  function amount(n) {
    return n.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
  }

  // 使用迭代走訪，深層輸入不會造成遞迴堆疊溢位。
  function strings(value, base, skipKeys) {
    var list = [], pending = [{ value: value, path: base || '', keys: [] }];
    while (pending.length) {
      var item = pending.pop(), v = item.value;
      if (typeof v === 'string' || typeof v === 'number') {
        list.push({ text: String(v), path: item.path, keys: item.keys });
      } else if (v && typeof v === 'object') {
        var keys = Object.keys(v);
        for (var j = keys.length - 1; j >= 0; j -= 1) {
          var k = keys[j];
          if (skipKeys && skipKeys.indexOf(k) !== -1) continue;
          var label = Array.isArray(v) ? '第 ' + (Number(k) + 1) + ' 項' : (own(LABELS, k) ? LABELS[k] : '其他內容');
          pending.push({ value: v[k], path: item.path ? item.path + '／' + label : label, keys: item.keys.concat(k) });
        }
      }
    }
    return list;
  }

  function validate(data, rawText, outsideText) {
    var errors = [], warnings = [];
    var error = function (code, message) { errors.push({ code: code, message: message }); };
    var warn = function (code, message) { warnings.push({ code: code, message: message }); };
    data = object(data) ? data : {};
    var card = object(data.card) ? data.card : {};
    var source = object(data.source) ? data.source : {};
    var leaves = strings(data);
    if (outsideText === undefined && typeof rawText === 'string') {
      var extracted = extract(rawText);
      outsideText = extracted.status === 'found' ? rawText.slice(0, extracted.start) + '\n' + rawText.slice(extracted.end) : rawText;
    }
    if (typeof outsideText === 'string') {
      outsideText.split(/\r?\n/).forEach(function (line, i) {
        if (line.trim()) leaves.push({ text: line, path: '小卡以外的說明第 ' + (i + 1) + ' 行', keys: [] });
      });
    }

    if (data.schema_version !== 1) error('M01', '小卡資料版本不正確，請改用第 1 版。');
    if (!filled(data.title)) error('M01', '缺少標題。');
    if (!filled(source.court)) error('M02', '缺少法院名稱。');
    if (!filled(source.case_number)) error('M02', '缺少完整案號。');
    if (!realDate(source.decision_date)) error('M02', '判決日期格式不對或日期不存在：' + short(source.decision_date) + '。請填西元年-月-日，例如 2026-06-12。');
    if (typeof source.url !== 'string' || (source.url.trim() && !isJudicialUrl(source.url))) {
      error('M03', '來源網址不是司法院的，請填司法院的安全網址；沒有網址時請留空。');
    }
    REQUIRED.forEach(function (key) {
      if (!present(card, key)) error('M04', '少了「' + LABELS[key] + '」這一塊。');
    });

    var result = object(card.result) ? card.result : {};
    var flow = object(result.flow) ? result.flow : {};
    var hasFault = present(flow, 'fault_op') && (typeof flow.fault_op !== 'string' || flow.fault_op.trim() !== '');
    var hasOffset = present(flow, 'offset_op') && (typeof flow.offset_op !== 'string' || flow.offset_op.trim() !== '');
    if (!hasFault && !hasOffset) {
      warn('M05', '沒有過失相抵與抵充的計算欄位，本次略過這段金額算式，請人工確認判命金額。');
    } else {
      var damage = money(flow.damage_total, false), ratio = percentage(flow.fault_op);
      var offsetValue = flow.offset_op;
      var noOffsetNote = typeof offsetValue === 'string' && /(?:（無抵充）|\(無抵充\))\s*$/.test(offsetValue);
      if (noOffsetNote) offsetValue = offsetValue.replace(/(?:（無抵充）|\(無抵充\))\s*$/, '');
      var after = money(flow.after_fault, false), offset = money(offsetValue, false), total = money(result.total, false);
      var missingOffset = !hasOffset || (typeof flow.offset_op === 'string' && /^(?:無抵充|無|沒有|沒有抵充|本案無抵充)$/.test(flow.offset_op.trim()));
      if (missingOffset) error('M05', '沒有抵充時，請 GPT 在抵充欄寫『− 0 元』，抵充說明寫『本案無抵充』。');
      if (!hasFault) error('M05', '沒有過失相抵時，請 GPT 在過失欄寫『× 100%（無過失相抵）』。');
      if (noOffsetNote && offset !== null && offset !== 0n) error('M05', '抵充欄寫了金額 ' + amount(offset) + ' 元又寫無抵充，前後矛盾，請 GPT 確認。');
      var bad = [];
      if (damage === null) bad.push('損害合計');
      if (ratio === null && hasFault) bad.push('過失相抵比例');
      if (after === null) bad.push('過失相抵後金額');
      if (offset === null && !missingOffset) bad.push('抵充金額');
      if (total === null) bad.push('最後判命金額');
      if (bad.length) error('M05', '金額算式無法核對，請補齊或修正：' + bad.join('、') + '。金額須填整數元，比例須填百分比。');
      if (damage !== null && ratio !== null && after !== null) {
        var multiplied = damage * ratio.n;
        var expected = (multiplied * 2n + ratio.denominator) / (ratio.denominator * 2n);
        if (after !== expected) error('M05', '損害 ' + amount(damage) + ' × ' + ratio.text + '，四捨五入到元應為 ' + amount(expected) + '，資料寫 ' + amount(after) + '。');
      }
      if (after !== null && offset !== null && total !== null && after - offset !== total) {
        error('M05', '過失相抵後 ' + amount(after) + ' − 抵充 ' + amount(offset) + ' 應為 ' + amount(after - offset) + '，最後判命金額寫 ' + amount(total) + '。');
      }
    }

    if (present(card, 'sum_checks')) {
      if (!Array.isArray(card.sum_checks)) error('M06', '金額加總清單的內容不正確，請逐組列出加總項目與總額。');
      else card.sum_checks.forEach(function (group, i) {
        if (!object(group) || !Array.isArray(group.parts) || !group.parts.length) {
          error('M06', '第 ' + (i + 1) + ' 組加總缺少金額項目。'); return;
        }
        var parts = group.parts.map(function (p) { return money(p, true); });
        var sumTotal = money(group.total, true);
        if (sumTotal === null || parts.some(function (p) { return p === null; })) {
          error('M06', '第 ' + (i + 1) + ' 組加總有無法辨認的金額，請填整數元並保留加減號。'); return;
        }
        var sum = parts.reduce(function (a, b) { return a + b; }, 0n);
        if (sum !== sumTotal) error('M06', '第 ' + (i + 1) + ' 組加總不對：' + parts.map(amount).join(' ＋ ') + ' ＝ ' + amount(sum) + '，不等於資料寫的 ' + amount(sumTotal) + '。');
      });
    }

    var unknownNames = [];
    if (object(card.parties)) Object.keys(card.parties).forEach(function (key) {
      var party = card.parties[key];
      if (!object(party) || party.natural_person !== true) return;
      var role = own(LABELS, key) ? LABELS[key] : '當事人';
      var name = typeof party.name === 'string' ? party.name : '';
      var chars = Array.from(name);
      var masked = chars.length >= 2 && /^\p{L}$/u.test(chars[0]) && chars.slice(1).every(function (c) { return c === '○'; });
      if (!masked) {
        var example = chars.length && !/[\s○〇◯●*xX×]/u.test(chars[0]) ? chars[0] + '○'.repeat(Math.max(1, chars.length - 1)) : '王○○';
        error('M07', role + '名字還沒遮好，請改成「' + example + '」這種第一個字加空心圓的格式。');
        if (filled(name) && chars.length > 1 && !/[○〇◯●*]/u.test(name)) {
          leaves.forEach(function (leaf) {
            if (leaf.keys.join('.') === 'card.parties.' + key + '.name') return;
            if (leaf.text.indexOf(name) !== -1) error('M07', leaf.path + '也出現' + role + '的未遮姓名，請一併遮蔽。');
          });
        }
      } else {
        unknownNames.push(role);
        var roleWords = key === 'plaintiff' ? '原告|勞工|當事人' : (key === 'defendant' ? '被告|雇主|當事人' : '原告|被告|勞工|雇主|當事人');
        var possibleName = new RegExp('(?:' + roleWords + ')(?:姓名|為|是)?[：:\\s「『]*' + chars[0] + '\\p{L}{' + (chars.length - 1) + '}', 'u');
        leaves.forEach(function (leaf) {
          if (possibleName.test(leaf.text)) warn('', leaf.path + '可能有' + role + '的未遮姓名，請人工核對；程式無法由已遮姓名確認是否為同一人。');
        });
      }
    });
    if (unknownNames.length) warn('', unknownNames.join('、') + '姓名已遮蔽；因未提供原始全名，其他文字仍請人工核對是否有漏遮的同一人姓名。');

    if (present(card, 'facts')) {
      if (!Array.isArray(card.facts)) error('M08', '事實需逐點列出，最多 5 點。');
      else {
        if (card.facts.length > 5) error('M08', '事實共有 ' + card.facts.length + ' 點，最多只能放 5 點。');
        card.facts.forEach(function (fact, i) {
          if (!object(fact) || ['overtime', 'newhire', 'event', 'course', 'phone', 'check'].indexOf(fact.icon) === -1) error('M08', '事實第 ' + (i + 1) + ' 點的圖示不在清單內，請使用規定的六種圖示之一。');
        });
      }
    }

    ['holdings', 'advisory'].forEach(function (key) {
      if (!present(card, key)) return;
      var items = card[key];
      if (!Array.isArray(items)) { error('M09', LABELS[key] + '需逐點列出，共 4 點。'); return; }
      if (items.length !== 4) error('M09', LABELS[key] + '有 ' + items.length + ' 點，應為 4 點。');
      items.forEach(function (item, i) {
        if (!object(item) || !filled(item.head)) error('M09', LABELS[key] + '第 ' + (i + 1) + ' 點缺少小標題。');
        if (!object(item) || !filled(item.body)) error('M09', LABELS[key] + '第 ' + (i + 1) + ' 點缺少內文。');
      });
    });
    if (present(card, 'disclaimer') && card.disclaimer !== DISCLAIMER) error('M10', '免責聲明被改過，請完整使用規定的固定文字。');

    var haystack = strings(card, '', ['immutable_checks']).concat(strings(source));
    if (Array.isArray(card.immutable_checks)) card.immutable_checks.forEach(function (value, i) {
      var needle = typeof value === 'string' || typeof value === 'number' ? String(value) : '';
      if (!needle || !haystack.some(function (leaf) { return leaf.text.indexOf(needle) !== -1; })) {
        warn('R01', '原文核對第 ' + (i + 1) + ' 項「' + short(value) + '」未出現在小卡或裁判來源文字中；可能是日期或法院由程式帶入，請人工確認。');
      }
    });

    function lengthWarning(text, limit, label) {
      if (typeof text !== 'string') return;
      var length = Array.from(text).length;
      if (length > limit) warn('R02', label + '有 ' + length + ' 字，超過 ' + limit + ' 字，出圖時會再檢查；請勿為縮短文字改動數字或意思。');
    }
    ['title', 'subtitle'].forEach(function (key) {
      var lines = Array.isArray(card[key]) ? card[key] : (typeof card[key] === 'string' ? card[key].split(/\r?\n/) : []);
      lines.forEach(function (line, i) { lengthWarning(line, 16, LABELS[key] + '第 ' + (i + 1) + ' 行'); });
    });
    if (Array.isArray(card.facts)) card.facts.forEach(function (item, i) { if (object(item)) lengthWarning(item.text, 28, '事實第 ' + (i + 1) + ' 點'); });
    ['holdings', 'advisory'].forEach(function (key) {
      if (Array.isArray(card[key])) card[key].forEach(function (item, i) { if (object(item)) lengthWarning(item.body, 30, LABELS[key] + '第 ' + (i + 1) + ' 點內文'); });
    });
    strings(card.advisory, '顧問建議').forEach(function (leaf) {
      var risky = ['一定會賠', '保證理賠', '全部可以抵充'].filter(function (word) { return leaf.text.indexOf(word) !== -1; });
      if (risky.length) warn('R03', leaf.path + '出現「' + risky.join('」、「') + '」，請核對是否過度保證理賠或抵充結果。');
    });

    var pending = leaves.map(function (leaf) { return { path: leaf.path, count: leaf.text.split('尚待確認').length - 1 }; }).filter(function (item) { return item.count > 0; });
    var pendingCount = pending.reduce(function (n, item) { return n + item.count; }, 0);
    pending.forEach(function (item) { warn('R04', '全文「尚待確認」共 ' + pendingCount + ' 次；' + item.path + '有 ' + item.count + ' 次，請逐一確認。'); });

    var hero = object(card.hero) ? card.hero : {};
    if (!filled(hero.photo) || (!filled(hero.hero_type) && !filled(card.hero_type) && !filled(data.hero_type))) {
      warn('R05', '示意圖會用預設圖：照片未填或尚未指定示意圖種類。');
    }
    return { errors: errors, warnings: warnings, canPublish: errors.length === 0 };
  }

  function inspect(text) {
    var extracted = extract(text);
    if (extracted.status !== 'found') {
      extracted.errors = []; extracted.warnings = []; extracted.canPublish = false;
      return extracted;
    }
    var checked = validate(extracted.data, text, text.slice(0, extracted.start) + '\n' + text.slice(extracted.end));
    extracted.errors = checked.errors; extracted.warnings = checked.warnings; extracted.canPublish = checked.canPublish;
    return extracted;
  }

  return { extract: extract, validate: validate, inspect: inspect };
}());
