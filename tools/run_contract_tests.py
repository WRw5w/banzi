#!/usr/bin/env python3
"""Extract formal listings and run compile/contract harnesses."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

import audit_listing_coverage as coverage


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "tests" / "contracts" / "manifest.json"


@dataclass
class Result:
    case_id: str
    status: str
    detail: str = ""


def load_cases() -> list[dict]:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1 or not isinstance(data.get("cases"), list):
        raise ValueError("unsupported contract manifest schema")
    seen_ids: set[str] = set()
    for case in data["cases"]:
        required = {"id", "description", "harness", "snippets"}
        if not isinstance(case, dict) or not required <= case.keys():
            raise ValueError(f"contract case must define {sorted(required)}")
        if case["id"] in seen_ids:
            raise ValueError(f"duplicate contract case id: {case['id']}")
        seen_ids.add(case["id"])
        if not isinstance(case["snippets"], list) or not case["snippets"]:
            raise ValueError(f"contract case {case['id']} has no snippets")
        markers: set[str] = set()
        for snippet in case["snippets"]:
            snippet_required = {"source", "contains", "marker"}
            if not isinstance(snippet, dict) or not snippet_required <= snippet.keys():
                raise ValueError(
                    f"contract case {case['id']} snippet must define "
                    f"{sorted(snippet_required)}"
                )
            marker = snippet["marker"]
            if not isinstance(snippet.get("support", False), bool):
                raise ValueError(
                    f"contract case {case['id']} snippet support must be boolean"
                )
            if marker in markers:
                raise ValueError(f"contract case {case['id']} repeats marker {marker!r}")
            markers.add(marker)
    return data["cases"]


def build_translation_unit(case: dict) -> str:
    harness_path = ROOT / case["harness"]
    text = harness_path.read_text(encoding="utf-8")
    for snippet in case["snippets"]:
        marker = snippet["marker"]
        if text.count(marker) != 1:
            raise ValueError(
                f"{case['harness']} must contain marker {marker!r} exactly once"
            )
        listing = coverage.extract_listing(
            ROOT / snippet["source"], snippet["contains"]
        )
        text = text.replace(marker, listing)
    return text


def run_case(case: dict, compiler: str, build_dir: Path) -> Result:
    case_id = case["id"]
    try:
        translation_unit = build_translation_unit(case)
    except (OSError, ValueError) as exc:
        return Result(case_id, "ERROR", str(exc))
    safe_name = case_id.replace(".", "_").replace("-", "_")
    cpp_path = build_dir / f"{safe_name}.cpp"
    exe_path = build_dir / f"{safe_name}.exe"
    cpp_path.write_text(translation_unit, encoding="utf-8", newline="\n")
    command = [
        compiler,
        "-std=c++17",
        "-O2",
        "-Wall",
        "-Wextra",
        "-Werror=return-type",
        str(cpp_path),
        "-o",
        str(exe_path),
    ]
    try:
        compiled = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=case.get("compile_timeout_seconds", 30),
        )
    except subprocess.TimeoutExpired:
        return Result(case_id, "ERROR", "compilation timed out")
    if compiled.returncode:
        output = (compiled.stdout + compiled.stderr).strip()
        return Result(case_id, "FAIL", f"compile failed\n{output}")
    if case.get("compile_only", False):
        return Result(case_id, "PASS", "compiled")
    try:
        executed = subprocess.run(
            [str(exe_path)],
            cwd=ROOT,
            input=case.get("stdin"),
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=case.get("run_timeout_seconds", 15),
        )
    except subprocess.TimeoutExpired:
        return Result(case_id, "ERROR", "execution timed out")
    output = (executed.stdout + executed.stderr).strip()
    if executed.returncode:
        return Result(case_id, "FAIL", output or f"exit code {executed.returncode}")
    expected_stdout = case.get("expected_stdout")
    if expected_stdout is not None:
        if not isinstance(expected_stdout, str):
            return Result(case_id, "ERROR", "expected_stdout must be a string")
        if executed.stdout != expected_stdout:
            return Result(
                case_id, "FAIL",
                f"stdout mismatch: expected {expected_stdout!r}, got {executed.stdout!r}",
            )
    return Result(case_id, "PASS", output)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", action="append", dest="case_ids")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--compiler", default="g++")
    return parser.parse_args()


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    args = parse_args()
    try:
        cases = load_cases()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"contract manifest error: {exc}", file=sys.stderr)
        return 2
    if args.list:
        for case in cases:
            print(f"{case['id']}\t{case['description']}")
        return 0
    if args.case_ids:
        selected = set(args.case_ids)
        known = {case["id"] for case in cases}
        unknown = sorted(selected - known)
        if unknown:
            print(f"unknown contract case ids: {', '.join(unknown)}", file=sys.stderr)
            return 2
        cases = [case for case in cases if case["id"] in selected]
    compiler = shutil.which(args.compiler)
    if compiler is None:
        print(f"compiler not found: {args.compiler}", file=sys.stderr)
        return 2
    tmp_root = ROOT / "tmp"
    tmp_root.mkdir(exist_ok=True)
    results: list[Result] = []
    with tempfile.TemporaryDirectory(prefix="contracts-", dir=tmp_root) as directory:
        build_dir = Path(directory)
        for case in cases:
            result = run_case(case, compiler, build_dir)
            results.append(result)
            print(f"[{result.status:5}] {result.case_id}")
            if result.detail:
                for line in result.detail.splitlines():
                    print(f"        {line}")
    counts = {status: 0 for status in ("PASS", "FAIL", "ERROR")}
    for result in results:
        counts[result.status] += 1
    print("summary: " + ", ".join(f"{key}={value}" for key, value in counts.items()))
    return 1 if counts["FAIL"] or counts["ERROR"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
