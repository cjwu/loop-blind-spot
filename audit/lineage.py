import sys; sys.path.insert(0,'/Users/cjw/@RESAECH/RTL-Code/analysis'); import recover as R
from collections import Counter, defaultdict
wb,rec=R.load(); lab=R.taxonomy(); MODS=[m for m,_,_ in R.MOD]
ve={R.norm(l.strip()) for l in open('/Users/cjw/@RESAECH/RTL-Code/analysis/problem_names_verilogeval.txt') if l.strip()}
def o(e,m):
    it=e[m]['iters']
    if it is None: return None
    if e[m]['pass'] and it==0: return 'z'
    return 'r' if e[m]['pass'] else 'n'
# duplicates
keys=Counter(e['key'] for e in rec); dups={k:v for k,v in keys.items() if v>1}
print("== duplicate keys among 220 rows ==", len(dups), dups)
print("distinct keys:", len(keys), "| distinct labeled keys:", len({e['key'] for e in rec if e['key'] in lab}))
print("\n== lineage split (pairs) : class x inVerilogEval ==")
T=defaultdict(lambda:[0,0,0,0])  # nprob, zero, fail, rec
for e in rec:
    if e['key'] not in lab: continue
    g=(lab[e['key']][0], 'VE' if e['key'] in ve else 'nonVE')
    T[g][0]+=1
    for m in MODS:
        x=o(e,m)
        if x=='z': T[g][1]+=1
        elif x in('r','n'):
            T[g][2]+=1; T[g][3]+=(x=='r')
for g,(n,z,f,r) in sorted(T.items()):
    print(f"{g[0]:26s} {g[1]:6s} problems={n:3d} zero-shot pairs={z:3d} ({100*z/(z+f):.0f}%) first-fail={f:3d} recovered={r:3d} efficacy={100*r/f if f else float('nan'):.1f}%")
print("\n== per model, sequential, by lineage ==")
for m in MODS:
    row=[]
    for lin in ('VE','nonVE'):
        z=f=r=0
        for e in rec:
            if e['key'] not in lab or lab[e['key']][0]!='sequential logic': continue
            if (e['key'] in ve)!=(lin=='VE'): continue
            x=o(e,m)
            if x=='z': z+=1
            elif x in('r','n'): f+=1; r+=(x=='r')
        row.append(f"{lin}: zero={z} fail={f} rec={r} eff={100*r/f if f else 0:.0f}%")
    print(f"{m:8s}", ' | '.join(row))
print("\n== combinational never-recovered pairs: which problems ==")
for e in rec:
    if e['key'] in lab and lab[e['key']][0]=='combinatial logic':
        os_=[o(e,m) for m in MODS]
        if 'n' in os_: print(f"  {e['name']:24s} {'VE' if e['key'] in ve else 'nonVE':6s} {''.join(x or '-' for x in os_)}")
