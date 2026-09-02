"""Core table for §4: outcomes split by testbench file type. Testbench type is looked up by
exact directory name first (fixes the edge_detect / Edgedetect collision), then by norm()."""
import sys,os; sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')); import recover as R
from collections import Counter, defaultdict
wb,rec=R.load(); lab=R.taxonomy(); MODS=[m for m,_,_ in R.MOD]
exact,bynorm={},{}
for t in os.listdir(R.ROOT):
    tp=os.path.join(R.ROOT,t)
    if not os.path.isdir(tp): continue
    for d in os.listdir(tp):
        dp=os.path.join(tp,d)
        if not os.path.isdir(dp): continue
        for p in os.listdir(dp):
            pp=os.path.join(dp,p)
            if not os.path.isdir(pp): continue
            e='sv' if any(f.endswith('.sv') for f in os.listdir(pp)) else 'v'
            exact[p]=e; bynorm.setdefault(R.norm(p),e)
def ext(e): return exact.get(e['name']) or bynorm.get(e['key'])
def o(e,m):
    it=e[m]['iters']
    if it is None: return None
    if e[m]['pass'] and it==0: return 'z'
    return 'r' if e[m]['pass'] else 'n'
C,Sq,B='combinatial logic','sequential logic','building larger circuits'
T=defaultdict(lambda:[0,0,0,0]); PM=defaultdict(lambda:defaultdict(lambda:[0,0,0]))
for e in rec:
    if e['key'] not in lab: continue
    g=(lab[e['key']][0],ext(e)); T[g][0]+=1
    for m in MODS:
        x=o(e,m)
        if x=='z': T[g][1]+=1; PM[g][m][0]+=1
        elif x in('r','n'): T[g][2]+=1; T[g][3]+=(x=='r'); PM[g][m][1]+=1; PM[g][m][2]+=(x=='r')
print("== class x testbench type (207 labelled problems, 4 models) ==")
for g,(n,z,f,r) in sorted(T.items()):
    print(f"{g[0]:26s} .{g[1]:3s} problems={n:3d} zero-shot={z:3d}/{z+f:3d} ({100*z/(z+f):.1f}%) first-fail={f:3d} recovered={r:3d} efficacy={100*r/f if f else 0:.1f}% never={f-r}")
print("\n== per model ==")
for g in ((C,'v'),(Sq,'v'),(Sq,'sv'),(B,'v')):
    print(f"{g[0][:12]} .{g[1]}: "+' | '.join(f"{m} z={PM[g][m][0]} eff={PM[g][m][2]}/{PM[g][m][1]}={100*PM[g][m][2]/PM[g][m][1] if PM[g][m][1] else 0:.0f}%" for m in MODS))
print("\n== .sv problems with any pass ==")
for e in rec:
    if e['key'] in lab and ext(e)=='sv':
        os_=[o(e,m) for m in MODS]
        if any(x in('z','r') for x in os_): print(' ',e['name'],lab[e['key']][0][:4],''.join(x or '-' for x in os_))
svseq=lambda e: e['key'] in lab and lab[e['key']][0]==Sq and ext(e)=='sv'
calls=lambda e,m: 0 if e[m]['iters'] is None else int(e[m]['iters'])
tot=sum(calls(e,m) for e in rec for m in MODS); sv=sum(calls(e,m) for e in rec if svseq(e) for m in MODS)
print(f"\n== repair calls: total={tot} on .sv-seq={sv} ({100*sv/tot:.1f}%) pairs={4*sum(1 for e in rec if svseq(e))}")
keep=[e for e in rec if not svseq(e)]
print("== pass rate all 220 vs excluding .sv-seq ==")
for m in MODS:
    a=100*sum(e[m]['pass'] for e in rec)/len(rec); b=100*sum(e[m]['pass'] for e in keep)/len(keep)
    print(f"  {m:8s} {a:.1f} -> {b:.1f} (+{b-a:.1f}) n={len(keep)}")
print("\n== .v only: unsolved by all four ==")
for c in (C,Sq,B):
    ps=[e for e in keep if e['key'] in lab and lab[e['key']][0]==c and ext(e)=='v']
    u=[e['name'] for e in ps if not any(e[m]['pass'] for m in MODS)]
    print(f"  {c:26s} {len(u)}/{len(ps)} {u}")
