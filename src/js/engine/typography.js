// 字型層：標題用思源宋體、大金額用 Barlow Condensed 窄數字、內文思源黑體。照 casecard/engine/typography.py。
// fonts = { url(fileName) → 網址, format: "woff2" | "truetype", file(原檔名) → 實際檔名 }
export const EXPECTED_FAMILIES = ["Noto Sans TC", "Noto Serif TC", "Barlow Condensed"];
const NUMS = "unicode-range:U+0030-0039,U+002C,U+002E,U+0025;";

export function typoCss(fonts, titleSel, amountSel) {
  const face = (fam, file, w, extra = "") =>
    `@font-face{font-family:"${fam}";src:url("${fonts.url(file)}") format("${fonts.format}");font-weight:${w};font-display:block;${extra}}`;
  return "<style>"
    + face("CardTitle", "NotoSerifTC-VF.ttf", "100 900")
    + face("CardNum", "BarlowCondensed-Bold.ttf", "100 800", NUMS)
    + face("CardNum", "BarlowCondensed-ExtraBold.ttf", "801 900", NUMS)
    + titleSel + '{font-family:"CardTitle","CardSans",serif}'
    + amountSel + '{font-family:"CardNum","CardSans",sans-serif}'
    + "</style>";
}

export const sansFace = (fonts) =>
  `@font-face{font-family:"CardSans";src:url("${fonts.url("NotoSansTC-VF.ttf")}") format("${fonts.format}");font-weight:100 900;font-display:block;}`;
