# Smoke test of the 292 testbenches (2026-09-02)

Tool: Icarus Verilog 13.0 (stable), installed via Homebrew on the local arm64 machine for this
test only and removed afterwards. No LLM was called. Scripts: `smoke.py` (compile sweep),
`golden.py` (reference-as-DUT run). Raw tables: `smoke_all_dirs.csv`, `golden_reference_run.csv`.
Plain-mode error text for five problems: `*_plain_mode_error.txt`.

## What was run

1. **Compile sweep, every problem directory (292).** The testbench alone was compiled twice,
   `iverilog -t null tb` (plain Verilog) and `iverilog -g2012 -t null tb` (SystemVerilog mode).
   Errors were classified as `syntax` (error inside the testbench) or `unknown_module_only`
   (testbench is fine, only the DUT is missing).
2. **Golden run, every testbench that embeds a `reference_module` (106).** The reference was
   copied out, renamed `top_module`, and simulated against its own testbench under `-g2012`.

## Results

| testbench file | n | plain mode | `-g2012` mode |
|---|---|---|---|
| `testbench.sv` | 103 | **103 syntax errors in the testbench** | 103 clean (DUT missing only) |
| `testbench.v` | 189 | 185 clean, 3 syntax (SystemVerilog content in a `.v` file: `m2014_q4a`, `m2014_q4c''`, `ece241_2013_q2''`), 1 other (`div_16bit`) | 188 clean, 1 other |

Golden run (106 VerilogEval-style testbenches with an embedded reference):

- Unpatched, Icarus 13.0 rejects all 106 at elaboration: `tb_mismatch` is used in `$dumpvars`
  before its declaration (`Unable to bind wire/reg/memory 'tb_mismatch'`). This is a strictness
  of Icarus 13; VerilogEval documents Icarus 12 for these files.
- With that single `$dumpvars` argument removed (no other change), **106 / 106 references pass
  their own testbench with 0 mismatches.**

## What this establishes

- The 46 `.sv` sequential problems that failed for every model on every attempt carry valid
  testbenches with correct references. The failures cannot be attributed to the designs.
- A plain-Verilog invocation rejects every `.sv` testbench at the testbench itself; the error
  text points at `testbench.sv` lines (`Task/function default argument requires SystemVerilog`,
  `Invalid module instantiation`), which no change to the DUT can fix.
- `m2014_q4a` is a VerilogEval-style SystemVerilog testbench stored as `testbench.v`, forward
  reference included, and two models passed it zero-shot in the recorded run. The recorded flow
  therefore could execute this content; the remaining difference to the 46 dead problems is the
  file extension. The harness code was not preserved, so the exact selection mechanism is
  inferred, not observed.

- `div_16bit`, the only combinational problem no model ever solved, has a plain-Verilog
  testbench that does not compile in any mode (`'expected_result' has already been declared`).
  A second instance of the same blind spot, inside the combinational class.

## Wording for the article

Confirmed: the testbenches are valid and their references pass; a plain-Verilog flow rejects
all of them before the DUT is considered. Inferred: the recorded flow did not execute
`testbench.sv` files, most plausibly by selecting `testbench.v` by name.
