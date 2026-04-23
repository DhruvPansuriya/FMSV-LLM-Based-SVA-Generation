#!/usr/bin/env python3
"""
Standalone SVA batch filter + repair script.

- Reads SVA files from an input directory.
- Loop A: signal-name validation against a mock alias table + 1 repair attempt.
- Loop B: Verible syntax validation + 1 repair attempt.
- Writes accepted and discarded outputs into separate folders.

"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import tempfile
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable


# -----------------------------------------------------------------------------
# Mock alias table (replace with your real extracted alias table when ready)
# -----------------------------------------------------------------------------
VALID_SIGNAL_ALIAS_TABLE: set[str] = {
    # TC3 top-level APB/SPI + internal example names
    "nrst",
    "pclk",
    "psel",
    "penable",
    "pwrite",
    "paddr",
    "pwdata",
    "prdata",
    "pready",
    "sck",
    "mosi",
    "miso",
    "ss_n",
    "irq_out",
    "we_n",
    # common lower-level names seen in TC3 logs
    "clk",
    "rst_n",
    "tx_start",
    "fc_en",
    "baud_div",
    "tx_data",
    "sck_out",
    "mosi_out",
    "tx_done",
    "fifo_empty",
    "ack_flag",
    "miso_in",
    "sck_in",
    "dv",
    "par_err",
    "buf_full_n",
    "rx_data",
}


# Conservative SystemVerilog keyword / token ignore set for identifier extraction.
IGNORED_IDENTIFIERS: set[str] = {
    "module",
    "endmodule",
    "logic",
    "wire",
    "reg",
    "property",
    "endproperty",
    "sequence",
    "endsequence",
    "assert",
    "assume",
    "cover",
    "disable",
    "iff",
    "if",
    "else",
    "begin",
    "end",
    "not",
    "or",
    "and",
    "xor",
    "xnor",
    "case",
    "endcase",
    "posedge",
    "negedge",
    "inside",
    "with",
    "throughout",
    "intersect",
    "first_match",
    "strong",
    "weak",
    "s_always",
    "s_eventually",
    "always",
    "eventually",
    "until",
    "until_with",
    "implies",
    "accept_on",
    "reject_on",
    "matches",
    "binsof",
    "default",
    "clk",       # requested to ignore clock-like generic names
    "clock",
    "reset",
    "rst",
    "true",
    "false",
    "input",
    "output",
}


# Regex for identifiers (supports optional leading '$' for system funcs/tasks).
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


def repair_sva_with_llm(original_sva: str, error_message: str, context: dict) -> str:
    """
    Stub for future LLM-based repair.

    TODO (future): integrate LLM call here.
    Current behavior: returns original string unchanged so pipeline can run end-to-end.
    """
    _ = error_message, context
    return original_sva


def discover_input_files(input_dir: Path) -> list[Path]:
    exts = {".txt", ".sv", ".sva"}
    return sorted([p for p in input_dir.iterdir() if p.is_file() and p.suffix.lower() in exts])


def extract_signal_candidates_from_sva(sva_text: str) -> list[str]:
    """
    Extract potential signal identifiers from SVA text.

    Rules:
    - Ignore SystemVerilog keywords and common tokens from IGNORED_IDENTIFIERS.
    - Ignore identifiers that start with '$' (e.g., $past, $rose, $stable).
    - Normalize to lowercase.
    """
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
) -> tuple[bool, str, bool, list[str], str]:
    """
    Loop A: zero-effort signal validity filter + max 1 repair attempt.

    Returns:
        success, updated_sva, repaired_flag, invalid_before_repair, reason
    """
    invalid = find_invalid_signals(sva_text, valid_aliases)
    if not invalid:
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
            "valid_alias_count": len(valid_aliases),
        },
    )

    invalid_after = find_invalid_signals(repaired, valid_aliases)
    if invalid_after:
        reason = (
            "Loop A failed after 1 repair attempt. "
            f"Still invalid signal(s): {', '.join(invalid_after)}"
        )
        return False, repaired, True, invalid, reason

    return True, repaired, True, invalid, "Loop A repaired and passed"


def wrap_sva_for_verible(sva_text: str) -> str:
    return (
        "module sva_check_wrapper(input logic clk);\n"
        f"  {sva_text.strip()}\n"
        "endmodule\n"
    )


def run_verible_syntax_check(sva_text: str) -> tuple[bool, str]:
    wrapped = wrap_sva_for_verible(sva_text)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".sv", delete=True) as tmp:
        tmp.write(wrapped)
        tmp.flush()

        proc = subprocess.run(
            ["verible-verilog-syntax", tmp.name],
            capture_output=True,
            text=True,
        )

    if proc.returncode == 0:
        return True, ""

    error = (proc.stderr or "").strip()
    if not error:
        error = (proc.stdout or "").strip()
    if not error:
        error = f"verible-verilog-syntax failed with return code {proc.returncode}"

    return False, error


def loop_b_syntax_validate_and_repair(
    sva_text: str,
    source_file: Path,
) -> tuple[bool, str, bool, str, str]:
    """
    Loop B: Verible syntax check + max 1 repair attempt.

    Returns:
        success, updated_sva, repaired_flag, syntax_error_before_repair, reason
    """
    ok, err = run_verible_syntax_check(sva_text)
    if ok:
        return True, sva_text, False, "", "Loop B passed"

    repaired = repair_sva_with_llm(
        original_sva=sva_text,
        error_message=err,
        context={"loop": "B", "file": source_file.name},
    )

    ok2, err2 = run_verible_syntax_check(repaired)
    if not ok2:
        reason = "Loop B failed after 1 repair attempt (Verible syntax still invalid)"
        return False, repaired, True, err, reason + f"\nFinal Verible error:\n{err2}"

    return True, repaired, True, err, "Loop B repaired and passed"


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def process_sva_file(file_path: Path, valid_aliases: set[str]) -> ProcessResult:
    original = file_path.read_text(encoding="utf-8", errors="ignore").strip()

    # Loop A
    a_ok, after_a, a_repaired, invalid_before, a_reason = loop_a_signal_validate_and_repair(
        original,
        valid_aliases,
        source_file=file_path,
    )
    if not a_ok:
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
        after_a,
        source_file=file_path,
    )
    if not b_ok:
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
    parser = argparse.ArgumentParser(description="Standalone SVA batch filter + repair")
    parser.add_argument(
        "--input-dir",
        type=Path,
        required=True,
        help="Directory containing input SVA files (.txt/.sv/.sva), one SVA per file",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory where accepted/discarded outputs and reports are written",
    )
    args = parser.parse_args()

    input_dir: Path = args.input_dir
    output_dir: Path = args.output_dir

    if not input_dir.exists() or not input_dir.is_dir():
        raise SystemExit(f"Input directory not found: {input_dir}")

    files = discover_input_files(input_dir)
    if not files:
        raise SystemExit(f"No .txt/.sv/.sva files found in: {input_dir}")

    accepted_dir = output_dir / "accepted"
    discarded_dir = output_dir / "discarded"
    report_dir = output_dir / "reports"

    accepted_dir.mkdir(parents=True, exist_ok=True)
    discarded_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    results: list[ProcessResult] = []

    for fp in files:
        res = process_sva_file(fp, VALID_SIGNAL_ALIAS_TABLE)
        results.append(res)

        out_path = (accepted_dir if res.status == "accepted" else discarded_dir) / fp.name
        write_text(out_path, res.final_sva + "\n")

    # Write structured reports
    details = [asdict(r) for r in results]
    write_text(report_dir / "detailed_results.json", json.dumps(details, indent=2))

    summary = summarize(results)
    write_text(report_dir / "summary.json", json.dumps(summary, indent=2))

    # Human-readable summary
    lines = [
        "SVA Batch Filter + Repair Summary",
        "=" * 34,
        f"Input dir: {input_dir}",
        f"Output dir: {output_dir}",
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

    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())