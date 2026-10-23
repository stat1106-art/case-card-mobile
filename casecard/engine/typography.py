"""v0.7.0 字型層：標題用思源宋體（明體），大金額用 Barlow Condensed 窄數字；內文仍是思源黑體。
三個版型共用這一份；各版型只給「哪些是標題、哪些是大金額」的選擇器。只換字型，不改字、不改字級。"""
FONT_FILES = {
    "Noto Sans TC": "NotoSansTC-VF.ttf",
    "Noto Serif TC": "NotoSerifTC-VF.ttf",
    "Barlow Condensed": ["BarlowCondensed-Bold.ttf", "BarlowCondensed-ExtraBold.ttf"],
}
EXPECTED_FAMILIES = tuple(FONT_FILES)  # F01：畫面上實際用到的字型只能是這三套隨包字型
_NUMS = "unicode-range:U+0030-0039,U+002C,U+002E,U+0025;"  # 只接管數字與 , . %，中文「元」仍走黑體

def css(ref, root, title_sel, amount_sel):
    f = lambda n: ref(root / "assets/fonts" / n)
    face = lambda fam, file, w, extra="": '@font-face{font-family:"%s";src:url("%s") format("truetype");font-weight:%s;font-display:block;%s}' % (fam, f(file), w, extra)
    return ("<style>"
            + face("CardTitle", "NotoSerifTC-VF.ttf", "100 900")
            + face("CardNum", "BarlowCondensed-Bold.ttf", "100 800", _NUMS)
            + face("CardNum", "BarlowCondensed-ExtraBold.ttf", "801 900", _NUMS)
            + title_sel + '{font-family:"CardTitle","CardSans",serif}'
            + amount_sel + '{font-family:"CardNum","CardSans",sans-serif}'
            + "</style>")
