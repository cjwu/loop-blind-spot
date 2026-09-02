import re
D='/Users/cjw/@RESAECH/RTL-Code/draft.md'; OUT='/Users/cjw/@RESAECH/RTL-Code/ieee-design-test/loop_blind_spot.tex'
md=open(D).read()
def esc_tt(s):
    return s.replace('\\','\\textbackslash{}').replace('_','\\_').replace('$','\\$').replace('#','\\#').replace('%','\\%').replace('&','\\&').replace('~','\\textasciitilde{}').replace('^','\\^{}')
def conv(body):
    # protect existing latex commands we wrote in markdown: ~\cite{}, \ref{}, Section~N, Table~\ref
    out=[]; 
    parts=re.split(r'(`[^`]*`)', body)
    for i,pt in enumerate(parts):
        if i%2==1: out.append('\\texttt{'+esc_tt(pt[1:-1])+'}'); continue
        t=pt
        t=re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', t, flags=re.S)
        t=re.sub(r'(?<![\w\\])\*(?!\*)([^*\n]+?)\*(?!\w)', r'\\emph{\1}', t)
        # straight double quotes -> latex quotes
        t=re.sub(r'"([^"]*)"', r"``\1''", t, flags=re.S)
        # escape bare % and & outside commands (none expected inside \cite etc.)
        t=t.replace('%','\\%').replace('&','\\&')
        t=re.sub(r'\((https?://[^\s)]+)\)', r'(\\url{\1})', t)
        out.append(t)
    return ''.join(out)
def section(n):
    m=re.search(r'^## %d\. ([^\n]+?) \(v2, 2026-09-02\)\n(.*?)(?=^### )'%n, md, re.S|re.M)
    assert m, n
    title=m.group(1).strip(); body=m.group(2).strip()
    return title, body
secs={n:section(n) for n in (1,2,3,4,5,6,7)}
# table from §4 (already latex)
tab=[t for t in re.findall(r'\\begin\{table\}\[t\].*?\\end\{table\}', md, re.S) if 'tab:split' in t][0]
tab=tab.replace('\\begin{table}[t]','\\begin{table*}[!t]').replace('\\end{table}','\\end{table*}')
tab=tab.replace('\\begin{tabular}','\\footnotesize\n\\begin{tabular}')
bodies={}
for n,(title,body) in secs.items():
    b=conv(body)
    bodies[n]=(title,b)
# targeted edits
t6=bodies[6][1]
assert 'Table~2' in t6; t6=t6.replace('Table~2','Table~\\ref{tab:split}'); bodies[6]=(bodies[6][0],t6)
t4=bodies[4][1]
anchor='The sequential deficit of Section 3 is this group and nothing else.'
assert anchor in t4
t4=t4.replace(anchor, anchor+' Figure~\\ref{fig:heat} shows the same records problem by problem.')
bodies[4]=(bodies[4][0],t4)
t5=bodies[5][1]
anchor5='gain from round 5 to round 25 is 3.2 to 8.6 points with them and 4.0 to 10.3 points without.'
assert anchor5 in t5
t5=t5.replace(anchor5, anchor5[:-1]+' (Figure~\\ref{fig:curves}).'); bodies[5]=(bodies[5][0],t5)
# section 4: insert table* after first paragraph mentioning the table; figures after relevant paragraphs
def insert_after_para(text, needle, block):
    idx=text.index(needle); end=text.index('\n\n', idx) if '\n\n' in text[idx:] else len(text)
    return text[:end]+'\n\n'+block+text[end:]
