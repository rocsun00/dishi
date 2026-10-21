#!/usr/bin/env python3
"""Offline, source-traceable multi-book reader. Python 3.9+, standard library only."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
from html import escape
import importlib.util
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
SAFE_ID = re.compile(r"[A-Za-z][A-Za-z0-9_-]*\Z")
# Load the sibling by path so direct CLI use and importlib-based callers agree.
_english_spec = importlib.util.spec_from_file_location("dishi_english_query", ROOT / "english_query.py")
_english_query = importlib.util.module_from_spec(_english_spec)
_english_spec.loader.exec_module(_english_query)
explain_query = _english_query.explain_query
_ranking_spec = importlib.util.spec_from_file_location("dishi_ranking", ROOT / "ranking.py")
_ranking = importlib.util.module_from_spec(_ranking_spec)
_ranking_spec.loader.exec_module(_ranking)


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def confined(root, relative):
    """Keep catalog and metadata paths inside their intended directory."""
    root = Path(root).resolve()
    path = (root / relative).resolve()
    if path == root or root not in path.parents:
        raise ValueError("路径超出知识库目录：" + str(relative))
    return path


def load_catalog(root=ROOT):
    catalog = read_json(Path(root) / "catalog.json")
    if catalog.get("schema_version") != 1 or not isinstance(catalog.get("books"), list):
        raise ValueError("catalog 必须为 schema_version=1 的 books 列表")
    seen = set()
    paths = set()
    for entry in catalog["books"]:
        if not SAFE_ID.fullmatch(entry["id"]) or entry["id"] in seen:
            raise ValueError("典籍编号无效或重复：" + entry["id"])
        seen.add(entry["id"])
        book_root = confined(root, entry["path"])
        if book_root in paths:
            raise ValueError("典籍目录重复：" + entry["path"])
        paths.add(book_root)
        if entry["status"] not in ("ready", "staged"):
            raise ValueError("典籍状态须为 ready 或 staged")
        if entry.get("adapter", "generic") not in ("generic", "sunzi"):
            raise ValueError("未知典籍适配器")
        if entry.get("adapter") == "sunzi" and (entry["id"] != "sunzi" or entry["path"] != "sunzi"):
            raise ValueError("sunzi 适配器仅用于现有孙子库")
    return catalog


def selected_entries(catalog, book=None, allow_staged=False):
    entries = [row for row in catalog["books"] if row["id"] == book] if book else catalog["books"]
    if book and not entries:
        raise ValueError("未登记典籍：" + book)
    if book and entries[0]["status"] != "ready" and not allow_staged:
        raise ValueError("该典籍尚在整理，不进入检索：" + book)
    return entries if allow_staged and book else [row for row in entries if row["status"] == "ready"]


def load_book(entry, root=ROOT):
    book_root = confined(root, entry["path"])
    passages = [json.loads(line) for line in (book_root / "data/passages.jsonl").read_text(encoding="utf-8").splitlines() if line.strip()]
    chapters = read_json(book_root / "data/analysis.json")
    return {
        "entry": entry, "root": book_root,
        "source": read_json(book_root / "source/source.json"),
        "search_text": read_json(book_root / "data/search_text.json"),
        "search_metadata": read_json(book_root / "source/search_normalization.json"),
        "passages": passages, "by_id": {p["id"]: p for p in passages},
        "chapters": chapters,
        "readings": {r["passage_id"]: r for c in chapters for r in c["readings"]},
        "concepts": [card for c in chapters for card in c["concepts"]],
        "examples": read_json(book_root / "data/examples.json"),
    }


def chapter_numbers(source):
    """Keep original chapter numbers when a transmitted work has lost chapters."""
    count = source["chapter_count"]
    if type(count) is not int or count < 1:
        raise ValueError("现存篇数须为正整数")
    numbers = source.get("chapter_numbers", list(range(1, count + 1)))
    if (not isinstance(numbers, list) or len(numbers) != count
            or any(type(number) is not int or number < 1 for number in numbers)
            or numbers != sorted(set(numbers))):
        raise ValueError("篇号清单须为与现存篇数相符的递增正整数列表")
    return numbers


def check_analysis(book, errors):
    passages, by_id = book["passages"], book["by_id"]
    chapters = book["chapters"]
    expected_chapters = chapter_numbers(book["source"])
    if [c["chapter"] for c in chapters] != expected_chapters:
        errors.append("释义篇次缺失、重复或乱序")
    reading_ids = [r["passage_id"] for c in chapters for r in c["readings"]]
    if Counter(reading_ids) != Counter(by_id.keys()):
        errors.append("逐段释义存在遗漏、重复或无效编号")
    for chapter in chapters:
        expected = [p["id"] for p in passages if p["chapter"] == chapter["chapter"]]
        mapped = {pid for block in chapter["argument_map"] for pid in block["passage_ids"]}
        if mapped != set(expected):
            errors.append("论证结构覆盖不符：" + str(chapter["chapter"]))
        if [r["passage_id"] for r in chapter["readings"]] != expected:
            errors.append("释义段落跨篇、遗漏或乱序：" + str(chapter["chapter"]))
        if not chapter.get("overview", "").strip():
            errors.append("篇章导读为空")
        for reading in chapter["readings"]:
            if not reading.get("explanation", "").strip() or not isinstance(reading.get("terms"), dict):
                errors.append("释义缺失或词义格式错误：" + reading["passage_id"])
        for card in chapter["concepts"]:
            if any(pid not in expected for pid in card["passage_ids"]):
                errors.append("思想卡跨篇：" + card["id"])
            required = ("title", "source_context", "interpretation", "misreading", "modern_application", "boundary")
            if any(not isinstance(card.get(field), str) or not card[field].strip() for field in required):
                errors.append("思想卡缺少语境、解释或应用边界：" + card["id"])
            if any(not isinstance(card.get(field), list) or not card[field] or any(not isinstance(value, str) or not value.strip() for value in card[field]) for field in ("tags", "conditions")):
                errors.append("思想卡关键词或条件格式无效：" + card["id"])
    ids = [card["id"] for card in book["concepts"]] + [q["id"] for q in book["examples"]]
    if len(ids) != len(set(ids)) or any(not SAFE_ID.fullmatch(pid) for pid in ids):
        errors.append("思想卡或示例编号无效或重复")
    verified = 0
    for card in book["concepts"]:
        refs = card["passage_ids"]
        if not refs or any(pid not in by_id for pid in refs):
            errors.append("思想卡原文编号无效：" + card["id"])
        elif not card.get("quote", "").strip() or not any(card["quote"] in by_id[pid]["text"] for pid in refs):
            errors.append("思想卡引句不在所列本书原文：" + card["id"])
        else:
            verified += 1
    for example in book["examples"]:
        refs = example["passage_ids"]
        if not refs or any(pid not in by_id for pid in refs):
            errors.append("示例原文编号无效：" + example["id"])
        if not example.get("question", "").strip() or not example.get("answer", "").strip():
            errors.append("问答内容为空：" + example["id"])
        for quote in example.get("quotes", []):
            pid, text = quote["passage_id"], quote["text"]
            if not text.strip() or pid not in refs or pid not in by_id or text not in by_id[pid]["text"]:
                errors.append("示例引句不在所列本书原文：" + example["id"])
            else:
                verified += 1
    return verified


def sunzi_report(book):
    """Reuse the established Sunzi validator; never alter the legacy corpus."""
    spec = importlib.util.spec_from_file_location("dishi_sunzi_legacy", book["root"] / "kb.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.validate(module.load_corpus(book["root"]), book["root"])


def validate_book(book):
    entry, root, source = book["entry"], book["root"], book["source"]
    errors = []
    quotes = 0
    try:
        if entry.get("adapter") == "sunzi":
            legacy = sunzi_report(book)
            errors.extend(legacy["errors"])
            quotes = legacy["verified_quotes"]
        else:
            if source["id"] != entry["id"] or source["title"] != entry["title"]:
                errors.append("典籍身份与目录不符")
            if not source.get("revision") or not safe_url(source.get("source_url", "")):
                errors.append("来源修订号或网页地址无效")
            raw_path = confined(root / "source", source["raw_file"])
            raw = raw_path.read_bytes().decode("utf-8")
            if digest(raw_path) != source["raw_sha256"]:
                errors.append("原始快照摘要不符")
            extraction = read_json(root / "source/extraction.json")
            if digest(root / "source/extraction.json") != source["extraction_sha256"]:
                errors.append("正文提取记录摘要不符")
            validate_extraction(book, extraction, raw, errors)
            if len(book["passages"]) != source["passage_count"]:
                errors.append("段落总数不符")
            if len(book["chapters"]) != source["chapter_count"]:
                errors.append("篇章总数不符")
            if len(book["by_id"]) != len(book["passages"]):
                errors.append("原文段落编号重复")
            if any(not SAFE_ID.fullmatch(p["id"]) for p in book["passages"]):
                errors.append("原文段落编号格式无效")
            if set(book["search_text"]) != set(book["by_id"]):
                errors.append("检索层未完整对应原文段落")
            if digest(root / "data/search_text.json") != book["search_metadata"]["sha256"]:
                errors.append("检索层摘要不符")
            if any(not isinstance(text, str) for text in book["search_text"].values()):
                errors.append("检索层正文格式无效")
            quotes = check_analysis(book, errors)
        # All books, including the legacy adapter, must have safe outbound links.
        if any(not safe_url(p["source_url"]) for p in book["passages"]):
            errors.append("原文来源链接须为 HTTP(S)")
    except (OSError, ValueError, KeyError, TypeError, IndexError) as error:
        errors.append("数据结构或来源记录不可校验：" + str(error))
    return {"id": entry["id"], "title": entry["title"], "valid": not errors,
            "chapters": len(book["chapters"]), "passages": len(book["passages"]),
            "readings": sum(len(c["readings"]) for c in book["chapters"]),
            "concepts": len(book["concepts"]), "examples": len(book["examples"]),
            "verified_quotes": quotes, "errors": errors}


def validate_extraction(book, extraction, raw, errors):
    """Validate the complete importer manifest, not merely its file hash."""
    if extraction.get("schema_version") != 1 or extraction.get("normalization") != "wiki-body-v1":
        errors.append("正文提取记录版本或处理规则无效")
        return
    module_path = book["root"].parent / "normalization.py"
    spec = importlib.util.spec_from_file_location("dishi_body_normalization", module_path)
    normalizer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(normalizer)
    cursor, selected = 0, []
    for segment in extraction["segments"]:
        start, end = segment["start"], segment["end"]
        if not isinstance(start, int) or not isinstance(end, int) or start != cursor or not start < end <= len(raw):
            errors.append("来源提取区间缺漏、重叠、乱序或越界")
            return
        cursor = end
        if segment["kind"] == "passage":
            selected.append(segment)
        elif segment["kind"] != "excluded" or not segment.get("reason", "").strip():
            errors.append("排除来源片段未说明原因或类型无效")
    if cursor != len(raw):
        errors.append("来源提取区间未覆盖全部快照")
    if [segment["id"] for segment in selected] != [p["id"] for p in book["passages"]]:
        errors.append("正文与提取记录未逐段完整依次对应")
        return
    prefix = book["source"]["prefix"]
    pages = book["source"].get("source_pages", [])
    previous_page_end = 0
    for page in pages:
        start, end = page["start"], page["end"]
        if not isinstance(start, int) or not isinstance(end, int) or not 0 <= start < end <= len(raw) or start < previous_page_end:
            errors.append("来源页面区间重叠、乱序或越界")
            return
        previous_page_end = end
    expected_chapters = chapter_numbers(book["source"])
    sequence = Counter()
    previous_chapter = 0
    for p, segment in zip(book["passages"], selected):
        start, end = segment["start"], segment["end"]
        markup = raw[start:end]
        if p["source_start"] != start or p["source_end"] != end or p["source_line"] != raw.count("\n", 0, start) + 1:
            errors.append("原文定位与快照不符：" + p["id"])
        if p["source_markup"] != markup or p["text"] != normalizer.normalize_markup(markup):
            errors.append("原文不忠于来源快照：" + p["id"])
        matches = [page for page in pages if page["start"] <= start and end <= page["end"]]
        origin = matches[0] if len(matches) == 1 else book["source"] if not pages else None
        if origin is None:
            errors.append("原文未唯一对应来源页面：" + p["id"])
        else:
            expected_url = origin.get("url", origin.get("source_url", ""))
            actual_url = urlsplit(p["source_url"])._replace(fragment="").geturl()
            if p["source_revision"] != origin["revision"] or actual_url != urlsplit(expected_url)._replace(fragment="").geturl():
                errors.append("原文修订号或来源链接与快照页面不符：" + p["id"])
        if not p["text"].strip():
            errors.append("原文段落为空：" + p["id"])
        if p["chapter"] not in expected_chapters or p["chapter"] < previous_chapter:
            errors.append("原文归篇次序无效：" + p["id"])
            continue
        previous_chapter = p["chapter"]
        sequence[p["chapter"]] += 1
        expected_id = "{}-{:02d}-{:03d}".format(prefix, p["chapter"], sequence[p["chapter"]])
        if p["id"] != expected_id:
            errors.append("原文编号与篇次段序不符：" + p["id"])
        if hasattr(normalizer, "extract_notes") and p.get("editorial_notes", []) != normalizer.extract_notes(markup):
            errors.append("底本异文与快照不符：" + p["id"])
    if sorted(sequence) != expected_chapters:
        errors.append("原文篇章存在缺失")
    for page in book["source"].get("source_pages", []):
        if not safe_url(page["url"]) or not page.get("revision"):
            errors.append("合并来源的页面地址或版本无效")
        if "start" in page and "end" in page:
            body = raw[page["start"]:page["end"]]
            if hashlib.sha256(body.encode("utf-8")).hexdigest() != page["raw_sha256"]:
                errors.append("合并来源的页面摘要不符")
            page_path = confined(book["root"] / "source", page["raw_file"])
            if page_path.read_bytes().decode("utf-8") != body:
                errors.append("合并来源与独立页面快照不符")


def validate_catalog(root=ROOT, book=None):
    catalog = load_catalog(root)
    entries = selected_entries(catalog, book, allow_staged=True)
    reports, books = [], []
    seen = {}
    for entry in entries:
        try:
            corpus = load_book(entry, root)
            report = validate_book(corpus)
            for pid in list(corpus["by_id"]) + [c["id"] for c in corpus["concepts"]] + [q["id"] for q in corpus["examples"]]:
                if pid in seen:
                    report["errors"].append("编号与其他记录碰撞：" + pid + " / " + seen[pid])
                    report["valid"] = False
                seen[pid] = entry["id"]
            reports.append(report)
            books.append(corpus)
        except (OSError, ValueError, KeyError, TypeError) as error:
            reports.append({"id": entry["id"], "valid": False, "errors": [str(error)]})
    return {"valid": all(r["valid"] for r in reports), "books": reports,
            "staged": [e["id"] for e in catalog["books"] if e["status"] == "staged"]}, books


def safe_url(value):
    parsed = urlsplit(value)
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


def result_record(p, book, score):
    reading = book["readings"][p["id"]]
    return {"book": book["entry"]["id"], "book_title": book["entry"]["title"],
            "id": p["id"], "chapter": p["chapter"], "chapter_title": p["chapter_title"],
            "score": score, "text": p["text"], "explanation": reading["explanation"],
            "caution": reading.get("caution", ""), "source_url": p["source_url"],
            "concepts": [c["title"] for c in book["concepts"] if p["id"] in c["passage_ids"]],
            **{key: p[key] for key in ("part", "source_section") if p.get(key)}}


def checked_query_explanation(query, books):
    """Add corpus availability to the adapter's syntax-only ID recognition."""
    explanation = explain_query(query)
    known_ids = {pid for book in books for pid in book["by_id"]}
    explanation["unresolved_passage_ids"] = [pid for pid in explanation.get("passage_ids", [])
                                             if pid not in known_ids]
    return explanation


