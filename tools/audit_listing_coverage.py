#!/usr/bin/env python3
"""Inventory every lstlisting rendered by the formal handbook entry.

Existing differential cases are mapped back to their source listings. Other
listings remain PENDING until tests/listing_coverage/classification.json gives
them an explicit framework, pseudocode, or explanatory classification.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENTRY = ROOT / "banzi" / "板子_大版本.tex"
DIFFERENTIAL_MANIFEST = ROOT / "tests" / "differential" / "manifest.json"
CLASSIFICATION_MANIFEST = ROOT / "tests" / "listing_coverage" / "classification.json"
REPORT = ROOT / "docs" / "代码块检验清单.md"

BEGIN_LISTING = "\\begin{lstlisting}"
END_LISTING = "\\end{lstlisting}"
INPUT_RE = re.compile(r"\\inputnewboard\{([^{}]+)\}")
HEADING_START_RE = re.compile(
    r"\\(chapter|section|subsection|subsubsection)\s*\{"
)
ALLOWED_EXPLICIT_CATEGORIES = {"framework", "pseudocode", "explanatory"}
ALLOWED_FRAMEWORK_CHECKS = {"static"}
STATUS_LABELS = {
    "differential": "DIFFERENTIAL",
    "framework": "FRAMEWORK",
    "pseudocode": "PSEUDOCODE",
    "explanatory": "EXPLANATORY",
    "pending": "PENDING",
}


@dataclass
class Listing:
    source: str
    ordinal: int
    line: int
    body: str
    headings: dict[str, str]
    differential_cases: list[str] = field(default_factory=list)
    category: str = "pending"
    note: str = ""
    check: str = ""

    @property
    def block_id(self) -> str:
        stem = Path(self.source).stem
        if self.source == ENTRY.relative_to(ROOT).as_posix():
            stem = "formal-entry"
        return f"{stem}:{self.ordinal:03d}"

    @property
    def digest(self) -> str:
        normalized = self.body.replace("\r\n", "\n").rstrip() + "\n"
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:12]

    @property
    def heading(self) -> str:
        parts = [
            self.headings.get(level, "")
            for level in ("chapter", "section", "subsection", "subsubsection")
        ]
        return " / ".join(part for part in parts if part) or "（入口/无标题）"


def relative(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def extract_braced(text: str, open_brace: int) -> tuple[str, int]:
    depth = 0
    for index in range(open_brace, len(text)):
        char = text[index]
        if char == "{" and (index == 0 or text[index - 1] != "\\"):
            depth += 1
        elif char == "}" and (index == 0 or text[index - 1] != "\\"):
            depth -= 1
            if depth == 0:
                return text[open_brace + 1 : index], index + 1
    raise ValueError("unclosed heading brace")


def clean_heading(value: str) -> str:
    marker = "\\texorpdfstring{"
    while marker in value:
        start = value.index(marker)
        first_open = start + len(marker) - 1
        _, after_first = extract_braced(value, first_open)
        if after_first >= len(value) or value[after_first] != "{":
            break
        plain, after_plain = extract_braced(value, after_first)
        value = value[:start] + plain + value[after_plain:]
    value = re.sub(r"\\label\{[^{}]*\}", "", value)
    previous = None
    while previous != value:
        previous = value
        value = re.sub(
            r"\\(?:textbf|texttt|emph|mathrm)\{([^{}]*)\}", r"\1", value
        )
    value = value.replace("\\_", "_").replace("~", " ")
    value = value.replace("$", "").replace("\\", "")
    return re.sub(r"\s+", " ", value).strip()


def update_heading(
    headings: dict[str, str], level: str, value: str
) -> dict[str, str]:
    levels = ("chapter", "section", "subsection", "subsubsection")
    result = dict(headings)
    result[level] = clean_heading(value)
    index = levels.index(level)
    for child in levels[index + 1 :]:
        result.pop(child, None)
    return result


def inventory_formal_tree() -> tuple[list[Listing], list[str]]:
    listings: list[Listing] = []
    rendered_sources: list[str] = []
    active_stack: list[Path] = []
    ordinals: Counter[str] = Counter()

    def visit(path: Path, headings: dict[str, str]) -> dict[str, str]:
        resolved = path.resolve()
        if resolved in active_stack:
            chain = " -> ".join(relative(item) for item in [*active_stack, resolved])
            raise ValueError(f"recursive formal include: {chain}")
        if not resolved.is_file():
            raise ValueError(f"formal source does not exist: {relative(resolved)}")

        active_stack.append(resolved)
        source = relative(resolved)
        if source not in rendered_sources:
            rendered_sources.append(source)
        text = resolved.read_text(encoding="utf-8")
        cursor = 0
        current = dict(headings)

        while cursor < len(text):
            listing_at = text.find(BEGIN_LISTING, cursor)
            input_match = INPUT_RE.search(text, cursor)
            heading_match = HEADING_START_RE.search(text, cursor)
            candidates: list[tuple[int, str, object]] = []
            if listing_at >= 0:
                candidates.append((listing_at, "listing", listing_at))
            if input_match:
                candidates.append((input_match.start(), "input", input_match))
            if heading_match:
                candidates.append((heading_match.start(), "heading", heading_match))
            if not candidates:
                break

            position, kind, match = min(candidates, key=lambda item: item[0])
            if kind == "listing":
                header_end = text.find("\n", position)
                if header_end < 0:
                    raise ValueError(f"unterminated listing header in {source}")
                body_end = text.find(END_LISTING, header_end)
                if body_end < 0:
                    line = text.count("\n", 0, position) + 1
                    raise ValueError(f"unterminated listing in {source}:{line}")
                ordinals[source] += 1
                line = text.count("\n", 0, position) + 1
                listings.append(
                    Listing(
                        source=source,
                        ordinal=ordinals[source],
                        line=line,
                        body=text[header_end + 1 : body_end].rstrip() + "\n",
                        headings=dict(current),
                    )
                )
                cursor = body_end + len(END_LISTING)
                continue

            if kind == "input":
                assert isinstance(match, re.Match)
                child = ROOT / match.group(1)
                current = visit(child, current)
                cursor = match.end()
                continue

            assert isinstance(match, re.Match)
            open_brace = match.end() - 1
            try:
                value, cursor = extract_braced(text, open_brace)
            except ValueError as exc:
                line = text.count("\n", 0, position) + 1
                raise ValueError(f"{exc} in {source}:{line}") from exc
            current = update_heading(current, match.group(1), value)

        active_stack.pop()
        return current

    visit(ENTRY, {})
    return listings, rendered_sources


def load_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read {relative(path)}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{relative(path)} must contain a JSON object")
    return data


def select_listing(
    listings: list[Listing], source: str, needle: str, owner: str
) -> Listing:
    matches = [
        listing
        for listing in listings
        if listing.source == Path(source).as_posix() and needle in listing.body
    ]
    if len(matches) != 1:
        raise ValueError(
            f"{owner}: selector {needle!r} matched {len(matches)} listings in {source}; "
            "expected exactly one"
        )
    return matches[0]


def select_listing_by_digest(
    listings: list[Listing], source: str, digest: str, owner: str
) -> Listing:
    matches = [
        listing
        for listing in listings
        if listing.source == Path(source).as_posix() and listing.digest == digest
    ]
    if len(matches) != 1:
        raise ValueError(
            f"{owner}: digest {digest!r} matched {len(matches)} listings in {source}; "
            "expected exactly one"
        )
    return matches[0]


def apply_differential_cases(listings: list[Listing]) -> int:
    data = load_json(DIFFERENTIAL_MANIFEST)
    if data.get("schema_version") != 1 or not isinstance(data.get("cases"), list):
        raise ValueError("tests/differential/manifest.json has an unsupported schema")
    for case in data["cases"]:
        case_id = case.get("id", "<missing-id>")
        listing = select_listing(
            listings, case.get("source", ""), case.get("contains", ""), case_id
        )
        listing.differential_cases.append(case_id)
        listing.category = "differential"
    return len(data["cases"])


def apply_explicit_classifications(listings: list[Listing]) -> None:
    data = load_json(CLASSIFICATION_MANIFEST)
    if data.get("schema_version") != 1 or not isinstance(data.get("classifications"), list):
        raise ValueError(
            "tests/listing_coverage/classification.json has an unsupported schema"
        )
    seen: set[tuple[str, str]] = set()
    classified_blocks: set[tuple[str, int]] = set()
    for index, item in enumerate(data["classifications"], start=1):
        owner = f"classification #{index}"
        required = {"source", "category", "note"}
        if not isinstance(item, dict) or not required <= item.keys():
            raise ValueError(f"{owner} must define {sorted(required)}")
        selectors = {name for name in ("contains", "digest") if item.get(name)}
        if len(selectors) != 1:
            raise ValueError(f"{owner} must define exactly one of contains or digest")
        category = item["category"]
        if category not in ALLOWED_EXPLICIT_CATEGORIES:
            raise ValueError(f"{owner}: unsupported category {category!r}")
        selector_name = selectors.pop()
        selector_value = item[selector_name]
        if not isinstance(selector_value, str):
            raise ValueError(f"{owner}: selector must be a string")
        if selector_name == "digest" and not re.fullmatch(
            r"[0-9a-f]{12}", selector_value
        ):
            raise ValueError(f"{owner}: digest must be 12 lowercase hexadecimal digits")
        if not isinstance(item["note"], str) or not item["note"].strip():
            raise ValueError(f"{owner}: note must be a non-empty string")
        key = (Path(item["source"]).as_posix(), f"{selector_name}:{selector_value}")
        if key in seen:
            raise ValueError(f"{owner}: duplicate selector")
        seen.add(key)
        if selector_name == "digest":
            listing = select_listing_by_digest(listings, key[0], selector_value, owner)
        else:
            listing = select_listing(listings, key[0], selector_value, owner)
        block_key = (listing.source, listing.ordinal)
        if block_key in classified_blocks:
            raise ValueError(f"{owner}: {listing.block_id} is classified more than once")
        classified_blocks.add(block_key)
        if listing.differential_cases:
            raise ValueError(
                f"{owner}: {listing.block_id} already has differential evidence"
            )
        check = item.get("check", "")
        if category == "framework" and check not in ALLOWED_FRAMEWORK_CHECKS:
            raise ValueError(
                f"{owner}: framework check must be one of "
                f"{sorted(ALLOWED_FRAMEWORK_CHECKS)}"
            )
        if category != "framework" and check:
            raise ValueError(f"{owner}: only framework entries may define check")
        listing.category = category
        listing.note = item["note"]
        listing.check = check


def escape_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


def build_report(
    listings: list[Listing], rendered_sources: list[str], differential_case_count: int
) -> str:
    category_counts = Counter(listing.category for listing in listings)
    lines = [
        "# 正式板子代码块检验清单",
        "",
        "本清单由 `tools/audit_listing_coverage.py` 从正式入口",
        "`banzi/板子_大版本.tex` 的实际渲染树生成。`PENDING` 只表示尚未归类，",
        "不表示代码已确认错误；`DIFFERENTIAL` 表示该正式代码块至少登记了一个直接",
        "提取源码的差分测试，是否通过以测试运行器的当次结果为准。测试用例数与",
        "代码块数不能混为一谈。验证状态只保存在测试与本报告中，不写回正式",
        "TeX/PDF。",
        "",
        "## 汇总",
        "",
        f"- 正式源文件：{len(rendered_sources)} 个",
        f"- `lstlisting`：{len(listings)} 段",
        f"- 差分测试用例：{differential_case_count} 个",
        f"- 有差分证据的唯一代码块：{category_counts['differential']} 段",
        f"- 已登记静态检查的框架代码块：{category_counts['framework']} 段",
        f"- 待归类代码块：{category_counts['pending']} 段",
        "",
        "| 分类 | 代码块数 | 含义 |",
        "| --- | ---: | --- |",
        f"| DIFFERENTIAL | {category_counts['differential']} | 已登记直接提取正式源的差分/性质测试 |",
        f"| FRAMEWORK | {category_counts['framework']} | 已登记摘要绑定的静态结构检查；结果以当次运行器为准 |",
        f"| PSEUDOCODE | {category_counts['pseudocode']} | 伪代码，不宣称可直接编译 |",
        f"| EXPLANATORY | {category_counts['explanatory']} | 命令、配置或说明性代码片段 |",
        f"| PENDING | {category_counts['pending']} | 尚未人工归类 |",
        "",
        "## 按源文件统计",
        "",
        "| 正式源 | 总数 | 差分 | 框架 | 伪代码 | 说明 | 待归类 |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]

    for source in rendered_sources:
        source_listings = [item for item in listings if item.source == source]
        counts = Counter(item.category for item in source_listings)
        lines.append(
            f"| `{source}` | {len(source_listings)} | {counts['differential']} | "
            f"{counts['framework']} | {counts['pseudocode']} | "
            f"{counts['explanatory']} | {counts['pending']} |"
        )

    lines.extend(
        [
            "",
            "## 逐段清单",
            "",
            "短摘要是代码正文 SHA-256 的前 12 位，用于发现代码块内容漂移。",
            "",
        ]
    )
    for source in rendered_sources:
        source_listings = [item for item in listings if item.source == source]
        if not source_listings:
            continue
        lines.extend(
            [
                f"### `{source}`",
                "",
                "| ID | 行 | 标题路径 | 分类 | 证据/备注 | 摘要 |",
                "| --- | ---: | --- | --- | --- | --- |",
            ]
        )
        for listing in source_listings:
            evidence = ", ".join(f"`{case}`" for case in listing.differential_cases)
            if not evidence:
                prefix = f"`{listing.check.upper()}`；" if listing.check else ""
                evidence = prefix + (escape_cell(listing.note) or "—")
            lines.append(
                f"| `{listing.block_id}` | {listing.line} | "
                f"{escape_cell(listing.heading)} | {STATUS_LABELS[listing.category]} | "
                f"{evidence} | `{listing.digest}` |"
            )
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--write",
        action="store_true",
        help="rewrite docs/代码块检验清单.md instead of checking it",
    )
    parser.add_argument(
        "--allow-pending",
        action="store_true",
        help="temporarily allow PENDING listings (strict coverage is the default)",
    )
    return parser.parse_args()


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    args = parse_args()
    try:
        listings, rendered_sources = inventory_formal_tree()
        differential_case_count = apply_differential_cases(listings)
        apply_explicit_classifications(listings)
        report = build_report(listings, rendered_sources, differential_case_count)
    except ValueError as exc:
        print(f"listing coverage error: {exc}", file=sys.stderr)
        return 2

    if args.write:
        REPORT.write_text(report, encoding="utf-8", newline="\n")
        action = "wrote"
    else:
        try:
            current = REPORT.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"listing coverage error: cannot read {relative(REPORT)}: {exc}")
            return 2
        if current != report:
            print(
                "listing coverage error: docs/代码块检验清单.md is stale; "
                "run python tools/audit_listing_coverage.py --write"
            )
            return 1
        action = "checked"

    counts = Counter(item.category for item in listings)
    print(
        f"{action} {relative(REPORT)}: sources={len(rendered_sources)}, "
        f"listings={len(listings)}, differential_cases={differential_case_count}, "
        f"differential_listings={counts['differential']}, "
        f"pending={counts['pending']}"
    )
    if counts["pending"] and not args.allow_pending:
        print(f"listing coverage error: {counts['pending']} listings remain PENDING")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
