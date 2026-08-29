#!/usr/bin/env python3
"""Inventory every lstlisting rendered by the formal handbook entry.

Existing differential cases are mapped back to their source listings. Other
listings remain PENDING until tests/listing_coverage/classification.json gives
them an explicit framework, pseudocode, or explanatory classification.
"""

from __future__ import annotations

import argparse
import difflib
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
CONTRACT_MANIFEST = ROOT / "tests" / "contracts" / "manifest.json"
CLASSIFICATION_MANIFEST = ROOT / "tests" / "listing_coverage" / "classification.json"
REPORT = ROOT / "docs" / "代码块检验清单.md"

BEGIN_LISTING = "\\begin{lstlisting}"
END_LISTING = "\\end{lstlisting}"
INPUT_RE = re.compile(r"\\inputnewboard\{([^{}]+)\}")
HEADING_START_RE = re.compile(
    r"\\(chapter|section|subsection|subsubsection)\s*\{"
)
ALLOWED_EXPLICIT_CATEGORIES = {"framework", "pseudocode", "explanatory"}
ALLOWED_FRAMEWORK_CHECKS = {"structural_contract"}
STATUS_LABELS = {
    "differential": "DIFFERENTIAL",
    "contract": "CONTRACT",
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
    contract_cases: list[str] = field(default_factory=list)
    category: str = "pending"
    note: str = ""
    check: str = ""
    required_patterns: list[str] = field(default_factory=list)
    forbidden_patterns: list[str] = field(default_factory=list)
    allowed_empty_hooks: list[str] = field(default_factory=list)
    missing_dependencies: list[str] = field(default_factory=list)
    validated_surface: str = ""

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


def extract_listing(source: Path, needle: str) -> str:
    """Return the unique lstlisting body in source containing needle."""
    text = source.read_text(encoding="utf-8")
    matches: list[str] = []
    cursor = 0
    while True:
        begin = text.find(BEGIN_LISTING, cursor)
        if begin < 0:
            break
        header_end = text.find("\n", begin)
        if header_end < 0:
            raise ValueError(f"unterminated listing header in {relative(source)}")
        end = text.find(END_LISTING, header_end)
        if end < 0:
            raise ValueError(f"unterminated listing in {relative(source)}")
        body = text[header_end + 1 : end].rstrip() + "\n"
        if needle in body:
            matches.append(body)
        cursor = end + len(END_LISTING)
    if len(matches) != 1:
        raise ValueError(
            f"selector {needle!r} matched {len(matches)} listings in "
            f"{relative(source)}; expected exactly one"
        )
    return matches[0]


def load_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read {relative(path)}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"{relative(path)} must contain a JSON object")
    return data


def framework_note_fingerprint(note: str) -> str:
    """Remove cosmetic block labels and shared report boilerplate from a basis note."""
    text = re.sub(
        r"(?:formal-entry|\d{2}_[^\s：:，；]+)\s*[:：]\s*\d{3}", "", note,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"^结构框架（[^）]*）[：:]", "", text.strip())
    text = re.split(r"[；;]当前只核对", text, maxsplit=1)[0]
    text = re.sub(r"[`'\"“”‘’（）()，,。；;：:\s]", "", text).lower()
    return text


def framework_notes_too_similar(left: str, right: str) -> bool:
    a, b = framework_note_fingerprint(left), framework_note_fingerprint(right)
    if not a or not b:
        return a == b
    if a == b or difflib.SequenceMatcher(None, a, b).ratio() >= 0.94:
        return True
    grams_a = {a[index:index + 3] for index in range(max(1, len(a) - 2))}
    grams_b = {b[index:index + 3] for index in range(max(1, len(b) - 2))}
    return len(grams_a & grams_b) / len(grams_a | grams_b) >= 0.90


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


