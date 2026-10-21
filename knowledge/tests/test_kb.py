"""Behavioral integrity checks for the shared multi-book tool."""

import contextlib
import copy
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location("corpus_kb", Path(__file__).resolve().parents[1] / "kb.py")
kb = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(kb)


class CorpusTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "normalization.py").write_text("def normalize_markup(text):\n    return text.strip()\ndef extract_notes(text):\n    return []\n", encoding="utf-8")
        self.entry = {"id": "sample", "title": "示例原典", "path": "sample", "status": "ready"}
        self.write("catalog.json", {"schema_version": 1, "books": [self.entry]})
        self.make_book(self.entry, "AB")

    def write(self, path, value):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def make_book(self, entry, prefix):
        base = entry["path"]
        book_root = self.root / base
        (book_root / "source").mkdir(parents=True, exist_ok=True)
        raw = "== 一章 ==\n知人者智。\n自知者明。\n"
        (book_root / "source/source.wikitext").write_text(raw, encoding="utf-8")
        start = raw.index("知人")
        middle = raw.index("自知")
        segments = [{"kind": "excluded", "start": 0, "end": start, "reason": "章题"},
                    {"kind": "passage", "id": prefix + "-01-001", "start": start, "end": middle},
                    {"kind": "passage", "id": prefix + "-01-002", "start": middle, "end": len(raw)}]
        self.write(base + "/source/extraction.json", {"schema_version": 1, "normalization": "wiki-body-v1", "segments": segments})
        passages = []
        for segment in segments[1:]:
            markup = raw[segment["start"]:segment["end"]]
            passages.append({"id": segment["id"], "chapter": 1, "chapter_title": "一章",
                             "source_start": segment["start"], "source_end": segment["end"],
                             "source_line": raw.count("\n", 0, segment["start"]) + 1,
                             "text": markup.strip(), "source_markup": markup,
                             "source_revision": 123, "source_url": "https://example.org/book?oldid=123",
                             "editorial_notes": []})
        (book_root / "data").mkdir(exist_ok=True)
        (book_root / "data/passages.jsonl").write_text("\n".join(json.dumps(p, ensure_ascii=False) for p in passages) + "\n", encoding="utf-8")
        ids = [p["id"] for p in passages]
        self.write(base + "/data/search_text.json", {p["id"]: p["text"] for p in passages})
        self.write(base + "/source/search_normalization.json", {"sha256": kb.digest(book_root / "data/search_text.json")})
        self.write(base + "/source/source.json", {"id": entry["id"], "title": entry["title"], "revision": 123,
                   "source_url": "https://example.org/book?oldid=123", "prefix": prefix,
                   "raw_file": "source.wikitext", "raw_sha256": kb.digest(book_root / "source/source.wikitext"),
                   "extraction_sha256": kb.digest(book_root / "source/extraction.json"),
                   "chapter_count": 1, "passage_count": 2})
        card = {"id": prefix + "-C01-01", "title": "认识自己", "tags": ["自知"], "passage_ids": [ids[1]], "quote": "自知者明",
                "source_context": "原典语境", "interpretation": "AI解释", "conditions": ["条件"], "misreading": "误读",
                "modern_application": "现代类比", "boundary": "应用边界"}
        analysis = [{"chapter": 1, "title_simplified": "一章", "overview": "原典概览",
                    "argument_map": [{"passage_ids": ids, "point": "认识人与自己"}],
                    "readings": [{"passage_id": pid, "explanation": "对应释义", "terms": {}, "caution": ""} for pid in ids], "concepts": [card]}]
        self.write(base + "/data/analysis.json", analysis)
        self.write(base + "/data/examples.json", [{"id": prefix + "-Q01", "type": "释义", "question": "怎样理解自知？", "answer": "依据原文的AI解释",
                   "passage_ids": [ids[1]], "quotes": [{"passage_id": ids[1], "text": "自知者明"}]}])

    def book(self):
        return kb.load_book(self.entry, self.root)

    def assert_invalid(self, book, phrase):
        report = kb.validate_book(book)
        self.assertFalse(report["valid"], report)
        self.assertIn(phrase, "；".join(report["errors"]))

    def test_complete_book_validates(self):
        report = kb.validate_book(self.book())
        self.assertTrue(report["valid"], report)
        self.assertEqual(report["verified_quotes"], 2)

    def make_sparse_book(self):
        self.make_book(self.entry, "AB")
        base = self.root / "sample"
        old_id, new_id = "AB-01-002", "AB-03-001"
        passages = [json.loads(line) for line in (base / "data/passages.jsonl").read_text(encoding="utf-8").splitlines()]
        passages[1].update(id=new_id, chapter=3, chapter_title="第三章")
        (base / "data/passages.jsonl").write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in passages), encoding="utf-8")
        analysis = kb.read_json(base / "data/analysis.json")
        first = analysis[0]
        third = copy.deepcopy(first)
        first["readings"] = first["readings"][:1]
        first["argument_map"][0]["passage_ids"] = [passages[0]["id"]]
        first["concepts"] = []
        third.update(chapter=3, title_simplified="第三章")
        third["readings"] = third["readings"][1:]
        third["readings"][0]["passage_id"] = new_id
        third["argument_map"][0]["passage_ids"] = [new_id]
        third["concepts"][0]["passage_ids"] = [new_id]
        self.write("sample/data/analysis.json", [first, third])
        examples = kb.read_json(base / "data/examples.json")
        examples[0]["passage_ids"] = [new_id]
        examples[0]["quotes"][0]["passage_id"] = new_id
        self.write("sample/data/examples.json", examples)
        extraction = kb.read_json(base / "source/extraction.json")
        extraction["segments"][-1]["id"] = new_id
        self.write("sample/source/extraction.json", extraction)
        source = kb.read_json(base / "source/source.json")
        source.update(chapter_count=2, chapter_numbers=[1, 3], extraction_sha256=kb.digest(base / "source/extraction.json"))
        self.write("sample/source/source.json", source)
        search = kb.read_json(base / "data/search_text.json")
        search[new_id] = search.pop(old_id)
        self.write("sample/data/search_text.json", search)
        self.write("sample/source/search_normalization.json", {"sha256": kb.digest(base / "data/search_text.json")})
        return self.book()

    def test_transmitted_chapter_gaps_validate_and_render(self):
        corpus = self.make_sparse_book()
        self.assertTrue(kb.validate_book(corpus)["valid"])
        kb.render_book(corpus)
        html = (corpus["root"] / "阅览.html").read_text(encoding="utf-8")
        self.assertIn('id="chapter-3"', html)
        self.assertNotIn('id="chapter-2"', html)
        self.assertEqual(kb.search("自知者明", [corpus])[0]["id"], "AB-03-001")

    def test_chapter_number_manifest_must_match_count_and_order(self):
        for numbers in ([1], [1, 1], [3, 1], [0, 3], [1, True], [1, "3"]):
            with self.subTest(numbers=numbers):
                corpus = self.make_sparse_book()
                corpus["source"]["chapter_numbers"] = numbers
                self.assert_invalid(corpus, "篇号清单")

    def test_unlisted_original_chapter_is_rejected(self):
        corpus = self.make_sparse_book()
        corpus["source"]["chapter_numbers"] = [1, 2]
        self.assert_invalid(corpus, "篇章存在缺失")

    def test_chapter_count_cannot_be_boolean(self):
        corpus = self.book()
        corpus["source"]["chapter_count"] = True
        self.assert_invalid(corpus, "现存篇数须为正整数")

    def test_source_corruption_rejected(self):
        path = self.root / "sample/source/source.wikitext"
        path.write_text(path.read_text(encoding="utf-8").replace("智", "明"), encoding="utf-8")
        self.assert_invalid(self.book(), "原始快照摘要不符")

    def test_wrong_source_revision_or_page_rejected(self):
        corpus = self.book()
        corpus["passages"][0]["source_revision"] = 999
        self.assert_invalid(corpus, "来源链接与快照页面不符")
        corpus = self.book()
        corpus["passages"][0]["source_url"] = "https://example.org/other?oldid=123"
        self.assert_invalid(corpus, "来源链接与快照页面不符")

    def test_real_normalizer_preserves_text_between_ref_types(self):
        path = Path(__file__).resolve().parents[1] / "normalization.py"
        spec = importlib.util.spec_from_file_location("real_normalizer", path)
        normalizer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(normalizer)
        self.assertEqual(normalizer.normalize_markup('甲<ref name="a" />乙<ref>注</ref>丙'), "甲乙丙")

    def test_real_normalizer_keeps_link_inside_alternate_primary(self):
        path = Path(__file__).resolve().parents[1] / "normalization.py"
        spec = importlib.util.spec_from_file_location("variant_normalizer", path)
        normalizer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(normalizer)
        text = '甲{{另2|《[[尚書|書]]》云|另一斷句}}乙'
        self.assertEqual(normalizer.normalize_markup(text), '甲《書》云乙')
        self.assertEqual(normalizer.extract_notes(text)[0]['kind'], 'source_variant_note')

    def test_reference_templates_are_notes_instead_of_primary_markup(self):
        path = Path(__file__).resolve().parents[1] / "normalization.py"
        spec = importlib.util.spec_from_file_location("reference_normalizer", path)
        normalizer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(normalizer)
        text = '正文<ref>{{unsupported|現代注記}}</ref>續文'
        self.assertEqual(normalizer.normalize_markup(text), '正文續文')
        notes = normalizer.extract_notes(text)
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0]['kind'], 'source_reference_excluded')
        self.assertIn('{{unsupported|現代注記}}', notes[0]['markup'])

    def test_language_conversion_selects_default_without_control_codes(self):
        path = Path(__file__).resolve().parents[1] / "normalization.py"
        spec = importlib.util.spec_from_file_location("language_normalizer", path)
        normalizer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(normalizer)
        self.assertEqual(normalizer.normalize_markup('-{zh:顚;zh-hant:顛;zh-hans:颠}-沛'), '顚沛')
        self.assertEqual(normalizer.normalize_markup('-{zh-hant:閒;zh-hans:间}-'), '閒')
        self.assertEqual(normalizer.normalize_markup('-{谷}-神'), '谷神')

    def test_wiki_bold_keeps_headings_without_formatting_markers(self):
        path = Path(__file__).resolve().parents[1] / "normalization.py"
        spec = importlib.util.spec_from_file_location("bold_normalizer", path)
        normalizer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(normalizer)
        self.assertEqual(normalizer.normalize_markup("'''參觀一'''"), "參觀一")
        self.assertEqual(normalizer.normalize_markup("'''甲'''乙'''丙'''"), "甲乙丙")
        self.assertEqual(normalizer.normalize_markup("O'Brien"), "O'Brien")
        with self.assertRaises(ValueError):
            normalizer.normalize_markup("'''未闭合")

    def test_pinned_glyph_description_is_preserved_but_other_angles_rejected(self):
        path = Path(__file__).resolve().parents[1] / "normalization.py"
        spec = importlib.util.spec_from_file_location("glyph_normalizer", path)
        normalizer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(normalizer)
        self.assertEqual(normalizer.normalize_markup('脊管高於頂，<月曷>下迫頤'),
                         '脊管高於頂，<月曷>下迫頤')
        for text in ('<span>正文</span>', '<未知字>', '甲>乙', '<月曷><span>',
                     '< 月曷>', '<月 曷>', '<月曷 >', '<月\n曷>', '<月\t曷>',
                     '<月\u3000曷>', '<月\u00a0曷>', '<月\u200b曷>',
                     '<<月曷>>', '<月曷/>', '{ {正文', '正文} }', '[ [正文', '正文] ]'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                normalizer.normalize_markup(text)

    def test_pinned_glyph_templates_preserve_character_or_explicit_description(self):
        path = Path(__file__).resolve().parents[1] / "normalization.py"
        spec = importlib.util.spec_from_file_location("template_glyph_normalizer", path)
        normalizer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(normalizer)
        for glyph, description in (("𩤝", "馬敄"), ("𱯇", "⿰王叕")):
            text = "甲{{!|" + glyph + "|" + description + "}}乙"
            with self.subTest(text=text):
                self.assertEqual(normalizer.normalize_markup(text), "甲" + glyph + "乙")
                note = normalizer.extract_notes(text)[0]
                self.assertEqual(note["kind"], "source_glyph_encoded")
                self.assertEqual(note["primary"], glyph)
                self.assertEqual(note["description"], description)
        for description in ("⿰耒殳", "⿷匚晏", "⿰扌⿱攵音", "⿰米⿱㒵夊", "⿱𥫗𠕀"):
            text = "甲{{？|" + description + "}}乙"
            with self.subTest(text=text):
                display = "〔字形:" + description + "〕"
                self.assertEqual(normalizer.normalize_markup(text), "甲" + display + "乙")
                note = normalizer.extract_notes(text)[0]
                self.assertEqual(note["kind"], "source_glyph_unencoded")
                self.assertEqual(note["description"], description)
                self.assertEqual(note["display"], display)

    def test_unpinned_or_malformed_glyph_templates_are_rejected(self):
        path = Path(__file__).resolve().parents[1] / "normalization.py"
        spec = importlib.util.spec_from_file_location("strict_glyph_normalizer", path)
        normalizer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(normalizer)
        for text in ("{{!}}", "{{!|𩤝}}", "{{!|𩤝|馬敄|extra}}", "{{!|甲|馬敄}}",
                     "{{!|𩤝|⿰王叕}}", "{{!| 𩤝|馬敄}}", "{{!|𩤝|馬 敄}}",
                     "{{!|{{另|𩤝|甲}}|馬敄}}", "{{？}}", "{{？|}}", "{{？|⿰木木}}",
                     "{{？|⿰耒殳|甲}}", "{{？|⿰耒 殳}}", "{{?|⿰耒殳}}"):
            for operation in (normalizer.normalize_markup, normalizer.extract_notes):
                with self.subTest(text=text, operation=operation.__name__), self.assertRaises(ValueError):
                    operation(text)

    def test_weiliaozi_siku_glyph_indices_remain_explicit_without_guessing(self):
        normalizer = self.load_format_normalizer()
        for index in ("3951", "1841", "195", "2982"):
            with self.subTest(index=index):
                display = "〔四库字形:" + index + "〕"
                markup = "甲{{SKchar|" + index + "}}{{*|旧注{{SKchar|1841}}}}乙"
                self.assertEqual(normalizer.normalize_markup(markup), "甲" + display + "乙")
                self.assertEqual(normalizer.extract_notes(markup), [
                    {"kind": "source_glyph_unencoded", "description": "SKchar:" + index,
                     "display": display},
                    {"kind": "ancient_note_excluded", "text": "旧注{{SKchar|1841}}"},
                ])

    def test_unpinned_siku_indices_and_extra_arguments_are_rejected(self):
        normalizer = self.load_format_normalizer()
        for markup in ("{{SKchar|1}}", "{{SKchar|03951}}", "{{SKchar|3951|乙}}",
                       "{{SKchar|3951|}}", "{{SKchar|{{!|3951}}}}", "{{SKchar}}"):
            for operation in (normalizer.normalize_markup, normalizer.extract_notes):
                with self.subTest(markup=markup, operation=operation.__name__):
                    with self.assertRaises(ValueError):
                        operation(markup)

    def load_format_normalizer(self):
        path = Path(__file__).resolve().parents[1] / "normalization.py"
        spec = importlib.util.spec_from_file_location("format_normalizer", path)
        normalizer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(normalizer)
        return normalizer

    def test_zhanguoce_glyph_description_stays_literal_and_other_tags_fail(self):
        normalizer = self.load_format_normalizer()
        text = '勝<上股下目>{{*|鮑本作「臀」。}}曰'
        self.assertEqual(normalizer.normalize_markup(text), '勝<上股下目>曰')
        self.assertEqual(normalizer.extract_notes(text), [
            {'kind': 'ancient_note_excluded', 'text': '鮑本作「臀」。'}])
        for text in ('<上股下目/>', '<上股下目 >', '<上股下 目>',
                     '<上股下\n目>', '<上股下目 class="x">',
                     '<<上股下目>>', '<上股下目><script>甲</script>'):
            for operation in (normalizer.normalize_markup, normalizer.extract_notes):
                with self.subTest(text=text, operation=operation.__name__), self.assertRaises(ValueError):
                    operation(text)

    def test_pinned_year_links_keep_era_text_and_record_supplied_year(self):
        normalizer = self.load_format_normalizer()
        for value, display, supplied_year in (
                ("建安十六年", "建安十六年", None),
                ("章武三年", "章武三年", None),
                ("建興元年|223年", "建興元年", "223年"),
                ("景耀六年", "景耀六年", None)):
            text = "甲{{YL|" + value + "}}乙"
            self.assertEqual(normalizer.normalize_markup(text), "甲" + display + "乙")
            self.assertEqual(normalizer.extract_notes(text), [
                {"kind": "source_era_link", "display": display,
                 "year_argument": supplied_year}])

    def test_unpinned_or_malformed_year_links_rejected(self):
        normalizer = self.load_format_normalizer()
        for text in ("{{YL}}", "{{YL|}}", "{{YL|甲年}}", "{{YL|章武三年|}}",
                     "{{YL|章武三年|223年}}", "{{YL|建興元年|223年|余}}",
                     "{{YL| 建興元年|223年}}", "{{YL|[[章武三年]]}}"):
            for operation in (normalizer.normalize_markup, normalizer.extract_notes):
                with self.subTest(text=text), self.assertRaises(ValueError):
                    operation(text)

    def test_underlining_keeps_all_visible_characters(self):
        normalizer = self.load_format_normalizer()
        self.assertEqual(normalizer.normalize_markup("<u>孔子</u>與<u>顏回</u>問答。"),
                         "孔子與顏回問答。")
        self.assertEqual(normalizer.extract_notes("甲<u>乙</u>丙"), [])
        for text in ("<u>甲", "甲</u>", "<u><u>甲</u></u>",
                     '<u class="name">甲</u>', "<U>甲</U>", "<u/>甲"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                normalizer.normalize_markup(text)

    def test_pinned_formatting_anomalies_keep_text_and_record_repairs(self):
        normalizer = self.load_format_normalizer()
        for markup, display in (
                ("皆聖人所能為，</u>堯</u>、<u>舜</u>何不盡為之", "皆聖人所能為，堯、舜何不盡為之"),
                ("<<u>有苗</u>", "有苗")):
            self.assertEqual(normalizer.normalize_markup(markup), display)
            notes = normalizer.extract_notes(markup)
            self.assertEqual(len(notes), 1)
            self.assertEqual(notes[0]["kind"], "source_formatting_anomaly")
            self.assertEqual(notes[0]["markup"], markup)
            self.assertEqual(notes[0]["display"], display)
        for text in ("<<u>別文</u>", "皆聖人所能為。</u>堯</u>、<u>舜</u>何不盡為之"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                normalizer.normalize_markup(text)

    def test_formatting_repairs_leave_excluded_and_variant_notes_raw(self):
        normalizer = self.load_format_normalizer()
        markup = "<<u>有苗</u>"
        cases = (
            ("{{*|" + markup + "}}", "", {"kind": "ancient_note_excluded", "text": markup}),
            ("{{另|正文|" + markup + "}}", "正文",
             {"kind": "source_variant_template", "primary": "正文", "alternative": markup}),
            ("{{另2|正文|" + markup + "}}", "正文",
             {"kind": "source_variant_note", "primary": "正文", "note": markup}),
            ("<ref>" + markup + "</ref>", "",
             {"kind": "source_reference_excluded", "markup": "<ref>" + markup + "</ref>"}),
        )
        for text, display, note in cases:
            with self.subTest(text=text):
                self.assertEqual(normalizer.normalize_markup("甲" + text + "乙"), "甲" + display + "乙")
                self.assertEqual(normalizer.extract_notes("甲" + text + "乙"), [note])

    def test_formatting_notes_record_repairs_in_variant_primary_and_joined_body(self):
        normalizer = self.load_format_normalizer()
        markup = "<<u>有苗</u>"
        repair = {"kind": "source_formatting_anomaly", "markup": markup, "display": "有苗"}
        for name, kind, field in (("另", "source_variant_template", "alternative"),
                                  ("另2", "source_variant_note", "note")):
            with self.subTest(template=name):
                text = "甲{{" + name + "|" + markup + "|異文}}乙"
                self.assertEqual(normalizer.normalize_markup(text), "甲有苗乙")
                self.assertEqual(normalizer.extract_notes(text), [
                    repair, {"kind": kind, "primary": markup, field: "異文"}])
        joined = "甲<<u>有{{*|旁注}}苗</u>乙"
        self.assertEqual(normalizer.normalize_markup(joined), "甲有苗乙")
        self.assertEqual(normalizer.extract_notes(joined), [
            repair, {"kind": "ancient_note_excluded", "text": "旁注"}])

    def test_extract_notes_rejects_invalid_primary_underlining(self):
        normalizer = self.load_format_normalizer()
        for text in ("<u>甲", "甲</u>", "<u><u>甲</u></u>",
                     '<u class="name">甲</u>', "<U>甲</U>", "<u/>甲", "<<u>別文</u>"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                normalizer.extract_notes(text)

    def test_missing_passage_rejected(self):
        corpus = self.book()
        corpus["passages"].pop()
        self.assert_invalid(corpus, "未逐段完整依次对应")

    def test_manifest_gap_rejected_even_after_rehash(self):
        path = "sample/source/extraction.json"
        extraction = kb.read_json(self.root / path)
        extraction["segments"][1]["start"] += 1
        self.write(path, extraction)
        source = kb.read_json(self.root / "sample/source/source.json")
        source["extraction_sha256"] = kb.digest(self.root / path)
        self.write("sample/source/source.json", source)
        self.assert_invalid(self.book(), "缺漏、重叠")

    def test_manifest_tampering_rejected(self):
        path = "sample/source/extraction.json"
        extraction = kb.read_json(self.root / path)
        extraction["segments"][1] = dict(extraction["segments"][1], kind="excluded", reason="伪造排除")
        self.write(path, extraction)
        self.assert_invalid(self.book(), "正文提取记录摘要不符")

    def test_wrong_quote_book_rejected(self):
        corpus = self.book()
        corpus["examples"][0]["quotes"][0]["passage_id"] = "OTHER-01-001"
        self.assert_invalid(corpus, "引句不在所列本书原文")

    def test_empty_quote_rejected(self):
        corpus = self.book()
        corpus["examples"][0]["quotes"][0]["text"] = ""
        self.assert_invalid(corpus, "引句不在所列本书原文")

    def test_analysis_missing_or_wrong_order_rejected(self):
        corpus = self.book()
        corpus["chapters"][0]["readings"].reverse()
        self.assert_invalid(corpus, "释义段落跨篇、遗漏或乱序")
        corpus["chapters"][0]["readings"].pop()
        self.assert_invalid(corpus, "逐段释义存在遗漏")

    def test_cross_book_id_collision_rejected(self):
        other = {"id": "other", "title": "另一原典", "path": "other", "status": "ready"}
        self.make_book(other, "AB")
        self.write("catalog.json", {"schema_version": 1, "books": [self.entry, other]})
        report, _ = kb.validate_catalog(self.root)
        self.assertFalse(report["valid"])
        self.assertIn("编号与其他记录碰撞", str(report))

    def test_staged_books_not_searched(self):
        other = {"id": "unfinished", "title": "待整理", "path": "unfinished", "status": "staged"}
        self.write("catalog.json", {"schema_version": 1, "books": [self.entry, other]})
        report, books = kb.validate_catalog(self.root)
        self.assertTrue(report["valid"], report)
        self.assertEqual([b["entry"]["id"] for b in books], ["sample"])
        with self.assertRaises(ValueError):
            kb.selected_entries(kb.load_catalog(self.root), "unfinished")

    def test_renderer_escapes_html(self):
        corpus = self.book()
        corpus["chapters"][0]["readings"][0]["explanation"] = '<script>alert("bad")</script>'
        corpus["chapters"][0]["overview"] = '<img src=x onerror="bad">'
        kb.render_book(corpus)
        html = (corpus["root"] / "阅览.html").read_text(encoding="utf-8")
        self.assertNotIn("<script>", html)
        self.assertNotIn("<img src=x", html)
        self.assertIn("&lt;script&gt;", html)
        self.assertIn("AI 释义提要", html)
        self.assertIn("现代类比", html)

    def test_javascript_source_link_rejected(self):
        corpus = self.book()
        corpus["passages"][0]["source_url"] = "javascript:alert(1)"
        self.assert_invalid(corpus, "来源链接须为 HTTP(S)")

    def test_collation_notice_tracks_available_notes(self):
        corpus = self.book()
        notes = corpus["root"] / "对读校记.md"
        for present in (True, False):
            with self.subTest(notes_present=present):
                if present:
                    notes.write_text("版本对读记录", encoding="utf-8")
                else:
                    notes.unlink()
                kb.render_book(corpus)
                html = (corpus["root"] / "阅览.html").read_text(encoding="utf-8")
                original = (corpus["root"] / "原文.md").read_text(encoding="utf-8")
                self.assertEqual('href="对读校记.md"' in html, present)
                self.assertEqual('[对读校记](对读校记.md)' in original, present)
                if present:
                    self.assertLess(html.index('href="对读校记.md"'), html.index('</header>'))

    def test_search_returns_actual_original_and_book(self):
        rows = kb.search("自知者明", [self.book()])
        self.assertEqual(rows[0]["id"], "AB-01-002")
        self.assertEqual(rows[0]["text"], "自知者明。")
        self.assertEqual(rows[0]["book"], "sample")

    def test_locator_metadata_is_returned_and_escaped_in_html(self):
        corpus = self.book()
        corpus['passages'][1]['part'] = '内篇<script>'
        corpus['passages'][1]['source_section'] = '二之一'
        row = kb.search('自知者明', [corpus])[0]
        self.assertEqual(row['source_section'], '二之一')
        self.assertEqual(row['part'], '内篇<script>')
        kb.render_book(corpus)
        html = (corpus['root'] / '阅览.html').read_text(encoding='utf-8')
        self.assertNotIn('内篇<script>', html)
        self.assertIn('内篇&lt;script&gt;', html)
        self.assertIn('二之一', html)

    def test_empty_search_and_unknown_terms(self):
        for term in ("", "   ", "!!!", "nonexistentword"):
            self.assertEqual(kb.search(term, [self.book()]), [])

    def test_catalog_cannot_escape_directory(self):
        self.write("catalog.json", {"schema_version": 1, "books": [dict(self.entry, path="../elsewhere")]})
        with self.assertRaises(ValueError):
            kb.load_catalog(self.root)

    def test_bad_book_has_nonzero_cli_exit(self):
        path = self.root / "sample/source/source.wikitext"
        path.write_text("corrupted", encoding="utf-8")
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(kb.main(["--root", str(self.root), "search", "自知", "--json"]), 1)


if __name__ == "__main__":
    unittest.main()
