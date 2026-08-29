#!/usr/bin/env python3
"""Regression tests for the framework listing static checker."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import audit_listing_coverage as coverage  # noqa: E402
import run_framework_checks as framework  # noqa: E402


class FrameworkCheckTests(unittest.TestCase):
    def make_listing(self, body: str) -> coverage.Listing:
        return coverage.Listing(
            source="remake/large/example.tex",
            ordinal=1,
            line=1,
            body=body,
            headings={},
            category="framework",
            check="static",
        )

    def test_comments_and_literals_do_not_create_false_placeholders(self) -> None:
        listing = self.make_listing(
            'int f() { cout << "... }"; /* TODO: ] */ return 0; }\n'
        )
        result = framework.check_listing(listing)
        self.assertTrue(result.ok, result.detail)

    def test_code_placeholder_is_rejected(self) -> None:
        listing = self.make_listing("int f() { return ...; }\n")
        result = framework.check_listing(listing)
        self.assertFalse(result.ok)
        self.assertIn("placeholder", result.detail)

    def test_unbalanced_delimiter_is_rejected(self) -> None:
        listing = self.make_listing("int f() { return 0;\n")
        result = framework.check_listing(listing)
        self.assertFalse(result.ok)
        self.assertIn("unclosed", result.detail)

    def test_raw_string_delimiters_are_ignored(self) -> None:
        listing = self.make_listing(
            'string s = R"tag(... { [ )tag"; int f() { return 0; }\n'
        )
        result = framework.check_listing(listing)
        self.assertTrue(result.ok, result.detail)

    def test_unterminated_literal_is_rejected(self) -> None:
        listing = self.make_listing('string s = "unterminated;\n')
        result = framework.check_listing(listing)
        self.assertFalse(result.ok)
        self.assertIn("unterminated string", result.detail)


if __name__ == "__main__":
    unittest.main()
