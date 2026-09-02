"""Fetch the VerilogEval-lineage problems from NVlabs/verilog-eval (MIT licence).

The public release does not redistribute VerilogEval or HDLBits problem text. For every problem
listed in verilogeval_index.csv this script copies the prompt, the reference module and the
SystemVerilog testbench from a clone of the VerilogEval repository into
problems_verilogeval/<release_name>/ and also writes testbench.sv in the merged form the study
used (reference module embedded in the testbench file).

Usage:
    python fetch_verilogeval.py --clone              # shallow-clones the repository next to this script
    python fetch_verilogeval.py --repo /path/to/verilog-eval
"""
import argparse, csv, os, shutil, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
REPO_URL = 'https://github.com/NVlabs/verilog-eval'

def merge(ref, test):
    """Study form: testbench header, then the reference module, then the rest of the testbench."""
    ref = ref.replace('module RefModule', 'module reference_module', 1)
    test = test.replace('RefModule', 'reference_module')
    lines = test.split('\n'); head = []
    while lines and (lines[0].startswith('`') or not lines[0].strip()):
        head.append(lines.pop(0))
    return '\n'.join(head).rstrip() + '\n' + ref.strip() + '\n\n\n' + '\n'.join(lines)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', help='local clone of NVlabs/verilog-eval')
    ap.add_argument('--clone', action='store_true', help='shallow-clone the repository into ./verilog-eval')
    ap.add_argument('--out', default=os.path.join(HERE, 'problems_verilogeval'))
    a = ap.parse_args()
    repo = a.repo
    if a.clone:
        repo = os.path.join(HERE, 'verilog-eval')
        if not os.path.isdir(repo):
            subprocess.check_call(['git', 'clone', '--depth', '1', REPO_URL, repo])
    if not repo or not os.path.isdir(os.path.join(repo, 'dataset_spec-to-rtl')):
        sys.exit('give --repo <clone of NVlabs/verilog-eval> or --clone')
    src = os.path.join(repo, 'dataset_spec-to-rtl'); ifcdir = os.path.join(repo, 'dataset_code-complete-iccad2023')
    n = 0
    with open(os.path.join(HERE, 'verilogeval_index.csv')) as f:
        for r in csv.DictReader(f):
            if not r['prob_id']: continue
            stem = f"{r['prob_id']}_{r['ve_name']}"
            dst = os.path.join(a.out, r['release_name']); os.makedirs(dst, exist_ok=True)
            for suffix, name in (('_prompt.txt', 'prompt.txt'), ('_ref.sv', 'ref.sv'), ('_test.sv', 'test.sv')):
                shutil.copy(os.path.join(src, stem + suffix), os.path.join(dst, name))
            ifc = os.path.join(ifcdir, stem + '_ifc.txt')
            if os.path.exists(ifc): shutil.copy(ifc, os.path.join(dst, 'interface.txt'))
            ref = open(os.path.join(dst, 'ref.sv'), errors='ignore').read(); test = open(os.path.join(dst, 'test.sv'), errors='ignore').read()
            open(os.path.join(dst, 'testbench.sv'), 'w').write(merge(ref, test))
            n += 1
    shutil.copy(os.path.join(repo, 'LICENSE'), os.path.join(a.out, 'LICENSE.verilog-eval'))
    print(f'fetched {n} problems into {a.out}')

if __name__ == '__main__':
    main()
