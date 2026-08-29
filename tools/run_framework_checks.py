#!/usr/bin/env python3
"""Run block-specific structural contracts for true formal-code frameworks.

This command deliberately does not call these checks algorithm verification.
Complete implementations belong in tests/contracts or tests/differential. A
FRAMEWORK entry is accepted only when its exact, digest-bound snippet satisfies
its own required/forbidden structure and the global anti-placeholder rules.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from dataclasses import dataclass

import audit_listing_coverage as coverage


PLACEHOLDER_RE = re.compile(
    r"\b(?:TODO|FIXME|TBD|XXX)\b|\.\.\."
)
IDENTIFIER_RE = re.compile(r"[A-Za-z_]\w*")
MALFORMED_RETURN_RE = re.compile(r"\breturn\s+[^;{}\n]*[+\-*/%&|^]\s*;")
TRIVIAL_FUNCTION_RE = re.compile(
    r"\b(?:int|long\s+long|bool|double|auto)\s+([A-Za-z_]\w*)\s*"
    r"\([^;{}]*\)\s*\{\s*(?:return\s+(?:0|1|true|false)\s*;)?\s*\}",
    re.DOTALL,
)
EMPTY_FUNCTION_RE = re.compile(
    r"\b(?:void|int|long\s+long|bool|double|auto)\s+([A-Za-z_]\w*)\s*"
    r"\([^;{}]*\)\s*\{\s*\}", re.DOTALL
)
OPEN_TO_CLOSE = {"(": ")", "[": "]", "{": "}"}
CLOSE_TO_OPEN = {value: key for key, value in OPEN_TO_CLOSE.items()}


@dataclass
class CheckResult:
    block_id: str
    source: str
    ok: bool
    detail: str = ""


def strip_cpp_comments_and_literals(text: str) -> str:
    """Replace comments and string/character literals while preserving newlines."""
    result: list[str] = []
    index = 0
    state = "code"
    raw_end = ""
    while index < len(text):
        char = text[index]
        nxt = text[index + 1] if index + 1 < len(text) else ""
        if state == "code":
            if char == "/" and nxt == "/":
                result.extend("  ")
                index += 2
                state = "line_comment"
                continue
            if char == "/" and nxt == "*":
                result.extend("  ")
                index += 2
                state = "block_comment"
                continue
            if char in {'"', "'"}:
                result.append(" ")
                index += 1
                state = "string" if char == '"' else "char"
                continue
            if char == "R" and nxt == '"':
                delimiter_end = text.find("(", index + 2)
                if delimiter_end >= 0:
                    delimiter = text[index + 2 : delimiter_end]
                    if len(delimiter) <= 16 and not any(
                        item in delimiter for item in " ()\\\t\r\n"
                    ):
                        raw_end = ")" + delimiter + '"'
                        result.extend(" " * (delimiter_end - index + 1))
                        index = delimiter_end + 1
                        state = "raw"
                        continue
            result.append(char)
            index += 1
            continue
        if state == "line_comment":
            if char == "\n":
                result.append("\n")
                state = "code"
            else:
                result.append(" ")
            index += 1
            continue
        if state == "block_comment":
            if char == "*" and nxt == "/":
                result.extend("  ")
                index += 2
                state = "code"
            else:
                result.append("\n" if char == "\n" else " ")
                index += 1
            continue
        if state in {"string", "char"}:
            quote = '"' if state == "string" else "'"
            if char == "\\" and index + 1 < len(text):
                result.append(" ")
                result.append("\n" if nxt == "\n" else " ")
                index += 2
            elif char == quote:
                result.append(" ")
                index += 1
                state = "code"
            else:
                result.append("\n" if char == "\n" else " ")
                index += 1
            continue
        if state == "raw":
            if text.startswith(raw_end, index):
                result.extend(" " * len(raw_end))
                index += len(raw_end)
                state = "code"
            else:
                result.append("\n" if char == "\n" else " ")
                index += 1
    if state not in {"code", "line_comment"}:
        raise ValueError(f"unterminated {state.replace('_', ' ')}")
    return "".join(result)


def balanced_delimiters(text: str) -> str:
    stack: list[tuple[str, int]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        for char in line:
            if char in OPEN_TO_CLOSE:
                stack.append((char, line_number))
            elif char in CLOSE_TO_OPEN:
                if not stack or stack[-1][0] != CLOSE_TO_OPEN[char]:
                    return f"unexpected {char!r} at listing line {line_number}"
                stack.pop()
    if stack:
        char, line_number = stack[-1]
        return f"unclosed {char!r} from listing line {line_number}"
    return ""


def check_listing(listing: coverage.Listing) -> CheckResult:
    if listing.check != "structural_contract":
        return CheckResult(
            listing.block_id, listing.source, False, f"unsupported check {listing.check!r}"
        )
    try:
        cleaned = strip_cpp_comments_and_literals(listing.body)
    except ValueError as exc:
        return CheckResult(listing.block_id, listing.source, False, str(exc))
    if not IDENTIFIER_RE.search(cleaned):
        return CheckResult(listing.block_id, listing.source, False, "no code identifier")
    placeholder = PLACEHOLDER_RE.search(cleaned)
    if placeholder:
        line = cleaned.count("\n", 0, placeholder.start()) + 1
        return CheckResult(
            listing.block_id, listing.source, False,
            f"placeholder {placeholder.group()!r} at listing line {line}",
        )
    malformed = MALFORMED_RETURN_RE.search(cleaned)
    if malformed:
        line = cleaned.count("\n", 0, malformed.start()) + 1
        return CheckResult(
            listing.block_id, listing.source, False,
            f"malformed return expression at listing line {line}",
        )
    empty_functions = [
        name for name in EMPTY_FUNCTION_RE.findall(cleaned)
        if name not in listing.allowed_empty_hooks
    ]
    if empty_functions:
        return CheckResult(
            listing.block_id, listing.source, False,
            f"empty function shell {empty_functions[0]!r} is not a declared external hook",
        )
    trivial = TRIVIAL_FUNCTION_RE.search(cleaned)
    if trivial:
        return CheckResult(
            listing.block_id, listing.source, False,
            f"trivial function shell {trivial.group(1)!r}",
        )
    delimiter_error = balanced_delimiters(cleaned)
    if delimiter_error:
        return CheckResult(listing.block_id, listing.source, False, delimiter_error)
    for pattern in listing.required_patterns:
        if re.search(pattern, listing.body, re.MULTILINE | re.DOTALL) is None:
            return CheckResult(
                listing.block_id, listing.source, False,
                f"required block contract pattern not found: {pattern!r}",
            )
    for pattern in listing.forbidden_patterns:
        if re.search(pattern, listing.body, re.MULTILINE | re.DOTALL) is not None:
            return CheckResult(
                listing.block_id, listing.source, False,
                f"forbidden block contract pattern found: {pattern!r}",
            )
    return CheckResult(listing.block_id, listing.source, True)


def compiler_rejects(source: str) -> bool:
    compiler = shutil.which("g++")
    if compiler is None:
        raise RuntimeError("g++ not found; cannot run counterexample gate")
    tmp_root = coverage.ROOT / "tmp"
    tmp_root.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="framework-gate-", dir=tmp_root) as directory:
        result = subprocess.run(
            [compiler, "-std=c++17", "-fsyntax-only", "-x", "c++", "-"],
            input=source,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            cwd=directory,
            timeout=15,
        )
    return result.returncode != 0


def run_counterexample_gate() -> list[str]:
    """Return failures if the gate ever accepts known invalid counterexamples."""
    failures: list[str] = []
    for name, source in {
        "malformed-expression": "int f(){ return missing_symbol + ; }\n",
        "unresolved-placeholder": "int f(){ return XXX; }\n",
    }.items():
        try:
            rejected = compiler_rejects(source)
        except (RuntimeError, subprocess.TimeoutExpired) as exc:
            failures.append(f"{name}: {exc}")
            continue
        if not rejected:
            failures.append(f"{name}: compiler unexpectedly accepted counterexample")
    shell = coverage.Listing(
        source="<counterexample>", ordinal=1, line=1,
        body="int maxflow(){return 0;}\n", headings={}, category="framework",
        check="structural_contract", required_patterns=[r"\bmaxflow\s*\("],
    )
    if check_listing(shell).ok:
        failures.append("trivial-maxflow-shell: structural gate accepted counterexample")
    return failures


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verbose", action="store_true", help="print every framework result")
    return parser.parse_args()


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    args = parse_args()
    counterexample_failures = run_counterexample_gate()
    for detail in counterexample_failures:
        print(f"[FAIL] counterexample gate: {detail}")
    if counterexample_failures:
        return 1
    print("[PASS] counterexample gate: syntax, unresolved placeholder, trivial shell")
    try:
        listings, _ = coverage.inventory_formal_tree()
        coverage.apply_differential_cases(listings)
        coverage.apply_contract_cases(listings)
        coverage.apply_explicit_classifications(listings)
    except ValueError as exc:
        print(f"framework check error: {exc}", file=sys.stderr)
        return 2

    pending = [listing for listing in listings if listing.category == "pending"]
    if pending:
        print(
            f"framework check error: {len(pending)} formal listings remain PENDING",
            file=sys.stderr,
        )
        return 2
    frameworks = [listing for listing in listings if listing.category == "framework"]
    results = [check_listing(listing) for listing in frameworks]
    failures = [result for result in results if not result.ok]
    if args.verbose:
        for result in results:
            status = "PASS" if result.ok else "FAIL"
            suffix = f": {result.detail}" if result.detail else ""
            print(f"[{status:4}] {result.block_id}{suffix}")
    else:
        per_source = Counter(result.source for result in results if result.ok)
        for source, count in per_source.items():
            print(f"[PASS] {source}: {count} framework structural contracts")
        for result in failures:
            print(f"[FAIL] {result.block_id}: {result.detail}")
    print(
        f"summary: FRAMEWORK={len(results)}, STRUCTURAL_PASS={len(results) - len(failures)}, "
        f"FAIL={len(failures)}, PENDING={len(pending)}"
    )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
