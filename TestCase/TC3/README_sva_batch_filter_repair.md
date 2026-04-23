# Standalone SVA Batch Filter + Repair (TC3)

This utility is **fully standalone** and does not integrate with repository pipelines.

## Script

- `sva_batch_filter_repair.py`

## What it does

For each SVA file in an input directory (`.txt`, `.sv`, `.sva`):

1. **Loop A: Signal-name validation**
   - Extract identifiers from SVA text using regex.
   - Ignore SystemVerilog keywords/system functions and generic tokens.
   - Compare against `VALID_SIGNAL_ALIAS_TABLE` (mock table at top of script).
   - If invalid signal found, attempt **one** LLM repair via stub.
   - If still invalid, discard.

2. **Loop B: Verible syntax validation**
   - Wrap SVA in module:
     ```systemverilog
     module sva_check_wrapper(input logic clk);
       // [INSERT SVA HERE]
     endmodule
     ```
   - Run `verible-verilog-syntax`.
   - If syntax fails, attempt **one** LLM repair via stub.
   - If still invalid, discard.

## Requirements

- Python 3.9+
- `verible-verilog-syntax` available in PATH

## Run

```bash
python3 TestCase/TC3/sva_batch_filter_repair.py \
  --input-dir TestCase/TC3/sva_input \
  --output-dir TestCase/TC3/sva_output
```

## Output layout

Under `--output-dir`:

- `accepted/` -> final accepted SVA files
- `discarded/` -> discarded SVA files after failed repair limits
- `reports/summary.json` -> aggregate counts
- `reports/detailed_results.json` -> per-file result metadata
- `reports/summary.txt` -> human-readable summary

## LLM integration point

Edit this function in script:

- `repair_sva_with_llm(original_sva, error_message, context)`

Current stub returns the input assertion unchanged.