def search(query, books, limit=5):
    """Field-aware lexical ranking; scores are overlap, never confidence."""
    original_query = query
    query = query.strip()
    if not query:
        return []
    for book in books:
        if query.upper() in book["by_id"]:
            row = result_record(book["by_id"][query.upper()], book, 1.0)
            row["match_type"] = "explicit_reference"
            return [row]
    explanation = checked_query_explanation(original_query, books) if re.search(r"[A-Za-z]", query) else None
    words = explanation["retrieval_terms"] if explanation else re.findall(r"[a-zA-Z0-9_-]+|[\u3400-\u9fff]+", query.lower())
    groups = _ranking.query_groups(words, explanation)
    rows = []
    # Explicit references are placed first and labeled separately. Their legacy
    # 1.0 lookup placeholder is not a lexical score or confidence estimate.
    for pid in explanation.get("passage_ids", []) if explanation else []:
        for book in books:
            if pid in book["by_id"] and not any(row["id"] == pid for row in rows):
                row = result_record(book["by_id"][pid], book, 1.0)
                row["match_type"] = "explicit_reference"
                row["query_explanation"] = explanation
                rows.append(row)
    if len(rows) >= limit:
        return rows[:limit]
    direct_ids = {row["id"] for row in rows}
    recommended = explanation.get("recommended_books", []) if explanation else []
    for book, passage, score in _ranking.rank(books, groups, include_titles=bool(explanation),
                                               recommended_books=recommended):
        if passage["id"] in direct_ids:
            continue
        row = result_record(passage, book, round(score, 4))
        row["match_type"] = "lexical"
        if book["entry"]["id"] in recommended:
            row["book_hint_boost"] = _ranking.BOOK_HINT_BOOST
        if explanation:
            row["query_explanation"] = explanation
        rows.append(row)
        if len(rows) >= limit:
            break
    return rows[:limit]


