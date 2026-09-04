"""Rebuild Table I of the article from labels.csv and outcomes.csv. The article's population is the
207 record names that match a directory in the collection, grouped by circuit class and testbench
FILE NAME (the variable the flow acted on); the second table repeats the accounting over all 220
record names, including the 13 that match no directory. Run from the package root:
python audit/table1_from_release.py"""
import csv, collections
labels = {r['release_name']: r for r in csv.DictReader(open('labels.csv'))}
rows = list(csv.DictReader(open('outcomes.csv')))
recs = collections.OrderedDict()
for r in rows: recs.setdefault(r['record_name'], []).append(r)
def group(rn):
    L = labels.get(recs[rn][0]['release_name'])
    if not L: return ('no directory', 'unknown')
    return (L['class'], 'testbench.sv' if L['testbench_file'].endswith('.sv') else 'testbench.v')
def calls(r):
    if r['repair_rounds'] == '': return 0
    return int(r['repair_rounds']) if r['passed'] == '1' else 25
order = [('combinational', 'testbench.v'), ('sequential', 'testbench.v'), ('sequential', 'testbench.sv'),
         ('larger_blocks', 'testbench.v'), ('larger_blocks', 'testbench.sv'), ('no directory', 'unknown')]
def table(sel, title):
    G = collections.defaultdict(lambda: dict(n=0, pairs=0, first=0, fail=0, rec=0, calls=0, never=0))
    for rn in sel:
        g = G[group(rn)]; g['n'] += 1; anypass = False
        for r in recs[rn]:
            g['calls'] += calls(r)
            if r['repair_rounds'] == '': continue          # GPT-4 on m2014_q6c: verdict recorded, round blank
            g['pairs'] += 1; passed = r['passed'] == '1'; k = int(r['repair_rounds'])
            anypass |= passed
            if passed and k == 0: g['first'] += 1
            else:
                g['fail'] += 1; g['rec'] += passed
        g['never'] += not anypass
    total = sum(g['calls'] for g in G.values())
    print(f"\n== {title}: {len(sel)} records, {total} repair calls ==")
    print(f"{'class':14} {'testbench':13} {'probs':>5} {'first-attempt':>16} {'fail':>5} {'rec':>4} {'efficacy':>9} {'never':>6} {'repair calls':>16}")
    T = collections.Counter()
    for k in order:
        if k not in G: continue
        g = G[k]
        print(f"{k[0]:14} {k[1]:13} {g['n']:5d} {g['first']:4d}/{g['pairs']:<4d}{100*g['first']/g['pairs']:6.1f}% {g['fail']:5d} {g['rec']:4d} {100*g['rec']/g['fail'] if g['fail'] else 0:8.1f}% {g['never']:6d} {g['calls']:6d} ({100*g['calls']/total:4.1f}%)")
        for kk in ('n', 'pairs', 'first', 'fail', 'rec', 'calls', 'never'): T[kk] += g[kk]
    print(f"{'all records':28} {T['n']:5d} {T['first']:4d}/{T['pairs']:<4d}{100*T['first']/T['pairs']:6.1f}% {T['fail']:5d} {T['rec']:4d} {100*T['rec']/T['fail']:8.1f}% {T['never']:6d} {T['calls']:6d}")
    never_calls = sum(calls(r) for rn in sel if not any(r['passed'] == '1' for r in recs[rn]) for r in recs[rn])
    print(f"repair calls on records no model ever passed: {never_calls} ({100*never_calls/total:.1f}%)")
matched = [rn for rn in recs if recs[rn][0]['release_name']]
table(matched, "article population: record names that match a directory")
table(list(recs), "all record names")
