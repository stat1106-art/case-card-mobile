"""自動上架的總關卡（GitHub Actions 與本機都可跑）：任何一關沒過就回傳 1，不得部署。

用法：python app_mobile/src/build/ci_publish.py --out <網站輸出資料夾> --work <暫存資料夾>
關卡：
  1. 案例資料夾：index.json 與檔案一致、檔名、.md 有同名 .json、格式、示意圖（hero_type 14 類或網站上有的專屬圖）、
     自然人姓名遮蔽（小卡 parties、小卡全文、.md 全文）
  2. 打包（build.py 本身也擋測試假案例、<script>、沒遮的 .md、照片來源紀錄）
  3. 每案 check.js（tools/card_check.js）0 項必須修正
  4. 網站上每案 × 三個版型「檢查全部通過」、離線快取、無外部連線（tests_cloud/case_render_test.py）、平台四頁
  5. App 回歸測試：用凍結的士林案（ci/regression_cases）另外打包，跑原本整套測試（不受日後撤案影響）
"""
import argparse, json, os, re, shutil, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent            # app_mobile/src/build
SRC = HERE.parent                                 # app_mobile/src
REPO = SRC.parent.parent
CASES = REPO / "cases"
TESTS = HERE / "tests_cloud"
sys.path.insert(0, str(REPO / "tools"))
from mask_analysis_md import candidates  # noqa: E402

HERO_TYPES = {"overwork", "fall", "machine", "traffic", "chemical", "electric", "collapse", "commute",
              "construction", "heat", "disease", "healthcare", "stress", "neutral"}
NAME_OK = re.compile(r"[^○〇]{1,2}[○〇]{1,3}")
FILE_OK = re.compile(r"[a-z0-9]+(?:_[a-z0-9]+)*\.(json|md)")
results = []


def gate(name, ok, lines=()):
    results.append((name, ok))
    print(f"\n【{'通過' if ok else '沒過'}】{name}")
    for l in lines: print("  - " + l)
    sys.stdout.flush()
    return ok


def strings(v):
    if isinstance(v, str): yield v
    elif isinstance(v, dict):
        for x in v.values(): yield from strings(x)
    elif isinstance(v, list):
        for x in v: yield from strings(x)


def check_cases():
    probs = []
    try:
        index = json.loads((CASES / "index.json").read_text(encoding="utf-8"))["cases"]
        assert isinstance(index, list) and all(isinstance(x, str) for x in index)
    except Exception as e:
        return gate("案例資料夾", False, [f"cases/index.json 讀不出來或格式不對：{e}"])
    if len(set(index)) != len(index): probs.append("index.json 有重複的檔名")
    files = {p.name for p in CASES.iterdir() if p.is_file()} - {"index.json"}
    for f in sorted(files):
        if not FILE_OK.fullmatch(f): probs.append(f"檔名不合規則（只能小寫英文、數字、底線，.json 或 .md）：{f}")
        if re.search(r"(^|_)(test|fixture|sample)", f): probs.append(f"像測試資料的檔名不得上架：{f}")
    jsons = {f for f in files if f.endswith(".json")}
    for f in sorted(set(index) - jsons): probs.append(f"index.json 列了但檔案不存在：{f}")
    for f in sorted(jsons - set(index)): probs.append(f"案例檔沒有列進 index.json：{f}")
    for f in sorted(x for x in files if x.endswith(".md")):
        if f[:-3] + ".json" not in jsons: probs.append(f"{f} 沒有同名的案例 .json")
    hero_lib = REPO / "hero_library"
    for f in sorted(jsons & set(index)):
        try: d = json.loads((CASES / f).read_text(encoding="utf-8"))
        except Exception as e: probs.append(f"{f} 不是正確的 JSON：{e}"); continue
        if d.get("format") != "case-card-app-case" or not isinstance(d.get("source"), dict) or not isinstance(d.get("card"), dict):
            probs.append(f"{f}：format 要是 case-card-app-case，且要有 source 與 card"); continue
        hero = d["card"].get("hero") or {}
        if hero.get("image"):
            if not (hero_lib / hero["image"]).is_file(): probs.append(f"{f}：hero.image 指的圖 {hero['image']} 不在 hero_library/")
        elif hero.get("hero_type") not in HERO_TYPES:
            probs.append(f"{f}：hero.hero_type 要填 14 類之一（目前：{hero.get('hero_type')!r}）")
        for who in (d["card"].get("parties") or {}).values():
            if isinstance(who, dict) and who.get("natural_person") and not NAME_OK.fullmatch(str(who.get("name", ""))):
                probs.append(f"{f}：自然人姓名沒遮好：{who.get('name')!r}")
        left = sorted({n for s in strings(d) for n, _ in candidates(s)})
        if left: probs.append(f"{f}：小卡內文疑似有沒遮的自然人姓名：{'、'.join(left)}")
    for f in sorted(x for x in files if x.endswith(".md")):
        left = sorted({n for n, _ in candidates((CASES / f).read_text(encoding="utf-8"))})
        if left: probs.append(f"{f}：疑似有沒遮的自然人姓名：{'、'.join(left)}")
    return gate(f"案例資料夾（{len(index)} 案）", not probs, probs or [f"index.json 與檔案一致；{len(files)} 個檔案格式、示意圖、姓名遮蔽都符合"])


