"""Deterministic markup processing for the pinned public working texts.

Ancient notes remain in raw snapshots; they are never merged into primary text.
Only the explicitly supported markup is accepted.
"""
from __future__ import annotations

import re


def _without_references(text: str):
    notes = []
    def remove(match):
        markup = match.group(0)
        notes.append({"kind": "source_reference_excluded", "markup": markup})
        return ""
    text = re.sub(r"<ref\b[^>]*/\s*>", remove, text, flags=re.I)
    text = re.sub(r"<ref\b[^>]*>.*?</ref\s*>", remove, text, flags=re.S | re.I)
    return text, notes


def _templates(text: str):
    index = 0
    while index < len(text):
        start = text.find("{{", index)
        if start < 0:
            yield text[index:], None
            return
        yield text[index:start], None
        depth, end = 1, start + 2
        while depth and end < len(text):
            if text.startswith("{{", end):
                depth += 1
                end += 2
            elif text.startswith("}}", end):
                depth -= 1
                end += 2
            else:
                end += 1
        if depth:
            raise ValueError("Unclosed template in selected source text")
        yield text[start + 2:end - 2], "template"
        index = end


def _split_variant(value: str):
    """Split template arguments without treating a link's display pipe as a separator."""
    braces, links, index = 0, 0, 0
    while index < len(value):
        token = value[index:index + 2]
        if token == "{{":
            braces += 1
            index += 2
        elif token == "}}":
            braces -= 1
            index += 2
        elif token == "[[":
            links += 1
            index += 2
        elif token == "]]":
            links -= 1
            index += 2
        elif value[index] == "|" and not braces and not links:
            return value[:index], value[index + 1:]
        else:
            index += 1
    raise ValueError("Incomplete alternate reading template")


def _language_text(match):
    value = match.group(1)
    if ":" not in value:
        return value
    variants = {}
    for item in value.split(";"):
        if not item.strip():
            continue
        language, separator, text = item.partition(":")
        if not separator or language.strip() not in ("zh", "zh-hant", "zh-hans"):
            raise ValueError("Unsupported language-conversion markup")
        variants[language.strip()] = text
    for language in ("zh", "zh-hant", "zh-hans"):
        if language in variants:
            return variants[language]
    raise ValueError("Empty language-conversion markup")


def _pinned_glyph(name: str, value: str):
    """Decode only pinned source glyphs; retain unresolved Siku indices explicitly."""
    encoded = {"𩤝|馬敄": ("𩤝", "馬敄"), "𱯇|⿰王叕": ("𱯇", "⿰王叕")}
    descriptions = {"⿰耒殳", "⿷匚晏", "⿰扌⿱攵音", "⿰米⿱㒵夊", "⿱𥫗𠕀"}
    if name == "!" and value in encoded:
        primary, description = encoded[value]
        return primary, {"kind": "source_glyph_encoded", "primary": primary,
                         "description": description}
    if name == "？" and value in descriptions:
        display = "〔字形:" + value + "〕"
        return display, {"kind": "source_glyph_unencoded", "description": value,
                         "display": display}
    if name == "SKchar" and value in {"3951", "1841", "195", "2982"}:
        display = "〔四库字形:" + value + "〕"
        return display, {"kind": "source_glyph_unencoded", "description": "SKchar:" + value,
                         "display": display}
    raise ValueError("Unsupported glyph template or arguments: " + name)


def _pinned_era_link(value: str):
    """Keep the displayed era in the four year links selected from SGZ volume 35."""
    values = {"建安十六年": ("建安十六年", None),
              "章武三年": ("章武三年", None),
              "建興元年|223年": ("建興元年", "223年"),
              "景耀六年": ("景耀六年", None)}
    if value not in values:
        raise ValueError("Unsupported year-link arguments")
    display, supplied_year = values[value]
    return display, {"kind": "source_era_link", "display": display,
                     "year_argument": supplied_year}


