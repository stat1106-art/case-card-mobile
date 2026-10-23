import json,glob,os,difflib
from playwright.sync_api import sync_playwright
K='/workspace/case_card_v02/src2/case_card_app_kit/'
case=json.load(open(K+'cases/shilin_110_laosu_72.json',encoding='utf-8'))
skins={json.load(open(f,encoding='utf-8'))['id']:json.load(open(f,encoding='utf-8')) for f in glob.glob(K+'casecard/skins/*.json')}
A={'heroSvg':open(K+'hero_library/'+case['card']['hero']['file'],encoding='utf-8').read(),'standardCss':open(K+'casecard/design/standard.css',encoding='utf-8').read(),'heroPhotoUrl':'REF:hero.png'}
jobs=[('classic',s) for s in sorted(skins, key=lambda s:(s!='original',s))]+[('light','original'),('standard','original')]
with sync_playwright() as p:
  b=p.chromium.launch(); pg=b.new_page(); pg.set_content('<html></html>')
  pg.add_script_tag(path='/workspace/case_card_v02/app_src/js/engine.js')
  bad=0
  for t,s in jobs:
    r=pg.evaluate('([k,t,s,sk,A])=>{const o=CardEngine.prepare(k,t,s,true,sk,A,n=>"REF:"+n);return {html:o.html,checks:o.checks,deco:o.deco}}',[case,t,s,skins,A])
    py=open(f'py_html/{t}_{s}.html',encoding='utf-8').read()
    meta=json.load(open(f'py_html/{t}_{s}.meta.json',encoding='utf-8'))
    same=r['html']==py
    pc=[[x[0],x[1],x[2]] for x in meta['checks']]
    jc=[[x[0],x[1],x[2]] for x in r['checks'][:len(pc)]]
    print(t,s,'HTML一致' if same else 'HTML不同', '內容檢查一致' if pc==jc else ('內容檢查不同',pc,jc))
    if not same:
      bad+=1
      for l in list(difflib.unified_diff(py.splitlines(),r['html'].splitlines(),lineterm='',n=0))[:6]: print('   ',l[:300])
  b.close()
