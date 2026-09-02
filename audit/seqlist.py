import sys; sys.path.insert(0,'/Users/cjw/@RESAECH/RTL-Code/analysis'); import recover as R
wb,rec=R.load(); lab=R.taxonomy(); MODS=[m for m,_,_ in R.MOD]
def o(e,m):
    it=e[m]['iters']
    if it is None: return None
    if e[m]['pass'] and it==0: return 'z'
    return 'r' if e[m]['pass'] else 'n'
rows=[]
for e in rec:
    if e['key'] in lab and lab[e['key']][0]=='sequential logic':
        os_=[o(e,m) for m in MODS]; f=sum(x in('r','n') for x in os_); r=sum(x=='r' for x in os_)
        rows.append((e['name'],lab[e['key']][1][:4],''.join(x or '-' for x in os_),f,r))
rows.sort(key=lambda t:(t[3]-t[4],-t[3],t[0]))
for n,d,p,f,r in rows: print(f"{n:24s} {d} {p} fail={f} rec={r}")
