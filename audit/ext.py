import sys,os; sys.path.insert(0,'/Users/cjw/@RESAECH/RTL-Code/analysis'); import recover as R
from collections import Counter, defaultdict
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
            if os.path.isdir(pp):
                fs=os.listdir(pp); ext[R.norm(p)]='sv' if any(f.endswith('.sv') for f in fs) else ('v' if any(f.endswith('.v') for f in fs) else 'none')
def o(e,m):
    it=e[m]['iters']
    if it is None: return None
    if e[m]['pass'] and it==0: return 'z'
    return 'r' if e[m]['pass'] else 'n'
print("== class x testbench extension (pairs) ==")
T=defaultdict(lambda:[0,0,0,0])
for e in rec:
    if e['key'] not in lab: continue
    g=(lab[e['key']][0],ext.get(e['key'],'?')); T[g][0]+=1
    for m in MODS:
        x=o(e,m)
        if x=='z': T[g][1]+=1
        elif x in('r','n'): T[g][2]+=1; T[g][3]+=(x=='r')
for g,(n,z,f,r) in sorted(T.items()):
    print(f"{g[0]:26s} .{g[1]:4s} problems={n:3d} zero-shot={z:3d} ({100*z/(z+f):.0f}%) first-fail={f:3d} recovered={r:3d} efficacy={100*r/f if f else float('nan'):.1f}%  never={f-r}")
print("\n== .sv problems that were ever passed (any model) ==")
for e in rec:
    if e['key'] in lab and ext.get(e['key'])=='sv':
        os_=[o(e,m) for m in MODS]
        if any(x in('z','r') for x in os_): print(f"  {e['name']:24s} {lab[e['key']][0][:4]} {''.join(x or '-' for x in os_)}")
print("\n== .v sequential problems never recovered by any model ==")
for e in rec:
    if e['key'] in lab and ext.get(e['key'])=='v' and lab[e['key']][0]=='sequential logic':
        os_=[o(e,m) for m in MODS]
        if all(x=='n' for x in os_ if x): print(f"  {e['name']:24s} {''.join(x or '-' for x in os_)}")
print("\n== pooled repair efficacy restricted to .v testbenches ==")
for c in ('combinatial logic','sequential logic','building larger circuits'):
    n,z,f,r=T[(c,'v')]; print(f"  {c:26s} {r}/{f} = {100*r/f if f else 0:.1f}%")
