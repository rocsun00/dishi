"""Behavioral checks for the finite, offline English query adapter."""

import contextlib
import importlib.util
import io
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("bilingual_corpus_kb", ROOT / "kb.py")
kb = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(kb)


def sample_book(book_id="sample", title="示例原典", text="自知者明。信任是合作的基础。"):
    passage = {"id": "AB-01-001", "chapter": 1, "chapter_title": "一章", "text": text,
               "source_url": "https://example.org/source"}
    return {"entry": {"id": book_id, "title": title}, "passages": [passage],
            "by_id": {passage["id"]: passage}, "search_text": {passage["id"]: text},
            "readings": {passage["id"]: {"explanation": "中文释义", "caution": ""}},
            "concepts": []}


class EnglishQueryTest(unittest.TestCase):
    def test_vocabulary_is_finite_reviewable_and_covers_all_catalog_books(self):
        vocabulary = json.loads((ROOT / "english_keywords.json").read_text(encoding="utf-8"))
        self.assertGreaterEqual(len([item for item in vocabulary["entries"] if item["kind"] == "concept"]), 50)
        aliases = {item["id"] for item in vocabulary["entries"] if item["kind"] == "book"}
        self.assertEqual(aliases, {item["id"] for item in kb.load_catalog()["books"]})

    def test_english_question_records_mapping_and_ignored_words(self):
        original = "  How can I build trust with partners?  "
        info = kb.explain_query(original)
        self.assertEqual(info["query"], original)
        self.assertEqual(info["mode"], "english_keyword_mapping")
        self.assertEqual([item["concept"] for item in info["mappings"]], ["trust", "partnership"])
        self.assertIn("How", info["ignored_terms"])
        self.assertEqual(info["unrecognized_terms"], ["build"])
        self.assertIn("信任", info["retrieval_terms"])
        self.assertNotIn("How", info["retrieval_terms"])
        self.assertEqual(kb.search(original, [sample_book()])[0]["query_explanation"]["query"], original)
        for item in info["mappings"]:
            self.assertEqual(original[item["start"]:item["end"]], item["input"])

    def test_practical_decision_terms_discovered_in_forward_use(self):
        for query, expected in (("missed deadlines", "执行"), ("budget and savings", "资金"),
                                ("harmony", "和而不同"), ("comparing myself", "攀比")):
            with self.subTest(query=query):
                self.assertIn(expected, kb.explain_query(query)["mapped_keywords"])
        self.assertIn("comparison", kb.explain_query("comparison")["unrecognized_terms"])

    def test_mixed_query_keeps_chinese_and_mapped_terms(self):
        info = kb.explain_query("合作 requires TRUST")
        self.assertEqual(info["mode"], "mixed_keyword_mapping")
        self.assertEqual(info["chinese_terms"], ["合作"])
        self.assertEqual(info["retrieval_terms"], ["合作", "信任", "诚信"])
        self.assertEqual(info["unrecognized_terms"], ["requires"])
        rows = kb.search("合作 requires TRUST", [sample_book()])
        # Search may add corpus-dependent ID diagnostics to the lexical report.
        for key, value in info.items():
            self.assertEqual(rows[0]["query_explanation"][key], value)

    def test_longest_phrase_case_and_hyphen_match_without_fragment_mapping(self):
        info = kb.explain_query("SELF-AWARENESS in The Art of War")
        self.assertEqual([item["concept"] for item in info["mappings"]], ["self_knowledge", "sunzi"])
        self.assertEqual(info["mappings"][0]["input"], "SELF-AWARENESS")
        self.assertNotIn("war", [item["concept"] for item in info["mappings"]])
        self.assertEqual(info["unrecognized_terms"], [])

    def test_word_boundaries_do_not_guess_substrings_or_stems(self):
        for query in ("distrust", "trustees", "warbler", "earning", "trust_me", "xtrust", "trust2", "partner's"):
            with self.subTest(query=query):
                self.assertEqual(kb.explain_query(query)["mappings"], [])
                self.assertEqual(kb.search(query, [sample_book()]), [])
        self.assertEqual(kb.explain_query("'trust'")["mapped_keywords"], ["信任", "诚信"])

    def test_phrase_does_not_cross_chinese_or_punctuation(self):
        for query in ("self自己awareness", "self, awareness"):
            with self.subTest(query=query):
                self.assertNotIn("self_knowledge", [item["concept"] for item in kb.explain_query(query)["mappings"]])

    def test_unknown_english_and_function_words_never_match_metadata(self):
        book = sample_book(text="原文。")
        book["concepts"] = [{"title": "中文卡", "passage_ids": ["AB-01-001"], "source_context": "说明"}]
        for query in ("What is the quuxnebula in this?", "in a the is", "the", "quuxnebula"):
            with self.subTest(query=query):
                self.assertEqual(kb.search(query, [book]), [])
        info = kb.explain_query("What is the quuxnebula in this?")
        self.assertEqual(info["unrecognized_terms"], ["quuxnebula"])
        self.assertEqual(info["retrieval_terms"], [])

    def test_negation_is_preserved_and_suppresses_affirmative_english_mapping(self):
        for query, token in (("Do not trust partners", "not"), ("don't trust partners", "don't"),
                             ("Avoid competition", "Avoid"), ("without trust", "without")):
            with self.subTest(query=query):
                info = kb.explain_query(query)
                self.assertIn(token, info["negation_terms"])
                self.assertTrue(any("Negation" in warning for warning in info["warnings"]))
                self.assertEqual(info["query"], query)
                self.assertEqual(info["mappings"], [])
                self.assertEqual(info["retrieval_terms"], [])
                self.assertTrue(info["suppressed_mappings"])
                self.assertEqual(kb.search(query, [sample_book()]), [])
        info = kb.explain_query("avoiding war")
        self.assertEqual(info["negation_terms"], ["avoiding"])
        self.assertEqual([item["concept"] for item in info["suppressed_mappings"]], ["war"])

    def test_negative_auxiliary_contractions_disable_english_mapping(self):
        for negative in ("haven't", "hasn't", "hadn't", "needn't", "shan't", "ain't"):
            for token in (negative, negative.replace("'", "’")):
                with self.subTest(token=token):
                    info = kb.explain_query("I " + token + " found trust")
                    self.assertIn(token, info["negation_terms"])
                    self.assertEqual(info["mapped_keywords"], [])
                    self.assertTrue(info["suppressed_mappings"])
                    self.assertEqual(kb.search("I " + token + " found trust", [sample_book()]), [])

    def test_negation_rule_does_not_guess_clause_scope_or_reverse_chinese(self):
        info = kb.explain_query("I don't want competition, but trust matters")
        self.assertEqual(info["mappings"], [])
        self.assertEqual({item["concept"] for item in info["suppressed_mappings"]}, {"competition", "trust"})
        info = kb.explain_query("不要竞争 not trust")
        self.assertEqual(info["retrieval_terms"], ["不要竞争"])
        self.assertTrue(any("Chinese terms" in warning for warning in info["warnings"]))
        info = kb.explain_query("not Laozi or AB-01-001")
        self.assertEqual(info["recommended_books"], [])
        self.assertEqual(info["passage_ids"], [])
        self.assertEqual(info["suppressed_passage_ids"], ["AB-01-001"])
        self.assertEqual(kb.search("not AB-01-001", [sample_book()]), [])

    def test_ambiguous_words_are_not_treated_as_philosophical_concepts(self):
        for query in ("power nap", "enough", "practice piano", "fair weather", "saving lives", "change a tire", "an interest in piano", "delivery of a baby"):
            with self.subTest(query=query):
                self.assertEqual(kb.explain_query(query)["mapped_keywords"], [])
                self.assertEqual(kb.search(query, [sample_book()]), [])
        for query in ("not enough money", "never enough time", "I don't have enough food"):
            with self.subTest(query=query):
                info = kb.explain_query(query)
                self.assertNotIn("知足", info["mapped_keywords"])
                self.assertEqual(info["retrieval_terms"], [])

    def test_explicit_phrases_support_their_topic_without_guessing_a_solution(self):
        expected = (("political power", "权力"), ("adapt to change", "应变"),
                    ("put knowledge into practice", "知行"), ("being content", "知足"),
                    ("task execution", "执行"), ("saving money", "节俭"))
        for query, word in expected:
            with self.subTest(query=query):
                self.assertIn(word, kb.explain_query(query)["mapped_keywords"])

    def test_finite_life_topics_add_reading_prompts_without_implicit_advice(self):
        expected = (("burnout", "exhaustion"), ("grief after father died", "grief"),
                    ("boss who micromanages", "micromanagement"), ("Should I quit or stay?", "exit_decision"),
                    ("layoffs", "employment_loss"), ("career", "career"),
                    ("startup", "entrepreneurship"), ("cofounder", "partnership"))
        for query, concept in expected:
            with self.subTest(query=query):
                info = kb.explain_query(query)
                self.assertIn(concept, [item["concept"] for item in info["mappings"]])
                self.assertTrue(info["retrieval_terms"])
        career = kb.explain_query("change my career")
        self.assertEqual([item["concept"] for item in career["mappings"]], ["career"])
        self.assertNotIn("应变", career["mapped_keywords"])
        pay = kb.explain_query("fair pay for women")
        self.assertIn("公平", pay["mapped_keywords"])
        self.assertNotIn("义利", pay["mapped_keywords"])
        self.assertIn("women", pay["unrecognized_terms"])
        # A possible response to micromanagement is not its lexical synonym.
        self.assertNotIn("授权", kb.explain_query("micromanagement")["mapped_keywords"])

    def test_unknown_external_thinker_remains_unknown(self):
        info = kb.explain_query("Machiavelli")
        self.assertEqual(info["unrecognized_terms"], ["Machiavelli"])
        self.assertEqual(info["mappings"], [])
        self.assertEqual(info["recommended_books"], [])
        self.assertEqual(kb.search("Machiavelli", [sample_book()]), [])

    def test_non_action_is_a_curated_phrase_not_negation_inference(self):
        info = kb.explain_query("non-action")
        self.assertEqual(info["mapped_keywords"], ["无为"])
        self.assertEqual(info["mappings"][0]["concept"], "inaction")

    def test_id_lookup_is_unchanged_and_unknown_id_is_not_guessed(self):
        rows = kb.search(" ab-01-001 ", [sample_book()])
        self.assertEqual(rows[0]["score"], 1.0)
        self.assertNotIn("query_explanation", rows[0])
        info = kb.explain_query("ab-01-001")
        self.assertEqual(info["mode"], "passage_id")
        self.assertEqual(info["direct_id"], "AB-01-001")
        self.assertEqual(info["passage_ids"], ["AB-01-001"])
        self.assertEqual(info["retrieval_terms"], [])
        self.assertEqual(kb.search("AB-99-999", [sample_book()]), [])

    def test_mixed_passage_ids_are_recognized_as_ids_and_not_unknown_tokens(self):
        info = kb.explain_query("GGZ-03-001 trust and ggz-03-001 AB-01-001")
        self.assertIsNone(info["direct_id"])
        self.assertEqual(info["passage_ids"], ["GGZ-03-001", "AB-01-001"])
        self.assertEqual(info["unrecognized_terms"], [])
        self.assertEqual(info["retrieval_terms"], ["信任", "诚信"])
        self.assertEqual(kb.explain_query("trust-01-001")["mapped_keywords"], [])

    def test_book_and_school_aliases_offer_explicit_scope_hints(self):
        named = kb.explain_query("The Art of War strategy")
        self.assertEqual(named["recommended_books"], ["sunzi"])
        self.assertTrue(any("--book" in line for line in named["limitations"]))
        school = kb.explain_query("Taoism")
        self.assertEqual(school["recommended_books"], ["laozi", "zhuangzi", "liezi"])
        self.assertIn("道家", school["mapped_keywords"])
        self.assertEqual(kb.explain_query("Stoicism")["recommended_books"], [])

    def test_book_alias_adds_keywords_without_restricting_books(self):
        other = sample_book("other", "其他典籍", "这里讨论孙子兵法。")
        named = sample_book("sunzi", "孙子兵法", "用兵。")
        named["passages"][0]["id"] = "SZ-01-001"
        named["by_id"] = {"SZ-01-001": named["passages"][0]}
        named["search_text"] = {"SZ-01-001": "用兵。"}
        named["readings"] = {"SZ-01-001": {"explanation": "中文释义", "caution": ""}}
        rows = kb.search("The Art of War", [other, named])
        self.assertEqual({row["book"] for row in rows}, {"other", "sunzi"})
        self.assertEqual(kb.search("Sun Tzu", [other])[0]["book"], "other")

    def test_chinese_query_retains_matching_record_and_literal_behavior(self):
        rows = kb.search("自知者明", [sample_book()])
        self.assertEqual(rows[0]["id"], "AB-01-001")
        self.assertGreater(rows[0]["score"], 0)
        self.assertEqual(rows[0]["text"], sample_book()["passages"][0]["text"])
        self.assertNotIn("query_explanation", rows[0])
        self.assertEqual(kb.search("不存在的关键词", [sample_book()]), [])

    def test_explain_cli_works_without_a_catalog_and_json_is_auditable(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            result = kb.main(["--root", "/path/that/does/not/exist", "explain-query", "How can I trust partners?", "--json"])
        self.assertEqual(result, 0)
        info = json.loads(stdout.getvalue())
        self.assertEqual(info["query"], "How can I trust partners?")
        self.assertEqual(info["mappings"][0]["concept"], "trust")

    def test_explain_text_reports_unknowns_and_negation(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            result = kb.main(["explain-query", "not quuxnebula"])
        self.assertEqual(result, 0)
        self.assertIn("Unrecognized: quuxnebula", stdout.getvalue())
        self.assertIn("Negation or avoidance: not", stdout.getvalue())

    def test_real_sunzi_english_and_mixed_queries_return_traceable_candidates(self):
        entry = next(item for item in kb.load_catalog()["books"] if item["id"] == "sunzi")
        book = kb.load_book(entry)
        for query in ("How can I choose a strategy?", "用兵 strategy", "Sun Tzu timing"):
            with self.subTest(query=query):
                rows = kb.search(query, [book], 2)
                self.assertTrue(rows)
                self.assertTrue(rows[0]["source_url"].startswith("https://"))
                self.assertIn(rows[0]["id"], book["by_id"])
                self.assertEqual(rows[0]["text"], book["by_id"][rows[0]["id"]]["text"])
                self.assertEqual(rows[0]["query_explanation"]["query"], query)


if __name__ == "__main__":
    unittest.main()
