#!/usr/bin/env python3
"""Regression tests for the strict formal-listing inventory gate."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import audit_listing_coverage as coverage  # noqa: E402


class ListingCoverageGateTests(unittest.TestCase):
    def classified_inventory(self) -> list[coverage.Listing]:
        listings, _ = coverage.inventory_formal_tree()
        coverage.apply_differential_cases(listings)
        coverage.apply_contract_cases(listings)
        coverage.apply_explicit_classifications(listings)
        return listings

    def test_formal_tree_has_exactly_327_registered_blocks(self) -> None:
        listings = self.classified_inventory()
        self.assertEqual(len(listings), 327)
        self.assertFalse([item.block_id for item in listings if item.category == "pending"])

    def test_body_drift_invalidates_digest_selector(self) -> None:
        listing = coverage.Listing(
            source="remake/large/example.tex", ordinal=1, line=1,
            body="int answer = 1;\n", headings={},
        )
        old_digest = listing.digest
        listing.body = "int answer = 2;\n"
        with self.assertRaisesRegex(ValueError, "matched 0 listings"):
            coverage.select_listing_by_digest(
                [listing], listing.source, old_digest, "drift regression"
            )

    def test_new_unregistered_block_remains_pending(self) -> None:
        listings = self.classified_inventory()
        added = coverage.Listing(
            source="remake/large/new.tex", ordinal=1, line=1,
            body="int new_algorithm(int x) { return x + 1; }\n", headings={},
        )
        listings.append(added)
        self.assertEqual(added.category, "pending")
        self.assertEqual(sum(item.category == "pending" for item in listings), 1)

    def test_frameworks_have_unique_specific_contracts(self) -> None:
        frameworks = [
            item for item in self.classified_inventory() if item.category == "framework"
        ]
        self.assertEqual(len({item.note for item in frameworks}), len(frameworks))
        for item in frameworks:
            self.assertTrue(item.required_patterns, item.block_id)
            self.assertGreaterEqual(len(item.missing_dependencies), 2, item.block_id)
            self.assertTrue(item.validated_surface, item.block_id)
            self.assertNotIn("验证由测试运行器承担", item.note)

    def test_block_id_cannot_disguise_a_duplicated_framework_reason(self) -> None:
        first = "结构框架（06_图论:004：最短路）：缺少图、源点、边权限制和不可达输出。"
        second = "结构框架（06_图论:005：最短路）：缺少图、源点、边权限制和不可达输出。"
        self.assertTrue(coverage.framework_notes_too_similar(first, second))

    def test_heading_swap_cannot_disguise_template_boilerplate(self) -> None:
        first = "结构框架（三分）：缺少窗口宽度、最大方向和过期下标规则；当前只核对正文。"
        second = "结构框架（斜率优化）：缺少窗口宽度、最大方向和过期下标规则；当前只核对正文。"
        self.assertTrue(coverage.framework_notes_too_similar(first, second))


if __name__ == "__main__":
    unittest.main()
