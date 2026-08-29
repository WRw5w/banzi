#!/usr/bin/env python3
"""Compile and execute all six refactored C++ regression programs."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCES = [
    ROOT / "tests" / name
    for name in (
        "refactored_strings.cpp",
        "refactored_mst.cpp",
        "refactored_core.cpp",
        "refactored_graph.cpp",
        "refactored_dp_geometry.cpp",
        "refactored_advanced.cpp",
    )
]


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    compiler = shutil.which("g++")
    if compiler is None:
        print("g++ not found", file=sys.stderr)
        return 2
    tmp_root = ROOT / "tmp"
    tmp_root.mkdir(exist_ok=True)
    failures = 0
    with tempfile.TemporaryDirectory(prefix="refactored-", dir=tmp_root) as directory:
        build_dir = Path(directory)
        for source in SOURCES:
            executable = build_dir / f"{source.stem}.exe"
            compile_result = subprocess.run(
                [compiler, "-std=c++17", "-O2", "-Wall", "-Wextra", str(source), "-o", str(executable)],
                cwd=ROOT, text=True, encoding="utf-8", errors="replace",
                capture_output=True, timeout=60,
            )
            if compile_result.returncode:
                failures += 1
                print(f"[FAIL] {source.name}: compile")
                print((compile_result.stdout + compile_result.stderr).strip())
                continue
            run_result = subprocess.run(
                [str(executable)], cwd=ROOT, text=True, encoding="utf-8",
                errors="replace", capture_output=True, timeout=60,
            )
            if run_result.returncode:
                failures += 1
                print(f"[FAIL] {source.name}: run")
                print((run_result.stdout + run_result.stderr).strip())
            else:
                detail = (run_result.stdout + run_result.stderr).strip()
                print(f"[PASS] {source.name}" + (f": {detail}" if detail else ""))
    print(f"summary: PASS={len(SOURCES)-failures}, FAIL={failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
