#!/usr/bin/env python3
"""Build the sole formal PDF in an isolated directory until references stabilize."""

from __future__ import annotations

import argparse
import hashlib
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENTRY = ROOT / "banzi" / "板子_大版本.tex"
OUTPUT = ROOT / "banzi" / "板子_大版本.pdf"
TMP_ROOT = ROOT / "tmp" / "pdfs"
STATE_SUFFIXES = (".aux", ".toc", ".out")
GENERATED_SUFFIXES = (
    ".aux", ".log", ".out", ".toc", ".xdv", ".synctex.gz", ".fls", ".fdb_latexmk"
)
RERUN_RE = re.compile(
    r"Rerun to get cross-references right|Label\(s\) may have changed|"
    r"Package rerunfilecheck Warning: File .* has changed|\(rerunfilecheck\).*Rerun",
    re.IGNORECASE,
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(max_passes: int) -> tuple[int, str]:
    engine = shutil.which("xelatex")
    if engine is None:
        raise RuntimeError("xelatex not found")
    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    previous_state: dict[str, str] | None = None
    with tempfile.TemporaryDirectory(prefix="formal-build-", dir=TMP_ROOT) as directory:
        build_dir = Path(directory)
        for pass_number in range(1, max_passes + 1):
            command = [
                engine,
                "-interaction=nonstopmode",
                "-halt-on-error",
                "-file-line-error",
                f"-output-directory={build_dir}",
                str(ENTRY),
            ]
            result = subprocess.run(
                command,
                cwd=ROOT,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                timeout=300,
            )
            combined = result.stdout + result.stderr
            if result.returncode:
                tail = "\n".join(combined.splitlines()[-80:])
                raise RuntimeError(f"XeLaTeX pass {pass_number} failed\n{tail}")
            stem = ENTRY.stem
            state = {
                suffix: digest(build_dir / f"{stem}{suffix}")
                for suffix in STATE_SUFFIXES
                if (build_dir / f"{stem}{suffix}").is_file()
            }
            rerun = bool(RERUN_RE.search(combined))
            stable = previous_state is not None and state == previous_state and not rerun
            print(
                f"pass {pass_number}: state={'stable' if previous_state == state else 'changed'}, "
                f"rerun_warning={'yes' if rerun else 'no'}"
            )
            if stable:
                built_pdf = build_dir / OUTPUT.name
                if not built_pdf.is_file():
                    raise RuntimeError("XeLaTeX succeeded but did not produce the formal PDF")
                staged = OUTPUT.with_suffix(".pdf.tmp")
                shutil.copy2(built_pdf, staged)
                staged.replace(OUTPUT)
                return pass_number, digest(OUTPUT)
            previous_state = state
        raise RuntimeError(
            f"cross-reference state did not stabilize without rerun warnings in {max_passes} passes"
        )


def clean_formal_directory() -> list[str]:
    removed: list[str] = []
    for suffix in GENERATED_SUFFIXES:
        path = OUTPUT.with_suffix(suffix)
        if path.is_file():
            path.unlink()
            removed.append(path.name)
    unexpected = sorted(
        path.name for path in OUTPUT.parent.iterdir()
        if path.is_file() and path.name not in {ENTRY.name, OUTPUT.name}
    )
    if unexpected:
        raise RuntimeError(
            "banzi/ contains files other than the formal TeX/PDF: " + ", ".join(unexpected)
        )
    return removed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max-passes", type=int, default=6)
    return parser.parse_args()


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = parse_args()
    if args.max_passes < 2:
        print("--max-passes must be at least 2", file=sys.stderr)
        return 2
    try:
        removed = clean_formal_directory()
        passes, pdf_hash = build(args.max_passes)
        clean_formal_directory()
    except (OSError, RuntimeError, subprocess.TimeoutExpired) as exc:
        print(f"formal PDF build error: {exc}", file=sys.stderr)
        return 1
    print("removed stale artifacts: " + (", ".join(removed) if removed else "none"))
    print(f"formal PDF stable after {passes} passes")
    print(f"sha256={pdf_hash}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
