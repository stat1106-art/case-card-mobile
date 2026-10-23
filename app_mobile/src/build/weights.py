import glob,os
from playwright.sync_api import sync_playwright
F='/workspace/case_card_v02/build/kitcopy/casecard/assets/fonts/'
JS='''()=>{const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let n;const s={};
while((n=w.nextNode())){if(!n.textContent.trim())continue;const cs=getComputedStyle(n.parentElement);
const k=cs.fontFamily.split(',')[0]+'|'+cs.fontWeight+'|'+cs.fontStyle;s[k]=(s[k]||'')+n.textContent.trim();}
return Object.fromEntries(Object.entries(s).map(([k,v])=>[k,[...new Set(v)].join('')]));}'''
agg={}
with sync_playwright() as p:
  b=p.chromium.launch(); pg=b.new_page(viewport={'width':1080,'height':1620})
  for f in sorted(glob.glob('py_html/*.html')):
    h=open(f,encoding='utf-8').read().replace('REF:','file://'+F)
    tmp='/workspace/case_card_v02/build/tmp.html'; open(tmp,'w').write(h)
    pg.goto('file://'+tmp); r=pg.evaluate(JS)
    for k,v in r.items(): agg.setdefault(k,set()).update(v)
for k,v in sorted(agg.items()): print(k,len(v),''.join(sorted(v))[:40])
