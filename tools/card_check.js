// 上架前檢查：用網站上的 platform/js/check.js（與發包人用的檢查頁同一份，不修改）在 Node 執行 CardCheck.validate。
// 用法：node tools/card_check.js <小卡資料.json ...>   全部「必須修正」0 項才回傳 0。
// check.js 是網頁程式，這裡提供它需要的網址解析（URL），其餘照原樣執行。
const fs = require('fs'), path = require('path'), vm = require('vm');
const CHECK = path.join(__dirname, '..', 'app_mobile', 'src', 'platform', 'js', 'check.js');
const ctx = { console, URL }; ctx.window = ctx; ctx.self = ctx; vm.createContext(ctx);
vm.runInContext(fs.readFileSync(CHECK, 'utf8'), ctx, { filename: 'check.js' });
let bad = 0;
for (const f of process.argv.slice(2)) {
  const r = ctx.CardCheck.validate(JSON.parse(fs.readFileSync(f, 'utf8')));
  console.log(`## ${path.basename(f)}：必須修正 ${r.errors.length} 項；提醒 ${r.warnings.length} 項；可上架＝${r.canPublish ? '是' : '否'}`);
  r.errors.forEach(e => console.log(`- 必須修正 ${e.code}：${e.message}`));
  r.warnings.forEach(e => console.log(`- 提醒 ${e.code || '—'}：${e.message}`));
  if (r.errors.length) bad++;
}
process.exit(bad ? 1 : 0);
