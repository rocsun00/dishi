"""Check adviser instructions, navigable docs, and exact source quotations."""

import importlib.util
import json
from pathlib import Path
import re
import unittest
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parent.parent
PORTABLE_PROMPTS = (
    "docs/portable-prompt.zh-CN.md",
    "docs/portable-prompt.en.md",
)
# A project compatibility budget, not a promise about any host's field limit.
PORTABLE_PROMPT_CHAR_BUDGET = 7500
RESEARCH_REFERENCES = (
    "references/research-method.md",
    "references/research-examples.zh-CN.md",
    "references/research-examples.en.md",
)
EXAMPLE_DOCUMENTS = (
    "docs/examples.zh-CN.md", "docs/examples.en.md",
    "references/research-examples.zh-CN.md", "references/research-examples.en.md",
)
RULES = ("忠于所托", "谋事不害人", "言必有据", "策不代断", "知所不知")
PASSAGE_ID = re.compile(r"\b[A-Z][A-Z0-9]*(?:-\d+){2,}\b")
CHINESE = re.compile(r"[\u3400-\u9fff]")


def parse_frontmatter(document):
    """Parse this project's string-only YAML subset without a runtime dependency.

    Plain strings, JSON-compatible double quotes, and YAML single quotes are
    supported. Unsupported YAML structures fail explicitly; the official skill
    validator remains an additional maintainer check for full YAML syntax.
    """
    lines = document.splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("Missing opening frontmatter delimiter")
    try:
        end = lines.index("---", 1)
    except ValueError as error:
        raise ValueError("Missing closing frontmatter delimiter") from error
    fields = {}
    for line in lines[1:end]:
        if not line.strip() or line.startswith("#"):
            continue
        match = re.fullmatch(r"([a-z][a-z_]*):\s+(.+)", line)
        if not match:
            raise ValueError("Only top-level string fields are supported")
        name, raw = match.groups()
        if name in fields:
            raise ValueError("Duplicate frontmatter field: " + name)
        if raw.startswith('"'):
            value = json.loads(raw)
            if not isinstance(value, str):
                raise ValueError("Frontmatter value must be a string")
        elif raw.startswith("'"):
            if not re.fullmatch(r"'(?:[^']|'')*'", raw):
                raise ValueError("Invalid single-quoted frontmatter string")
            value = raw[1:-1].replace("''", "'")
        else:
            if (raw.startswith(("|", ">", "[", "{", "!", "&", "*", "#"))
                    or ": " in raw or " #" in raw
                    or raw.lower() in {"true", "false", "null", "~"}
                    or re.fullmatch(r"[-+]?\d+(?:\.\d+)?", raw)):
                raise ValueError("Unsupported or non-string YAML value")
            value = raw
        fields[name] = value
    return fields


def prose_without_code(document, remove_inline=True):
    """Remove fenced/indented code and inline code before finding real links."""
    result = []
    fence = None
    for line in document.splitlines():
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence is not None:
            if (marker and marker.group(1)[0] == fence[0]
                    and len(marker.group(1)) >= len(fence)
                    and not marker.group(2).strip()):
                fence = None
            continue
        if marker:
            fence = marker.group(1)
            continue
        if line.startswith(("    ", "\t")):
            continue
        result.append(re.sub(r"(`+)(.+?)\1", "", line) if remove_inline else line)
    return re.sub(r"<!--.*?-->", "", "\n".join(result), flags=re.DOTALL)


def markdown_targets(document):
    """Read inline/image destinations, including escaped or nested parentheses."""
    prose = prose_without_code(document)
    position = 0
    while True:
        start = prose.find("](", position)
        if start < 0:
            break
        cursor = start + 2
        while cursor < len(prose) and prose[cursor].isspace():
            cursor += 1
        angled = cursor < len(prose) and prose[cursor] == "<"
        if angled:
            cursor += 1
        target, depth = [], 0
        while cursor < len(prose):
            character = prose[cursor]
            if character == "\\" and cursor + 1 < len(prose):
                target.append(prose[cursor + 1])
                cursor += 2
                continue
            if angled and character == ">":
                break
            if not angled:
                if character.isspace() or (character == ")" and depth == 0):
                    break
                if character == "(":
                    depth += 1
                elif character == ")":
                    depth -= 1
            target.append(character)
            cursor += 1
        if target:
            yield "".join(target)
        position = cursor + 1
    # Reference-style link definitions also name destinations even if the
    # visible reference uses a shortcut or collapsed label.
    for match in re.finditer(r"^ {0,3}\[[^\]]+\]:\s*(<[^>]+>|\S+)", prose, re.MULTILINE):
        yield match.group(1).strip("<>")


