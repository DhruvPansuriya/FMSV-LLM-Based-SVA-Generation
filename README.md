# LLM-Guided Verification Plan and SVA Generation

This repository contains a full workflow for converting hardware specifications and RTL into:

1. structured knowledge graphs,
2. verification plans, and
3. generated SystemVerilog Assertions (SVAs),

with logging-heavy traceability and standalone quality filtering utilities.

Project context: CS525 formal methods project work by Group 2.

## What this repository includes

- A graph-assisted LLM pipeline under the core project directory.
- helper scripts at repository root (embedding proxy, inspection scripts, test utilities).
- testcase assets under `TestCase/` (including TC3 standalone checker flows).
- report support material in `report_notes/`.
- runtime logs under the core project's `logs/` directory for reproducibility.

## End-to-end architecture

The system uses a staged architecture:

1. **Specification and RTL ingestion**
  - reads specification text/PDF-derived content and RTL files,
  - normalizes and prepares data for downstream extraction.

2. **Embedding generation (local service)**
  - `local_embedding_proxy.py` serves embeddings (typically `all-MiniLM-L6-v2`) on a local HTTP endpoint,
  - reduces dependency on external embedding APIs.

3. **Knowledge graph construction (GraphRAG-oriented flow)**
  - entities/relationships are extracted from spec content,
  - graph artifacts are stored (including parquet-based outputs in GraphRAG folders).

4. **Spec-to-RTL signal alignment**
  - alignment logic maps natural-language signal mentions to concrete RTL identifiers,
  - confidence-gated mapping and alias tables are produced,
  - alignment diagnostics are logged for auditability.

5. **Plan generation**
  - graph context is queried to produce verification intent and signal-level test intent,
  - output is persisted in `nl_plans.txt` and related run artifacts.

6. **SVA generation**
  - generated plans are converted to SystemVerilog assertion candidates,
  - candidates are emitted under timestamped run directories.

7. **Post-generation quality filtering**
  - standalone TC3 utility supports loop-based filtering and syntax checks,
  - Verible integration enables parser-level syntax validation.

## Important directories

### Repository root

- `README.md`: this project guide.
- `local_embedding_proxy.py`: local embedding service.
- `report_notes/`: explanatory writeups and consolidated notes.
- `TestCase/`: testcase-focused experiments and standalone tooling.

### Core pipeline directory

- `src/`: core pipeline source files.
- `data/`: dataset-specific inputs and graph artifacts.
- `logs/`: timestamped run outputs, plans, generated SVAs, and diagnostics.

### `TestCase/TC3/`

- `src/sva_batch_filter_repair.py`: standalone SVA batch filter/repair checker.
- smoke input/output folders and reports for local validation runs.

## Logs and reproducibility

This repository is configured to allow uploading run logs so executions can be audited and compared. Logs typically include:

- prompt/response traces,
- plan files,
- generated SVA files,
- signal-mapping decisions,
- run-level metadata and iterative checker diagnostics.

These files support reproducibility for reports, debugging, and paper artifacts.

## Environment setup

### Python environment

Use Python 3.10+ where possible.

Create and activate a virtual environment, then install dependencies from project requirements (for submodules that include their own `requirements.txt`).

If you use testcase-specific scripts, install additional dependencies documented alongside those scripts.

### API configuration

For LLM-enabled paths, configure required keys in the environment files used by your selected flow. Common locations in this repository include GraphRAG-related `.env` files under the core data directories.

Use your own secret values and do not commit private API keys.

## Running core workflow

### 1) Start embedding proxy

Run local embedding service first so graph/indexing steps can resolve embeddings.

### 2) Run pipeline entrypoint

From the core pipeline `src/` directory, run the main orchestration script used by your current task mode.

### 3) Inspect generated outputs

After run completion, inspect the latest folder in the project's `logs/` directory.

Typical run folders include files such as:

- `nl_plans.txt`
- `sva_details.csv`
- generated assertions in `tbs/`
- auxiliary diagnostics and decision logs

## Standalone TC3 quality checker

`TestCase/TC3/src/sva_batch_filter_repair.py` provides isolated filtering and syntax validation without requiring full pipeline execution.

Capabilities:

- optional Loop A alias-name validation,
- Loop B Verible syntax validation,
- optional repair hook interface,
- structured outputs in accepted/discarded and report files,
- per-run and per-iteration logs.

Current default mode is Verible-focused validation; Loop A can be enabled explicitly via CLI flag.

## Verible notes

The checker supports multiple ways to resolve `verible-verilog-syntax`:

1. explicit CLI argument,
2. PATH lookup,
3. project-local fallback under `.tools/verible/...`.

If PATH-based installation is unavailable on a machine, local binary fallback can be used.

## Development and testing notes

Repository contains helper tests and diagnostics scripts at root, including import checks and API smoke tests.

When modifying generation or checker behavior, validate with:

- at least one short end-to-end run,
- one malformed-SVA syntax rejection scenario,
- one known-good SVA acceptance scenario.

## Known limitations

- full multiagent orchestration with shared GPTCache remains an architectural plan and is not yet merged as a single production controller,
- repair function hooks in standalone checker may still require full LLM-backed implementation,
- mapping edge creation can be sensitive to mention normalization and confidence thresholds.

## Future work

- complete multiagent controller with role-based model routing,
- add semantic/formal validity stage beyond syntax checks,
- expose run metrics dashboard (cost, latency, cache hit ratio, acceptance rate),
- strengthen alignment fallback and graph edge materialization robustness.

## Reference notes for report preparation

The following documents are prepared for report/PPT generation:

- `report_notes/1_signal_mapping.txt`
- `report_notes/2_two_phase_verible_checking.txt`
- `report_notes/3_multiagent_gptcache_plan.txt`
- the consolidated master note file in `report_notes/`

Use the consolidated master note for one-shot LLM ingestion when generating report narrative.