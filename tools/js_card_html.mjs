// 用 JavaScript 版引擎產生圖卡 HTML（給 check_engine_parity.py 比對用）。
// 用法：node tools/js_card_html.mjs [--real] <案例檔> <draft 0|1> <template:skin> ...  → stdout 輸出 JSON {key: html}
// --real：字型改用 src/fonts 的 woff2、原版右上用示意圖 SVG（實際出圖用）；不加則用代號（和 Python 比對用）
import { readFileSync, readdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import { cardHtml } from "../src/js/engine/card.js";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const argv = process.argv.slice(2);
const real = argv[0] === "--real";
const [casePath, draftArg, ...jobs] = real ? argv.slice(1) : argv;
const fileUrl = (...p) => pathToFileURL(join(ROOT, ...p)).href;
const caseObj = JSON.parse(readFileSync(casePath, "utf8"));
const skinDir = join(ROOT, "casecard", "skins");
const skins = {};
for (const f of readdirSync(skinDir).filter((n) => /^skin_.*\.json$/.test(n))) {
  const s = JSON.parse(readFileSync(join(skinDir, f), "utf8"));
  skins[s.id] = s;
}
const hero = caseObj.card.hero || {};
const assets = {
  fonts: real
    ? { url: (name) => fileUrl("src", "fonts", name.replace(/\.ttf$/, ".woff2")), format: "woff2" }
    : { url: (name) => "@fonts/" + name, format: "truetype" },
  skins,
  heroSvg: hero.file ? readFileSync(join(ROOT, "hero_library", hero.file), "utf8") : "",
  heroUrl: real ? (hero.file ? fileUrl("hero_library", hero.file) : "") : "@hero.png",
  standardCss: readFileSync(join(ROOT, "casecard", "design", "standard.css"), "utf8"),
};
const out = {};
for (const job of jobs) {
  const [template, skin] = job.split(":");
  try {
    out[job] = cardHtml(caseObj, template, skin, draftArg === "1", assets).html;
  } catch (e) {
    out[job] = "ERROR: " + e.message;
  }
}
process.stdout.write(JSON.stringify(out));
