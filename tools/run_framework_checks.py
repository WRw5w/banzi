#!/usr/bin/env python3
"""Run baseline static checks for every classified formal framework listing."""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from dataclasses import dataclass

import audit_listing_coverage as coverage


PLACEHOLDER_RE = re.compile(r"\b(?:TODO|FIXME|TBD)\b|\.\.\.")
IDENTIFIER_RE = re.compile(r"[A-Za-z_]\w*")
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
            continue
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
    if listing.check != "static":
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
            listing.block_id,
            listing.source,
            False,
            f"placeholder {placeholder.group()!r} at listing line {line}",
        )
    delimiter_error = balanced_delimiters(cleaned)
    if delimiter_error:
        return CheckResult(listing.block_id, listing.source, False, delimiter_error)
    return CheckResult(listing.block_id, listing.source, True)


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
    try:
        listings, _ = coverage.inventory_formal_tree()
        coverage.apply_differential_cases(listings)
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
            print(f"[PASS] {source}: {count} framework listings")
        for result in failures:
            print(f"[FAIL] {result.block_id}: {result.detail}")
    print(
        f"summary: FRAMEWORK={len(results)}, STATIC_PASS={len(results) - len(failures)}, "
        f"FAIL={len(failures)}, PENDING={len(pending)}"
    )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
