import os, re, subprocess, csv
ROOT='/Users/cjw/@RESAECH/RTL-Code/分類(292題)'; OUT='/Users/cjw/@RESAECH/RTL-Code/analysis/audit/smoke'
W='/private/tmp/claude-501/-Users-cjw--RESAECH--Other-idea/2f8afd07-836c-4ae8-ad17-1ae359ee17ed/scratchpad/smoke'
def run(cmd,cwd,t=120):
    try: p=subprocess.run(cmd,cwd=cwd,capture_output=True,text=True,timeout=t); return p.returncode,p.stdout+p.stderr
    except subprocess.TimeoutExpired: return -9,'TIMEOUT'
rows=[]
for t in sorted(os.listdir(ROOT)):
    tp=os.path.join(ROOT,t)
    if not os.path.isdir(tp): continue
    for d in sorted(os.listdir(tp)):
        dp=os.path.join(tp,d)
        if not os.path.isdir(dp): continue
        for p in sorted(os.listdir(dp)):
            pp=os.path.join(dp,p)
            if not os.path.isdir(pp): continue
            fs=os.listdir(pp)
            tb=next((f for f in fs if f.endswith('.sv')),None)
            if not tb:
                v=next((f for f in fs if f.endswith('.v')),None)
                if not v or 'reference_module' not in open(os.path.join(pp,v),errors='ignore').read(): continue
                tb=v
            src=os.path.join(pp,tb); txt=open(src,errors='ignore').read()
            m=re.search(r'module\s+reference_module\b.*?\bendmodule',txt,re.S)
            if not m: rows.append([t,d,p,tb,'no_reference_module','','']); continue
            wd=os.path.join(W,re.sub(r'[^A-Za-z0-9_]','_',f'{t}_{d}_{p}')); os.makedirs(wd,exist_ok=True)
            open(os.path.join(wd,'top.v'),'w').write(m.group(0).replace('module reference_module','module top_module',1))
            # unpatched
            rc0,e0=run(['iverilog','-g2012','-o','simU',src,'top.v'],wd)
            unp='compile_ok' if rc0==0 else ('fwdref_tb_mismatch' if 'tb_mismatch' in e0 and 'Unable to bind' in e0 else 'compile_fail:'+e0.strip().splitlines()[0][-80:])
            # patched: drop forward-referenced tb_mismatch from $dumpvars only
            pt=re.sub(r'(\$dumpvars\([^)]*?)\btb_mismatch\s*,\s*',r'\1',txt); pt=re.sub(r'(\$dumpvars\([^)]*?),\s*tb_mismatch\b',r'\1',pt)
            open(os.path.join(wd,'tb_patched.sv'),'w').write(pt)
            rc1,e1=run(['iverilog','-g2012','-o','simP','tb_patched.sv','top.v'],wd)
            if rc1!=0: res='compile_fail_patched:'+e1.strip().splitlines()[0][-80:]
            else:
                rc2,e2=run(['vvp','simP'],wd)
                mm=re.search(r'Mismatches:\s*(\d+)\s+in\s+(\d+)',e2)
                res=('PASS' if mm.group(1)=='0' else 'FAIL')+f' {mm.group(1)}/{mm.group(2)}' if mm else ('TIMEOUT' if rc2==-9 else 'no_mismatch_line')
            rows.append([t,d,p,tb,unp,res,'patched' if pt!=txt else 'unpatched'])
with open(os.path.join(OUT,'golden_reference_run.csv'),'w',newline='') as f:
    w=csv.writer(f); w.writerow(['class','difficulty','problem','tb','g2012_unpatched','golden_result','patch']); w.writerows(rows)
from collections import Counter
print('n testbenches with reference_module:',len(rows))
print('unpatched -g2012 compile:',Counter(r[4] for r in rows))
print('golden result (patched where needed):',Counter(r[5].split()[0] for r in rows))
print('patch applied:',Counter(r[6] for r in rows))
print('non-PASS:',[(r[2],r[5]) for r in rows if not r[5].startswith('PASS')])