def print_query_hints(explanation):
    """Display adapter aids that must not look like positive source evidence."""
    for item in explanation.get("suppressed_mappings", []):
        print("英文否定下未启用的映射 / Suppressed mapping: {} -> {}".format(
            item["input"], "、".join(item["keywords"])))
    if explanation.get("recommended_books"):
        scopes = " / ".join("--book " + bid for bid in explanation["recommended_books"])
        print("阅读提示（匹配候选有轻微排序加权，未限定典籍） / Book hints: " + scopes)
    if explanation.get("passage_ids") and not explanation["direct_id"]:
        print("显式段号（须核验是否存在） / Explicit passage IDs: " + ", ".join(explanation["passage_ids"]))
    if explanation.get("suppressed_passage_ids"):
        print("英文否定下未直达的段号 / Suppressed passage IDs: "
              + ", ".join(explanation["suppressed_passage_ids"]))
    if explanation.get("unresolved_passage_ids"):
        print("当前检索范围未找到段号 / IDs not found in selected corpus: "
              + ", ".join(explanation["unresolved_passage_ids"]))


def ref(pid):
    return "[{}](原文.md#{})".format(pid, pid.lower())


def editorial_summary(notes):
    variants = ["正文作“{}”，异文作“{}”".format(v["primary"], v["alternative"]) for v in notes if v.get("kind") == "source_variant_template"]
    variants += ["正文作“{}”；底本注记：{}".format(v["primary"], v["note"]) for v in notes if v.get("kind") == "source_variant_note"]
    ancient = sum(v.get("kind") == "ancient_note_excluded" for v in notes)
    if ancient:
        variants.append("本段来源古注 {} 条另存于来源数据，未混入正文与 AI 释义".format(ancient))
    references = sum(v.get("kind") == "source_reference_excluded" for v in notes)
    if references:
        variants.append("源页面参考注记 {} 条另存来源数据；属于编者注记，未混入正文".format(references))
    return "；".join(variants)