def apply_contract_cases(listings: list[Listing]) -> int:
    data = load_json(CONTRACT_MANIFEST)
    if data.get("schema_version") != 1 or not isinstance(data.get("cases"), list):
        raise ValueError("tests/contracts/manifest.json has an unsupported schema")
    seen_case_ids: set[str] = set()
    for case in data["cases"]:
        if not isinstance(case, dict):
            raise ValueError("contract case must be a JSON object")
        case_id = case.get("id", "")
        if not isinstance(case_id, str) or not case_id:
            raise ValueError("contract case id must be a non-empty string")
        if case_id in seen_case_ids:
            raise ValueError(f"duplicate contract case id: {case_id}")
        seen_case_ids.add(case_id)
        snippets = case.get("snippets")
        if not isinstance(snippets, list) or not snippets:
            raise ValueError(f"contract case {case_id} must define non-empty snippets")
        seen_blocks: set[tuple[str, int]] = set()
        evidence_blocks = 0
        for snippet_index, snippet in enumerate(snippets, start=1):
            if not isinstance(snippet, dict):
                raise ValueError(f"contract case {case_id} snippet {snippet_index} is invalid")
            required = {"source", "contains", "marker"}
            if not required <= snippet.keys():
                raise ValueError(
                    f"contract case {case_id} snippet {snippet_index} must define "
                    f"{sorted(required)}"
                )
            listing = select_listing(
                listings,
                snippet["source"],
                snippet["contains"],
                f"contract case {case_id} snippet {snippet_index}",
            )
            block_key = (listing.source, listing.ordinal)
            if block_key in seen_blocks:
                raise ValueError(
                    f"contract case {case_id} selects {listing.block_id} more than once"
                )
            seen_blocks.add(block_key)
            support = snippet.get("support", False)
            if not isinstance(support, bool):
                raise ValueError(
                    f"contract case {case_id} snippet {snippet_index}: support must be boolean"
                )
            if support:
                continue
            evidence_blocks += 1
            if listing.differential_cases:
                raise ValueError(
                    f"contract case {case_id}: {listing.block_id} already has differential evidence"
                )
            listing.contract_cases.append(case_id)
            listing.category = "contract"
        if evidence_blocks == 0:
            raise ValueError(f"contract case {case_id} has no evidence-bearing snippet")
    return len(data["cases"])


def apply_explicit_classifications(listings: list[Listing]) -> None:
    data = load_json(CLASSIFICATION_MANIFEST)
    if data.get("schema_version") != 1 or not isinstance(data.get("classifications"), list):
        raise ValueError(
            "tests/listing_coverage/classification.json has an unsupported schema"
        )
    seen: set[tuple[str, str]] = set()
    classified_blocks: set[tuple[str, int]] = set()
    framework_notes: list[tuple[str, str]] = []
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
        if listing.differential_cases or listing.contract_cases:
            raise ValueError(
                f"{owner}: {listing.block_id} already has executable test evidence"
            )
        check = item.get("check", "")
        if category == "framework" and check not in ALLOWED_FRAMEWORK_CHECKS:
            raise ValueError(
                f"{owner}: framework check must be one of "
                f"{sorted(ALLOWED_FRAMEWORK_CHECKS)}"
            )
        if category != "framework" and check:
            raise ValueError(f"{owner}: only framework entries may define check")
        if category == "framework":
            required_patterns = item.get("required_patterns")
            if not isinstance(required_patterns, list) or not required_patterns:
                raise ValueError(f"{owner}: framework must define required_patterns")
            if not all(isinstance(pattern, str) and pattern for pattern in required_patterns):
                raise ValueError(f"{owner}: required_patterns must contain non-empty strings")
            missing_dependencies = item.get("missing_dependencies")
            if not isinstance(missing_dependencies, list) or len(missing_dependencies) < 2:
                raise ValueError(
                    f"{owner}: framework must list at least two concrete missing_dependencies"
                )
            if not all(isinstance(value, str) and value.strip() for value in missing_dependencies):
                raise ValueError(f"{owner}: missing_dependencies must be non-empty strings")
            validated_surface = item.get("validated_surface")
            if not isinstance(validated_surface, str) or not validated_surface.strip():
                raise ValueError(f"{owner}: framework must define validated_surface")
            if re.search(
                r"(?:formal-entry|\d{2}_[^\s：:，；]+)\s*[:：]\s*\d{3}", item["note"]
            ):
                raise ValueError(f"{owner}: framework note must not use a block id as uniqueness filler")
            for dependency in missing_dependencies:
                if dependency not in item["note"]:
                    raise ValueError(
                        f"{owner}: framework note must name missing dependency {dependency!r}"
                    )
            for previous_owner, previous_note in framework_notes:
                if framework_notes_too_similar(previous_note, item["note"]):
                    raise ValueError(
                        f"{owner}: framework note is materially the same as {previous_owner}; "
                        "every framework needs a block-specific classification basis"
                    )
            framework_notes.append((owner, item["note"]))
            listing.missing_dependencies = missing_dependencies
            listing.validated_surface = validated_surface
            forbidden_patterns = item.get("forbidden_patterns", [])
            if not isinstance(forbidden_patterns, list) or not all(
                isinstance(pattern, str) and pattern for pattern in forbidden_patterns
            ):
                raise ValueError(
                    f"{owner}: forbidden_patterns must be a list of non-empty strings"
                )
            listing.required_patterns = required_patterns
            listing.forbidden_patterns = forbidden_patterns
            allowed_empty_hooks = item.get("allowed_empty_hooks", [])
            if not isinstance(allowed_empty_hooks, list) or not all(
                isinstance(name, str) and re.fullmatch(r"[A-Za-z_]\w*", name)
                for name in allowed_empty_hooks
            ):
                raise ValueError(
                    f"{owner}: allowed_empty_hooks must contain C++ identifiers"
                )
            listing.allowed_empty_hooks = allowed_empty_hooks
        elif any(name in item for name in (
            "required_patterns", "forbidden_patterns", "allowed_empty_hooks",
            "missing_dependencies", "validated_surface",
        )):
            raise ValueError(
                f"{owner}: only framework entries may define structural patterns"
            )
        if "验证由测试运行器承担" in item["note"]:
            raise ValueError(
                f"{owner}: unsupported execution claim without an executable test id"
            )
        listing.category = category
        listing.note = item["note"]
        listing.check = check


