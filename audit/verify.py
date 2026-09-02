import sys, os, random, statistics as st, math
sys.path.insert(0, '/Users/cjw/@RESAECH/RTL-Code/analysis')
import recover as R
from collections import Counter, defaultdict
random.seed(7)
wb, rec = R.load(); lab = R.taxonomy()
MODS = [m for m,_,_ in R.MOD]
C, Sq, B = 'combinatial logic', 'sequential logic', 'building larger circuits'

# --- h. iters distribution for Fail rows / None cells / >25
print("== raw cell audit ==")
for m in MODS:
    fails = [e[m]['iters'] for e in rec if not e[m]['pass']]
    nones = [e['name'] for e in rec if e[m]['iters'] is None]
    over = [(e['name'], e[m]['iters']) for e in rec if e[m]['iters'] is not None and e[m]['iters']>25]
    print(m, 'fail iters values:', Counter(fails).most_common(5), '| None cells:', nones, '| >25:', over)

unl = [e['name'] for e in rec if e['key'] not in lab]
print("\n== unlabeled (%d) =="%len(unl), unl)

# --- per problem-model outcomes for labeled
def outcome(e,m):
    it = e[m]['iters']
    if it is None: return None
    if e[m]['pass'] and it==0: return 'zero'
    return 'rec' if e[m]['pass'] else 'never'

labeled = [e for e in rec if e['key'] in lab]
print("\n== labeled problems by type ==", Counter(lab[e['key']][0] for e in labeled))

# --- a,b. per-model Fisher + Wilson
def wilson(k,n,z=1.96):
    if n==0: return (None,None)
    p=k/n; d=1+z*z/n; c=(p+z*z/(2*n))/d; h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return (100*(c-h),100*(c+h))
def fisher(a,b,c,d):
    # two-sided Fisher exact via hypergeometric enumeration
    from math import factorial as F
    def comb(n,k): return F(n)//(F(k)*F(n-k)) if 0<=k<=n else 0
    n=a+b+c+d; r1=a+b; c1=a+c
    def pr(x): return comb(r1,x)*comb(n-r1,c1-x)/comb(n,c1)
    p0=pr(a); lo=max(0,c1-(n-r1)); hi=min(r1,c1)
    return sum(pr(x) for x in range(lo,hi+1) if pr(x)<=p0*(1+1e-9))
print("\n== per-model repair efficacy: Wilson CI + Fisher p (comb vs seq) ==")
per = {}
for m in MODS:
    t = defaultdict(lambda:[0,0])
    for e in labeled:
        o = outcome(e,m)
        if o in ('rec','never'):
            ty = lab[e['key']][0]; t[ty][1]+=1; t[ty][0]+= (o=='rec')
    per[m]=t
    a,n1 = t[C]; c,n2 = t[Sq]
    p = fisher(a,n1-a,c,n2-c)
    print(f"{m:8s} comb {a}/{n1}={100*a/n1:.1f} W[{wilson(a,n1)[0]:.1f},{wilson(a,n1)[1]:.1f}] | seq {c}/{n2}={100*c/n2:.1f} W[{wilson(c,n2)[0]:.1f},{wilson(c,n2)[1]:.1f}] | Fisher p={p:.4f} | larger {t[B][0]}/{t[B][1]}")
A=sum(per[m][C][0] for m in MODS); N1=sum(per[m][C][1] for m in MODS)
Cc=sum(per[m][Sq][0] for m in MODS); N2=sum(per[m][Sq][1] for m in MODS)
print(f"pooled   comb {A}/{N1}={100*A/N1:.1f} W[{wilson(A,N1)[0]:.1f},{wilson(A,N1)[1]:.1f}] | seq {Cc}/{N2}={100*Cc/N2:.1f} W[{wilson(Cc,N2)[0]:.1f},{wilson(Cc,N2)[1]:.1f}] | naive Fisher p={fisher(A,N1-A,Cc,N2-Cc):.2e}")

# --- c. cluster bootstrap over problems
def pooled_eff(problems):
    t = defaultdict(lambda:[0,0])
    for e in problems:
        ty = lab[e['key']][0]
        for m in MODS:
            o=outcome(e,m)
            if o in ('rec','never'): t[ty][1]+=1; t[ty][0]+=(o=='rec')
    return t
