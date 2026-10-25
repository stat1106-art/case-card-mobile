"""案例分析 .md：自然人姓名遮成「姓＋○○」（例如「王○○」）。原告、被告、證人、家屬等都算；公司與機關名稱不遮。

用法：python tools/mask_analysis_md.py <檔案.md ...> [--check]
  不加 --check：直接改寫檔案，印出每一處（前後文）與總數，供維護人員逐檔人工檢查。
  加 --check：只檢查不改，還有沒遮的就回傳 1（build.py 打包時用同一套規則）。
找法：「稱謂（原告、被告、證人、配偶、父親、主管…）＋人名」，人名第一個字要是常見姓氏（避免把「原告主張」當成人名）；
找到的名字在全文其他地方也一併換掉。沒有稱謂在前面的人名（例如「王小明表示…」）抓不到，一定要人工看過。
"""
import re
import sys
from pathlib import Path

SURNAMES = ("陳林黃張李王吳劉蔡楊許鄭謝郭洪曾邱廖賴周徐蘇葉莊呂江何蕭羅高簡朱鍾施游詹沈彭胡余盧潘顏梁趙柯翁魏方孫戴范宋"
            "鄧杜傅侯曹薛丁卓阮馬董温唐藍石蔣古紀姚連歐程湯黃田康姜白汪鄒尤巫鐘黎涂龔嚴韓袁金童陸夏柳凃邵錢伍倪溫于譚駱熊任甘秦顧毛章史官萬俞雷粘饒張闕凌崔尹孔辛武辜陶段龍韋葛池孟褚殷麥賀賈莫文管關向包丘梅利華裴樊房全佘左花")
COMPOUND = ("歐陽", "司馬", "諸葛", "上官", "東方", "皇甫", "張簡", "范姜", "周黃", "徐辜", "張廖", "簡陳")
ROLES = ("被上訴人", "上訴人", "原告", "被告", "證人", "鑑定人", "訴訟代理人", "法定代理人", "代理人", "配偶", "妻子", "丈夫", "太太", "先生",
         "父親", "母親", "兒子", "女兒", "長子", "長女", "次子", "次女", "胞兄", "胞弟", "胞姊", "胞妹", "兄長", "家屬", "繼承人", "遺屬",
         "主管", "經理", "課長", "組長", "廠長", "店長", "同事", "員工", "勞工", "醫師", "負責人", "董事長", "雇主", "被害人", "死者")
# 稱謂後面若是這些字開頭，就不是人名（「原告主張」「被告公司」…）
NOT_NAME_START = set("主請於即係為因之與自等已未則應所等並及就對向在乃均仍亦皆再曾稱另各提起所提經無有不公機")
# 姓氏字開頭、但常見不是人名的詞（「被告陳述」「勞工向第三人」「主管簡報」…）：稱謂後面接到這些就不算人名
COMMON_WORDS = set("""陳述 陳稱 陳報 陳明 陳情 向第 向肇 向法 向雇 向公 向勞 向被 向原 向保 向他 向其 向對 向主 向該 向本 向漁 向醫
簡報 簡易 簡單 高處 高度 高額 高於 高雄 高壓 高溫 高齡 金額 金錢 程序 程度 任何 任職 任意 連帶 連續 連同 方式 方面 方法 方可
周知 周延 全部 全額 全體 全數 何時 何種 何者 何人 曾經 曾於 施工 施行 康復 管理 管制 尤其 馬上 文書 文件 包括 夏季 葉片 石材
范圍 黃金 白天 江湖 林地 林業 余額 史實 孔洞 武器 宋體 時間 時候 莫非 段落 龍頭 韋籬 洪水 游泳 邱陵 毛額 章程 史料""".split())
NAME_TAIL = set("主表到於未亦的之等說稱與及曾已則因在向對就並也均仍乃即係為請提經無有不受遭自將被由")
ORG_END = re.compile(r"(公司|股份|有限|企業|行號|工廠|機關|政府|局|署|處|部|會|院|所|校|學|銀行|協會|基金|醫院|診所|社|團|廠)$")
NAME = r"(?:%s|[%s])[一-龥]{1,2}" % ("|".join(COMPOUND), SURNAMES)
PAT = re.compile(r"(?P<role>%s)[ 　：:、，,（(]*(?P<name>%s)" % ("|".join(sorted(ROLES, key=len, reverse=True)), NAME))


def candidates(text):
    """回傳 [(全名, 位置)]：稱謂後面接的、看起來像自然人姓名、還沒遮的。"""
    out = []
    for m in PAT.finditer(text):
        name = m.group("name")
        sur = next((c for c in COMPOUND if name.startswith(c)), name[0])
        rest = name[len(sur):]
        if not rest or rest[0] in NOT_NAME_START or "○" in name or "〇" in name or ORG_END.search(name) or name[:2] in COMMON_WORDS:
            continue
        # 兩字名後面緊接動詞時會多抓一字（「原告王明主張」抓成「王明主」）：最後一字是常見的接續字就去掉
        if len(rest) == 2 and rest[1] in NAME_TAIL:
            name = sur + rest[0]
        # 名字後面緊接公司／機關字樣（例如「被告王大公司」）就不是自然人
        tail = text[m.end("name"):m.end("name") + 4]
        if re.match(r"(股份|有限|公司|企業|工廠|醫院|機關)", tail):
            continue
        out.append((name, m.start("name")))
    return out


def masked(name):
    sur = next((c for c in COMPOUND if name.startswith(c)), name[0])
    return sur + "○○"


def mask_text(text):
    """遮蔽並回傳（新文字, [(全名, 遮後, 次數)]）"""
    names = sorted({n for n, _ in candidates(text)}, key=len, reverse=True)
    report = []
    for n in names:
        k = text.count(n)
        if k:
            text = text.replace(n, masked(n)); report.append((n, masked(n), k))
    return text, report


def main():
    files = [Path(a) for a in sys.argv[1:] if not a.startswith("--")]
    check = "--check" in sys.argv
    total, bad = 0, 0
    for f in files:
        text = f.read_text(encoding="utf-8")
        if check:
            left = candidates(text)
            for n, pos in left:
                print(f"沒遮：{f.name}「…{text[max(0, pos - 12):pos + 12]}…」")
            bad += len(left); continue
        new, rep = mask_text(text)
        n = sum(k for _, _, k in rep); total += n
        print(f"## {f.name}：遮蔽 {n} 處")
        for full, m, k in rep:
            print(f"- {full} → {m}（{k} 處）")
        if rep: f.write_text(new, encoding="utf-8")
        for line_no, line in enumerate(new.splitlines(), 1):
            if "○○" in line: print(f"  {line_no}: {line.strip()[:80]}")
    if check:
        print("全部已遮" if not bad else f"還有 {bad} 處沒遮"); sys.exit(1 if bad else 0)
    print(f"\n.md 已遮蔽自然人姓名，共 {total} 處（工具只抓得到「稱謂＋人名」；請逐檔人工確認沒有遺漏）")


if __name__ == "__main__":
    main()