def _pinned_formatting(text: str):
    """Remove only two observed broken formatting fragments, keeping every character."""
    repairs = {
        "皆聖人所能為，</u>堯</u>、<u>舜</u>何不盡為之": "皆聖人所能為，堯、舜何不盡為之",
        "<<u>有苗</u>": "有苗",
    }
    notes = []
    for markup, display in repairs.items():
        for _ in range(text.count(markup)):
            notes.append({"kind": "source_formatting_anomaly", "markup": markup,
                          "display": display})
        text = text.replace(markup, display)
    return text, notes


def _without_underlining(text: str):
    """Strip paired, attribute-free name underlining; reject unbalanced/nested tags."""
    opened = False
    for match in re.finditer(r"</?u>", text):
        opening = match.group() == "<u>"
        if opening == opened:
            raise ValueError("Unbalanced or nested underline markup in primary text")
        opened = opening
    if opened:
        raise ValueError("Unbalanced underline markup in primary text")
    return re.sub(r"</?u>", "", text)


def extract_notes(text: str) -> list[dict]:
    text, notes = _without_references(text)
    # Record only repairs made to primary text; keep excluded note fields raw.
    formatting_notes = []
    _normalize_markup(text, formatting_notes)
    notes.extend(formatting_notes)
    for part, kind in _templates(text):
        if kind != "template":
            continue
        name, _, value = part.partition("|")
        if name.strip() == "*":
            notes.append({"kind": "ancient_note_excluded", "text": value.strip()})
        elif name.strip() in ("另", "另2"):
            primary, alternative = _split_variant(value)
            if name.strip() == "另2":
                notes.append({"kind": "source_variant_note", "primary": primary,
                              "note": alternative})
            else:
                notes.append({"kind": "source_variant_template", "primary": primary,
                              "alternative": alternative})
        elif name.strip() in ("!", "？", "SKchar"):
            _, note = _pinned_glyph(name.strip(), value)
            notes.append(note)
        elif name.strip() == "YL":
            _, note = _pinned_era_link(value)
            notes.append(note)
        else:
            raise ValueError("Unsupported template in body: " + name)
    return notes


def _normalize_markup(text: str, formatting_notes: list[dict]) -> str:
    """Normalize primary text and collect only the formatting repairs it uses."""
    text, _ = _without_references(text)
    result = []
    for part, kind in _templates(text):
        if kind != "template":
            result.append(part)
            continue
        name, _, value = part.partition("|")
        if name.strip() == "*":
            continue
        if name.strip() in ("另", "另2"):
            primary, _ = _split_variant(value)
            result.append(_normalize_markup(primary, formatting_notes))
        elif name.strip() in ("!", "？", "SKchar"):
            primary, _ = _pinned_glyph(name.strip(), value)
            result.append(primary)
        elif name.strip() == "YL":
            primary, _ = _pinned_era_link(value)
            result.append(primary)
        else:
            raise ValueError("Unsupported template in body: " + name)
    body = "".join(result)
    body = re.sub(r"<ref\b[^>]*/\s*>", "", body, flags=re.I)
    body = re.sub(r"<ref\b[^>]*>.*?</ref\s*>", "", body, flags=re.S | re.I)
    body = re.sub(r"\[\[(?:[^\]|]+\|)?([^\]]+)\]\]", r"\1", body)
    body = re.sub(r"-\{([^{}]+)\}-", _language_text, body)
    body = re.sub(r"'''([^']*)'''", r"\1", body)
    if "'''" in body:
        raise ValueError("Unpaired wiki bold markup in primary text")
    body = re.sub(r"(?m)^:+\s*", "", body)
    body, repairs = _pinned_formatting(body)
    formatting_notes.extend(repairs)
    body = _without_underlining(body)
    # These exact glyph descriptions occur in the pinned Huainanzi/Zhanguoce texts.
    # Preserve uncertain source text while still rejecting HTML/unknown markup.
    markup_check = body.replace("<月曷>", "").replace("<上股下目>", "")
    if "<" in markup_check or ">" in markup_check:
        raise ValueError("Unsupported remaining markup in primary text")
    body = re.sub(r"\s+", "", body)
    if any(token in body for token in ("{{", "}}", "[[", "]]")):
        raise ValueError("Unsupported remaining markup in primary text")
    return body


def normalize_markup(text: str) -> str:
    """Return primary text after removing the explicitly supported markup."""
    return _normalize_markup(text, [])
