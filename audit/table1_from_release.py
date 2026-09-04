"""Rebuild Table I of the article from labels.csv and outcomes.csv: all 220 records, grouped by
circuit class and testbench FILE NAME (the variable the flow acted on), plus the 13 records whose
names match no directory. Run from the package root: python audit/table1_from_release.py"""
import csv, collections
labels = {r['release_name']: r for r in csv.DictReader(open('labels.csv'))}
rows = list(csv.DictReader(open('outcomes.csv')))
recs = collections.OrderedDict()
for r in rows: recs.setdefault(r['record_name'], []).append(r)
def group(rn):
    L = labels.get(recs[rn][0]['release_name'])
    if not L: return ('no directory', 'unknown')
    return (L['class'], 'testbench.sv' if L['testbench_file'].endswith('.sv') else 'testbench.v')
G = collections.defaultdict(lambda: dict(n=0, pairs=0, first=0, fail=0, rec=0, calls=0, never=0))
for rn in recs:
    g = G[group(rn)]; g['n'] += 1; anypass = False
    for r in recs[rn]:
        if r['repair_rounds'] == '': continue          # GPT-4 on m2014_q6c: verdict recorded, round blank
        g['pairs'] += 1; passed = r['passed'] == '1'; k = int(r['repair_rounds'])
        anypass |= passed
        if passed and k == 0: g['first'] += 1
        else:
            g['fail'] += 1; g['rec'] += passed
        g['calls'] += k if passed else 25
    g['never'] += not anypass
order = [('combinational', 'testbench.v'), ('sequential', 'testbench.v'), ('sequential', 'testbench.sv'),
         ('larger_blocks', 'testbench.v'), ('larger_blocks', 'testbench.sv'), ('no directory', 'unknown')]
total = 8663
T = collections.Counter()
print(f"{'class':14} {'testbench':13} {'probs':>5} {'first-attempt':>16} {'fail':>5} {'rec':>4} {'efficacy':>9} {'never':>6} {'repair calls':>16}")
for k in order:
    g = G[k]
    print(f"{k[0]:14} {k[1]:13} {g['n']:5d} {g['first']:4d}/{g['pairs']:<4d}{100*g['first']/g['pairs']:6.1f}% {g['fail']:5d} {g['rec']:4d} {100*g['rec']/g['fail'] if g['fail'] else 0:8.1f}% {g['never']:6d} {g['calls']:6d} ({100*g['calls']/total:4.1f}%)")
    for kk in ('n', 'pairs', 'first', 'fail', 'rec', 'calls', 'never'): T[kk] += g[kk]
print(f"{'all records':28} {T['n']:5d} {T['first']:4d}/{T['pairs']:<4d}{100*T['first']/T['pairs']:6.1f}% {T['fail']:5d} {T['rec']:4d} {100*T['rec']/T['fail']:8.1f}% {T['never']:6d} {T['calls']:6d}")
never_calls = sum((int(r['repair_rounds']) if r['passed'] == '1' else 25) for rn in recs if not any(r['passed'] == '1' for r in recs[rn]) for r in recs[rn] if r['repair_rounds'] != '')
print(f"repair calls on records no model ever passed: {never_calls} ({100*never_calls/total:.1f}%)")
