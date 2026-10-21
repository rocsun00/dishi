"""Field-aware lexical ranking for the offline reader, without book priors.

Scores describe query overlap, not historical authority or answer confidence.
Original text and its simplified search copy are alternative representations of
one field. Editorial labels, explanations and cautions have smaller weights.
"""

from __future__ import annotations

from collections import Counter, defaultdict, deque
import hashlib
import math
import re

CHINESE = re.compile(r"[\u3400-\u9fff]+\Z")
CONTENT = re.compile(r"[\u3400-\u9fffA-Za-z0-9]")
# Field weights express the strength of lexical evidence, never book identity.
WEIGHTS = {"source": 4.0, "heading": 1.2, "labels": 1.2,
           "reading": 0.8, "commentary": 0.35, "caution": 0.08,
           "book_title": 0.5}
BOOK_HINT_BOOST = 1.1


def unique(values):
    return list(dict.fromkeys(value for value in values if value))


def join_text(values):
    """Repeated copies of an editorial sentence do not create new evidence."""
    return " ".join(unique(str(value).lower() for value in values if value))


def query_groups(words, explanation=None):
    """Keep synonyms in one evidence group; repeated input has no extra vote."""
    if explanation is None:
        candidates = [[word] for word in words]
    else:
        candidates = [[word] for word in explanation["chinese_terms"]]
        candidates += [item["keywords"] for item in explanation["mappings"]]
    groups, seen = [], set()
    for candidate in candidates:
        group = unique(word.strip().lower() for word in candidate)
        key = tuple(sorted(group))
        if group and key not in seen:
            groups.append(group)
            seen.add(key)
    return groups


def features(word):
    # Bigrams retain partial recall for unsegmented Chinese questions. Full
    # phrases receive additional evidence below, so scattered grams are weaker.
    if len(word) > 2 and CHINESE.fullmatch(word):
        return unique(word[index:index + 2] for index in range(len(word) - 1))
    return [word]


def documents(books, include_titles):
    records = []
    for book in books:
        cards_by_passage = defaultdict(list)
        for card in book["concepts"]:
            for pid in set(card["passage_ids"]):
                cards_by_passage[pid].append(card)
        for passage in book["passages"]:
            pid = passage["id"]
            reading = book["readings"][pid]
            cards = cards_by_passage[pid]
            fields = {
                "source": tuple(unique([passage["text"].lower(), book["search_text"][pid].lower()])),
                "heading": (passage["chapter_title"].lower(),),
                "labels": (join_text(value for card in cards
                                     for value in [card.get("title", "")] + card.get("tags", [])),),
                "reading": (join_text([reading["explanation"]]
                                       + list(reading.get("terms", {}).keys())
                                       + list(reading.get("terms", {}).values())),),
                "commentary": (join_text(value for card in cards for key in
                                         ("source_context", "interpretation", "modern_application", "conditions")
                                         for value in (card.get(key, []) if key == "conditions"
                                                       else [card.get(key, "")])),),
                "caution": (join_text([reading.get("caution", "")]
                                       + [card.get(key, "") for card in cards
                                          for key in ("misreading", "boundary")]),),
                "book_title": (book["entry"]["title"].lower() if include_titles else "",),
            }
            lengths = {name: max(1, max(len(CONTENT.findall(text)) for text in texts))
                       for name, texts in fields.items()}
            # Stable under passage-ID renaming and changes in catalog order.
            fingerprint = hashlib.sha256("\n".join(text for texts in fields.values()
                                                  for text in texts).encode("utf-8")).hexdigest()
            records.append({"book": book, "passage": passage, "fields": fields,
                            "lengths": lengths, "fingerprint": fingerprint})
    return records


def rank(books, groups, include_titles=False, recommended_books=()):
    """Return (book, passage, raw_score) with saturated, length-aware evidence.

    Each query group contributes its best alternative, rather than rewarding
    English mappings with many synonyms. BM25 term frequency saturates; source
    and annotation fields use their own average lengths. Exact-score ties are
    interleaved by source, then content hash, without disturbing stronger hits.
    Explicit adapter book hints add a small disclosed boost, not a filter.
    """
    if not groups:
        return []
    recommended_books = set(recommended_books)
    records = documents(books, include_titles)
    if not records:
        return []
    grams = unique(gram for group in groups for word in group for gram in features(word))
    terms = unique(grams + [word for group in groups for word in group if len(features(word)) > 1])
    averages = {name: sum(record["lengths"][name] for record in records) / len(records)
                for name in WEIGHTS}
    frequencies = Counter()
    for record in records:
        counts = {term: {name: max(text.count(term) for text in texts)
                         for name, texts in record["fields"].items()} for term in terms}
        record["counts"] = counts
        frequencies.update(term for term in terms if any(counts[term].values()))
    idfs = {term: math.log(1 + (len(records) - frequencies[term] + 0.5)
                           / (frequencies[term] + 0.5)) for term in terms}

    def evidence(record, term):
        score = 0.0
        for name, weight in WEIGHTS.items():
            frequency = record["counts"][term][name]
            if not frequency:
                continue
            # A bounded tf also prevents repeated boilerplate from winning by
            # volume. The continuous BM25 factor still distinguishes focus.
            frequency = min(frequency, 8)
            norm = 0.3 + 0.7 * record["lengths"][name] / averages[name]
            score += weight * frequency * 2.2 / (frequency + 1.2 * norm)
        return idfs[term] * score

    ranked = []
    for record in records:
        scores = {}
        for group in groups:
            alternatives = []
            for word in group:
                word_grams = features(word)
                base = sum(evidence(record, gram) for gram in word_grams) / len(word_grams)
                if len(word_grams) > 1:
                    base += 0.75 * evidence(record, word)
                alternatives.append(base)
            scores[tuple(group)] = max(alternatives)
        covered = sum(score > 0 for score in scores.values())
        if covered:
            # Multi-topic queries favor passages covering the requested topics;
            # a large number of weak matches in one group cannot cover another.
            score = sum(scores.values()) * (0.5 + 0.5 * covered / len(groups))
            if record["book"]["entry"]["id"] in recommended_books:
                score *= BOOK_HINT_BOOST
            ranked.append((score, record))
    ranked.sort(key=lambda item: (-item[0], item[1]["fingerprint"], item[1]["passage"]["id"]))

    diversified = []
    start = 0
    while start < len(ranked):
        end = start + 1
        while end < len(ranked) and ranked[end][0] == ranked[start][0]:
            end += 1
        buckets = defaultdict(deque)
        for score, record in ranked[start:end]:
            buckets[record["book"]["entry"]["id"]].append((score, record))
        # The best content hash chooses the first source, not its alphabetic ID.
        sources = sorted(buckets, key=lambda source: buckets[source][0][1]["fingerprint"])
        while sources:
            for source in sources:
                diversified.append(buckets[source].popleft())
            sources = [source for source in sources if buckets[source]]
        start = end
    return [(record["book"], record["passage"], score) for score, record in diversified]
