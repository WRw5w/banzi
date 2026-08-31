#!/usr/bin/env python3
"""Tests for the runtime-only searchable snippet picker."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import serve_snippet_picker as picker  # noqa: E402
import export_snippet_text as text_exporter  # noqa: E402


class SnippetPickerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = picker.build_catalog()

    def test_catalog_is_the_complete_formal_tree(self) -> None:
        self.assertEqual(self.catalog["source_count"], 24)
        self.assertEqual(self.catalog["snippet_count"], 327)
        self.assertEqual(len(self.catalog["snippets"]), 327)
        self.assertEqual(
            len({item["id"] for item in self.catalog["snippets"]}), 327
        )

    def test_qpow_comes_from_the_authoritative_math_source(self) -> None:
        matches = [
            item for item in self.catalog["snippets"]
            if "long long qpow(long long a" in item["code"]
        ]
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["source"], "remake/large/03_数学.tex")
        self.assertIn("模运算与快速幂", matches[0]["title"])

    def test_payload_is_utf8_json_serializable(self) -> None:
        encoded = json.dumps(self.catalog, ensure_ascii=False).encode("utf-8")
        decoded = json.loads(encoded)
        self.assertEqual(decoded["snippet_count"], 327)
        self.assertIn("快速幂", encoded.decode("utf-8"))

    def test_html_contains_copy_ui_but_no_duplicated_template_body(self) -> None:
        self.assertIn("navigator.clipboard", picker.INDEX_HTML)
        self.assertIn("刷新源码", picker.INDEX_HTML)
        self.assertNotIn("long long qpow(long long a", picker.INDEX_HTML)

    def test_text_export_is_generated_from_the_same_catalog(self) -> None:
        rendered = text_exporter.render_text(self.catalog)
        self.assertIn("本文件为自动生成的复制视图，请勿手工维护", rendered)
        self.assertIn("数学 / 模运算与快速幂", rendered)
        self.assertEqual(rendered.count("long long qpow(long long a"), 1)
        self.assertIn("remake/large/03_数学.tex", rendered)
        self.assertEqual(
            text_exporter.DEFAULT_OUTPUT,
            ROOT / "板子代码集合.txt",
        )


if __name__ == "__main__":
    unittest.main()