def render_book(book):
    report = validate_book(book)
    if not report["valid"]:
        raise ValueError("；".join(report["errors"]))
    root, source = book["root"], book["source"]
    title = book["entry"]["title"]
    revision = source.get("revision", source.get("source_revision"))
    original = ["# " + title + "原文", "", "电子工作底本：[固定修订版 {}]({})。段落编号为本库所加；保留来源正文，异文单列。".format(revision, source["source_url"]), ""]
    collation_notice = ""
    if (root / "对读校记.md").is_file():
        original += ["本电子底本含已列出的疑字或校改，请查 [对读校记](对读校记.md) 后再引用；此处保留固定页面原貌。", ""]
        collation_notice = '<p class="notice">本电子底本含已列出的疑字或校改。引用时须区分版本，参阅<a href="对读校记.md">对读校记</a>；不能把工作本疑字直接当作古人主张。</p>'
    guide = ["# " + title + "逐篇导读", "", "以下为 AI 依据固定原文撰写的释义提要，不是古代注家原注或逐字全译。现代应用另列；版本与校核范围见《质量说明》。", ""]
    index = ["# " + title + "思想索引", "", "原典语境、AI 解释和现代类比分列；引句可按段号回查。", ""]
    examples = ["# " + title + "问答示例", "", "以下为可审查的阅读与应用示例；现代建议为类比推演，不等同于原典直接结论，也不是模型训练成绩。", ""]
    nav, sections = [], []
    for chapter in book["chapters"]:
        n, heading = chapter["chapter"], chapter["title_simplified"]
        original += ["## {:02d} {}".format(n, heading), ""]
        guide += ["## {:02d} {}".format(n, heading), "", chapter["overview"], "", "论证结构：", ""]
        for block in chapter["argument_map"]:
            guide += ["- " + "、".join(ref(pid) for pid in block["passage_ids"]) + "：" + block["point"]]
        guide.append("")
        nav.append('<a href="#chapter-{}">{:02d} {}</a>'.format(n, n, escape(heading)))
        segments = []
        for reading in chapter["readings"]:
            pid = reading["passage_id"]
            p = book["by_id"][pid]
            notes = editorial_summary(p.get("editorial_notes", []))
            locator = " · ".join(str(p[key]) for key in ("part", "source_section") if p.get(key))
            original += ["### " + pid, "", p["text"], ""]
            if locator:
                original += ["篇组或源章句标记：" + locator, ""]
            if notes:
                original += ["来源处理说明：" + notes, ""]
            guide += ["### " + pid, "", "原文：" + ref(pid), "", reading["explanation"], ""]
            terms = "；".join(k + "：" + v for k, v in reading.get("terms", {}).items())
            caution = reading.get("caution", "")
            if terms:
                guide += ["词义提示：" + terms, ""]
            if caution:
                guide += ["读法与边界：" + caution, ""]
            extras = "".join('<p class="note">{}　{}</p>'.format(label, escape(value)) for label, value in [("词义提示", terms), ("读法与边界", caution), ("来源处理", notes)] if value)
            display_id = pid + (" · " + locator if locator else "")
            segments.append('<article id="{}"><p class="id">{} · <a href="{}">核对来源</a></p><div class="parallel"><div><b>原文</b><p class="original">{}</p></div><div><b>AI 释义提要</b><p>{}</p>{}</div></div></article>'.format(pid.lower(), escape(display_id), escape(p["source_url"], quote=True), escape(p["text"]), escape(reading["explanation"]), extras))
        cards = []
        index += ["## {:02d} {}".format(n, heading), ""]
        for card in chapter["concepts"]:
            index += ["### " + card["id"] + " " + card["title"], "", "关键词：" + "、".join(card["tags"]), "", "> " + card["quote"], "", "原文定位：" + "、".join(ref(pid) for pid in card["passage_ids"]), ""]
            fields = [("原典语境", card["source_context"]), ("思想解释", card["interpretation"]), ("成立条件", "；".join(card["conditions"])), ("常见误读", card["misreading"]), ("现代类比", card["modern_application"]), ("应用边界", card["boundary"])]
            for label, value in fields:
                index += [label + "：" + value, ""]
            links = "、".join('<a href="#{}">{}</a>'.format(pid.lower(), pid) for pid in card["passage_ids"])
            cards.append('<details><summary>{}</summary><blockquote>{}</blockquote><p>原文定位：{}</p>{}</details>'.format(escape(card["title"]), escape(card["quote"]), links, "".join('<p><b>{}</b>　{}</p>'.format(label, escape(value)) for label, value in fields)))
        sections.append('<section id="chapter-{}"><h2>{:02d} {}</h2><p class="overview">{}</p>{}<div class="cards"><h3>本篇思想卡</h3>{}</div></section>'.format(n, n, escape(heading), escape(chapter["overview"]), "".join(segments), "".join(cards)))
    answers = []
    for example in book["examples"]:
        examples += ["## " + example["id"] + " " + example["question"], "", example["answer"], "", "原文依据：" + "、".join(ref(pid) for pid in example["passage_ids"]), ""]
        links = "、".join('<a href="#{}">{}</a>'.format(pid.lower(), pid) for pid in example["passage_ids"])
        answers.append('<details><summary>{}</summary><p>{}</p><p>原文定位：{}</p></details>'.format(escape(example["question"]), escape(example["answer"]), links))
    for name, lines in [("原文.md", original), ("逐篇导读.md", guide), ("思想索引.md", index), ("问答示例.md", examples)]:
        (root / name).write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    html = '<!doctype html><html lang="zh-Hans"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>帝师知识库 · ' + escape(title) + '</title><style>' + CSS + '</style></head><body><aside><h1>帝师知识库</h1><p>' + escape(title) + '</p><nav>' + "".join(nav) + '<a href="#examples">问答示例</a></nav><p><a href="../知识库总览.md">全部典籍</a></p></aside><main><header><p>公开原典与可核查解读</p><h1>' + escape(title) + '</h1><p>' + str(report["chapters"]) + ' ' + escape(str(source.get("chapter_unit", "篇"))) + '原文 · ' + str(report["passages"]) + ' 段对应释义 · ' + str(report["concepts"]) + ' 张思想卡 · ' + str(report["examples"]) + ' 个问答</p><p class="notice">固定电子工作底本，修订版 ' + escape(str(revision)) + '。AI 释义不等于古注，现代应用属于类比。未进行模型微调；未经专家逐字校勘。<a href="质量说明.md">质量与来源说明</a></p></header>' + "".join(sections) + '<section id="examples"><h2>问答示例</h2>' + "".join(answers) + '</section><footer><a href="' + escape(source["source_url"], quote=True) + '">来源与版本</a> · 原始快照与整理数据均保存在本地。</footer></main></body></html>'
    if collation_notice:
        html = html.replace("</header>", collation_notice + "</header>", 1)
    (root / "阅览.html").write_text(html + "\n", encoding="utf-8")
    (root / "data/validation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


CSS = """:root{color-scheme:light;--ink:#263532;--muted:#5b6864;--paper:#f6f3ec;--line:#d9dfd8;--accent:#235d4c}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:17px/1.85 -apple-system,BlinkMacSystemFont,'PingFang SC','Microsoft YaHei',sans-serif}a{color:var(--accent);text-underline-offset:4px}a:focus-visible,summary:focus-visible{outline:3px solid #8c4e1d;outline-offset:4px}aside{position:fixed;inset:0 auto 0 0;width:240px;padding:32px 22px;overflow:auto;border-right:1px solid var(--line);background:#eeeee5}aside h1{font-size:22px}aside p{font-size:14px}nav a{display:block;padding:5px 0;font-size:14px}main{margin-left:240px;max-width:1450px;padding:45px 5vw}header{margin-bottom:45px}h1,h2,h3{line-height:1.4}main h1{font-size:36px}h2{font-size:27px}h3{font-size:20px}.notice,.note{border-left:3px solid #b58950;padding:12px 18px;background:#f0e8d9;font-size:14px}.overview{color:var(--muted)}section{margin:55px 0;scroll-margin-top:25px}article{border-top:1px solid var(--line);padding:22px 0;scroll-margin-top:20px}.id{font-size:12px;color:var(--muted)}.parallel{display:grid;grid-template-columns:1fr 1fr;gap:32px}.parallel b{font-size:13px;color:var(--accent)}.original{font-family:'Songti SC','Noto Serif CJK TC',serif;font-size:19px;line-height:2}.cards{background:#eeeee5;padding:15px 24px}details{border-top:1px solid var(--line);padding:12px 0}summary{cursor:pointer;font-weight:600}details p,blockquote{font-size:15px}blockquote{border-left:3px solid #8caa9b;margin:18px 0;padding-left:18px}footer{font-size:13px;border-top:1px solid var(--line);padding-top:20px}@media(max-width:850px){aside{position:static;width:auto;padding:20px}nav{display:flex;gap:4px 18px;flex-wrap:wrap}nav a{font-size:13px}main{margin:0;padding:28px 20px}.parallel{grid-template-columns:1fr;gap:10px}main h1{font-size:30px}}@media print{aside{display:none}main{margin:0;padding:0}details{break-inside:avoid}.cards{background:none}}"""


def main(argv=None):
    parser = argparse.ArgumentParser(description="帝师多典籍本地知识库：只检索已验收原典，不联网或自动生成答案")
    parser.add_argument("--root", type=Path, default=ROOT, help=argparse.SUPPRESS)
    sub = parser.add_subparsers(dest="command", required=True)
    find = sub.add_parser("search", help="跨已完成典籍检索原文与释义")
    find.add_argument("query")
    find.add_argument("--limit", type=int, choices=range(1, 21), default=5)
    find.add_argument("--book")
    find.add_argument("--json", action="store_true")
    explain = sub.add_parser("explain-query", help="说明有限英文关键词映射 / Explain offline keyword mapping")
    explain.add_argument("query")
    explain.add_argument("--json", action="store_true")
    show = sub.add_parser("show", help="按段号读取原文与释义")
    show.add_argument("passage_id")
    show.add_argument("--book")
    for name in ("validate", "build"):
        command = sub.add_parser(name)
        command.add_argument("--book", help="可指定待验收典籍；默认仅处理 ready")
    sub.add_parser("list", help="列出已完成与整理中的典籍")
    args = parser.parse_args(argv)
    try:
        if args.command == "explain-query":
            explanation = explain_query(args.query)
            if args.json:
                print(json.dumps(explanation, ensure_ascii=False, indent=2))
            else:
                print("原查询 / Original query: " + explanation["query"])
                if explanation["direct_id"]:
                    print("段号直达（是否存在由 search/show 核验） / Passage ID (search/show checks existence): " + explanation["direct_id"])
                for item in explanation["mappings"]:
                    print("{} -> {} ({})".format(item["input"], "、".join(item["keywords"]), item["concept"]))
                print("检索词 / Retrieval keywords: " + "、".join(explanation["retrieval_terms"]))
                print("忽略的功能词 / Ignored function words: " + ", ".join(explanation["ignored_terms"]))
                print("未识别 / Unrecognized: " + ", ".join(explanation["unrecognized_terms"]))
                print("否定或回避词 / Negation or avoidance: " + ", ".join(explanation["negation_terms"]))
                print_query_hints(explanation)
                for notice in explanation["warnings"] + explanation["limitations"]:
                    print(notice)
            return 0
        catalog = load_catalog(args.root)
        if args.command == "list":
            print(json.dumps(catalog, ensure_ascii=False, indent=2))
            return 0
        report, books = validate_catalog(args.root, getattr(args, "book", None))
        if args.command in ("validate", "build"):
            if args.command == "build" and report["valid"]:
                for corpus in books:
                    # Keep all existing Sunzi exports exactly as established.
                    if corpus["entry"].get("adapter") != "sunzi":
                        render_book(corpus)
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return 0 if report["valid"] else 1
        selected_entries(catalog, getattr(args, "book", None))
        if not report["valid"]:
            raise ValueError("已登记典籍校验失败：" + json.dumps(report, ensure_ascii=False))
        if args.command == "show":
            rows = [result_record(b["by_id"][args.passage_id.upper()], b, 1.0) for b in books if args.passage_id.upper() in b["by_id"]]
            if not rows:
                print("未找到已完成典籍段落：" + args.passage_id, file=sys.stderr)
                return 2
            print(json.dumps(rows[0], ensure_ascii=False, indent=2))
            return 0
        rows = search(args.query, books, args.limit)
        explanation = (checked_query_explanation(args.query, books)
                       if re.search(r"[A-Za-z]", args.query)
                       and not any(args.query.strip().upper() in b["by_id"] for b in books) else None)
        if not args.json and explanation:
            print("有限英文关键词映射 / Finite English keyword mapping: " + "、".join(explanation["retrieval_terms"]))
            if explanation["unrecognized_terms"]:
                print("未识别 / Unrecognized: " + ", ".join(explanation["unrecognized_terms"]))
            if explanation["negation_terms"]:
                print("否定或回避词 / Negation or avoidance: " + ", ".join(explanation["negation_terms"]))
            print_query_hints(explanation)
            for notice in explanation["warnings"]:
                print(notice)
            print("候选须回看中文原文；映射详情 / Check Chinese source; inspect mapping: explain-query QUERY --json")
        if args.json:
            print(json.dumps(rows, ensure_ascii=False, indent=2))
            # Keep the JSON result a compatible list while making an empty
            # unknown-ID lookup distinguishable from a silent successful hit.
            if not rows and explanation and explanation.get("unresolved_passage_ids"):
                print("当前检索范围未找到段号 / IDs not found in selected corpus: "
                      + ", ".join(explanation["unresolved_passage_ids"]), file=sys.stderr)
        elif not rows:
            print("没有找到相关关键词；可换词或查阅原文目录。这不证明原典没有该思想。")
            if re.search(r"[A-Za-z]", args.query):
                print("No matching keywords; try another term or the source index.")
        else:
            for row in rows:
                label = ("显式段号直达 / Explicit passage reference" if row.get("match_type") == "explicit_reference"
                         else "关键词匹配分 {}".format(row["score"]))
                print("{} · {} · {} · {}".format(row["book_title"], row["id"], row["chapter_title"], label))
                if row.get("book_hint_boost"):
                    print("书名阅读提示排序加权 / Book-hint ranking multiplier: " + str(row["book_hint_boost"]))
                locator = " · ".join(str(row[key]) for key in ("part", "source_section") if row.get(key))
                if locator:
                    print("篇组或源章句标记：" + locator)
                print("原文：" + row["text"] + "\nAI 释义提要：" + row["explanation"])
                if row["caution"]:
                    print("读法与边界：" + row["caution"])
                print("来源：" + row["source_url"] + "\n")
        return 0
    except (OSError, ValueError, KeyError, TypeError, IndexError) as error:
        print("知识库读取或校验失败：" + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
