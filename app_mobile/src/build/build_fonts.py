"""用 fonttools 產生 woff2 子集：可變字型→各粗細靜態字型→分成「常用字」與「其他」兩塊。不用 Node。"""
import json, os, sys, subprocess
from concurrent.futures import ProcessPoolExecutor
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools import subset
B=os.path.dirname(os.path.abspath(__file__)); F=os.path.join(B,'kitcopy/casecard/assets/fonts')
OUT=sys.argv[1]; os.makedirs(OUT,exist_ok=True)
allc=open(os.path.join(B,'charset.txt'),encoding='utf-8').read()
t=open(os.path.join(B,'charsets/zhangyong1979.txt'),encoding='utf-8').read().split('\n',1)[1]
jia={c for c in t if ord(c)>0x2E7F and not c.isspace()}
A=sorted({c for c in allc if ord(c)<0x2E80 or c in jia or 0x3000<=ord(c)<0x3040 or 0xFF00<=ord(c)<0xFFF0})
Bc=sorted(set(allc)-set(A))
JOBS=[('NotoSansTC-VF.ttf','sans',w) for w in (400,500,700,800,900)]+[('NotoSerifTC-VF.ttf','serif',w) for w in (500,700,900)]
def ranges(cs):
    cps=sorted(ord(c) for c in cs); out=[]; s=p=cps[0]
    for c in cps[1:]:
        if c==p+1: p=c; continue
        out.append((s,p)); s=p=c
    out.append((s,p)); return ','.join(f'U+{a:X}' if a==b else f'U+{a:X}-{b:X}' for a,b in out)
def job(j):
    src,name,w=j
    f=TTFont(os.path.join(F,src)); f=instancer.instantiateVariableFont(f,{"wght":w})
    cmap=set(f.getBestCmap())
    res=[]
    for part,cs in (('a',A),('b',Bc)):
        g=TTFont(); 
        o=subset.Options(); o.flavor='woff2'; o.layout_features=['*']; o.name_IDs=['*']
        ff=instancer.instantiateVariableFont(TTFont(os.path.join(F,src)),{"wght":w})
        s=subset.Subsetter(o); s.populate(unicodes=[ord(c) for c in cs]); s.subset(ff)
        fn=f'{name}{w}{part}.woff2'; ff.flavor='woff2'; ff.save(os.path.join(OUT,fn))
        res.append(fn)
    return name,w,res,sorted(c for c in allc if ord(c) in cmap)
if __name__=='__main__':
    with ProcessPoolExecutor(8) as ex: R=list(ex.map(job,JOBS))
    covered=set(allc)
    for _,_,_,cov in R: covered&=set(cov)
    meta={'faces':[{'family':'CardSans' if n=='sans' else 'CardTitle','weight':w,'files':fs} for n,w,fs,_ in R],
          'range_a':ranges(A),'range_b':ranges(Bc),'covered':''.join(sorted(covered))}
    json.dump(meta,open(os.path.join(OUT,'fonts.json'),'w',encoding='utf-8'),ensure_ascii=False)
    for n in ('BarlowCondensed-Bold','BarlowCondensed-ExtraBold'):
        subprocess.run(['pyftsubset',os.path.join(F,n+'.ttf'),'--unicodes=U+0020-007E','--flavor=woff2',"--layout-features=*",'--output-file='+os.path.join(OUT,n+'.woff2')],check=True)
    print(len(A),len(Bc),len(covered),'missing in some face:',''.join(sorted(set(allc)-covered))[:80])
