"""正式上架：把 GPT 02 的回覆（可能一次好幾案）轉成 cases/ 裡的案例檔。

用法：python tools/ingest_gpt_replies.py <回覆文字檔 ...> [--cases cases] [--dry-run]
做的事：
  1. 抽出所有 format 為 case-card-app-case 的資料（前後說明文字、```json 圍欄、「情境圖：」那一行都略過）。
  2. 自然人姓名遮成「姓＋○○」（複姓留兩字），案例裡其他地方出現的全名也一併換掉。
  3. 用電腦版出圖程式的內容檢查（C01 必要欄位、C02 加總、C03 來源卡、C04 過失相抵）＋判決來源欄位檢查完整性；不完整的不上。
  4. hero_type：有填且在 14 類就用；沒填就依關鍵字「建議」一類並在報告標明，由維護人員確認。
  5. 回覆裡寫「本案不適合現有版型」的段落列進報告（這種段落本來就不會有小卡資料）。
  6. 寫進 cases/<法院代碼>_<年度>_<字別>_<號>.json、更新 index.json；同一案（同 jid）已存在就略過並報告。
最後印出上架報告（新增哪幾案、各配哪張示意圖、哪些沒上與原因）。打包時 build.py 會再檢查一次姓名有沒有遮好。
"""
import copy
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "casecard" / "engine"))
sys.path.insert(0, str(ROOT))
import render as engine  # noqa: E402
from verify_engine import build_card  # noqa: E402

HERO_TYPES = {
    "overwork": ("過勞", ["過勞", "加班", "工時", "腦中風", "心肌梗塞", "猝死", "腦出血", "腦梗塞"]),
    "fall": ("高處墜落", ["墜落", "高處", "鷹架", "屋頂", "樓梯", "跌落", "梯子"]),
    "machine": ("機械捲夾", ["捲入", "夾傷", "捲夾", "機械", "機台", "沖床", "輸送帶", "滾輪"]),
    "traffic": ("交通", ["車禍", "交通事故", "機車", "汽車", "貨車", "撞擊", "外送"]),
    "chemical": ("化學", ["化學", "中毒", "溶劑", "有機溶劑", "氣體", "灼傷"]),
    "electric": ("感電", ["感電", "觸電", "電擊", "高壓電"]),
    "collapse": ("物體倒塌", ["倒塌", "崩塌", "掉落物", "物體飛落", "貨架", "壓傷"]),
    "commute": ("通勤", ["通勤", "上下班途中", "上班途中", "下班途中"]),
    "construction": ("營造", ["工地", "營造", "施工", "工程"]),
    "heat": ("熱危害", ["中暑", "熱衰竭", "高溫", "熱危害"]),
    "disease": ("職業病", ["職業病", "塵肺", "聽力損失", "肌肉骨骼", "癌"]),
    "healthcare": ("醫療照護", ["醫院", "護理", "照護", "看護", "醫師"]),
    "stress": ("職場壓力", ["霸凌", "壓力", "憂鬱", "精神", "創傷後"]),
    "neutral": ("其他／中性", []),
}
COMPOUND_SURNAMES = ["歐陽", "司馬", "諸葛", "上官", "東方", "皇甫", "張簡", "范姜", "周黃", "徐辜", "張廖", "簡陳"]
CASE_WORDS = {"勞訴": "laosu", "勞上": "laoshang", "勞上易": "laoshangyi", "勞簡": "laojian", "勞小": "laoxiao",
              "重勞訴": "zhonglaosu", "勞再": "laozai", "勞抗": "laokang", "勞簡上": "laojianshang", "勞訴更": "laosugeng"}
NOT_SUITABLE = "本案不適合現有版型"


def extract_cases(text):
    """和 App 的 extractCases() 同一套做法。"""
    found, i = [], text.find("{")
    def walk(v):
        if isinstance(v, list):
            for x in v: walk(x)
        elif isinstance(v, dict):
            if v.get("format") == "case-card-app-case": found.append(v)
            else:
                for x in v.values(): walk(x)
    while i != -1:
        depth, in_str, bs, end = 0, False, False, -1
        for j in range(i, len(text)):
            ch = text[j]
            if in_str:
                if bs: bs = False
                elif ch == "\\": bs = True
                elif ch == '"': in_str = False
                continue
            if ch == '"': in_str = True
            elif ch == "{": depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0: end = j; break
        parsed = None
        if end != -1:
            try: parsed = json.loads(text[i:end + 1])
            except ValueError: parsed = None
        if parsed is not None:
            walk(parsed); i = text.find("{", end + 1)
        else:
            i = text.find("{", i + 1)
    return found


