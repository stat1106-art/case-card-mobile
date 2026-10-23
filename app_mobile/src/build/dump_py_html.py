import sys,json,shutil,os
from pathlib import Path
K=Path('/workspace/case_card_v02/build/kitcopy'); sys.path.insert(0,str(K)); sys.path.insert(0,str(K/'casecard/engine'))
import verify_engine as V, render as R, skins
case=json.loads((K/'cases/shilin_110_laosu_72.json').read_text(encoding='utf-8'))
out=Path(sys.argv[1]); out.mkdir(exist_ok=True,parents=True)
root=K/'casecard'
jobs=[("classic",s["id"]) for s in skins.list_skins()]+[("light","original"),("standard","original")]
for t,s in jobs:
    c=V.build_card(case,t,s,True)
    wd=root/'_dump'/'case'; wd.mkdir(parents=True,exist_ok=True)
    hero=case['card'].get('hero') or {}
    for key,target in (("file",None),("photo","hero.png")):
        if hero.get(key): shutil.copyfile(K/'hero_library'/hero[key], wd/(target or hero[key]))
    c["_case_dir"]=os.path.relpath(wd,root)
    c["facts"]=[f if isinstance(f,dict) else {"text":f,"icon":"check"} for f in c.get("facts",[])]
    skin,_=skins.load(s); c["_skin_roles"]=skins.roles(skin)
    deco=skins.decorations(skin,c["_skin_roles"]) if t=="classic" else []
    dc=skins.decoration_css(deco); bb=skins.page_background(skin,c["_skin_roles"])
    c["_page_bg"]=f"{dc}, {bb}" if dc else bb
    html=R.TEMPLATES[t].build_html(c,root,True,lambda p:"REF:"+Path(p).name)
    (out/f"{t}_{s}.html").write_text(html,encoding='utf-8')
    json.dump({"checks":[list(x) for x in R.content_checks(c)],"contrast":skins.contrast_failures(c["_skin_roles"]),"deco":deco},open(out/f"{t}_{s}.meta.json","w"),ensure_ascii=False)
print(len(jobs))
