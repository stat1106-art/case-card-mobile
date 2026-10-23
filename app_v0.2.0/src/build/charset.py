import json,glob
K='/workspace/case_card_v02/src/case_card_app_kit/'
s=set()
for f in ['charsets/zhangyong1979.txt','charsets/cizhangyong1982.txt']:
    t=open(f,encoding='utf-8').read().split('\n',1)[1]
    s|={c for c in t if ord(c)>0x2E7F and not c.isspace()}
s|={chr(i) for i in range(0x20,0x7F)}
s|={chr(i) for i in range(0x3000,0x3040)}
s|={chr(i) for i in range(0xFF01,0xFF5F)}
s|=set('、。，．：；？！…—–‧·「」『』（）〈〉《》【】〔〕‘’“”○●□■△▲▽▼◎★☆※→←↑↓×÷±≤≥％℃')
for f in glob.glob(K+'cases/*.json')+glob.glob(K+'docs/*.json')+glob.glob(K+'casecard/engine/*.py')+glob.glob(K+'verify_engine.py'):
    s|={c for c in open(f,encoding='utf-8').read() if ord(c)>=0x20}
s.discard('\x7f')
open('charset.txt','w',encoding='utf-8').write(''.join(sorted(s)))
print(len(s))
