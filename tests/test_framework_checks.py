#!/usr/bin/env python3
"""Regression tests for the framework structural-contract gate."""

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
            check="structural_contract",
            required_patterns=[r"\bf\s*\("],
        )

    def test_comments_and_literals_do_not_create_false_placeholders(self) -> None:
        listing = self.make_listing(
            'int f(int x) { cout << "... }"; /* TODO: ] */ return x + 1; }\n'
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
            'string s = R"tag(... { [ )tag"; int f(int x) { return x + 1; }\n'
        )
        result = framework.check_listing(listing)
        self.assertTrue(result.ok, result.detail)

    def test_unterminated_literal_is_rejected(self) -> None:
        listing = self.make_listing('string s = "unterminated;\n')
        result = framework.check_listing(listing)
        self.assertFalse(result.ok)
        self.assertIn("unterminated string", result.detail)

    def test_malformed_return_is_rejected(self) -> None:
        result = framework.check_listing(
            self.make_listing("int f() { return missing_symbol + ; }\n")
        )
        self.assertFalse(result.ok)
        self.assertIn("malformed return", result.detail)

    def test_xxx_placeholder_is_rejected(self) -> None:
        result = framework.check_listing(self.make_listing("int f() { return XXX; }\n"))
        self.assertFalse(result.ok)
        self.assertIn("placeholder", result.detail)

    def test_trivial_algorithm_shell_is_rejected(self) -> None:
        listing = self.make_listing("int maxflow(){return 0;}\n")
        listing.required_patterns = [r"\bmaxflow\s*\("]
        result = framework.check_listing(listing)
        self.assertFalse(result.ok)
        self.assertIn("trivial function shell", result.detail)

    def test_missing_required_contract_pattern_is_rejected(self) -> None:
        listing = self.make_listing("int f(int x) { return x + 1; }\n")
        listing.required_patterns = [r"\bpush_down\s*\("]
        result = framework.check_listing(listing)
        self.assertFalse(result.ok)
        self.assertIn("required block contract", result.detail)

    def test_empty_void_shell_is_rejected(self) -> None:
        listing = self.make_listing("void f(int x) { /* fill later */ }\n")
        result = framework.check_listing(listing)
        self.assertFalse(result.ok)
        self.assertIn("empty function shell", result.detail)

    def test_declared_external_hook_may_be_empty(self) -> None:
        listing = self.make_listing("void f(int x) { /* supplied by problem */ }\n")
        listing.allowed_empty_hooks = ["f"]
        result = framework.check_listing(listing)
        self.assertTrue(result.ok, result.detail)


if __name__ == "__main__":
    unittest.main()
