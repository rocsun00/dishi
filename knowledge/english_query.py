"""Finite, auditable English-to-Chinese query keywords; no translation or network.

Aliases are hand curated in english_keywords.json. Matching is case insensitive,
uses whole English tokens, and prefers longer phrases over overlapping aliases.
The output is a retrieval aid, not an interpretation of the user's question.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
ENGLISH_TOKEN = re.compile(r"[A-Za-z][A-Za-z0-9_]*(?:['’][A-Za-z]+)?")
CHINESE_TOKEN = re.compile(r"[\u3400-\u9fff]+")
PASSAGE_ID = re.compile(r"[A-Za-z][A-Za-z0-9_]*-\d+-\d+\Z")
PASSAGE_ID_IN_QUERY = re.compile(r"(?<![A-Za-z0-9_-])[A-Za-z][A-Za-z0-9_]*-\d+-\d+(?![A-Za-z0-9_-])")
LIMITATIONS = [
    "有限人工词法映射 / Finite curated keyword mapping; not sentence translation or semantic search.",
    "结果仅为阅读候选，须回看中文原文和语境 / Read the Chinese source and context before drawing conclusions.",
    "书名与学派仅提示候选典籍；用 --book 明确限定典籍 / Book and school names suggest reading candidates; only --book restricts the corpus.",
    "现代生活主题仅作阅读线索，不表示古今处境相同 / Modern-life topics are reading prompts, not claims of historical equivalence.",
]
NEGATION_WARNING = (
    "检测到否定或回避词：已保守停用全部英文映射及段号直达，不推断否定范围；"
    "请保留原意，用准确中文重述后检索。中文原词仍可参与检索，候选不解释否定逻辑 / "
    "Negation or avoidance detected: all English mappings and passage-ID lookup are suppressed; "
    "scope is not inferred. Restate the intended relation in precise Chinese. "
    "Existing Chinese terms may still retrieve candidates, which do not interpret negation."
)


def unique(values):
    return list(dict.fromkeys(values))


@lru_cache(maxsize=1)
def vocabulary():
    """Load the bundled, reviewable vocabulary once; never fetch expansions."""
    data = json.loads((ROOT / "english_keywords.json").read_text(encoding="utf-8"))
    if data.get("schema_version") != 1:
        raise ValueError("英文关键词表版本无效 / Invalid English vocabulary version")
    entries, aliases = [], set()
    book_ids = {entry["id"] for entry in data["entries"] if entry["kind"] == "book"}
    for entry in data["entries"]:
        if entry["kind"] not in ("concept", "book") or not entry["keywords"]:
            raise ValueError("英文关键词条格式无效 / Invalid English keyword entry")
        if any(not CHINESE_TOKEN.fullmatch(word) for word in entry["keywords"]):
            raise ValueError("映射目标须为中文关键词 / Mapped keywords must be Chinese")
        if any(book_id not in book_ids for book_id in entry.get("recommended_books", [])):
            raise ValueError("推荐典籍须为词表中已登记典籍 / Recommended books must be registered in the vocabulary")
        for alias in entry["aliases"]:
            normalized = re.sub(r"[ -]+", " ", alias.lower()).strip()
            if not normalized or normalized in aliases or not re.fullmatch(r"[a-z]+(?: [a-z]+)*", normalized):
                raise ValueError("英文别名无效或重复 / Invalid or duplicate English alias: " + alias)
            aliases.add(normalized)
            phrase = r"[ -]+".join(re.escape(part) for part in normalized.split())
            pattern = re.compile(r"(?<![A-Za-z0-9_])" + phrase + r"(?![A-Za-z0-9_])", re.IGNORECASE)
            entries.append((pattern, normalized, entry))
    return data, entries


def explain_query(query):
    """Return exact input, mapped keywords, and all unmatched English tokens.

    Function words never become search terms. On detecting English negation,
    suppress all English mappings rather than guess its scope or retrieve the
    affirmative concept. Chinese terms remain literal, with an explicit warning.
    """
    data, entries = vocabulary()
    chinese = CHINESE_TOKEN.findall(query)
    has_english = bool(ENGLISH_TOKEN.search(query))
    direct_id = query.strip().upper() if PASSAGE_ID.fullmatch(query.strip()) else None
    id_matches = list(PASSAGE_ID_IN_QUERY.finditer(query))
    passage_ids = unique(match.group().upper() for match in id_matches)
    explanation = {
        "schema_version": 1, "query": query,
        "mode": "passage_id" if direct_id else "mixed_keyword_mapping" if has_english and chinese
        else "english_keyword_mapping" if has_english else "chinese_keywords",
        "has_english": has_english, "direct_id": direct_id, "passage_ids": passage_ids,
        "vocabulary_version": data["version"], "mappings": [],
        "chinese_terms": chinese, "mapped_keywords": [], "retrieval_terms": [],
        "ignored_terms": [], "unrecognized_terms": [], "negation_terms": [],
        "recommended_books": [], "suppressed_mappings": [], "suppressed_passage_ids": [],
        "warnings": [], "limitations": list(LIMITATIONS),
    }
    if direct_id:
        return explanation
    tokens = list(ENGLISH_TOKEN.finditer(query))
    id_spans = [(match.start(), match.end()) for match in id_matches]
    tokens = [token for token in tokens if not any(start <= token.start() and token.end() <= end for start, end in id_spans)]
    token_starts, token_ends = {token.start() for token in tokens}, {token.end() for token in tokens}
    candidates = []
    for pattern, normalized, entry in entries:
        for match in pattern.finditer(query):
            if match.start() not in token_starts or match.end() not in token_ends:
                continue
            candidates.append((match.start(), -len(normalized.split()), -len(match.group()), match.end(), normalized, entry))
    occupied_until = -1
    for start, _, _, end, normalized, entry in sorted(candidates, key=lambda row: row[:3]):
        if start < occupied_until:
            continue
        explanation["mappings"].append({
            "input": query[start:end], "start": start, "end": end,
            "alias": normalized, "concept": entry["id"], "kind": entry["kind"],
            "keywords": list(entry["keywords"]),
            "recommended_books": [entry["id"]] if entry["kind"] == "book" else list(entry.get("recommended_books", [])),
        })
        occupied_until = end
    spans = [(item["start"], item["end"]) for item in explanation["mappings"]]
    ignored, negations = set(data["function_words"]), set(data["negation_words"])
    for token in tokens:
        original = token.group()
        normalized = original.lower().replace("’", "'")
        if normalized in negations:
            explanation["negation_terms"].append(original)
        elif any(start <= token.start() and token.end() <= end for start, end in spans):
            continue
        elif normalized in ignored:
            explanation["ignored_terms"].append(original)
        else:
            explanation["unrecognized_terms"].append(original)
    if explanation["negation_terms"]:
        explanation["suppressed_mappings"] = explanation["mappings"]
        explanation["mappings"] = []
        explanation["suppressed_passage_ids"] = explanation["passage_ids"]
        explanation["passage_ids"] = []
        explanation["warnings"].append(NEGATION_WARNING)
    explanation["mapped_keywords"] = unique(word for item in explanation["mappings"] for word in item["keywords"])
    explanation["retrieval_terms"] = unique(chinese + explanation["mapped_keywords"])
    explanation["recommended_books"] = unique(book_id for item in explanation["mappings"] for book_id in item["recommended_books"])
    if explanation["unrecognized_terms"]:
        explanation["warnings"].append(
            "未识别英文未参与检索 / Unrecognized English tokens were not used for retrieval."
        )
    return explanation
