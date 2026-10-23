// 共用小工具：照 Python 原始碼（casecard/engine）的行為寫，讓產生的 HTML 一字不差。

// html.escape(s, quote=True)
export function esc(s) {
  return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;").replace(/'/g, "&#x27;");
}

// Python str.replace(old, new)（全部取代；old 為空字串時在每個字之間插入）
export function pyReplace(s, oldStr, newStr) {
  if (oldStr === "") return newStr + Array.from(s).join(newStr) + newStr;
  return s.split(oldStr).join(newStr);
}

// 以字（code point）計算長度與切片，對應 Python 的 len／slice
export const chars = (s) => Array.from(s);
export const plen = (s) => chars(s).length;
export const pslice = (s, a, b) => chars(s).slice(a, b).join("");

// sorted(xs, key=len, reverse=True)（穩定排序）
export const byLenDesc = (xs) => [...xs].sort((a, b) => plen(b) - plen(a));

// E()：跳脫並把 keep_together 的詞包成不斷行；wrap 決定包法（classic／light 用 style，standard 用 class）
export function makeE(keep, wrap) {
  const words = byLenDesc(keep);
  return (s) => {
    let out = esc(s);
    for (const w of words) {
      const ew = esc(w);
      out = pyReplace(out, ew, wrap(ew));
    }
    return out;
  };
}

export const zip = (a, b) => a.slice(0, Math.min(a.length, b.length)).map((x, i) => [x, b[i]]);

export function maskName(name) {
  const cs = chars(name);
  if (cs.length <= 1) return name;
  if (cs.length === 2) return cs[0] + "○";
  return cs[0] + "○".repeat(cs.length - 2) + cs[cs.length - 1];
}

// Python 印 float 的寫法（整數值也帶 .0；負的零印成 -0.0）
export const pyFloat = (x) => (Object.is(x, -0) ? "-0.0" : Number.isInteger(x) ? x.toFixed(1) : String(x));

// round(x, 1)：Python 用四捨六入五成雙
export function pyRound1(x) {
  const s = x * 10, f = Math.floor(s), d = s - f;
  let n;
  if (d === 0.5) n = f % 2 === 0 ? f : f + 1;
  else n = Math.round(s);
  const v = n / 10;
  return v === 0 && x < 0 ? -0 : v;  // round(-0.04, 1) 在 Python 是 -0.0
}
