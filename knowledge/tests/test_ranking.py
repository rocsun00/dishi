"""Behavioral ranking checks, independent of numeric score constants."""

import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("ranking_corpus_kb", ROOT / "kb.py")
kb = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(kb)


def make_book(rows, book_id="sample", title="示例原典"):
    passages = [{"id": pid, "chapter": 1, "chapter_title": "一章", "text": text,
                 "source_url": "https://example.org/source"} for pid, text, _ in rows]
    return {"entry": {"id": book_id, "title": title}, "passages": passages,
            "by_id": {p["id"]: p for p in passages},
            "search_text": {pid: text for pid, text, _ in rows},
            "readings": {pid: {"explanation": explanation, "caution": ""}
                         for pid, _, explanation in rows}, "concepts": []}


class SyntheticRankingTest(unittest.TestCase):
    def test_frequency_distinguishes_equally_long_passages(self):
        book = make_book([("AA-01-001", "仁者爱人而行事有序。", "释义"),
                          ("ZZ-01-001", "仁者仁也，仁而有序。", "释义")])
        rows = kb.search("仁", [book])
        self.assertEqual(rows[0]["id"], "ZZ-01-001")
        self.assertGreater(rows[0]["score"], rows[1]["score"])

    def test_length_and_saturation_limit_keyword_stuffing(self):
        book = make_book([("AA-01-001", "仁" * 100 + "天地四时万物各得其所，" * 100, "释义"),
                          ("ZZ-01-001", "仁者安仁。", "释义")])
        self.assertEqual(kb.search("仁", [book])[0]["id"], "ZZ-01-001")

    def test_short_focused_passage_beats_one_mention_in_a_long_passage(self):
        filler = "天地四时万物各得其所，" * 30
        book = make_book([("AA-01-001", filler + "无为。", "释义"),
                          ("ZZ-01-001", "道常无为。", "释义")])
        self.assertEqual(kb.search("无为", [book])[0]["id"], "ZZ-01-001")

    def test_source_evidence_outweighs_ai_labels_reading_and_caution(self):
        book = make_book([("AA-01-001", "其他论说。", "这里解释赏罚。"),
                          ("ZZ-01-001", "明主赏罚必信。", "释义")])
        book["readings"]["AA-01-001"]["caution"] = "不要把赏罚视作任意威胁。"
        book["concepts"] = [{"id": "AB-C01", "passage_ids": ["AA-01-001"],
                             "title": "赏罚", "tags": ["赏罚"], "quote": "其他论说。",
                             "interpretation": "赏罚的现代读法", "boundary": "赏罚须有限度"}]
        self.assertEqual(kb.search("赏罚", [book])[0]["id"], "ZZ-01-001")

    def test_caution_is_weaker_than_affirmative_reading(self):
        book = make_book([("AA-01-001", "其他论说。", "对应释义。"),
                          ("ZZ-01-001", "其他论说。", "这里讨论赏罚。")])
        book["readings"]["AA-01-001"]["caution"] = "赏罚不适用于这里。"
        rows = kb.search("赏罚", [book])
        self.assertEqual(rows[0]["id"], "ZZ-01-001")

    def test_simplified_copy_does_not_double_count_source(self):
        book = make_book([("AB-01-001", "明主赏罚必信。", "释义")])
        duplicate = kb.search("赏罚", [book])[0]["score"]
        book["search_text"]["AB-01-001"] = ""
        self.assertEqual(kb.search("赏罚", [book])[0]["score"], duplicate)
        book["passages"][0]["text"] = "明主賞罰必信。"
        book["search_text"]["AB-01-001"] = "明主赏罚必信。"
        self.assertEqual(kb.search("赏罚", [book])[0]["score"], duplicate)

    def test_repeated_query_words_do_not_add_votes(self):
        book = make_book([("AB-01-001", "诚信使合作成为可能。", "释义")])
        for query, repeated in (("诚信", "诚信 诚信"), ("trust", "trust TRUST trust")):
            with self.subTest(query=query):
                self.assertEqual(kb.search(query, [book])[0]["score"],
                                 kb.search(repeated, [book])[0]["score"])

    def test_full_phrase_beats_scattered_bigrams(self):
        book = make_book([("AA-01-001", "自知其短，者明其长。", "释义"),
                          ("ZZ-01-001", "知人者智，自知者明。", "释义")])
        self.assertEqual(kb.search("自知者明", [book])[0]["id"], "ZZ-01-001")

    def test_metadata_ids_and_card_quote_do_not_create_hits(self):
        book = make_book([("AB-01-001", "其他论说。", "释义")])
        book["concepts"] = [{"id": "赏罚", "passage_ids": ["AB-01-001"],
                             "title": "概念", "quote": "不可检索"}]
        book["passages"][0]["source_url"] = "https://example.org/元数据"
        for query in ("赏罚", "不可检索", "元数据"):
            with self.subTest(query=query):
                self.assertEqual(kb.search(query, [book]), [])

    def test_equal_scores_are_stable_under_id_renaming_and_input_order(self):
        book = make_book([("AA-01-001", "仁甲。", "释义"), ("ZZ-01-001", "仁乙。", "释义")])
        before = [row["text"] for row in kb.search("仁", [book])]
        changed = copy.deepcopy(book)
        renamed = {"AA-01-001": "ZZ-01-001", "ZZ-01-001": "AA-01-001"}
        for passage in changed["passages"]:
            old = passage["id"]
            passage["id"] = renamed[old]
        changed["passages"].reverse()
        changed["by_id"] = {p["id"]: p for p in changed["passages"]}
        for key in ("search_text", "readings"):
            changed[key] = {renamed[pid]: value for pid, value in changed[key].items()}
        self.assertEqual([row["text"] for row in kb.search("仁", [changed])], before)

    def test_only_exact_score_ties_interleave_sources(self):
        first = make_book([("AA-01-001", "仁。", "释义"), ("AA-01-002", "仁。", "释义"),
                           ("AA-01-003", "仁。", "释义")], "first")
        second = make_book([("ZZ-01-001", "仁。", "释义")], "second")
        rows = kb.search("仁", [first, second], 2)
        self.assertEqual({row["book"] for row in rows}, {"first", "second"})

    def test_book_hint_boost_is_disclosed_without_filtering_other_sources(self):
        other = make_book([("OT-01-001", "孟子见梁惠王。", "释义")], "other", "其他典籍")
        named = make_book([("MJ-01-001", "孟子曰：人皆有不忍人之心。", "释义")], "mengzi", "孟子")
        rows = kb.search("Mencius", [other, named])
        self.assertEqual(rows[0]["book"], "mengzi")
        self.assertEqual({row["book"] for row in rows}, {"other", "mengzi"})
        self.assertGreater(rows[0]["book_hint_boost"], 1)

    def test_explicit_id_is_labeled_and_unknown_id_is_reported(self):
        book = make_book([("AB-01-001", "诚信使合作成为可能。", "释义")])
        rows = kb.search("AB-01-001 AB-99-999 trust", [book])
        self.assertEqual(rows[0]["id"], "AB-01-001")
        self.assertEqual(rows[0]["match_type"], "explicit_reference")
        self.assertEqual(rows[0]["query_explanation"]["unresolved_passage_ids"], ["AB-99-999"])
        self.assertEqual(len(rows), 1)


class RealCorpusRankingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.books = [kb.load_book(entry) for entry in kb.selected_entries(kb.load_catalog())]
        cls.by_id = {p["id"]: (book, p) for book in cls.books for p in book["passages"]}

    def test_relevant_source_passages_surface_for_broad_chinese_terms(self):
        # These assertions name passages whose source discusses the term. They
        # do not prescribe a first-ranked book or an exact score.
        anchors = {"无为": (10, {"LZ-43-001", "LZ-48-001", "LZ-37-001"}),
                   "仁": (10, {"LY-04-002", "LY-04-006", "LY-06-028"}),
                   "赏罚": (10, {"HF-38-016", "HF-27-007", "GZ-04-005"}),
                   "兼爱": (10, {"MZ-28-003", "MZ-44-024"})}
        for query, (limit, expected) in anchors.items():
            with self.subTest(query=query):
                rows = kb.search(query, self.books, limit)
                self.assertTrue({row["id"] for row in rows} & expected, [row["id"] for row in rows])
                supported = sum(query in self.by_id[row["id"]][0]["search_text"][row["id"]]
                                or query in row["text"] for row in rows)
                self.assertGreaterEqual(supported / len(rows), 0.8)

    def test_exact_quotation_remains_first_and_traceable(self):
        rows = kb.search("自知者明", self.books)
        self.assertEqual(rows[0]["id"], "LZ-33-001")
        for row in rows:
            self.assertEqual(row["text"], self.by_id[row["id"]][1]["text"])
            self.assertTrue(row["source_url"].startswith("https://"))

    def test_debates_about_human_nature_and_knowledge_remain_retrievable(self):
        cases = {"性善": {"MJ-11-006", "MJ-05-001"},
                 "知行合一": {"WYM-03-026", "WYM-01-006"},
                 "Mencius human nature": {"MJ-05-001"}}
        for query, anchors in cases.items():
            with self.subTest(query=query):
                ids = {row["id"] for row in kb.search(query, self.books, 5)}
                self.assertTrue(ids & anchors, ids)

    def test_two_english_topics_do_not_put_financial_coercion_first(self):
        rows = kb.search("trust cooperation", self.books, 5)
        self.assertNotEqual(rows[0]["id"], "GGZ-03-001")
        book, passage = self.by_id[rows[0]["id"]]
        source = passage["text"] + book["search_text"][passage["id"]]
        self.assertTrue(any(term in source for term in ("信任", "诚信", "合作", "协作")))
        self.assertEqual(rows[0]["query_explanation"]["query"], "trust cooperation")

    def test_lexical_json_cli_is_compatible(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = kb.main(["search", "无为", "--book", "laozi", "--limit", "2", "--json"])
        self.assertEqual(code, 0)
        rows = json.loads(stdout.getvalue())
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(row["book"] == "laozi" for row in rows))
        self.assertTrue(all(isinstance(row["score"], (int, float)) for row in rows))

    def test_unknown_id_keeps_json_list_and_reports_why_it_is_empty(self):
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = kb.main(["search", "AB-99-999", "--book", "laozi", "--json"])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(stdout.getvalue()), [])
        self.assertIn("AB-99-999", stderr.getvalue())

    def test_text_cli_separates_explicit_references_from_lexical_scores(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = kb.main(["search", "LZ-43-001 trust", "--book", "laozi", "--limit", "1"])
        self.assertEqual(code, 0)
        self.assertIn("Explicit passage reference", stdout.getvalue())
        self.assertNotIn("关键词匹配分 1.0", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
