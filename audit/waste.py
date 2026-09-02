import sys,os; sys.path.insert(0,'/Users/cjw/@RESAECH/RTL-Code/analysis'); import recover as R
from collections import Counter, defaultdict
wb,rec=R.load(); lab=R.taxonomy(); MODS=[m for m,_,_ in R.MOD]
# taxonomy collisions
seen=defaultdict(list)
for t in os.listdir(R.ROOT):
    tp=os.path.join(R.ROOT,t)
    if not os.path.isdir(tp): continue
    for d in os.listdir(tp):
        dp=os.path.join(tp,d)
        if not os.path.isdir(dp): continue
        for p in os.listdir(dp):
            if os.path.isdir(os.path.join(dp,p)): seen[R.norm(p)].append(f"{t[:4]}/{d[:4]}/{p}")
print("== taxonomy name collisions ==", {k:v for k,v in seen.items() if len(v)>1})
ext={}
for k,v in seen.items():
    for path in v:
        t,d,p=path.split('/')
        full=[os.path.join(R.ROOT,tt,dd,p) for tt in os.listdir(R.ROOT) if os.path.isdir(os.path.join(R.ROOT,tt)) for dd in os.listdir(os.path.join(R.ROOT,tt)) if os.path.isdir(os.path.join(R.ROOT,tt,dd,p))]
        for f in full: ext[k]='sv' if any(x.endswith('.sv') for x in os.listdir(f)) else 'v'
run={e['key'] for e in rec}
notrun=[k for k in seen if k not in run]
print("\n== 292 dirs: run vs not run, by ext ==")
print("run (in xlsx):", Counter(ext[k] for k in seen if k in run), "| not run:", Counter(ext[k] for k in notrun), "n_notrun=",len(notrun))
# waste: repair calls
def calls(e,m):
    it=e[m]['iters']; return 0 if it is None else int(it)
tot=0; sv_seq=0; sv_seq_pairs=0
for e in rec:
    for m in MODS:
        c=calls(e,m); tot+=c
        if e['key'] in lab and lab[e['key']][0]=='sequential logic' and ext.get(e['key'])=='sv':
            sv_seq+=c; sv_seq_pairs+=1
print(f"\n== repair-call budget == total repair calls across 220x4 = {tot}; on .sv sequential pairs ({sv_seq_pairs} pairs) = {sv_seq} ({100*sv_seq/tot:.0f}%)")
# per-model waste share
for m in MODS:
    t=sum(calls(e,m) for e in rec); s=sum(calls(e,m) for e in rec if e['key'] in lab and lab[e['key']][0]=='sequential logic' and ext.get(e['key'])=='sv')
    print(f"  {m:8s} total={t} sv-seq={s} ({100*s/t:.0f}%)")
# pass rate if .sv sequential excluded
print("\n== pass rate on 220 vs excluding .sv-sequential problems ==")
keep=[e for e in rec if not (e['key'] in lab and lab[e['key']][0]=='sequential logic' and ext.get(e['key'])=='sv')]
for m in MODS:
    print(f"  {m:8s} all={100*sum(e[m]['pass'] for e in rec)/len(rec):.1f}% ({len(rec)})  excl-sv-seq={100*sum(e[m]['pass'] for e in keep)/len(keep):.1f}% ({len(keep)})  zero-shot excl={100*sum(1 for e in keep if e[m]['pass'] and e[m]['iters']==0)/len(keep):.1f}%")
