#!/usr/bin/env python3
"""Extract formal LaTeX listings and run manifest-driven differential tests."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = ROOT / "tests" / "differential" / "manifest.json"
INJECTION_MARKER = "// @@@TEMPLATE@@@"


@dataclass
class Result:
    case_id: str
    status: str
    detail: str = ""


def load_manifest(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1:
        raise ValueError("manifest schema_version must be 1")
    cases = data.get("cases")
    if not isinstance(cases, list):
        raise ValueError("manifest cases must be a list")
    seen: set[str] = set()
    for case in cases:
        required = {"id", "source", "contains", "harness", "expected"}
        missing = required - case.keys()
        if missing:
            raise ValueError(f"case {case.get('id', '<unknown>')} misses {sorted(missing)}")
        if case["id"] in seen:
            raise ValueError(f"duplicate case id: {case['id']}")
        if case["expected"] not in {"pass", "xfail"}:
            raise ValueError(f"invalid expected status for {case['id']}")
        failure_stage = case.get("expected_failure_stage", "run")
        if failure_stage not in {"compile", "run"}:
            raise ValueError(f"invalid expected_failure_stage for {case['id']}")
        if case["expected"] == "pass" and "expected_failure_stage" in case:
            raise ValueError(
                f"pass case {case['id']} must not define expected_failure_stage"
            )
        if case["expected"] == "xfail" and not case.get("expected_failure_contains"):
            raise ValueError(f"xfail case {case['id']} requires expected_failure_contains")
        seen.add(case["id"])
    return cases


def extract_listing(source: Path, needle: str) -> str:
    text = source.read_text(encoding="utf-8")
    blocks: list[str] = []
    cursor = 0
    begin_token = "\\begin{lstlisting}"
    end_token = "\\end{lstlisting}"
    while True:
        begin = text.find(begin_token, cursor)
        if begin < 0:
            break
        body_start = text.find("\n", begin)
        if body_start < 0:
            raise ValueError(f"unterminated lstlisting header in {source}")
        end = text.find(end_token, body_start)
        if end < 0:
            raise ValueError(f"unterminated lstlisting body in {source}")
        body = text[body_start + 1 : end]
        if needle in body:
            blocks.append(body.rstrip() + "\n")
        cursor = end + len(end_token)
    if len(blocks) != 1:
        raise ValueError(
            f"selector {needle!r} matched {len(blocks)} listings in {source}; expected exactly one"
        )
    return blocks[0]


def build_translation_unit(listing: str, harness: Path) -> str:
    text = harness.read_text(encoding="utf-8")
    if text.count(INJECTION_MARKER) != 1:
        raise ValueError(f"{harness} must contain exactly one {INJECTION_MARKER}")
    return text.replace(INJECTION_MARKER, listing)


def run_case(case: dict, compiler: str, build_dir: Path) -> Result:
    case_id = case["id"]
    try:
        source = ROOT / case["source"]
        harness = ROOT / case["harness"]
        listing = extract_listing(source, case["contains"])
        translation_unit = build_translation_unit(listing, harness)
    except (OSError, ValueError) as exc:
        return Result(case_id, "ERROR", str(exc))

    safe_name = case_id.replace(".", "_").replace("-", "_")
    cpp_path = build_dir / f"{safe_name}.cpp"
    exe_path = build_dir / f"{safe_name}.exe"
    cpp_path.write_text(translation_unit, encoding="utf-8", newline="\n")

    compile_cmd = [
        compiler,
        "-std=c++17",
        "-O2",
        "-Wall",
        "-Wextra",
        str(cpp_path),
        "-o",
        str(exe_path),
    ]
    try:
        compiled = subprocess.run(
            compile_cmd,
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=case.get("compile_timeout_seconds", 30),
        )
    except subprocess.TimeoutExpired:
        return Result(case_id, "ERROR", "compilation timed out")
    if compiled.returncode != 0:
        detail = (compiled.stdout + compiled.stderr).strip()
        if case["expected"] == "xfail" and case.get(
            "expected_failure_stage", "run"
        ) == "compile":
            signature = case["expected_failure_contains"]
            if signature in detail:
                return Result(case_id, "XFAIL", detail)
            return Result(
                case_id,
                "FAIL",
                f"compile failure did not contain expected signature {signature!r}\n{detail}",
            )
        return Result(case_id, "ERROR", f"compile failed\n{detail}")

    if case["expected"] == "xfail" and case.get(
        "expected_failure_stage", "run"
    ) == "compile":
        return Result(case_id, "XPASS", "known compile failure unexpectedly compiled")

    regression_paths = [str(ROOT / item) for item in case.get("regressions", [])]
    try:
        executed = subprocess.run(
            [str(exe_path), *regression_paths],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=case.get("run_timeout_seconds", 10),
        )
    except subprocess.TimeoutExpired:
        return Result(case_id, "ERROR", "execution timed out")

    output = (executed.stdout + executed.stderr).strip()
    expected = case["expected"]
    if expected == "pass":
        if executed.returncode == 0:
            return Result(case_id, "PASS", output)
        return Result(case_id, "FAIL", output or f"exit code {executed.returncode}")
    if executed.returncode != 0:
        signature = case.get("expected_failure_contains")
        if signature and signature not in output:
            return Result(
                case_id,
                "FAIL",
                f"failure did not contain expected signature {signature!r}\n{output}",
            )
        return Result(case_id, "XFAIL", output or f"exit code {executed.returncode}")
    return Result(case_id, "XPASS", output or "known failure unexpectedly passed")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--case", action="append", dest="case_ids", help="run one case id")
    parser.add_argument("--list", action="store_true", help="list available cases")
    parser.add_argument("--compiler", default="g++", help="C++ compiler command")
    return parser.parse_args()


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    args = parse_args()
    manifest_path = args.manifest.resolve()
    try:
        cases = load_manifest(manifest_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"manifest error: {exc}", file=sys.stderr)
        return 2

    if args.list:
        for case in cases:
            print(f"{case['id']}\t{case['expected']}\t{case.get('description', '')}")
        return 0

    if args.case_ids:
        selected = set(args.case_ids)
        known = {case["id"] for case in cases}
        unknown = sorted(selected - known)
        if unknown:
            print(f"unknown case ids: {', '.join(unknown)}", file=sys.stderr)
            return 2
        cases = [case for case in cases if case["id"] in selected]

    compiler = shutil.which(args.compiler)
    if compiler is None:
        print(f"compiler not found: {args.compiler}", file=sys.stderr)
        return 2

    tmp_root = ROOT / "tmp"
    tmp_root.mkdir(exist_ok=True)
    results: list[Result] = []
    with tempfile.TemporaryDirectory(prefix="differential-", dir=tmp_root) as directory:
        build_dir = Path(directory)
        for case in cases:
            result = run_case(case, compiler, build_dir)
            results.append(result)
            print(f"[{result.status:5}] {result.case_id}")
            if result.detail:
                for line in result.detail.splitlines():
                    print(f"        {line}")

    counts = {status: 0 for status in ("PASS", "XFAIL", "FAIL", "XPASS", "ERROR")}
    for result in results:
        counts[result.status] += 1
    print(
        "summary: "
        + ", ".join(f"{name}={count}" for name, count in counts.items())
    )
    return 1 if counts["FAIL"] or counts["XPASS"] or counts["ERROR"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