def mask(name):
    name = str(name)
    if re.fullmatch(r"[^○〇]{1,2}[○〇]{1,3}", name): return name
    sur = next((s for s in COMPOUND_SURNAMES if name.startswith(s) and len(name) > len(s)), name[:1])
    return sur + "○○"


def name_changes(case):
    """這一案當事人裡的自然人：[(全名, 遮後)]"""
    out = []
    for who in (case.get("card", {}).get("parties") or {}).values():
        if isinstance(who, dict) and who.get("natural_person") and who.get("name"):
            m = mask(who["name"])
            if m != who["name"]: out.append((who["name"], m))
    return out


def mask_case(case, batch_changes):
    """把這一批所有案子遮掉的全名，在這一案全文裡都換成「姓＋○○」（一案的當事人可能出現在另一案的事實裡）。"""
    text = json.dumps(case, ensure_ascii=False)
    for full, m in sorted(batch_changes, key=lambda x: -len(x[0])):
        text = text.replace(full, m)
    case = json.loads(text)
    case.setdefault("card", {}).setdefault("display", {})["mask_natural_person_name"] = True
    return case


def suggest_type(case):
    """依關鍵字建議事故類型：標題、標籤裡的字算 3 分，內文算 1 分（只是建議，維護人員要確認）。"""
    c = case.get("card", {})
    head = json.dumps([case.get("title"), c.get("tags"), c.get("title")], ensure_ascii=False)
    body = json.dumps([c.get("subtitle"), c.get("facts"), c.get("basics"), (c.get("info") or {}).get("cause")], ensure_ascii=False)
    best, best_score, hits = "neutral", 0, []
    for t, (_, words) in HERO_TYPES.items():
        score = sum(3 for w in words if w in head) + sum(1 for w in words if w in body)
        if score > best_score: best, best_score, hits = t, score, [w for w in words if w in head or w in body]
    return best, hits


def check(case):
    """完整性：判決來源欄位＋電腦版的內容檢查（C01–C04）。回傳不通過的原因（空＝通過）。"""
    probs = []
    src = case.get("source") or {}
    for k in ("court", "case_number", "decision_date", "jid"):
        if not str(src.get(k) or "").strip(): probs.append(f"判決來源缺 {k}")
    if probs: return probs
    try:
        card = build_card(copy.deepcopy(case), "classic", "original", True)
    except Exception as e:  # 日期格式等
        return [f"判決來源格式不對：{e}"]
    card["facts"] = [f if isinstance(f, dict) else {"text": f, "icon": "check"} for f in card.get("facts", [])]
    for cid, ok, detail in engine.content_checks(card):
        if not ok: probs.append(f"{cid}：{detail}")
    return probs


