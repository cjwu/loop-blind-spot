import sys,os; sys.path.insert(0,'/Users/cjw/@RESAECH/RTL-Code/analysis'); import recover as R
from collections import Counter
wb,rec=R.load(); lab=R.taxonomy(); MODS=[m for m,_,_ in R.MOD]
ext={}
for t in os.listdir(R.ROOT):
    tp=os.path.join(R.ROOT,t)
    if not os.path.isdir(tp): continue
    for d in os.listdir(tp):
        dp=os.path.join(tp,d)
        if not os.path.isdir(dp): continue
        for p in os.listdir(dp):
            pp=os.path.join(dp,p)
            if os.path.isdir(pp): ext[R.norm(p)]='sv' if any(f.endswith('.sv') for f in os.listdir(pp)) else 'v'
svseq=lambda e: e['key'] in lab and lab[e['key']][0]=='sequential logic' and ext.get(e['key'])=='sv'
keep=[e for e in rec if not svseq(e)]
print("== solve curve: all 220 vs excl .sv-seq (174) ==")
for m in MODS:
    a=[100*sum(1 for e in rec if e[m]['pass'] and e[m]['iters'] is not None and e[m]['iters']<=k)/len(rec) for k in (0,1,5,15,25)]
    b=[100*sum(1 for e in keep if e[m]['pass'] and e[m]['iters'] is not None and e[m]['iters']<=k)/len(keep) for k in (0,1,5,15,25)]
    print(f"{m:8s} all  k0/1/5/15/25 = "+' / '.join(f"{x:.1f}" for x in a)+f"   gain k5→25 = {a[4]-a[2]:.1f}")
    print(f"{'':8s} excl k0/1/5/15/25 = "+' / '.join(f"{x:.1f}" for x in b)+f"   gain k5→25 = {b[4]-b[2]:.1f}")
print("\n== .sv sequential problems (46) by difficulty ==", Counter(lab[e['key']][1] for e in rec if svseq(e)))
print("== .v  sequential problems (55) by difficulty ==", Counter(lab[e['key']][1] for e in rec if e['key'] in lab and lab[e['key']][0]=='sequential logic' and ext.get(e['key'])=='v'))
# unsolved-by-all on .v only
for c in ('combinatial logic','sequential logic','building larger circuits'):
    ps=[e for e in keep if e['key'] in lab and lab[e['key']][0]==c]
    n=sum(1 for e in ps if not any(e[m]['pass'] for m in MODS))
    print(f"unsolved by all four, .v only: {c:26s} {n}/{len(ps)}")
