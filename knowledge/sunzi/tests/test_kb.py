"""Corpus integrity and retrieval regressions; not a scholarly accuracy score."""

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("sunzi_kb", ROOT / "kb.py")
kb = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(kb)


class SunziKnowledgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.corpus = kb.load_corpus(ROOT)

    def test_complete_corpus_is_valid(self):
        report = kb.validate(self.corpus, ROOT)
        self.assertTrue(report["valid"], report["errors"])
        self.assertEqual(report["chapters"], 13)
        self.assertEqual(report["passages"], 74)
        self.assertEqual(report["readings"], 74)
        self.assertEqual(report["concepts"], 39)
        self.assertEqual(report["examples"], 18)

    def test_original_text_corruption_is_rejected(self):
        corpus = deepcopy(self.corpus)
        corpus["passages"][0]["text"] += "伪造文字"
        self.assertFalse(kb.validate(corpus, ROOT)["valid"])

    def test_reading_reordering_is_rejected(self):
        corpus = deepcopy(self.corpus)
        readings = corpus["chapters"][0]["readings"]
        readings[0], readings[1] = readings[1], readings[0]
        self.assertFalse(kb.validate(corpus, ROOT)["valid"])

    def test_quote_cannot_point_outside_displayed_references(self):
        corpus = deepcopy(self.corpus)
        corpus["examples"][0]["passage_ids"] = ["SZ-01-001"]
        corpus["examples"][0]["quotes"] = [{"passage_id": "SZ-03-001", "text": "不戰而屈人之兵"}]
        self.assertFalse(kb.validate(corpus, ROOT)["valid"])

    def test_empty_quote_is_not_counted_as_verified(self):
        corpus = deepcopy(self.corpus)
        corpus["examples"][0]["quotes"][0]["text"] = ""
        self.assertFalse(kb.validate(corpus, ROOT)["valid"])

    def test_fabricated_variant_is_rejected(self):
        corpus = deepcopy(self.corpus)
        corpus["by_id"]["SZ-06-006"]["editorial_notes"][0]["alternative"] = "虚构的异文"
        self.assertFalse(kb.validate(corpus, ROOT)["valid"])

    def test_missing_source_headers_returns_validation_failure(self):
        with tempfile.TemporaryDirectory(prefix="dishi-sunzi-header-test-") as temporary:
            root = Path(temporary)
            (root / "source").mkdir()
            (root / "data").mkdir()
            shutil.copy2(ROOT / "data/search_text.json", root / "data/search_text.json")
            text = (ROOT / "source/wikisource.wikitext").read_text(encoding="utf-8")
            (root / "source/wikisource.wikitext").write_text(text.replace("==", ""), encoding="utf-8")
            report = kb.validate(self.corpus, root)
            self.assertFalse(report["valid"])

    def test_exact_quote_retrieves_its_original_passage(self):
        results = kb.search("知彼知己", self.corpus, 1)
        self.assertEqual(results[0]["id"], "SZ-03-008")
        self.assertIn("百戰不殆", results[0]["text"])

    def test_identifier_is_a_direct_lookup(self):
        result = kb.search("sz-12-003", self.corpus, 1)[0]
        self.assertEqual(result["id"], "SZ-12-003")
        self.assertIn("不可以怒而興師", result["text"])

    def test_simplified_quote_finds_traditional_original(self):
        results = kb.search("数赏 数罚", self.corpus, 1)
        self.assertEqual(results[0]["id"], "SZ-09-004")
        self.assertIn("數賞者，窘也；數罰者，困也", results[0]["text"])

    def test_empty_and_unrelated_queries_return_no_matches(self):
        self.assertEqual(kb.search("   ", self.corpus), [])
        self.assertEqual(kb.search("量子纠缠粒子加速器", self.corpus), [])

    def test_renderer_escapes_annotation_html(self):
        with tempfile.TemporaryDirectory(prefix="dishi-sunzi-html-test-") as temporary:
            root = Path(temporary)
            shutil.copytree(ROOT / "source", root / "source")
            shutil.copytree(ROOT / "data", root / "data")
            analysis = kb.read_json(root / "data/analysis.json")
            analysis[0]["overview"] += "<script>alert('example')</script>"
            (root / "data/analysis.json").write_text(json.dumps(analysis, ensure_ascii=False), encoding="utf-8")
            kb.render(root)
            html = (root / "阅览.html").read_text(encoding="utf-8")
            self.assertNotIn("<script>", html)
            self.assertIn("&lt;script&gt;", html)


if __name__ == "__main__":
    unittest.main()
