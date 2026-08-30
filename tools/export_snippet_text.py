#!/usr/bin/env python3
"""Export the authoritative TeX listings as a disposable searchable text file."""

from __future__ import annotations

import argparse
import os
import sys
import webbrowser
from pathlib import Path
from typing import Any

from serve_snippet_picker import build_catalog


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "板子代码集合.txt"
SEPARATOR = "=" * 88


def render_text(catalog: dict[str, Any]) -> str:
    """Render the current formal listing tree without creating another source of truth."""
    lines = [
        "算法板子代码集合",
        SEPARATOR,
        "",
        "本文件为自动生成的复制视图，请勿手工维护。",
        "唯一来源：banzi/板子_大版本.tex 与其引入的 remake/large/*.tex。",
        f"当前共 {catalog['source_count']} 个源文件、{catalog['snippet_count']} 个代码块。",
        "使用 Ctrl+F 搜索中文标题、函数名或代码内容。",
        "",
    ]
    for index, item in enumerate(catalog["snippets"], start=1):
        lines.extend(
            [
                SEPARATOR,
                f"[{index:03d}] {item['title']}",
                f"来源：{item['source']}:{item['line']}    分类：{item['category']}",
                SEPARATOR,
                "",
                item["code"].rstrip(),
                "",
                "",
            ]
        )
    return "\n".join(lines)


def export_text(output: Path = DEFAULT_OUTPUT) -> Path:
    """Regenerate the text view from the authoritative source tree."""
    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8-sig", newline="\r\n") as stream:
        stream.write(render_text(build_catalog()))
    return output


def open_text(path: Path) -> None:
    if sys.platform == "win32":
        os.startfile(path)  # type: ignore[attr-defined]
    else:
        webbrowser.open(path.as_uri())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="输出位置，默认仓库根目录的板子代码集合.txt",
    )
    parser.add_argument("--no-open", action="store_true", help="生成后不自动打开")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output = export_text(args.output)
    print(f"已从正式 TeX 生成：{output}")
    if not args.no_open:
        open_text(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