def bold_source_quotes(document):
    """Yield quoted Chinese bold text and IDs in its source row/paragraph."""
    for paragraph in prose_without_code(document, remove_inline=False).split("\n\n"):
        rows = paragraph.splitlines() if paragraph.lstrip().startswith("|") else [paragraph]
        for row in rows:
            for match in re.finditer(r"\*\*(.+?)\*\*", row, re.DOTALL):
                value = match.group(1).strip()
                if (len(value) > 2 and CHINESE.search(value)
                        and (value[0], value[-1]) in {("“", "”"), ("「", "」"), ("『", "』")}):
                    yield value[1:-1], PASSAGE_ID.findall(row)


class AdvisorContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.passages = {}
        for path in sorted(ROOT.glob("knowledge/*/data/passages.jsonl")):
            for line in path.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                passage = json.loads(line)
                if passage["id"] in cls.passages:
                    raise ValueError("Duplicate corpus passage ID: " + passage["id"])
                cls.passages[passage["id"]] = passage["text"]
        if not cls.passages:
            raise ValueError("No source passages loaded")

    def test_skill_frontmatter_contract(self):
        fields = parse_frontmatter((ROOT / "SKILL.md").read_text(encoding="utf-8"))
        self.assertEqual(fields.get("name"), "dishi")
        description = fields.get("description", "")
        self.assertTrue(description.strip())
        self.assertLessEqual(len(description), 1024)

    def test_frontmatter_parser_rejects_ambiguous_or_nonstring_fields(self):
        for document in (
            "name: dishi",
            "---\nname: dishi\n",
            "---\nname: dishi\nname: other\n---",
            "---\nname: [dishi]\n---",
            "---\nname: true\n---",
            "---\nname: dishi # ignored?\n---",
        ):
            with self.subTest(document=document), self.assertRaises(ValueError):
                parse_frontmatter(document)
        parsed = parse_frontmatter("---\nname: dishi\ndescription: 'It''s clear.'\n---")
        self.assertEqual(parsed["description"], "It's clear.")

    def test_local_document_links_exist(self):
        documents = [ROOT / name for name in ("SKILL.md", "README.md", "README.en.md")]
        documents.extend(sorted((ROOT / "docs").rglob("*.md")))
        documents.extend(sorted((ROOT / "references").rglob("*.md")))
        checked = 0
        missing = []
        for document in documents:
            for target in markdown_targets(document.read_text(encoding="utf-8")):
                parsed = urlsplit(target)
                if parsed.scheme or parsed.netloc or not parsed.path or target.startswith("/"):
                    continue
                checked += 1
                linked = document.parent / unquote(parsed.path)
                if not linked.exists():
                    missing.append(document.relative_to(ROOT).as_posix() + " -> " + target)
        self.assertGreater(checked, 0)
        self.assertEqual(missing, [], "Broken local links:\n" + "\n".join(missing))

    def test_markdown_target_reader_skips_code_and_keeps_real_links(self):
        document = (
            "[real](docs/a.md#part) ![picture](<image name.png>)\n"
            "[nested](file_(draft).md) [escaped](file\\(draft\\).md)\n"
            "`[inline](missing.md)`\n```md\n[code](missing.md)\n```\n"
            "~~~text\n[more code](missing.md)\n~~~\n"
            "    [indented](missing.md)\n<!-- [comment](missing.md) -->\n"
            "[reference]: relative.md\n[external](https://example.com/a)\n"
        )
        self.assertEqual(list(markdown_targets(document)), [
            "docs/a.md#part", "image name.png", "file_(draft).md", "file(draft).md",
            "https://example.com/a", "relative.md",
        ])

    def test_all_example_passage_ids_exist(self):
        for filename in EXAMPLE_DOCUMENTS:
            document = (ROOT / filename).read_text(encoding="utf-8")
            identifiers = set(PASSAGE_ID.findall(document))
            self.assertTrue(identifiers, filename + " has no source IDs")
            self.assertEqual(sorted(identifiers.difference(self.passages)), [], filename)

    def test_bold_example_quotes_match_their_local_passage(self):
        for filename in EXAMPLE_DOCUMENTS:
            quotes = list(bold_source_quotes((ROOT / filename).read_text(encoding="utf-8")))
            self.assertTrue(quotes, filename + " has no bold Chinese source quotations")
            for quotation, identifiers in quotes:
                with self.subTest(file=filename, quotation=quotation):
                    self.assertTrue(identifiers, "Quote needs a passage ID in the same source row/paragraph")
                    self.assertTrue(any(quotation in self.passages.get(identifier, "")
                                        for identifier in identifiers),
                                    "Quote does not occur exactly in its cited passage: " + ", ".join(identifiers))

    def test_five_adviser_rules_exist_in_skill_and_both_portable_prompts(self):
        for filename in ("SKILL.md",) + PORTABLE_PROMPTS:
            document = (ROOT / filename).read_text(encoding="utf-8")
            for rule in RULES:
                with self.subTest(file=filename, rule=rule):
                    self.assertIn(rule, document)

    def test_portable_prompts_fit_project_character_budget(self):
        for filename in PORTABLE_PROMPTS:
            document = (ROOT / filename).read_text(encoding="utf-8")
            with self.subTest(file=filename):
                fences = re.findall(r"^ {0,3}(?:`{3,}|~{3,}).*$", document,
                                    flags=re.MULTILINE)
                self.assertEqual(len(fences), 2, "Expected only one fenced prompt block")
                blocks = re.findall(r"^~~~text\n(.*?)\n~~~[ \t]*$", document,
                                    flags=re.MULTILINE | re.DOTALL)
                self.assertEqual(len(blocks), 1, "Expected one complete copyable prompt")
                prompt = blocks[0]
                self.assertTrue(prompt.strip())
                self.assertLessEqual(len(prompt), PORTABLE_PROMPT_CHAR_BUDGET,
                                     "Copyable prompt exceeds the project's character budget")

    def test_portable_prompts_are_required_runtime_files(self):
        spec = importlib.util.spec_from_file_location("advisor_package_rules", ROOT / "scripts/package_rules.py")
        rules = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(rules)
        for filename in PORTABLE_PROMPTS:
            with self.subTest(file=filename):
                self.assertTrue((ROOT / filename).is_file())
                self.assertIn(filename, rules.RUNTIME_DOCS)
                self.assertIn(filename, rules.REQUIRED)
                self.assertTrue(rules.runtime_includes(filename))

    def test_research_references_are_required_runtime_files(self):
        spec = importlib.util.spec_from_file_location("research_package_rules", ROOT / "scripts/package_rules.py")
        rules = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(rules)
        for filename in RESEARCH_REFERENCES:
            with self.subTest(file=filename):
                self.assertTrue((ROOT / filename).is_file())
                self.assertIn(filename, rules.REQUIRED)
                self.assertTrue(rules.runtime_includes(filename))

    def test_runtime_content_has_no_retired_mottos(self):
        spec = importlib.util.spec_from_file_location("advisor_package_rules", ROOT / "scripts/package_rules.py")
        rules = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(rules)
        retired = ("以实求真", "以事择术", "以果验言", "按用户事实和共同原则")
        checked = 0
        violations = []
        for path, relative in rules.inventory(ROOT):
            if path.suffix not in {".md", ".json", ".html"} or rules.process_exclusion(relative):
                continue
            # In addition to installed files, cover book-facing source inputs.
            # Archived process records and non-installed upstream evidence are
            # outside this check; do not rewrite evidence to satisfy a motto.
            book_input = (relative.startswith("knowledge/")
                          and "source" not in relative.split("/"))
            if not (rules.runtime_includes(relative) or book_input):
                continue
            checked += 1
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                for phrase in retired:
                    if phrase in line:
                        violations.append("{}:{}: {}".format(relative, number, phrase))
        self.assertGreater(checked, 0)
        self.assertEqual(violations, [], "Retired mottos in runtime content:\n" + "\n".join(violations))

    def test_case_two_has_conditional_reranking_in_both_languages(self):
        expectations = (
            ("docs/examples.zh-CN.md", "**条件变化时怎样重排**", "首选", "**逆言**",
             "退出条件", "中策"),
            ("docs/examples.en.md", "**When conditions change, the ranking changes**",
             "first choice", "**Candid objection**", "exit conditions", "option B"),
        )
        for filename, heading, first_choice, objection, exit_conditions, deferred_option in expectations:
            document = (ROOT / filename).read_text(encoding="utf-8")
            with self.subTest(file=filename):
                self.assertIn('<a id="case-2"></a>', document)
                self.assertIn('<a id="case-3"></a>', document)
                case = document.split('<a id="case-2"></a>', 1)[1].split('<a id="case-3"></a>', 1)[0]
                self.assertEqual(case.count(heading), 1)
                reranking = case.split(heading, 1)[1].split(objection, 1)[0]
                self.assertIn(first_choice, reranking)
                scenarios = [line for line in reranking.splitlines() if line.startswith("- **")]
                self.assertEqual(len(scenarios), 3)
                self.assertIn(exit_conditions, scenarios[0])
                self.assertIn(deferred_option, scenarios[2])


if __name__ == "__main__":
    unittest.main()
