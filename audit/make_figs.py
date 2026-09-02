"""Figures for the D&T article. Fig 1: per-problem outcomes by testbench type. Fig 2: convergence
curves with and without the 46 SystemVerilog-testbench sequential problems."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import recover as R
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'ieee-design-test', 'figs')
wb, rec = R.load(); lab = R.taxonomy(); MODS = [m for m, _, _ in R.MOD]
NAMES = {'GPT-4': 'GPT-4', '4o': 'GPT-4o', '4o-mini': 'GPT-4o-mini', 'o1-mini': 'o1-mini'}
exact, bynorm = {}, {}
for t in os.listdir(R.ROOT):
    tp = os.path.join(R.ROOT, t)
    if not os.path.isdir(tp): continue
    for d in os.listdir(tp):
        dp = os.path.join(tp, d)
        if not os.path.isdir(dp): continue
        for p in os.listdir(dp):
            pp = os.path.join(dp, p)
            if os.path.isdir(pp):
                e = 'sv' if any(f.endswith('.sv') for f in os.listdir(pp)) else 'v'
                exact[p] = e; bynorm.setdefault(R.norm(p), e)
ext = lambda e: exact.get(e['name']) or bynorm.get(e['key'])
def outcome(e, m):
    it = e[m]['iters']
    if it is None: return np.nan
    if e[m]['pass'] and it == 0: return 0
    return 1 if e[m]['pass'] else 2
C, S = 'combinatial logic', 'sequential logic'
groups = [('Combinational\nplain-Verilog testbench (92)', lambda e: lab[e['key']][0] == C and ext(e) == 'v'),
          ('Sequential\nplain-Verilog testbench (55)', lambda e: lab[e['key']][0] == S and ext(e) == 'v'),
          ('Sequential\nSystemVerilog testbench (46)', lambda e: lab[e['key']][0] == S and ext(e) == 'sv')]
mats = []
for title, f in groups:
    ps = sorted([e for e in rec if e['key'] in lab and f(e)], key=lambda e: e['name'].lower())
    M = np.array([[outcome(e, m) for e in ps] for m in MODS], dtype=float)
    mats.append((title, M))
plt.rcParams.update({'font.size': 7, 'font.family': 'sans-serif', 'pdf.fonttype': 42, 'ps.fonttype': 42})
fig, axes = plt.subplots(1, 3, figsize=(7.1, 1.75), gridspec_kw={'width_ratios': [m.shape[1] for _, m in mats], 'wspace': 0.06})
cmap = ListedColormap(['#e6e6e6', '#4c72b0', '#b22222']); cmap.set_bad('white')
for ax, (title, M) in zip(axes, mats):
    ax.pcolormesh(np.ma.masked_invalid(M), cmap=cmap, vmin=0, vmax=2, edgecolors='none', rasterized=False)
    ax.invert_yaxis()
    ax.set_title(title, fontsize=7, pad=3)
    ax.set_xticks([]); ax.set_yticks([k + 0.5 for k in range(4)])
    ax.set_yticklabels([NAMES[m] for m in MODS] if ax is axes[0] else [''] * 4)
    for s in ax.spines.values(): s.set_linewidth(0.4)
axes[1].set_xlabel('one column per problem', fontsize=7)
fig.legend(handles=[Patch(color='#e6e6e6', label='passed on first attempt'), Patch(color='#4c72b0', label='recovered by the loop'), Patch(color='#b22222', label='never passed (25 rounds)')],
           loc='lower center', ncol=3, frameon=False, fontsize=7, bbox_to_anchor=(0.5, -0.16))
fig.savefig(os.path.join(OUT, 'fig_heat.pdf'), bbox_inches='tight', dpi=600)
# Fig 2
svseq = lambda e: e['key'] in lab and lab[e['key']][0] == S and ext(e) == 'sv'
keep = [e for e in rec if not svseq(e)]
ks = list(range(0, 26))
fig, ax = plt.subplots(figsize=(3.5, 2.6))
cols = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
for m, c in zip(MODS, cols):
    a = [100 * sum(1 for e in rec if e[m]['pass'] and e[m]['iters'] is not None and e[m]['iters'] <= k) / len(rec) for k in ks]
    b = [100 * sum(1 for e in keep if e[m]['pass'] and e[m]['iters'] is not None and e[m]['iters'] <= k) / len(keep) for k in ks]
    ax.plot(ks, a, '-', color=c, lw=1.2, label=f'{NAMES[m]}, all 220')
    ax.plot(ks, b, '--', color=c, lw=1.2, label=f'{NAMES[m]}, 174 without the 46')
ax.set_xlabel('repair rounds allowed, k'); ax.set_ylabel('designs passing by round k (%)')
ax.set_xlim(0, 25); ax.set_ylim(30, 90); ax.grid(alpha=0.3, lw=0.4)
ax.legend(fontsize=6, ncol=2, frameon=False, loc='upper center', bbox_to_anchor=(0.5, -0.22))
for s in ax.spines.values(): s.set_linewidth(0.4)
fig.savefig(os.path.join(OUT, 'fig_curves.pdf'), bbox_inches='tight', dpi=600)
print('figs written:', os.listdir(OUT), [(t, m.shape) for t, m in mats])
