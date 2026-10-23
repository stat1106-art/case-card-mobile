"""把 casecard/assets/fonts 的字型裁成手機用的 woff2 子集（不改原檔）。

收字：教育部常用字（4808）＋次常用字（6343）＋全形標點、CJK 符號、注音＋英數與常用符號
＋案例、版型、畫面文字實際用到的字。字型裡本來就沒有的字不會出現（出圖前另做缺字檢查）。
用法：python tools/build_fonts.py → src/fonts/*.woff2、src/fonts/charset.txt
"""
import sys
from pathlib import Path
from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "casecard" / "assets" / "fonts"
OUT = ROOT / "src" / "fonts"
RANGES = [(0x20, 0x7E), (0xA0, 0xFF), (0x2010, 0x2027), (0x2030, 0x205E), (0x2190, 0x2199),
          (0x2212, 0x2212), (0x2260, 0x2265), (0x2500, 0x257F), (0x25A0, 0x25FF), (0x2605, 0x2606),
          (0x3000, 0x303F), (0x3105, 0x312F), (0xFE30, 0xFE4F), (0xFF01, 0xFF65), (0xFFE0, 0xFFE6)]
USED_FROM = ["casecard/engine/*.py", "casecard/skins/*.json", "cases/*.json", "docs/*.json",
             "reference/grok_v0.1_desktop/*", "verify_engine.py"]


def moe_chars():
    chars = set()
    for name in ("edu_standard_1.txt", "edu_standard_2.txt"):
        for line in (ROOT / "tools" / "charset" / name).read_text(encoding="utf-8").splitlines():
            if line and not line.startswith("#"):
                chars.add(line.split("\t")[0])
    return chars


def charset():
    chars = moe_chars()
    for a, b in RANGES:
        chars |= {chr(c) for c in range(a, b + 1)}
    for pattern in USED_FROM:
        for p in ROOT.glob(pattern):
            chars |= {c for c in p.read_text(encoding="utf-8") if ord(c) > 0x7F}
    return {c for c in chars if c.isprintable() or c == "　"}


def build(src: Path, dst: Path, chars):
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["*"]
    opts.name_IDs = ["*"]
    opts.name_languages = ["*"]
    opts.notdef_outline = True
    opts.drop_tables += ["DSIG"]
    font = subset.load_font(str(src), opts)
    sub = subset.Subsetter(opts)
    sub.populate(unicodes=[ord(c) for c in chars])
    sub.subset(font)
    subset.save_font(font, str(dst), opts)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    chars = charset()
    jobs = [("NotoSansTC-VF.ttf", chars), ("NotoSerifTC-VF.ttf", chars),
            ("BarlowCondensed-Bold.ttf", None), ("BarlowCondensed-ExtraBold.ttf", None)]
    for name, cs in jobs:
        src = SRC / name
        cmap = TTFont(src).getBestCmap()
        use = cs if cs is not None else {chr(c) for c in cmap}
        dst = OUT / (src.stem + ".woff2")
        build(src, dst, use)
        kept = TTFont(dst).getBestCmap()
        missing = sorted(c for c in moe_chars() if ord(c) not in cmap) if cs is not None else []
        print(f"{dst.name}: {dst.stat().st_size / 1e6:.2f} MB，{len(kept)} 字"
              + (f"；教育部表內字型本身沒有：{''.join(missing)}" if missing else ""))
    (OUT / "charset.txt").write_text("".join(sorted(chars)), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