def escape_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ").strip()


def build_report(
    listings: list[Listing],
    rendered_sources: list[str],
    differential_case_count: int,
    contract_case_count: int,
) -> str:
    category_counts = Counter(listing.category for listing in listings)
    lines = [
        "# 正式板子代码块检验清单",
        "",
        "本清单由 `tools/audit_listing_coverage.py` 从正式入口",
        "`banzi/板子_大版本.tex` 的实际渲染树生成。`PENDING` 只表示尚未归类，",
        "不表示代码已确认错误；`DIFFERENTIAL` 与 `CONTRACT` 都要求直接提取正式",
        "源码并真实编译/运行，是否通过以测试运行器的当次结果为准。`FRAMEWORK`",
        "只有逐块结构契约，明确不算编译或算法验证。测试用例数与代码块数不能",
        "混为一谈。验证状态只保存在测试与本报告中，不写回正式",
        "TeX/PDF。",
        "",
        "## 汇总",
        "",
        f"- 正式源文件：{len(rendered_sources)} 个",
        f"- `lstlisting`：{len(listings)} 段",
        f"- 差分测试用例：{differential_case_count} 个",
        f"- 编译/契约测试用例：{contract_case_count} 个",
        f"- 有差分证据的唯一代码块：{category_counts['differential']} 段",
        f"- 有编译/契约证据的唯一代码块：{category_counts['contract']} 段",
        f"- 仅有逐块结构契约的框架代码块：{category_counts['framework']} 段",
        f"- 待归类代码块：{category_counts['pending']} 段",
        "",
        "| 分类 | 代码块数 | 含义 |",
        "| --- | ---: | --- |",
        f"| DIFFERENTIAL | {category_counts['differential']} | 已登记直接提取正式源的差分/性质测试 |",
        f"| CONTRACT | {category_counts['contract']} | 已登记直接提取正式源的真实编译/运行契约测试 |",
        f"| FRAMEWORK | {category_counts['framework']} | 缺少统一可执行语义；仅保留逐块结构契约，不称为算法验证 |",
        f"| PSEUDOCODE | {category_counts['pseudocode']} | 伪代码，不宣称可直接编译 |",
        f"| EXPLANATORY | {category_counts['explanatory']} | 命令、配置或说明性代码片段 |",
        f"| PENDING | {category_counts['pending']} | 尚未人工归类 |",
        "",
        "## 按源文件统计",
        "",
        "| 正式源 | 总数 | 差分 | 契约 | 框架 | 伪代码 | 说明 | 待归类 |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]

    for source in rendered_sources:
        source_listings = [item for item in listings if item.source == source]
        counts = Counter(item.category for item in source_listings)
        lines.append(
            f"| `{source}` | {len(source_listings)} | {counts['differential']} | "
            f"{counts['contract']} | {counts['framework']} | {counts['pseudocode']} | "
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
            if listing.contract_cases:
                evidence = ", ".join(f"`{case}`" for case in listing.contract_cases)
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
        contract_case_count = apply_contract_cases(listings)
        apply_explicit_classifications(listings)
        report = build_report(
            listings, rendered_sources, differential_case_count, contract_case_count
        )
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
        f"contract_cases={contract_case_count}, "
        f"differential_listings={counts['differential']}, "
        f"contract_listings={counts['contract']}, "
        f"pending={counts['pending']}"
    )
    if counts["pending"] and not args.allow_pending:
        print(f"listing coverage error: {counts['pending']} listings remain PENDING")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
