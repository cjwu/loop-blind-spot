import os, re, subprocess, csv, sys, shutil
ROOT='/Users/cjw/@RESAECH/RTL-Code/分類(292題)'
OUT='/Users/cjw/@RESAECH/RTL-Code/analysis/audit/smoke'
W='/private/tmp/claude-501/-Users-cjw--RESAECH--Other-idea/2f8afd07-836c-4ae8-ad17-1ae359ee17ed/scratchpad/smoke'
def run(cmd, cwd, t=60):
    try:
        p=subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=t); return p.returncode, p.stdout+p.stderr
    except subprocess.TimeoutExpired: return -9, 'TIMEOUT'
def classify(err):
    if 'syntax error' in err or 'error:' in err.lower() and 'Unknown module type' not in err: 
        if 'syntax error' in err: return 'syntax'
    if 'Unknown module type' in err: return 'unknown_module_only'
    return 'other' if err.strip() else 'clean'
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
            fs=os.listdir(pp); tb=next((f for f in fs if f.endswith('.sv')), None) or next((f for f in fs if f.endswith('.v')), None)
            if not tb: rows.append([t,d,p,'-','no_tb','','','','']); continue
            ext=tb.rsplit('.',1)[1]; src=os.path.join(pp,tb)
            wd=os.path.join(W, re.sub(r'[^A-Za-z0-9_]','_',f'{t}_{d}_{p}')); os.makedirs(wd, exist_ok=True)
            rcA,eA=run(['iverilog','-t','null','-o','x',src],wd); rcB,eB=run(['iverilog','-g2012','-t','null','-o','x',src],wd)
            cA=classify(eA); cB=classify(eB)
            golden=''; plain_full=''
            txt=open(src,errors='ignore').read()
            m=re.search(r'module\s+reference_module\b.*?\bendmodule', txt, re.S)
            if m:
                top=m.group(0).replace('module reference_module','module top_module',1)
                open(os.path.join(wd,'top.v'),'w').write(top)
                rc1,e1=run(['iverilog','-g2012','-o','sim',src,'top.v'],wd)
                if rc1==0:
                    rc2,e2=run(['vvp','sim'],wd,120)
                    mm=re.search(r'Mismatches:\s*(\d+)\s+in\s+(\d+)', e2)
                    golden=f'{mm.group(1)}/{mm.group(2)}' if mm else ('TIMEOUT' if rc2==-9 else 'no_mismatch_line')
                else: golden='compile_fail_g2012'
                rc3,e3=run(['iverilog','-o','sim2',src,'top.v'],wd)
                plain_full='rc=%d %s'%(rc3, classify(e3))
                if p in ('Dff','Count10','Shift4','Fsm3','Dff8'):
                    open(os.path.join(OUT,f'{p}_plain_mode_error.txt'),'w').write(e3)
            rows.append([t,d,p,ext,cA,rcA,cB,rcB,golden,plain_full])
with open(os.path.join(OUT,'smoke_all_dirs.csv'),'w',newline='') as f:
    w=csv.writer(f); w.writerow(['class','difficulty','problem','tb_ext','plain_mode','plain_rc','sv_mode','sv_rc','golden_g2012_mismatches','ref_as_dut_plain_mode']); w.writerows(rows)
from collections import Counter
print('iverilog:', run(['iverilog','-V'],W)[1].splitlines()[0])
print('n dirs', len(rows))
print('\n== plain mode (no -g2012), by tb ext ==')
for e in ('sv','v'): print(' ', e, Counter(r[4] for r in rows if r[3]==e))
print('== -g2012 mode, by tb ext ==')
for e in ('sv','v'): print(' ', e, Counter(r[6] for r in rows if r[3]==e))
print('== golden (reference as DUT, -g2012) for .sv ==', Counter(('PASS 0 mismatches' if r[8].startswith('0/') else r[8]) for r in rows if r[3]=='sv'))
print('== reference-as-DUT compile in plain mode, .sv ==', Counter(r[9] for r in rows if r[3]=='sv'))
bad=[r for r in rows if r[3]=='sv' and not r[8].startswith('0/')]
print('.sv not passing golden:', [(r[0][:4],r[2],r[8]) for r in bad][:20])
