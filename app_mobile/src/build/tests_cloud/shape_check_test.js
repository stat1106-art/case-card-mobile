// 0.6.0 多方當事人版、勞工敗訴（0 元）版的 check.js 規則測試。
// 用法：node shape_check_test.js <check.js> <多方範例.json> <敗訴範例.json>；全部符合預期印「全部通過」。
const fs = require('fs'), vm = require('vm');
const ctx = { URL, console }; vm.createContext(ctx);
vm.runInContext(fs.readFileSync(process.argv[2], 'utf8'), ctx, { filename: 'check.js' });
const multi = JSON.parse(fs.readFileSync(process.argv[3], 'utf8')), lost = JSON.parse(fs.readFileSync(process.argv[4], 'utf8'));
const codes = d => ctx.CardCheck.validate(d).errors.map(e => e.code);
const tweak = (base, f) => { const c = JSON.parse(JSON.stringify(base)); f(c.card); return c; };
const CASES = [
  ['多方範例可上架', multi, []],
  ['敗訴 0 元範例可上架', lost, []],
  ['各原告金額加總不等於合計 → 擋', tweak(multi, c => { c.result.total = '7,000,000 元'; }), ['M11']],
  ['第二位原告名字沒遮 → 擋', tweak(multi, c => { c.parties.plaintiffs[1].name = '徐小美'; }), ['M07']],
  ['第三位被告名字沒遮 → 擋', tweak(multi, c => { c.parties.defendants[2].name = '阿沙'; }), ['M07']],
  ['陣列寫成一對一 → 擋（請用一般版）', tweak(multi, c => { c.parties.plaintiffs = c.parties.plaintiffs.slice(0, 1); c.parties.defendants = c.parties.defendants.slice(0, 1); }), ['M11']],
  ['原告寫了 5 位 → 擋', tweak(multi, c => { while (c.parties.plaintiffs.length < 5) c.parties.plaintiffs.push(c.parties.plaintiffs[0]); }), ['M11']],
  ['敗訴版 0% 後金額不是 0 → 擋', tweak(lost, c => { c.result.flow.after_fault = '100 元'; }), ['M05']],
];
let bad = 0;
for (const [name, data, want] of CASES) {
  const got = codes(data);
  const ok = want.length ? want.every(w => got.includes(w)) : got.length === 0;
  bad += !ok; console.log((ok ? '通過 ' : 'FAIL ') + name + '：' + (got.length ? got.join('、') : '無必須修正'));
}
console.log(bad ? `有 ${bad} 項不符` : '全部通過');
process.exit(bad ? 1 : 0);