def run(cmd, name, ok_text=None):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    out = (r.stdout + r.stderr).strip().splitlines()
    ok = r.returncode == 0 and (ok_text is None or (out and out[-1].strip() == ok_text)) and not any(l.startswith("FAIL") for l in out)
    show = [l for l in out if l.startswith("FAIL") or "沒過" in l or "停止" in l] if not ok else out[-1:]
    return gate(name, ok, (show or out[-15:]) if not ok else show)


def serve_dir(work, name, site):
    d = work / name; d.mkdir(parents=True, exist_ok=True)
    link = d / "repo"
    if link.exists() or link.is_symlink(): link.unlink()
    link.symlink_to(site.resolve()); return d


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--out", required=True); ap.add_argument("--work", required=True)
    a = ap.parse_args(); out, work = Path(a.out).resolve(), Path(a.work).resolve()
    shutil.rmtree(out, ignore_errors=True); shutil.rmtree(work, ignore_errors=True); work.mkdir(parents=True)
    py = sys.executable
    if not check_cases(): return finish()
    if not run([py, str(HERE / "build.py"), str(out)], "打包（含測試假案例、<script>、.md 遮蔽、圖片來源紀錄攔截）"): return finish()
    index = json.loads((CASES / "index.json").read_text(encoding="utf-8"))["cases"]
    run(["node", str(REPO / "tools/card_check.js")] + [str(CASES / f) for f in index], f"check.js 每案 0 項必須修正（{len(index)} 案）")
    run(["node", str(TESTS / "m07_test.js"), str(REPO / "app_mobile/src/platform/js/check.js"), str(HERE / "ci/regression_cases/shilin_110_laosu_72.json")], "check.js 姓名遮蔽規則（李林○○、歐陽○○、王○○ 通過；王小明 擋）", "全部通過")
    run([py, "-I", str(TESTS / "mask_rules_test.py")], "姓名掃描規則（「原告曾帶…」等不算人名；王小明、李林雪嬌等仍抓得到）", "全部通過")
    sd = serve_dir(work, "serve_site", out)
    run([py, "-I", str(TESTS / "case_render_test.py"), str(sd)], "網站上每案 × 三個版型出圖檢查、離線快取、無外部連線", "全部通過")
    pv = re.search(r"VERSION\s*=\s*'([0-9.]+)'", (SRC / "platform/js/common.js").read_text(encoding="utf-8")).group(1)
    run([py, "-I", str(TESTS / "platform_test.py"), str(sd), pv], f"平台四頁（平台版本 {pv}）", "全部通過")
    # App 回歸測試：凍結的士林案另外打包（不部署）
    reg = work / "regression_site"
    if run([py, str(HERE / "build.py"), str(reg), "--cases", str(HERE / "ci/regression_cases")], "App 回歸測試用打包（凍結士林案，不部署）"):
        rd = serve_dir(work, "serve_reg", reg); shot = work / "reg_out"; shot.mkdir()
        ref = REPO / "reference/expected_png"; shilin = HERE / "ci/regression_cases/shilin_110_laosu_72.json"
        run([py, "-I", str(TESTS / "app_test.py"), str(rd), str(shot)], "App 整套（11 張出圖、離線、外部連線）", "全部通過")
        run([py, "-I", str(TESTS / "overlap_check.py"), str(shot), str(ref)], "右上圖不蓋住資訊列", "全部通過")
        adm = work / "admin_out"; adm.mkdir()
        run([py, "-I", str(TESTS / "admin_test.py"), str(rd), str(adm), str(shilin), str(ref)], "同仁端／管理端驗收", "全部通過")
        run([py, "-I", str(TESTS / "hash_test.py"), str(rd)], "#case= 預選")
    return finish()


def finish():
    bad = [n for n, ok in results if not ok]
    print("\n" + ("全部通過，可以部署" if not bad else f"有 {len(bad)} 關沒過，不部署：" + "、".join(bad)))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
