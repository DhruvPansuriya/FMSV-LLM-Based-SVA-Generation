# Standalone SVA Batch Filter + Repair (TC3 / src)

This utility is fully standalone and intentionally **not integrated** with repository pipeline code.

## Location

- Script: `TestCase/TC3/src/sva_batch_filter_repair.py`

## What it does

For each input SVA file (`.txt`, `.sv`, `.sva`), runs:

1. **Loop A: Signal Name Validator**
   - Extract identifiers via regex.
   - Ignore SV keywords/system functions/clock tokens.
   - Compare against valid alias table.
   - If invalid signal exists, call one repair attempt via `repair_sva_with_llm(...)` stub.
   - If still invalid after 1 attempt, discard.

2. **Loop B: Verible Syntax Check**
   - Wrap assertion in module:
     ```systemverilog
     module sva_check_wrapper(input logic clk);
       // [INSERT SVA HERE]
     endmodule
     ```
   - Run `verible-verilog-syntax`.
   - On syntax failure, call one repair attempt via stub.
   - If still invalid after 1 attempt, discard.

## Alias table source

The script auto-loads the latest TC3 alias file from:

- `AssertionForge/logs/gen_plan_*/output/TC3/signal_aliases.json`

You can override with:

- `--alias-json /absolute/path/to/signal_aliases.json`

## Defaults (inside src)

- Default input dir: `TestCase/TC3/src/sva_input`
- Default output dir: `TestCase/TC3/src/sva_output`

## Run

```bash
python3 TestCase/TC3/src/sva_batch_filter_repair.py
```

or explicit paths:

```bash
python3 TestCase/TC3/src/sva_batch_filter_repair.py \
  --input-dir TestCase/TC3/src/sva_input \
  --output-dir TestCase/TC3/src/sva_output
```

## Output layout

Under output dir:

- `accepted/`
- `discarded/`
- `reports/detailed_results.json`
- `reports/summary.json`
- `reports/summary.txt`

## LLM repair integration point

Replace stub function in script:

- `repair_sva_with_llm(original_sva, error_message, context)`