comb_p=[e for e in labeled if lab[e['key']][0]==C]; seq_p=[e for e in labeled if lab[e['key']][0]==Sq]
diffs=[];ratios=[];ce=[];se=[]
for _ in range(4000):
    bc=[random.choice(comb_p) for _ in comb_p]; bs=[random.choice(seq_p) for _ in seq_p]
    t=pooled_eff(bc+bs)
    x=t[C][0]/t[C][1]; y=t[Sq][0]/t[Sq][1]
    ce.append(x); se.append(y); diffs.append(x-y); ratios.append(x/y)
def pct(v): v=sorted(v); return (100*v[int(0.025*len(v))],100*v[int(0.975*len(v))])
def pctr(v): v=sorted(v); return (v[int(0.025*len(v))],v[int(0.975*len(v))])
print("\n== problem-level cluster bootstrap (4000 reps, resample problems within class) ==")
print("comb efficacy CI %.1f-%.1f | seq CI %.1f-%.1f | diff CI %.1f-%.1f pp | ratio CI %.2f-%.2f"%(*pct(ce),*pct(se),*pct(diffs),*pctr(ratios)))

# --- d. problem-level view
print("\n== problem-level: among problems with >=1 first-attempt failure ==")
for ty in (C,Sq,B):
    pats=Counter(); eff=[]
    for e in labeled:
        if lab[e['key']][0]!=ty: continue
        os_=[outcome(e,m) for m in MODS]; f=sum(o in('rec','never') for o in os_); r=sum(o=='rec' for o in os_)
        if f==0: continue
        pats['all recovered' if r==f else ('none' if r==0 else 'partial')]+=1; eff.append(r/f)
    print(f"{ty:26s} problems w/ failure={sum(pats.values())} | {dict(pats)} | mean per-problem efficacy={100*st.mean(eff):.1f}")

# --- f. rounds among recovered
print("\n== repair rounds among recovered ==")
allr=[]
for ty in (C,Sq,B):
    r=[e[m]['iters'] for e in labeled if lab[e['key']][0]==ty for m in MODS if outcome(e,m)=='rec']
    allr+=r
    print(f"{ty:26s} n={len(r)} median={st.median(r)} at1={100*sum(v==1 for v in r)/len(r):.0f}% <=2={100*sum(v<=2 for v in r)/len(r):.0f}% <=5={100*sum(v<=5 for v in r)/len(r):.0f}% max={max(r)} mean={st.mean(r):.2f}")
r=allr
print(f"{'all':26s} n={len(r)} median={st.median(r)} at1={100*sum(v==1 for v in r)/len(r):.0f}% <=2={100*sum(v<=2 for v in r)/len(r):.0f}% <=5={100*sum(v<=5 for v in r)/len(r):.0f}% max={max(r)}")
# Mann-Whitney-ish: compare comb vs seq rounds via rank-sum p (normal approx)
rc=[e[m]['iters'] for e in labeled if lab[e['key']][0]==C for m in MODS if outcome(e,m)=='rec']
rs=[e[m]['iters'] for e in labeled if lab[e['key']][0]==Sq for m in MODS if outcome(e,m)=='rec']
allv=sorted(rc+rs); ranks={}
i=0
while i<len(allv):
    j=i
    while j<len(allv) and allv[j]==allv[i]: j+=1
    ranks[allv[i]]=(i+1+j)/2; i=j
U=sum(ranks[v] for v in rc)-len(rc)*(len(rc)+1)/2
mu=len(rc)*len(rs)/2; sd=math.sqrt(len(rc)*len(rs)*(len(rc)+len(rs)+1)/12)
z=(U-mu)/sd; p=2*(1-0.5*(1+math.erf(abs(z)/math.sqrt(2))))
print(f"rank-sum comb vs seq rounds: z={z:.2f} p~{p:.3f} (no tie correction)")

# --- i. building larger problems
print("\n== building larger labeled problems ==")
for e in labeled:
    if lab[e['key']][0]==B:
        print(f"  {e['name']:28s} {lab[e['key']][1]:16s}", ' '.join(f"{m}:{outcome(e,m)}/{e[m]['iters']}" for m in MODS))
