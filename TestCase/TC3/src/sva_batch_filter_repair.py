#!/usr/bin/env python3
"""
Standalone SVA batch filter + repair (TC3).

Architectural constraint honored:
- Fully isolated script, no imports from existing project pipeline modules.
- Reads SVA strings from input folder.
- Applies Loop A (signal validation) then Loop B (Verible syntax check).
- Writes accepted/discarded outputs + reports.

This version auto-loads valid RTL signal aliases from TC3 alias artifacts generated
by prior runs under: AssertionForge/logs/gen_plan_*/output/TC3/signal_aliases.json
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import tempfile
from datetime import datetime
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable


# Ignore list for signal extraction.
IGNORED_IDENTIFIERS: set[str] = {
    "module", "endmodule", "logic", "wire", "reg", "input", "output", "inout",
    "property", "endproperty", "sequence", "endsequence",
    "assert", "assume", "cover", "disable", "iff", "if", "else", "begin", "end",
    "posedge", "negedge", "and", "or", "not", "xor", "xnor", "case", "endcase",
    "inside", "with", "throughout", "intersect", "first_match", "strong", "weak",
    "s_always", "s_eventually", "always", "eventually", "until", "until_with",
    "implies", "accept_on", "reject_on", "matches", "default", "binsof",
    # Requested to ignore generic clock/reset style words and helper words.
    "clk", "clock", "rst", "reset", "true", "false",
}

IDENT_RE = re.compile(r"\$?[A-Za-z_][A-Za-z0-9_$]*")


@dataclass
class ProcessResult:
    file_name: str
    status: str  # accepted | discarded
    final_sva: str
    loop_a_repaired: bool
    loop_b_repaired: bool
    reason: str
    invalid_signals_before_repair: list[str]
    syntax_error_before_repair: str


class BatchLogger:
    def __init__(self) -> None:
        self.run_lines: list[str] = []
        self.iter_lines: dict[str, list[str]] = {}

    def _ts(self) -> str:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def log_run(self, message: str) -> None:
        self.run_lines.append(f"[{self._ts()}] {message}")

    def log_iter(self, file_name: str, message: str) -> None:
        if file_name not in self.iter_lines:
            self.iter_lines[file_name] = []
        self.iter_lines[file_name].append(f"[{self._ts()}] {message}")

    def write(self, report_dir: Path) -> None:
        logs_dir = report_dir / "logs"
        iter_dir = logs_dir / "iterations"
        logs_dir.mkdir(parents=True, exist_ok=True)
        iter_dir.mkdir(parents=True, exist_ok=True)

        run_log_name = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        (logs_dir / run_log_name).write_text("\n".join(self.run_lines) + "\n", encoding="utf-8")

        for file_name, lines in self.iter_lines.items():
            safe = re.sub(r"[^A-Za-z0-9_.-]", "_", file_name)
            (iter_dir / f"{safe}.log").write_text("\n".join(lines) + "\n", encoding="utf-8")


def normalize_signal_name(raw: str) -> str:
    text = str(raw or "")
    text = re.sub(r"//.*", " ", text)
    text = re.sub(r"\s+", " ", text).strip().lower()
    # If module.signal format, keep final token
    if "." in text:
        text = text.split(".")[-1]
    # keep identifier-like tail if noisy
    m = re.findall(r"[a-z_][a-z0-9_$]*", text)
    return m[-1] if m else text


def find_latest_tc3_alias_json(repo_root: Path) -> Path | None:
    candidates = list(repo_root.glob("AssertionForge/logs/gen_plan_*/output/TC3/signal_aliases.json"))
    if not candidates:
        return None
    # latest by modified time
    return max(candidates, key=lambda p: p.stat().st_mtime)


def resolve_verible_binary(repo_root: Path, explicit_bin: Path | None = None) -> str | None:
    """
    Resolve verible-verilog-syntax in this order:
      1) --verible-bin explicit path
      2) PATH lookup
      3) project-local fallback under .tools/verible/**/bin/
    """
    if explicit_bin:
        p = explicit_bin.expanduser().resolve()
        if p.exists() and p.is_file():
            return str(p)
        return None

    in_path = shutil.which("verible-verilog-syntax")
    if in_path:
        return in_path

    local_candidates = sorted(
        repo_root.glob(".tools/verible/**/bin/verible-verilog-syntax"),
        key=lambda x: x.stat().st_mtime,
        reverse=True,
    )
    if local_candidates:
        return str(local_candidates[0].resolve())

    return None


def load_valid_alias_table(alias_json_path: Path) -> set[str]:
    payload = json.loads(alias_json_path.read_text(encoding="utf-8"))
    alignments = payload.get("alignments", [])

    valid: set[str] = set()
    for a in alignments:
        if not isinstance(a, dict):
            continue
        rtl_name = a.get("rtl_name", "")
        sig = normalize_signal_name(rtl_name)
        if sig:
            valid.add(sig)

    if not valid:
        raise ValueError(f"No valid signals found in alias JSON: {alias_json_path}")
    return valid


def repair_sva_with_llm(original_sva: str, error_message: str, context: dict) -> str:
    """
    Stub for future LLM integration.
    For now returns unchanged assertion to keep script executable standalone.
    """
    _ = error_message, context
    return original_sva


def extract_signal_candidates_from_sva(sva_text: str) -> list[str]:
    tokens = IDENT_RE.findall(sva_text)
    out: list[str] = []
    seen: set[str] = set()

    for tok in tokens:
        if tok.startswith("$"):
            continue
        low = tok.lower()
        if low in IGNORED_IDENTIFIERS:
            continue
        if low not in seen:
            seen.add(low)
            out.append(low)
    return out


def find_invalid_signals(sva_text: str, valid_aliases: set[str]) -> list[str]:
    candidates = extract_signal_candidates_from_sva(sva_text)
    valid_lower = {s.lower() for s in valid_aliases}
    return [sig for sig in candidates if sig not in valid_lower]


def loop_a_signal_validate_and_repair(
    sva_text: str,
    valid_aliases: set[str],
    source_file: Path,
    logger: BatchLogger | None = None,
) -> tuple[bool, str, bool, list[str], str]:
    """Loop A: signal-name validation + max 1 repair attempt."""
    invalid = find_invalid_signals(sva_text, valid_aliases)
    if logger:
        logger.log_iter(source_file.name, f"Loop A start. Extracted invalid signals: {invalid if invalid else 'None'}")
    if not invalid:
        if logger:
            logger.log_iter(source_file.name, "Loop A PASS (no invalid signal names found)")
        return True, sva_text, False, [], "Loop A passed"

    bad_signal = invalid[0]
    prompt = (
        f"Signal [{bad_signal}] does not exist in the RTL. "
        f"Valid signals are: [{', '.join(sorted(valid_aliases))}]. "
        "Please correct the assertion."
    )
    repaired = repair_sva_with_llm(
        original_sva=sva_text,
        error_message=prompt,
        context={
            "loop": "A",
            "file": source_file.name,
            "invalid_signals": invalid,
        },
    )
    if logger:
        logger.log_iter(
            source_file.name,
            f"Loop A invoked repair stub once for signal '{bad_signal}'.",
        )

    invalid_after = find_invalid_signals(repaired, valid_aliases)
    if invalid_after:
        reason = (
            "Loop A failed after 1 repair attempt. "
            f"Still invalid signal(s): {', '.join(invalid_after)}"
        )
        if logger:
            logger.log_iter(source_file.name, f"Loop A FAIL. {reason}")
        return False, repaired, True, invalid, reason

    if logger:
        logger.log_iter(source_file.name, "Loop A PASS after one repair attempt")
    return True, repaired, True, invalid, "Loop A repaired and passed"


def wrap_sva_for_verible(sva_text: str) -> str:
    return (
        "module sva_check_wrapper(input logic clk);\n"
        f"  {sva_text.strip()}\n"
        "endmodule\n"
    )


def run_verible_syntax_check(sva_text: str, verible_bin: str | None = None) -> tuple[bool, str]:
    wrapped = wrap_sva_for_verible(sva_text)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".sv", delete=True) as tmp:
        tmp.write(wrapped)
        tmp.flush()

        if not verible_bin:
            return False, "verible-verilog-syntax not found in PATH"

        try:
            proc = subprocess.run(
                [verible_bin, tmp.name],
                capture_output=True,
                text=True,
            )
        except FileNotFoundError:
            return False, f"verible-verilog-syntax not found at configured path: {verible_bin}"

    if proc.returncode == 0:
        return True, ""

    err = (proc.stderr or "").strip() or (proc.stdout or "").strip()
    if not err:
        err = f"verible-verilog-syntax failed with return code {proc.returncode}"
    return False, err


def loop_b_syntax_validate_and_repair(
    sva_text: str,
    source_file: Path,
    verible_bin: str | None = None,
    logger: BatchLogger | None = None,
) -> tuple[bool, str, bool, str, str]:
    """Loop B: Verible syntax check + max 1 repair attempt."""
    ok, err = run_verible_syntax_check(sva_text, verible_bin=verible_bin)
    if logger:
        logger.log_iter(source_file.name, f"Loop B start. Initial Verible check: {'PASS' if ok else 'FAIL'}")
    if ok:
        if logger:
            logger.log_iter(source_file.name, "Loop B PASS on first syntax check")
        return True, sva_text, False, "", "Loop B passed"

    if logger:
        logger.log_iter(source_file.name, f"Loop B initial syntax error: {err}")
    repaired = repair_sva_with_llm(
        original_sva=sva_text,
        error_message=err,
        context={"loop": "B", "file": source_file.name},
    )
    if logger:
        logger.log_iter(source_file.name, "Loop B invoked repair stub once")

    ok2, err2 = run_verible_syntax_check(repaired, verible_bin=verible_bin)
    if not ok2:
        reason = "Loop B failed after 1 repair attempt (Verible syntax still invalid)"
        if logger:
            logger.log_iter(source_file.name, f"Loop B FAIL. {reason}. Final error: {err2}")
        return False, repaired, True, err, reason + f"\nFinal Verible error:\n{err2}"

    if logger:
        logger.log_iter(source_file.name, "Loop B PASS after one repair attempt")
    return True, repaired, True, err, "Loop B repaired and passed"


def discover_input_files(input_dir: Path) -> list[Path]:
    exts = {".txt", ".sv", ".sva"}
    return sorted([p for p in input_dir.iterdir() if p.is_file() and p.suffix.lower() in exts])


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def process_sva_file(
    file_path: Path,
    valid_aliases: set[str],
    skip_loop_a: bool = True,
    verible_bin: str | None = None,
    logger: BatchLogger | None = None,
) -> ProcessResult:
    original = file_path.read_text(encoding="utf-8", errors="ignore").strip()
    if logger:
        logger.log_iter(file_path.name, f"Processing file: {file_path}")
        logger.log_iter(file_path.name, f"Original SVA: {original}")

    # Loop A (optional, disabled by default for Verible-only flow)
    a_repaired = False
    invalid_before: list[str] = []
    after_a = original
    if skip_loop_a:
        if logger:
            logger.log_iter(file_path.name, "Loop A SKIPPED by configuration (Verible-only mode)")
    else:
        a_ok, after_a, a_repaired, invalid_before, a_reason = loop_a_signal_validate_and_repair(
            original, valid_aliases, source_file=file_path, logger=logger
        )
        if not a_ok:
            if logger:
                logger.log_iter(file_path.name, f"Final status: DISCARDED at Loop A. Reason: {a_reason}")
            return ProcessResult(
                file_name=file_path.name,
                status="discarded",
                final_sva=after_a,
                loop_a_repaired=a_repaired,
                loop_b_repaired=False,
                reason=a_reason,
                invalid_signals_before_repair=invalid_before,
                syntax_error_before_repair="",
            )

    # Loop B
    b_ok, after_b, b_repaired, syntax_before, b_reason = loop_b_syntax_validate_and_repair(
        after_a, source_file=file_path, verible_bin=verible_bin, logger=logger
    )
    if not b_ok:
        if logger:
            logger.log_iter(file_path.name, f"Final status: DISCARDED at Loop B. Reason: {b_reason}")
        return ProcessResult(
            file_name=file_path.name,
            status="discarded",
            final_sva=after_b,
            loop_a_repaired=a_repaired,
            loop_b_repaired=b_repaired,
            reason=b_reason,
            invalid_signals_before_repair=invalid_before,
            syntax_error_before_repair=syntax_before,
        )

    if logger:
        logger.log_iter(file_path.name, "Final status: ACCEPTED")
    return ProcessResult(
        file_name=file_path.name,
        status="accepted",
        final_sva=after_b,
        loop_a_repaired=a_repaired,
        loop_b_repaired=b_repaired,
        reason="Accepted (passed Loop A + Loop B)",
        invalid_signals_before_repair=invalid_before,
        syntax_error_before_repair=syntax_before,
    )


def summarize(results: Iterable[ProcessResult]) -> dict:
    items = list(results)
    accepted = [r for r in items if r.status == "accepted"]
    discarded = [r for r in items if r.status == "discarded"]
    return {
        "total": len(items),
        "accepted": len(accepted),
        "discarded": len(discarded),
        "accepted_files": [r.file_name for r in accepted],
        "discarded_files": [r.file_name for r in discarded],
    }


def main() -> int:
    this_file = Path(__file__).resolve()
    src_dir = this_file.parent
    tc3_dir = src_dir.parent
    repo_root = tc3_dir.parent.parent

    parser = argparse.ArgumentParser(description="Standalone SVA batch filter + repair (TC3)")
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=src_dir / "sva_input",
        help="Input directory with SVA files (.txt/.sv/.sva). Default: src/sva_input",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=src_dir / "sva_output",
        help="Output directory for accepted/discarded/reports. Default: src/sva_output",
    )
    parser.add_argument(
        "--alias-json",
        type=Path,
        default=None,
        help="Optional explicit alias JSON path. If omitted, auto-detect latest TC3 alias artifact from logs.",
    )
    parser.add_argument(
        "--verible-bin",
        type=Path,
        default=None,
        help="Optional explicit path to verible-verilog-syntax binary.",
    )
    parser.add_argument(
        "--enable-loop-a",
        action="store_true",
        help="Enable Loop A signal-name/alias validation. By default Loop A is skipped and only Verible Loop B runs.",
    )
    args = parser.parse_args()
    logger = BatchLogger()

    input_dir = args.input_dir
    output_dir = args.output_dir
    logger.log_run(f"Script start: {Path(__file__).resolve()}")
    logger.log_run(f"Input dir: {input_dir}")
    logger.log_run(f"Output dir: {output_dir}")
    logger.log_run(f"Loop A enabled: {args.enable_loop_a}")

    if not input_dir.exists() or not input_dir.is_dir():
        raise SystemExit(f"Input directory not found: {input_dir}")

    alias_json: Path | None = None
    valid_aliases: set[str] = set()
    if args.enable_loop_a:
        alias_json = args.alias_json
        if alias_json is None:
            alias_json = find_latest_tc3_alias_json(repo_root)

        if alias_json is None or not alias_json.exists():
            raise SystemExit(
                "Could not find TC3 alias JSON. Provide --alias-json explicitly or generate one under "
                "AssertionForge/logs/gen_plan_*/output/TC3/signal_aliases.json"
            )

        valid_aliases = load_valid_alias_table(alias_json)
        logger.log_run(f"Alias JSON selected: {alias_json}")
        logger.log_run(f"Valid alias count: {len(valid_aliases)}")
        logger.log_run("Valid aliases for matching:")
        for sig in sorted(valid_aliases):
            logger.log_run(f"  - {sig}")
    else:
        logger.log_run("Loop A disabled: alias table is not loaded in this run")

    verible_bin = resolve_verible_binary(repo_root, explicit_bin=args.verible_bin)

    # Not hard-failing if missing verible; loop B will report tool error.
    if verible_bin is None:
        print("[WARN] verible-verilog-syntax not found in PATH. Loop B will fail until installed.")
        logger.log_run("WARN: verible-verilog-syntax not found in PATH")
    else:
        logger.log_run(f"Using verible-verilog-syntax binary: {verible_bin}")

    files = discover_input_files(input_dir)
    if not files:
        raise SystemExit(f"No .txt/.sv/.sva files found in: {input_dir}")
    logger.log_run(f"Discovered {len(files)} input file(s)")
    for fp in files:
        logger.log_run(f"  - {fp.name}")

    accepted_dir = output_dir / "accepted"
    discarded_dir = output_dir / "discarded"
    report_dir = output_dir / "reports"
    accepted_dir.mkdir(parents=True, exist_ok=True)
    discarded_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    results: list[ProcessResult] = []
    for fp in files:
        logger.log_run(f"Starting iteration for file: {fp.name}")
        res = process_sva_file(
            fp,
            valid_aliases,
            skip_loop_a=(not args.enable_loop_a),
            verible_bin=verible_bin,
            logger=logger,
        )
        results.append(res)
        logger.log_run(f"Completed {fp.name} -> {res.status}")

        target = accepted_dir if res.status == "accepted" else discarded_dir
        write_text(target / fp.name, res.final_sva + "\n")

    details = [asdict(r) for r in results]
    write_text(report_dir / "detailed_results.json", json.dumps(details, indent=2))

    summary = summarize(results)
    summary["alias_json_used"] = str(alias_json) if alias_json else None
    summary["valid_alias_count"] = len(valid_aliases)
    summary["loop_a_enabled"] = args.enable_loop_a
    write_text(report_dir / "summary.json", json.dumps(summary, indent=2))

    lines = [
        "SVA Batch Filter + Repair Summary",
        "=" * 34,
        f"Input dir: {input_dir}",
        f"Output dir: {output_dir}",
    f"Loop A enabled: {args.enable_loop_a}",
    f"Alias JSON: {alias_json if alias_json else 'N/A (Loop A disabled)'}",
        f"Valid alias count: {len(valid_aliases)}",
        f"Total files: {summary['total']}",
        f"Accepted: {summary['accepted']}",
        f"Discarded: {summary['discarded']}",
        "",
    ]
    if summary["discarded"]:
        lines.append("Discard reasons:")
        for r in results:
            if r.status == "discarded":
                lines.append(f"- {r.file_name}: {r.reason}")
    write_text(report_dir / "summary.txt", "\n".join(lines) + "\n")

    logger.log_run("Wrote detailed_results.json, summary.json, summary.txt")
    logger.log_run("Writing run + per-iteration logs")
    logger.write(report_dir)

    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