fig_heat='''\\begin{figure*}[!t]
\\centering
\\includegraphics[width=\\textwidth]{figs/fig_heat.pdf}
\\caption{Every problem-model pair in the 207 labelled problems, one column per problem, grouped by circuit class and testbench file. The 46 sequential problems with a SystemVerilog testbench form the block at the right: no first-attempt pass in 184 pairs and three recoveries, each a duplicated problem.}
\\label{fig:heat}
\\end{figure*}'''
fig_curves='''\\begin{figure}[!t]
\\centering
\\includegraphics[width=\\columnwidth]{figs/fig_curves.pdf}
\\caption{Designs passing by repair round, per model, on all 220 problems (solid) and on the 174 that remain when the 46 SystemVerilog-testbench problems are set aside (dashed). Removing them raises every curve and leaves its shape unchanged.}
\\label{fig:curves}
\\end{figure}'''
t4=bodies[4][1]
t4=insert_after_para(t4,'Table~\\ref{tab:split} splits', tab)
t4=insert_after_para(t4,'Figure~\\ref{fig:heat} shows', fig_heat)
bodies[4]=(bodies[4][0],t4)
t5=bodies[5][1]; t5=insert_after_para(t5,'(Figure~\\ref{fig:curves})', fig_curves); bodies[5]=(bodies[5][0],t5)
abstract=r'''Simulator-feedback repair loops are the standard way to turn a language model's Verilog into a passing design, and building such loops now has a name, loop engineering. Every such loop rests on an assumption it never checks: that its verifier is able to say pass. This article reports what happened when that assumption failed silently. In a 220-problem, four-model study, 46 of the 101 sequential-logic problems shipped SystemVerilog testbenches the flow did not execute. The loop spent 52.5\% of its 8,663 repair calls on them, every convergence curve kept its ordinary shape, and the aggregate read as a finding that agreed with published trends: sequential logic is where the loop fails. On testbenches that ran, the loop repaired sequential and combinational failures at the same rate, and every model's pass rate was 16 to 17 points higher. A golden check on the reference designs would have removed the 46 problems in seconds. The article sets out the checks a repair loop has to carry inside it, because nothing in its own output will ask for them.'''
head=r'''\documentclass[lettersize,journal]{IEEEtran}
\usepackage{amsmath,amsfonts}
\usepackage{array}
\usepackage{booktabs}
\usepackage{textcomp}
\usepackage{url}
\usepackage{graphicx}
\usepackage{cite}
\usepackage[colorlinks=true,linkcolor=blue,citecolor=blue,urlcolor=blue]{hyperref}
\hyphenation{Verilog System-Verilog test-bench test-benches}

\begin{document}

\title{Loop Engineering Has a Blind Spot}

\author{Hong-An~Jiang, Dun-Wei~Hu, Tian-Jun~Xie, Hung-Wei~Wu, Chen-Mou~Cheng, and Chi-Jen~Wu%
\thanks{H.-A. Jiang and C.-M. Cheng are with the Department of Artificial Intelligence, Chang Gung University, Taiwan (e-mail: chiang142536@gmail.com; cheng@cgu.edu.tw).}%
\thanks{D.-W. Hu is with the Department of Electrical Engineering, Chang Gung University, Taiwan (e-mail: dunwaihu@gmail.com).}%
\thanks{T.-J. Xie, H.-W. Wu, and C.-J. Wu are with the Department of Computer Science and Information Engineering, Chang Gung University, Taiwan (e-mail: xietangent300@gmail.com; wesley93721@gmail.com; cjwu@cgu.edu.tw).}%
\thanks{Corresponding author: Chi-Jen Wu, ORCID 0000-0002-6468-0952.}}

\markboth{IEEE Design \& Test}%
{Jiang \MakeLowercase{\textit{et al.}}: Loop Engineering Has a Blind Spot}

\maketitle

\begin{abstract}
'''+abstract+r'''
\end{abstract}

\begin{IEEEkeywords}
RTL generation, Verilog, large language models, repair loops, verification, evaluation.
\end{IEEEkeywords}

'''
body=''
for n in (1,2,3,4,5,6,7):
    title,b=bodies[n]
    if n==1:
        b=re.sub(r'^The question asked', r'\\IEEEPARstart{T}{he} question asked', b)
    b=re.sub(r'Section[~ ](\d)', r'Section~\\ref{sec:\1}', b)
    b=b.replace("just 'output mismatch at time X'", "just `output mismatch at time X'")
    body+='\\section{%s}\n\\label{sec:%d}\n%s\n\n'%(title,n,b)
tail=r'''\bibliographystyle{IEEEtran}
\bibliography{refs}

\end{document}
'''
tex=head+body+tail
open(OUT,'w').write(tex)
print('written', OUT, len(tex.splitlines()), 'lines')
# sanity: leftover markdown artifacts
for pat in ['**','`','## ']:
    print(pat, 'occurrences:', tex.count(pat))
print('comment lines (%% at line start):', sum(1 for l in tex.splitlines() if l.lstrip().startswith('%')))