def file_name(src):
    code, year, word, no = (src["jid"].split(",") + ["", "", "", ""])[:4]
    w = CASE_WORDS.get(word) or "case"
    return f"{code.lower()}_{year}_{w}_{no}.json"


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    md_files = [a for a in args if a.lower().endswith(".md")]
    args = [a for a in args if a not in md_files]
    dry = "--dry-run" in sys.argv
    cases_dir = Path(sys.argv[sys.argv.index("--cases") + 1]) if "--cases" in sys.argv else ROOT / "cases"
    if "--cases" in sys.argv: args.remove(str(cases_dir))
    idx_path = cases_dir / "index.json"
    index = json.loads(idx_path.read_text(encoding="utf-8"))["cases"] if idx_path.exists() else []
    existing = {}
    for f in index:
        try: existing[json.loads((cases_dir / f).read_text(encoding="utf-8"))["source"]["jid"]] = f
        except Exception: pass
    added, skipped, notes, batch = [], [], [], []
    for path in args:
        text = Path(path).read_text(encoding="utf-8")
        for m in re.finditer(NOT_SUITABLE, text):
            notes.append(f"{Path(path).name}：「…{text[max(0, m.start() - 60):m.end() + 60].strip()}…」")
        found = extract_cases(text)
        if not found and NOT_SUITABLE not in text:
            skipped.append((Path(path).name, "整段回覆裡沒有小卡資料"))
        batch += found
    batch_changes = sorted({c for case in batch for c in name_changes(case)})
    for case in batch:
        label = f'{(case.get("source") or {}).get("case_number", "？")}（{case.get("title", "")}）'
        probs = check(case)
        if probs: skipped.append((label, "資料不完整：" + "；".join(probs))); continue
        jid = case["source"]["jid"]
        if jid in existing: skipped.append((label, f"已上架（{existing[jid]}），這次略過")); continue
        changes = name_changes(case)
        case = mask_case(case, batch_changes)
        hero = case["card"].setdefault("hero", {})
        given = hero.get("hero_type")
        if given in HERO_TYPES: how = "GPT 已填"
        else:
            t, hits = suggest_type(case); hero["hero_type"] = t
            how = f"建議（關鍵字：{'、'.join(hits) or '無，暫用中性'}）{'，原本寫的「' + str(given) + '」不在 14 類' if given else ''}"
        hero.setdefault("file", "overwork_night_desk.svg"); hero.setdefault("caption", "示意圖")
        name = file_name(case["source"])
        if not dry:
            (cases_dir / name).write_text(json.dumps(case, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        existing[jid] = name; index.append(name)
        t = hero["hero_type"]
        added.append((name, label, f"{t}（{HERO_TYPES[t][0]}）", how, "、".join(f"{a}→{b}" for a, b in changes) or "無自然人或已遮好"))
    # 案例分析 .md：自然人姓名遮成「王○○」後放進 cases/（檔名要和案例檔同名，例如 tpdv_112_laosu_15.md）
    sys.path.insert(0, str(ROOT / "tools"))
    from mask_analysis_md import mask_text, candidates as md_left
    md_done, md_total = [], 0
    for path in md_files:
        src = Path(path); text = src.read_text(encoding="utf-8")
        for full, m in batch_changes: text = text.replace(full, m)          # 同一批小卡資料裡遮掉的全名
        text, rep = mask_text(text)
        n = sum(k for _, _, k in rep) + sum(src.read_text(encoding="utf-8").count(f) for f, _ in batch_changes)
        md_total += n
        stem = src.stem
        if not (cases_dir / f"{stem}.json").exists() and f"{stem}.json" not in index:
            skipped.append((src.name, "找不到同名的案例檔（.md 檔名要和案例檔一樣），沒有放")); continue
        if md_left(text): skipped.append((src.name, "遮蔽後仍有疑似姓名，請人工處理")); continue
        if not dry: (cases_dir / src.name).write_text(text, encoding="utf-8")
        md_done.append((src.name, n, rep))
    if added and not dry:
        idx_path.write_text(json.dumps({"cases": sorted(set(index))}, ensure_ascii=False) + "\n", encoding="utf-8")
    print("# 上架報告" + ("（試跑，沒有寫檔）" if dry else ""))
    print(f"\n## 新增 {len(added)} 案")
    for name, label, t, how, ch in added:
        print(f"- {label}\n  - 檔名：{name}\n  - 示意圖：{t}，{how}\n  - 姓名遮蔽：{ch}")
    if added:
        print("\n> 當事人以外的人名（證人、主管、醫師等）工具抓不到，上架前請人工看過每一案的事實與見解。")
    if md_done:
        print(f"\n## 案例分析 .md {len(md_done)} 份")
        for name, n, rep in md_done:
            print(f"- {name}：遮蔽 {n} 處" + ("（" + "、".join(f"{a}→{b}×{k}" for a, b, k in rep) + "）" if rep else ""))
        print(f"\n.md 已遮蔽自然人姓名，共 {md_total} 處（工具只抓得到「稱謂＋人名」與同批小卡的當事人；回報前要逐檔人工確認沒有遺漏）")
    print(f"\n## 沒上 {len(skipped)} 項")
    for label, why in skipped: print(f"- {label}：{why}")
    if notes:
        print(f"\n## 回覆裡寫「{NOT_SUITABLE}」的段落 {len(notes)} 處（沒有產生小卡資料）")
        for n in notes: print(f"- {n}")


if __name__ == "__main__":
    main()
