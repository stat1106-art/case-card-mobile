// check.js M07（自然人姓名遮蔽）規則測試：開頭 1～2 個漢字＋至少兩個○ 才算已遮。
// 用法：node m07_test.js <check.js> <範本小卡資料.json>；全部符合預期印「全部通過」並回傳 0。
const fs = require('fs'), vm = require('vm');
const ctx = { URL, console }; vm.createContext(ctx);
vm.runInContext(fs.readFileSync(process.argv[2], 'utf8'), ctx, { filename: 'check.js' });
const base = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));
// [名字, 應該算已遮]
const CASES = [['李林○○', true], ['歐陽○○', true], ['王○○', true], ['王○○○', true],
  ['王小明', false], ['王○', false], ['歐陽小○○', false], ['〇○○', false], ['A○○', false]];
let bad = 0;
for (const [name, want] of CASES) {
  const c = JSON.parse(JSON.stringify(base));
  c.card.parties.plaintiff.name = name;
  const blocked = /M07/.test(JSON.stringify(ctx.CardCheck.validate(c)));
  const ok = !blocked === want; bad += !ok;
  console.log((ok ? '通過 ' : 'FAIL ') + name + '：' + (blocked ? '被擋（M07）' : '不擋') + (want ? '（應通過）' : '（應被擋）'));
}
console.log(bad ? `有 ${bad} 項不符` : '全部通過');
process.exit(bad ? 1 : 0);
