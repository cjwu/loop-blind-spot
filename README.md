# Loop Engineering Has a Blind Spot: problem collection, run records and audit

Material behind the article *Loop Engineering Has a Blind Spot* (under submission).
The article reports a simulator-feedback repair loop for Verilog generation, run on 220 problems
with four OpenAI models, in which 46 sequential-logic problems shipped SystemVerilog testbenches
the flow did not execute. This package holds the problem collection, the per-problem run
records, the labels, and the scripts and outputs of the audit that found the artifact.

## What is here and what is not

| Path | Content |
|---|---|
| `labels.csv` | One row per problem directory (292 rows, 278 distinct problems): circuit class, difficulty label, testbench kind, whether the problem comes from VerilogEval, duplicate-of marker, and what this package releases for it |
| `outcomes.csv` | The run records: 220 problems x 4 models, pass/fail and repair rounds (25 = budget exhausted); `gpt_results_source.xlsx` is the original spreadsheet |
| `problems/` | The 123 problems that do not come from VerilogEval, in full: `description.txt` and the testbench |
| `testbenches_ours/` | For 63 VerilogEval-lineage problems, the plain-Verilog testbench written for this study (the problem text itself is not redistributed) |
| `verilogeval_index.csv` + `fetch_verilogeval.py` | Mapping from our problem names to VerilogEval problem ids, and a script that fetches prompt, reference and SystemVerilog testbench from the VerilogEval repository (MIT) into `problems_verilogeval/`, also writing the merged `testbench.sv` form the study used |
| `manifest_golden_check.csv` | Golden check: for each of the 106 testbenches that embed a reference module, the result of simulating the reference against its own testbench (Icarus Verilog 13.0, `-g2012`) |
| `audit/` | Scripts and outputs of the audit: per-problem outcome tables, testbench-kind split, budget accounting, the compile sweep over all 292 testbenches, the golden run, and the figure generator |
| `analysis/` | `recover.py`, which rebuilds every table from the spreadsheet and the directory tree, and its output |

Not redistributed: VerilogEval problem statements and testbenches (fetch them with the script;
they are MIT-licensed by NVIDIA Research Projects and OpenAI) and any HDLBits text.

## Provenance

The collection was assembled for a course and a study in 2024. By name, 155 of VerilogEval's 156
problems are present; 123 further problems are datapath and storage blocks (FIFOs, RAMs, an ALU,
shifters, counters, pipelined multipliers) with plain-Verilog testbenches written for the study.
Difficulty labels (1 to 5) were assigned for course use without inter-annotator agreement and
are not validated; circuit-class labels are the objective part.

## Accounting of the run records

`outcomes.csv` has 220 record names, each run once by each of the four models (880 rows).
207 record names match a directory in the collection and take its class label; they cover 201
distinct problems, because six are recorded twice (with and without an `Exams_` prefix, or with
a leading underscore). 13 record names match no directory (`release_name` empty): `2014_q4b`,
`calender`, `clock`, `ece241_2014_q7a`, `ece241_2014_q7b`, `Fsm_serialdp`, `Module_name`,
`Module_pos`, `Module_shift`, `Module_shift8_b`, `mulri_booth_8bit`, `Tb_and`, `tff`. Two of
these look like misspellings of directories that exist (`calendar`, `multi_booth_8bit`); they are
left unmatched because nothing in the records shows which directory was run. Twelve of the 13
never passed for any model. One cell, GPT-4 on `m2014_q6c`, has a pass verdict and no repair-round
count; it counts in pass rates and is excluded from round-based statistics (879 pairs).

`testbench_kind` in `labels.csv` is by authorship: `systemverilog` means a VerilogEval-authored
testbench (it embeds a `reference_module`), whatever the file name. Two problems, `m2014_q4a` and
`ece241_2013_q2`, carry such a testbench in a file named `testbench.v`; the article groups problems
by file name (`testbench_file`), under which these two fall in the plain-Verilog rows, because the
flow executed them. `Popcount3` was filed under two classes in the source tree; the combinational
row keeps the name and the sequential copy is `Popcount3_seq` with `duplicate_of = Popcount3`.
Other second copies carry `-2` or `_alt` suffixes and a `duplicate_of` marker.
`audit/table1_from_release.py` rebuilds Table I of the article (all 220 records) from these two files.

## Reproducing the checks

Compile sweep and golden run (requires Icarus Verilog; version 13 rejects a forward reference
in the VerilogEval testbenches' `$dumpvars` line, which `audit/golden.py` removes before
simulating; version 12, the one VerilogEval documents, accepts it):

    python fetch_verilogeval.py --clone
    python audit/smoke.py
    python audit/golden.py

Tables and figures: `python analysis/recover.py`, `python audit/split_v2.py`, `python audit/make_figs.py`.
The scripts read the original directory layout; paths at the top of each file point at it.

## Licence

Everything authored for this study (labels, our testbenches, the 123 released problems, scripts,
outputs) is released under the MIT License (see `LICENSE`). Files fetched from VerilogEval keep
their own MIT notice (`problems_verilogeval/LICENSE.verilog-eval`).

## Citation

Article under review; citation to be added.
