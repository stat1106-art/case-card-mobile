/* 風險試算：計算與畫面沿用原工具程式；資料改讀 data/risk_data_masked.json。 */
(function () {
  function fail() {
    var box = document.getElementById('loadError');
    if (box) box.hidden = false;
  }
  var req = new XMLHttpRequest();
  req.open('GET', 'data/risk_data_masked.json', true);
  req.onload = function () {
    if (req.status < 200 || req.status >= 300) { fail(); return; }
    var raw;
    try { raw = JSON.parse(req.responseText); } catch (e) { fail(); return; }
    try { start(raw); } catch (e) { fail(); }
  };
  req.onerror = fail;
  req.send();
  function start(RAW_RISK_DATA) {
"use strict";
var __spreadArray = (this && this.__spreadArray) || function (to, from, pack) {
    if (pack || arguments.length === 2) for (var i = 0, l = from.length, ar; i < l; i++) {
        if (ar || !(i in from)) {
            if (!ar) ar = Array.prototype.slice.call(from, 0, i);
            ar[i] = from[i];
        }
    }
    return to.concat(ar || Array.prototype.slice.call(from));
};
/* Compatibility helpers for older iOS Safari/WebKit. */
if (!Number.isFinite) {
    Number.isFinite = function (value) {
        return typeof value === "number" && isFinite(value);
    };
}
if (!Object.entries) {
    Object.entries = function (object) {
        var ownProps = Object.keys(object);
        var result = new Array(ownProps.length);
        for (var i = 0; i < ownProps.length; i += 1) {
            result[i] = [ownProps[i], object[ownProps[i]]];
        }
        return result;
    };
}
if (!Array.prototype.find) {
    Array.prototype.find = function (predicate, thisArg) {
        if (this == null)
            throw new TypeError("Array.prototype.find called on null or undefined");
        if (typeof predicate !== "function")
            throw new TypeError("predicate must be a function");
        var list = Object(this);
        var length = list.length >>> 0;
        for (var i = 0; i < length; i += 1) {
            var value = list[i];
            if (predicate.call(thisArg, value, i, list))
                return value;
        }
        return undefined;
    };
}
if (!Array.isArray) {
    Array.isArray = function (value) {
        return Object.prototype.toString.call(value) === "[object Array]";
    };
}
if (window.Element && !Element.prototype.matches) {
    Element.prototype.matches = Element.prototype.webkitMatchesSelector || Element.prototype.msMatchesSelector || function (selector) {
        var matches = (this.document || this.ownerDocument).querySelectorAll(selector);
        var i = matches.length;
        while (i >= 0 && matches.item(i) !== this)
            i -= 1;
        return i > -1;
    };
}
if (window.Element && !Element.prototype.closest) {
    Element.prototype.closest = function (selector) {
        var element = this;
        while (element && element.nodeType === 1) {
            if (element.matches ? element.matches(selector) : element.msMatchesSelector(selector))
                return element;
            element = element.parentElement || element.parentNode;
        }
        return null;
    };
}
function clearElement(element) {
    while (element && element.firstChild) {
        element.removeChild(element.firstChild);
    }
}
/* Editable data format, version 1. No external libraries. */
function cloneRiskData(value) { return JSON.parse(JSON.stringify(value)); }
function validateRiskData(input) {
    function fail(message) { throw new Error(message); }
    function object(value, label) {
        if (!value || typeof value !== 'object' || Array.isArray(value)) fail(label + '必須是物件。');
    }
    function text(value, label, max, empty) {
        if (typeof value !== 'string' || (!empty && !value.trim()) || value.length > max) fail(label + '文字格式或長度不正確。');
        if (['__proto__', 'constructor', 'prototype'].indexOf(value) !== -1) fail(label + '名稱不適用。');
    }
    function number(value, label, min, max) {
        if (typeof value !== 'number' || !Number.isFinite(value) || value < min || value > max) fail(label + '必須介於 ' + min + ' 與 ' + max + '。');
    }
    function safeKeys(value, depth) {
        if (depth > 15) fail('資料巢狀層數過多。');
        if (!value || typeof value !== 'object') return;
        Object.keys(value).forEach(function (key) {
            if (['__proto__', 'constructor', 'prototype'].indexOf(key) !== -1) fail('資料含不適用的欄位名稱。');
            safeKeys(value[key], depth + 1);
        });
    }
    function safeUrl(value, label) {
        if (!value) return;
        text(value, label, 2000, true);
        var parsed;
        try { parsed = new URL(value); } catch (_) { fail(label + '網址格式不正確。'); }
        if (parsed.protocol !== 'https:' || !/(^|\.)judicial\.gov\.tw$/i.test(parsed.hostname) || parsed.username || parsed.password) fail(label + '請使用司法院 judicial.gov.tw 的 HTTPS 官方網址。');
    }
    object(input, '資料'); safeKeys(input, 0);
    if (input.schemaVersion !== 1) fail('資料格式版本不相容；請使用本工具匯出的 JSON。');
    object(input.meta, '資料版本');
    ['dataVersion', 'rateYear', 'salaryPeriod', 'accidentPeriod', 'snapshotId'].forEach(function (key) { text(input.meta[key], key, 160, false); });
    text(input.meta.updatedAt || '', '更新時間', 80, true);
    text(input.meta.notes || '', '資料備註', 3000, true);
    number(input.overallWorkplaceRate, '全產業職災率', 0, 1000);
    if (!Array.isArray(input.majorIndustries) || !input.majorIndustries.length || input.majorIndustries.length > 100) fail('產業大類須有 1–100 筆。');
    object(input.detailIndustries, '細分產業'); object(input.accidentStats, '事故統計');
    var majors = Object.create(null), details = Object.create(null);
    input.majorIndustries.forEach(function (item) {
        object(item, '產業'); text(item.name, '產業名稱', 120, false);
        if (majors[item.name]) fail('產業大類重複：' + item.name);
        majors[item.name] = true;
        number(item.workplaceRate, item.name + '職場職災率', 0, 1000);
        number(item.includingTrafficRate, item.name + '含交通職災率', 0, 1000);
        if (item.includingTrafficRate < item.workplaceRate) fail(item.name + '含交通事故數值不得低於不含交通事故數值。');
        var children = input.detailIndustries[item.name];
        if (!Array.isArray(children) || !children.length || children.length > 300) fail(item.name + '須有細分產業。');
        children.forEach(function (detail) {
            object(detail, '細分產業'); text(detail.name, '細分產業名稱', 120, false);
            if (details[detail.name]) fail('細分產業名稱重複：' + detail.name);
            details[detail.name] = item.name;
            number(detail.salary, detail.name + '薪資', 0, 10000000);
        });
    });
    Object.keys(input.detailIndustries).forEach(function (name) { if (!majors[name]) fail('細分產業找不到大類：' + name); });
    Object.keys(input.accidentStats).forEach(function (name) {
        if (!details[name]) fail('事故統計找不到細分產業：' + name);
        object(input.accidentStats[name], name + '事故統計');
        Object.keys(input.accidentStats[name]).forEach(function (kind) {
            text(kind, '事故類型', 100, false);
            var count = input.accidentStats[name][kind];
            number(count, name + '／' + kind + '件數', 0, 100000000);
            if (Math.floor(count) !== count) fail('事故件數必須是整數。');
        });
    });
    if (!Array.isArray(input.courtCases) || input.courtCases.length > 10000) fail('案例須為陣列，最多 10,000 筆。');
    var ids = Object.create(null), jids = Object.create(null);
    input.courtCases.forEach(function (item) {
        object(item, '案例'); text(item.id, '案例 ID', 200, false);
        if (ids[item.id]) fail('案例 ID 重複：' + item.id);
        ids[item.id] = true;
        text(item.industry, '案例產業', 120, false);
        if (!details[item.industry]) fail('案例產業不存在：' + item.industry);
        if (item.major && item.major !== details[item.industry]) fail('案例產業與大類不一致：' + item.id);
        ['accident', 'court', 'caseNo'].forEach(function (key) { text(item[key], '案例 ' + key, 200, false); });
        number(item.amount, '案例金額', 0, 1000000000000);
        number(Number(item.year), '案例年度', 1, 9999);
        if (Math.floor(Number(item.year)) !== Number(item.year)) fail('案例年度必須是整數。');
        ['title','level','date','diagnosis','reason','accidentReason','groupInsurance','offsetNote','death','permanentDisability','reviewStatus','reviewedAt'].forEach(function (key) {
            if (item[key] !== undefined) text(item[key], '案例 ' + key, 12000, true);
        });
        safeUrl(item.sourceUrl, '案例原文網址');
        if (item.jid) { text(item.jid, 'JID', 240, false); if (!/^[A-Z0-9]{2,10}[VMAPC],\d{1,4},[^,\x00-\x1f]{1,60},\d{1,12},\d{8},\d{1,6}$/.test(item.jid)) fail('JID 格式不正確：' + item.jid); if (jids[item.jid]) fail('JID 重複：' + item.jid); jids[item.jid] = true; }
    });
    if (input.courtInbox !== undefined) {
        if (!Array.isArray(input.courtInbox) || input.courtInbox.length > 10000) fail('待覆核案例格式不正確。');
        input.courtInbox.forEach(function (item) {
            object(item, '待覆核案例'); text(item.jid, '待覆核 JID', 240, false);
            if (jids[item.jid]) fail('已收錄與待覆核案例的 JID 重複：' + item.jid);
            jids[item.jid] = true;
            ['court','caseNo','title','date','excerpt','fetchedAt'].forEach(function (key) { text(item[key] || '', key, 16000, true); });
            text(item.sourceHash, '待覆核原文識別值', 128, false);
            safeUrl(item.sourceUrl, '待覆核原文網址');
        });
    }
    if (input.removedCourtJids !== undefined) {
        if (!Array.isArray(input.removedCourtJids) || input.removedCourtJids.length > 50000) fail('撤回紀錄格式不正確。');
        input.removedCourtJids.forEach(function (jid) { text(jid, '撤回 JID', 240, false); });
    }
    var result = cloneRiskData(input);
    result.courtInbox = result.courtInbox || [];
    result.removedCourtJids = result.removedCourtJids || [];
    return result;
}
function makeSafeJson(value) {
    return JSON.stringify(value, null, 2).replace(/</g, '\\u003c').replace(/\u2028/g, '\\u2028').replace(/\u2029/g, '\\u2029');
}
function removeWithdrawnCases(data, withdrawn) {
    var excluded = Object.create(null);
    (data.removedCourtJids || []).concat(withdrawn || []).forEach(function (jid) { excluded[jid] = true; });
    data.courtCases = data.courtCases.filter(function (item) { return !item.jid || !excluded[item.jid]; });
    data.courtInbox = (data.courtInbox || []).filter(function (item) { return !excluded[item.jid]; });
    data.removedCourtJids = Object.keys(excluded);
    return data;
}
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { validateRiskData: validateRiskData, makeSafeJson: makeSafeJson, removeWithdrawnCases: removeWithdrawnCases };
}


var BUILTIN_DATA = validateRiskData(RAW_RISK_DATA);
var PREF_STORAGE_KEY = 'occPlatformPreferences.' + BUILTIN_DATA.meta.snapshotId;
var dataHistory = {current: cloneRiskData(BUILTIN_DATA), previous: null};
var DATA_META = dataHistory.current.meta;
var OVERALL_WORKPLACE_RATE = dataHistory.current.overallWorkplaceRate;
var MAJOR_INDUSTRIES = dataHistory.current.majorIndustries;
var DETAIL_INDUSTRIES = dataHistory.current.detailIndustries;
var ACCIDENT_STATS = dataHistory.current.accidentStats;
var COURT_CASES = dataHistory.current.courtCases;
var COURT_INBOX = dataHistory.current.courtInbox;
var REMOVED_COURT_JIDS = dataHistory.current.removedCourtJids;
var RATE_SCALE_MAX = Math.max(12,OVERALL_WORKPLACE_RATE,Math.max.apply(Math,MAJOR_INDUSTRIES.map(function(item){return item.includingTrafficRate;})));
var ALL_ACCIDENTS = '全部事故';
var JUDGMENT_URL = 'https://judgment.judicial.gov.tw/FJUD/default.aspx';

var colors = {
    low: "#2f8a5f",
    medium: "#a8790d",
    elevated: "#ef8a2f",
    high: "#d8443e"
};
var state = {
    accident: ALL_ACCIDENTS,
    showAllCases: false,
    salaryManuallyEdited: false,
    showAllAccidents: false
};
var elements = {
    form: document.getElementById("riskForm"),
    industryGroup: document.getElementById("industryGroup"),
    industry: document.getElementById("industry"),
    salary: document.getElementById("salary"),
    salaryReference: document.getElementById("salaryReference"),
    applySalaryReference: document.getElementById("applySalaryReference"),
    salaryError: document.getElementById("salaryError"),
    accidentButtons: document.getElementById("accidentButtons"),
    accidentHelp: document.getElementById("accidentHelp"),
    results: document.getElementById("results"),
    heroDescription: document.getElementById("heroDescription"),
    industryName: document.getElementById("industryName"),
    salaryTag: document.getElementById("salaryTag"),
    accidentTag: document.getElementById("accidentTag"),
    rateValue: document.getElementById("rateValue"),
    riskLevel: document.getElementById("riskLevel"),
    riskDial: document.getElementById("riskDial"),
    deathAmount: document.getElementById("deathAmount"),
    disabilityAmount: document.getElementById("disabilityAmount"),
    workAbilityAmount: document.getElementById("workAbilityAmount"),
    deathFormula: document.getElementById("deathFormula"),
    disabilityFormula: document.getElementById("disabilityFormula"),
    courtAmount: document.getElementById("courtAmount"),
    courtFormula: document.getElementById("courtFormula"),
    courtBadge: document.getElementById("courtBadge"),
    workplaceRateLabel: document.getElementById("workplaceRateLabel"),
    workplaceRateText: document.getElementById("workplaceRateText"),
    includingTrafficLabel: document.getElementById("includingTrafficLabel"),
    includingTrafficText: document.getElementById("includingTrafficText"),
    workplaceBar: document.getElementById("workplaceBar"),
    overallBar: document.getElementById("overallBar"),
    includingTrafficBar: document.getElementById("includingTrafficBar"),
    comparisonText: document.getElementById("comparisonText"),
    comparisonDot: document.getElementById("comparisonDot"),
    caseCount: document.getElementById("caseCount"),
    caseList: document.getElementById("caseList"),
    caseFooter: document.getElementById("caseFooter"),
    toggleCases: document.getElementById("toggleCases"),
    queryText: document.getElementById("queryText"),
    copyQuery: document.getElementById("copyQuery"),
    printButton: document.getElementById("printButton"),
    printMajorIndustry: document.getElementById("printMajorIndustry"),
    printDetailIndustry: document.getElementById("printDetailIndustry"),
    printSalary: document.getElementById("printSalary"),
    printAccident: document.getElementById("printAccident"),
    toast: document.getElementById("toast")
};
var moneyFormatter = (window.Intl && typeof window.Intl.NumberFormat === "function")
    ? new window.Intl.NumberFormat("zh-TW", { maximumFractionDigits: 0 })
    : {
        format: function (value) {
            var rounded = String(Math.round(Number(value) || 0));
            return rounded.replace(/\B(?=(\d{3})+(?!\d))/g, ",");
        }
    };
function formatMoney(value) {
    return moneyFormatter.format(Math.round(Number(value) || 0));
}
function formatRate(value) {
    return Number(value).toFixed(3);
}
function escapeHtml(value) {
    return String(value == null ? "" : value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
function readable(value, fallback) {
    if (fallback === void 0) { fallback = "未載明"; }
    var text = String(value == null ? "" : value).trim();
    return !text || ["未載明", "未認定", "未請求", "不適用"].indexOf(text) !== -1 ? fallback : text;
}
function quantile(sortedValues, q) {
    var position = (sortedValues.length - 1) * q;
    var base = Math.floor(position);
    var rest = position - base;
    var next = sortedValues[base + 1];
    return next === undefined ? sortedValues[base] : sortedValues[base] + rest * (next - sortedValues[base]);
}
var sortedRates = MAJOR_INDUSTRIES.map(function (item) { return item.workplaceRate; }).sort(function (a, b) { return a - b; });
var thresholds = {
    q1: quantile(sortedRates, 0.25),
    q2: quantile(sortedRates, 0.5),
    q3: quantile(sortedRates, 0.75)
};
function getRiskLevel(rate) {
    if (rate <= thresholds.q1)
        return { label: "低風險", color: colors.low, key: "low" };
    if (rate <= thresholds.q2)
        return { label: "中風險", color: colors.medium, key: "medium" };
    if (rate <= thresholds.q3)
        return { label: "中高風險", color: colors.elevated, key: "elevated" };
    return { label: "高風險", color: colors.high, key: "high" };
}
function getSelectedMajor() {
    return MAJOR_INDUSTRIES.find(function (item) { return item.name === elements.industryGroup.value; }) || MAJOR_INDUSTRIES[0];
}
function getDetailOptions(groupName) {
    return Array.isArray(DETAIL_INDUSTRIES[groupName]) ? DETAIL_INDUSTRIES[groupName] : [];
}
function getSelectedDetail() {
    var options = getDetailOptions(elements.industryGroup.value);
    return options.find(function (item) { return item.name === elements.industry.value; }) || options[0] || { name: elements.industryGroup.value, salary: 0 };
}
function populateMajorIndustries(preferred) {
    if (preferred === void 0) { preferred = "製造業"; }
    clearElement(elements.industryGroup);
    MAJOR_INDUSTRIES.forEach(function (item) {
        var option = document.createElement("option");
        option.value = item.name;
        option.textContent = item.name;
        option.selected = item.name === preferred;
        elements.industryGroup.appendChild(option);
    });
}
function populateDetailIndustries(preferred) {
    if (preferred === void 0) { preferred = ""; }
    var options = getDetailOptions(elements.industryGroup.value);
    clearElement(elements.industry);
    options.forEach(function (item) {
        var option = document.createElement("option");
        option.value = item.name;
        option.textContent = item.name;
        option.selected = item.name === preferred;
        elements.industry.appendChild(option);
    });
    if (options.length) {
        var preferredOption = options.find(function (item) { return item.name === preferred; });
        var metalOption = options.find(function (item) { return item.name === "金屬製品製造業"; });
        var defaultName = elements.industryGroup.value === "製造業"
            ? ((metalOption && metalOption.name) || options[0].name)
            : options[0].name;
        elements.industry.value = preferredOption ? preferredOption.name : defaultName;
    }
}
function applyReferenceSalary(force) {
    var reference = Number(getSelectedDetail().salary) || 0;
    elements.salaryReference.textContent = reference ? DATA_META.salaryPeriod + '產業平均：NT$ ' + formatMoney(reference) : '此產業暫無薪資參考值，請自行輸入';
    elements.applySalaryReference.disabled = !reference;
    if (force || !state.salaryManuallyEdited) elements.salary.value = reference ? String(reference) : '';
}

function getAccidentEntries(detailName) {
    var stats = ACCIDENT_STATS[detailName] || {};
    return Object.entries(stats)
        .map(function (_a) {
        var name = _a[0], count = _a[1];
        return ({ name: name, count: Number(count) || 0 });
    })
        .filter(function (item) { return item.count > 0; })
        .sort(function (a, b) { return b.count - a.count || a.name.localeCompare(b.name, "zh-Hant"); });
}
function renderAccidentButtons() {
    var detail = getSelectedDetail(), entries = getAccidentEntries(detail.name);
    var total = entries.reduce(function(sum,item){return sum+item.count;},0);
    var all = entries.slice();
    COURT_CASES.filter(function(item){return item.industry===detail.name;}).forEach(function(item){
        if(!all.some(function(row){return row.name===item.accident;})) {
            var stats = ACCIDENT_STATS[detail.name] || {};
            all.push({name:item.accident,count:Object.prototype.hasOwnProperty.call(stats,item.accident)?stats[item.accident]:null});
        }
    });
    if(state.accident!==ALL_ACCIDENTS&&!all.some(function(item){return item.name===state.accident;}))state.accident=ALL_ACCIDENTS;
    var visible=state.showAllAccidents?all:all.slice(0,7);
    if(state.accident!==ALL_ACCIDENTS&&!visible.some(function(item){return item.name===state.accident;})) {
        visible.push(all.find(function(item){return item.name===state.accident;}));
    }
    clearElement(elements.accidentButtons);
    [{name:ALL_ACCIDENTS,count:entries.length?total:null}].concat(visible).forEach(function(item){
        var button=document.createElement('button');button.type='button';button.className='accident-chip';
        button.dataset.accident=item.name;button.setAttribute('aria-pressed',String(state.accident===item.name));
        button.innerHTML='<span>'+escapeHtml(item.name)+'</span><span class="chip-count">'+(item.count===null?'未提供統計':formatMoney(item.count))+'</span>';
        elements.accidentButtons.appendChild(button);
    });
    if(all.length>7){var toggle=document.createElement('button');toggle.type='button';toggle.className='accident-chip toggle-accidents';toggle.dataset.toggleAccidents='true';toggle.textContent=state.showAllAccidents?'收合事故類型':'顯示全部 '+all.length+' 類';toggle.setAttribute('aria-expanded',String(state.showAllAccidents));elements.accidentButtons.appendChild(toggle);}
    elements.accidentHelp.textContent=entries.length ? DATA_META.accidentPeriod+'年共'+formatMoney(total)+'件；'+(state.showAllAccidents?'顯示全部可篩選類型':'先顯示件數較多的類型')+'。案件分類有值但無統計者另行標示，點選同步篩選案例。' : '此產業未提供正件數事故統計；法院案例仍可依產業及已收錄類型篩選，不能據此認定沒有風險。';
}

function validateSalary() {
    var salary = Number(elements.salary.value);
    if (!Number.isFinite(salary) || salary <= 0) {
        elements.salaryError.textContent = "請輸入大於0的平均月薪。";
        elements.salary.setAttribute("aria-invalid", "true");
        return null;
    }
    if (salary > 10000000) {
        elements.salaryError.textContent = "單月薪資上限請勿超過新臺幣1,000萬元。";
        elements.salary.setAttribute("aria-invalid", "true");
        return null;
    }
    elements.salaryError.textContent = "";
    elements.salary.removeAttribute("aria-invalid");
    return salary;
}
function median(values) {
    if (!values.length)
        return 0;
    var sorted = __spreadArray([], values, true).sort(function (a, b) { return a - b; });
    var middle = Math.floor(sorted.length / 2);
    return sorted.length % 2 ? sorted[middle] : Math.round((sorted[middle - 1] + sorted[middle]) / 2);
}
function filterCases(detailName) {
    return COURT_CASES.filter(function (item) {
        return item.industry === detailName &&
            (state.accident === ALL_ACCIDENTS || item.accident === state.accident);
    });
}
function renderCases(detail, cases) {
    clearElement(elements.caseList);
    elements.caseCount.textContent = "".concat(cases.length, "筆案例");
    elements.courtBadge.textContent = "".concat(cases.length, "筆收錄");
    elements.caseFooter.hidden = cases.length <= 5;
    elements.toggleCases.textContent = state.showAllCases ? "收合案例" : "顯示全部".concat(cases.length, "筆案例");
    if (!cases.length) {
        elements.courtAmount.textContent = "暫無相關法院判決案例";
        elements.courtAmount.classList.add("empty");
        elements.courtFormula.textContent = state.accident === ALL_ACCIDENTS
            ? "目前無符合產業與金額條件的收錄案例"
            : "目前無「".concat(state.accident, "」且金額明確的案例");
        var emptyState = document.createElement("div");
        emptyState.className = "no-cases";
        emptyState.innerHTML = "\n          <div>\n            <strong>暫無相關法院判決案例</strong>\n            <p>目前尚無同時符合「".concat(escapeHtml(detail.name), "」與「").concat(escapeHtml(state.accident), "」且目前資料記載明確金額的案例。此結果不代表實務上沒有相關爭議。</p>\n          </div>\n        ");
        elements.caseList.appendChild(emptyState);
        return;
    }
    var amounts = cases.map(function (item) { return Number(item.amount); }).filter(Number.isFinite);
    var min = Math.min.apply(Math, amounts);
    var max = Math.max.apply(Math, amounts);
    var medianAmount = median(amounts);
    var rangeText = min === max
        ? "NT$ ".concat(formatMoney(min))
        : "NT$ ".concat(formatMoney(min), "－").concat(formatMoney(max));
    elements.courtAmount.textContent = rangeText;
    elements.courtAmount.classList.remove("empty");
    elements.courtFormula.textContent = "".concat(cases.length, "筆收錄案例｜中位數 NT$ ").concat(formatMoney(medianAmount));
    var shownCases = state.showAllCases ? cases : cases.slice(0, 5);
    shownCases.forEach(function (item, index) {
        var diagnosis = readable(item.diagnosis, "傷勢資訊未載明");
        var reason = readable(item.reason, readable(item.accidentReason, "請以原裁判書內容為準"));
        var groupInsurance = readable(item.groupInsurance, "團險抵充未載明");
        var offsetNote = readable(item.offsetNote, "");
        var caseQuery = "".concat(item.court, " ").concat(item.year, "年度 ").concat(item.caseNo);
        var conditionalTags = [
            item.reviewStatus === "人工覆核" ? '<span>人工覆核紀錄</span>' : '<span class="review-pending">沿用原附件・未重核</span>',
            "<span class=\"tag-accent\">".concat(escapeHtml(item.accident), "</span>"),
            groupInsurance === "是" ? '<span>' + (item.reviewStatus==='人工覆核'?'團險抵充：已人工確認':'原資料團險註記：是（待核）') + '</span>' : "",
            groupInsurance === "否" ? '<span>' + (item.reviewStatus==='人工覆核'?'團險抵充：未准許':'原資料團險註記：否（待核）') + '</span>' : "",
            item.death === "是" ? '<span>死亡案件</span>' : "",
            item.permanentDisability === "是" ? '<span>永久失能</span>' : ""
        ].filter(Boolean).join("");
        var offsetHtml = offsetNote ? "<p class=\"case-offset-note\">抵充摘要：".concat(escapeHtml(offsetNote), "</p>") : "";
        var article = document.createElement("article");
        article.className = "case-card";
        article.innerHTML = "\n          <div class=\"case-card-main\">\n            <div class=\"case-title-row\">\n              <span class=\"case-index\">".concat(index + 1, "</span>\n              <div>\n                <h4>").concat(escapeHtml(item.accident), "｜").concat(escapeHtml(diagnosis), "</h4>\n                <div class=\"case-meta\">\n                  <span>").concat(escapeHtml(item.court), "</span>\n                  <span>").concat(escapeHtml(item.year), "年度 ").concat(escapeHtml(item.caseNo), "</span>\n                  <span>").concat(escapeHtml(item.level), "</span>\n                </div>\n              </div>\n            </div>\n            <p>").concat(escapeHtml(reason), "</p>\n            ").concat(offsetHtml, "\n            <div class=\"case-tags\">").concat(conditionalTags, "</div>\n          </div>\n          <div class=\"case-amount\">\n            <span>本件判決／剩餘應給付</span>\n            <strong>NT$ ").concat(formatMoney(item.amount), "</strong>\n            <div class=\"case-actions\">\n              <button class=\"case-link copy-case\" type=\"button\" data-query=\"").concat(escapeHtml(caseQuery), "\">複製案號</button>\n              <a class=\"case-link\" href=\"").concat(escapeHtml(item.sourceUrl || JUDGMENT_URL), "\" target=\"_blank\" rel=\"noopener noreferrer\">開啟查詢 ↗</a>\n            </div>\n          </div>\n        ");
        elements.caseList.appendChild(article);
    });
}
function render() {
    var salary = validateSalary();
    elements.results.hidden = false;
    elements.results.classList.toggle("salary-invalid", salary === null);
    if (salary === null) {
        return false;
    }
    elements.results.hidden = false;
    var major = getSelectedMajor();
    var detail = getSelectedDetail();
    var level = getRiskLevel(major.workplaceRate);
    var cases = filterCases(detail.name);
    elements.industryName.textContent = detail.name;
    elements.heroDescription.textContent = '職災率採「'+major.name+'」'+DATA_META.rateYear+'年資料；薪資、事故類型與案例依「'+detail.name+'」篩選。分級為產業間相對比較，供企業風險溝通參考。';
    elements.salaryTag.textContent = "試算月薪 NT$ ".concat(formatMoney(salary));
    elements.accidentTag.textContent = "事故類型：".concat(state.accident);
    elements.printMajorIndustry.textContent = major.name;
    elements.printDetailIndustry.textContent = detail.name;
    elements.printSalary.textContent = "NT$ ".concat(formatMoney(salary));
    elements.printAccident.textContent = state.accident;
    elements.rateValue.textContent = formatRate(major.workplaceRate);
    elements.riskLevel.textContent = level.label;
    elements.riskLevel.style.background = level.color;
    elements.riskDial.style.setProperty("--dial-color", level.color);
    elements.riskDial.style.setProperty("--dial-angle", "".concat(Math.min(major.workplaceRate / RATE_SCALE_MAX, 1) * 360, "deg"));
    elements.riskDial.setAttribute("aria-label", "".concat(major.name, "職場職災千人率").concat(formatRate(major.workplaceRate), "，相對分級").concat(level.label));
    elements.deathAmount.textContent = formatMoney(salary * 45);
    elements.disabilityAmount.textContent = formatMoney(salary * 60);
    elements.workAbilityAmount.textContent = formatMoney(salary * 40);
    elements.deathFormula.textContent = "".concat(formatMoney(salary), " × 45個月");
    elements.disabilityFormula.textContent = "".concat(formatMoney(salary), " × 60個月");
    elements.workplaceRateLabel.textContent = "".concat(major.name, "｜職場事故（不含交通）");
    elements.workplaceRateText.textContent = "".concat(formatRate(major.workplaceRate), "‰");
    elements.includingTrafficLabel.textContent = "".concat(major.name, "｜含交通事故參考值");
    elements.includingTrafficText.textContent = "".concat(formatRate(major.includingTrafficRate), "‰");
    elements.workplaceBar.style.width = "".concat(Math.min(major.workplaceRate / RATE_SCALE_MAX, 1) * 100, "%");
    elements.overallBar.style.width = "".concat(Math.min(OVERALL_WORKPLACE_RATE / RATE_SCALE_MAX, 1) * 100, "%");
    elements.includingTrafficBar.style.width = "".concat(Math.min(major.includingTrafficRate / RATE_SCALE_MAX, 1) * 100, "%");
    var difference = OVERALL_WORKPLACE_RATE > 0 ? ((major.workplaceRate-OVERALL_WORKPLACE_RATE)/OVERALL_WORKPLACE_RATE)*100 : null;
    elements.comparisonText.textContent = difference===null ? '全產業基準為0，無法計算相對百分比；請確認資料版本。' : major.name+'職場職災千人率較全產業平均'+(difference>=0?'高':'低')+'約'+Math.abs(difference).toFixed(1)+'%；含交通事故數值僅作補充參考，不納入分級。';
    elements.comparisonDot.style.background = level.color;
    elements.comparisonDot.style.boxShadow = "0 0 0 5px ".concat(level.color, "1f");
    var accidentEntries = getAccidentEntries(detail.name);
    var topAccident = accidentEntries.length ? accidentEntries[0].name : "職業災害";
    var queryAccident = state.accident === ALL_ACCIDENTS ? topAccident : state.accident;
    elements.queryText.textContent = "".concat(detail.name, " ").concat(queryAccident, " 職業災害 損害賠償 勞動基準法第59條");
    renderCases(detail, cases);
    elements.results.classList.remove("pulse");
    void elements.results.offsetWidth;
    elements.results.classList.add("pulse");
    try {
        localStorage.setItem(PREF_STORAGE_KEY, JSON.stringify({
            group: major.name,
            industry: detail.name,
            accident: state.accident
        }));
    }
    catch (_) { }
    return true;
}
function restorePreferences() {
    try {
        var stored_1 = JSON.parse(localStorage.getItem(PREF_STORAGE_KEY) || "null");
        if (!stored_1)
            return null;
        if (MAJOR_INDUSTRIES.some(function (item) { return item.name === stored_1.group; }))
            elements.industryGroup.value = stored_1.group;
        state.accident = typeof stored_1.accident === "string" ? stored_1.accident : ALL_ACCIDENTS;
        return stored_1;
    }
    catch (_) {
        return null;
    }
}
function showToast(message) {
    elements.toast.textContent = message;
    elements.toast.classList.add("show");
    window.clearTimeout(showToast.timer);
    showToast.timer = window.setTimeout(function () { return elements.toast.classList.remove("show"); }, 1900);
}
function legacyCopyText(text, successMessage) {
    var textarea = document.createElement("textarea");
    textarea.value = text;
    textarea.setAttribute("readonly", "");
    textarea.style.position = "fixed";
    textarea.style.left = "-9999px";
    textarea.style.top = "0";
    document.body.appendChild(textarea);
    textarea.focus();
    textarea.select();
    var success = false;
    try {
        success = document.execCommand("copy");
    }
    catch (_) {
        success = false;
    }
    if (textarea.parentNode)
        textarea.parentNode.removeChild(textarea);
    showToast(success ? successMessage : "無法自動複製，請手動選取文字");
}
function copyText(text, successMessage) {
    if (navigator.clipboard && typeof navigator.clipboard.writeText === "function") {
        navigator.clipboard.writeText(text).then(function () {
            showToast(successMessage);
        }).catch(function () {
            legacyCopyText(text, successMessage);
        });
        return;
    }
    legacyCopyText(text, successMessage);
}
populateMajorIndustries("製造業");
var stored = restorePreferences();
populateDetailIndustries(stored && stored.industry ? stored.industry : "金屬製品製造業");
applyReferenceSalary(!state.salaryManuallyEdited);
renderAccidentButtons();
render();
elements.industryGroup.addEventListener("change", function () {
    state.salaryManuallyEdited = false;
    state.accident = ALL_ACCIDENTS;
    state.showAllCases = false;
    state.showAllAccidents = false;
    populateDetailIndustries();
    applyReferenceSalary(true);
    renderAccidentButtons();
    render();
});
elements.industry.addEventListener("change", function () {
    state.salaryManuallyEdited = false;
    state.accident = ALL_ACCIDENTS;
    state.showAllCases = false;
    state.showAllAccidents = false;
    applyReferenceSalary(true);
    renderAccidentButtons();
    render();
});
elements.salary.addEventListener("input", function () {
    state.salaryManuallyEdited = true;
    render();
});
elements.applySalaryReference.addEventListener("click", function () {
    state.salaryManuallyEdited = false;
    applyReferenceSalary(true);
    render();
});
elements.accidentButtons.addEventListener("click", function (event) {
    if(event.target.closest("button[data-toggle-accidents]")){state.showAllAccidents=!state.showAllAccidents;renderAccidentButtons();return;}
    var button = event.target.closest("button[data-accident]");
    if (!button)
        return;
    state.accident = button.dataset.accident || ALL_ACCIDENTS;
    state.showAllCases = false;
    renderAccidentButtons();
    render();
});
elements.form.addEventListener("submit", function (event) {
    event.preventDefault();
    if (!render()) {
        elements.salary.focus();
        return;
    }
    if (window.matchMedia("(max-width: 850px)").matches) {
        try {
            document.querySelector(".result-hero").scrollIntoView({ behavior: "smooth", block: "start" });
        }
        catch (_) {
            document.querySelector(".result-hero").scrollIntoView(true);
        }
    }
});
elements.toggleCases.addEventListener("click", function () {
    state.showAllCases = !state.showAllCases;
    render();
    if (!state.showAllCases) {
        try {
            document.querySelector(".cases-section").scrollIntoView({ behavior: "smooth", block: "start" });
        }
        catch (_) {
            document.querySelector(".cases-section").scrollIntoView(true);
        }
    }
});
elements.caseList.addEventListener("click", function (event) {
    var button = event.target.closest(".copy-case");
    if (!button)
        return;
    copyText(button.dataset.query || "", "已複製法院與裁判字號");
});
elements.copyQuery.addEventListener("click", function () { return copyText(elements.queryText.textContent.trim(), "已複製司法院建議檢索字詞"); });
elements.printButton.addEventListener("click", function () {
    if (!render()) {
        elements.salary.focus();
        showToast("請先輸入有效月薪，再列印報告。");
        return;
    }
    window.print();
});
var originalDocumentTitle = document.title;
window.addEventListener("beforeprint", function () {
    render();
    document.title = "";
});
window.addEventListener("afterprint", function () {
    document.title = originalDocumentTitle;
});
function refreshDatasetLabels() {
    var dm = function (id) { return document.getElementById(id); };
    dm('industryHelp').textContent = '職災千人率依目前資料集' + MAJOR_INDUSTRIES.length + '個產業大類呈現；事故類型、薪資與法院案例再依細分產業篩選。';
    dm('dataBadge').textContent = DATA_META.rateYear + '年職災率｜' + DATA_META.accidentPeriod + '年事故類型｜' + COURT_CASES.length + '筆案例';
    dm('rateSourcePill').textContent = DATA_META.rateYear + '年資料';
    dm('accidentSourcePill').textContent = DATA_META.accidentPeriod + '年資料';
    dm('overallRateText').textContent = formatRate(OVERALL_WORKPLACE_RATE) + '‰';
    dm('salaryHelp').textContent = '參考' + DATA_META.salaryPeriod + '每人每月經常性薪資平均。暫以同一金額近似「平均工資」與「平均月投保薪資」，正式口徑可能不同。';
    dm('sourceRateTitle').textContent = DATA_META.rateYear + '年行業別職災千人率';
    dm('sourceRateNote').textContent = '數值依目前資料版本呈現；原始附件採113年職安署統計。顏色依現有產業大類四分位數計算，為相對分級。';
    dm('sourceSalaryNote').textContent = '目前薪資資料期間：' + DATA_META.salaryPeriod + '。原始資料沿用附件彙整值，可在上方自行輸入月薪。';
    dm('sourceAccidentNote').textContent = '目前事故資料期間：' + DATA_META.accidentPeriod + '。件數為資料集加總，未提供統計者不以0件推論沒有風險。';
    dm('sourceCasesNote').textContent = '目前收錄' + COURT_CASES.length + '筆案例。原附件86筆未逐案重新查證。' + (DATA_META.notes ? ' 版本備註：' + DATA_META.notes : '');
    var label = '資料版本：' + DATA_META.dataVersion + '｜職災率' + DATA_META.rateYear + '年｜薪資' + DATA_META.salaryPeriod + '｜事故' + DATA_META.accidentPeriod + '年。更新時間：' + (DATA_META.updatedAt || '未記錄') + '。';
    dm('dataFooter').textContent = label + ' 統計數值由網站維護，非即時更新。';
    dm('printDataVersion').textContent = label + ' 原附件案例未逐案覆核。';
}
refreshDatasetLabels();
document.getElementById('copyBasicQuery').addEventListener('click',function(){copyText('職業災害','已複製基本檢索字詞');});
document.getElementById('copyOffsetQuery').addEventListener('click',function(){copyText('職業災害 團體保險 抵充','已複製抵充檢索字詞');});

  }
})();
