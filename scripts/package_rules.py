"""Auditable public/runtime policy. Original evidence is never rewritten."""

from fnmatch import fnmatchcase
import json
from pathlib import Path, PurePosixPath
import posixpath
import re
from urllib.parse import unquote, urlsplit

SUMMARY = "docs/provenance-summary.md"
SUMMARY_ANCHOR = SUMMARY + "#archived-records"
SKIP_DIRS = {".git", "__pycache__", "dist", ".pytest_cache", ".venv"}
# Same-depth matching deliberately preserves API/fetch manifests, source JSON,
# extraction/chapter maps, ancient notes, import checks, and quality documents.
PROCESS_EXCLUSIONS = (
    ("knowledge/验收覆盖-*.json", "Historical full workflow/tool transcripts"),
    ("knowledge/诸子百家覆盖与缺口.json", "Internal coverage-audit workflow record; Markdown overview retained"),
    ("knowledge/*/source/author_self_check.json", "Author workflow self-check; quality notes retained"),
    ("knowledge/*/source/author_source_selfcheck.json", "Author workflow self-check; source evidence retained"),
    ("knowledge/*/source/author_build_report.json", "Author build workflow report"),
    ("knowledge/*/source/draft_freeze.json", "Intermediate author draft freeze record"),
    ("knowledge/*/source/first_half_handoff.json", "Intermediate author handoff record"),
)
# Only this process note contains a local author-workspace path. Source/API text
# and author attributions never pass through this path redaction.
PROCESS_PATH_NOTES = {"knowledge/liezi/source/处理说明.md"}
LOCAL_PROCESS_PATH = re.compile(
    r"/(?:Users/[^/\s\"'<>，。；、]+|root|private/(?:tmp|var))"
    r"(?:/[^\s\"'<>，。；、)\]}]*)?"
)
MARKDOWN_LINK = re.compile(r"\]\((<?)([^\s<>)]*)(>?)\)")
# Require an actual child component: bare directory names and documented
# placeholders are not a concrete local workspace. The boundary avoids URLs.
PRIVATE_WORKSPACE_PATH = re.compile(
    r"(?<![A-Za-z0-9_.-])/(?:Users|root|private/(?:tmp|var))/"
    r"[^\s\"'<>`，。；、)\]{}]+"
)
ACTOR_WORD = re.compile(r"\b(?:root|agent)\b", re.IGNORECASE)
# These exact source fields describe historical acquisition/review roles.
# Their values are reported as allowed metadata only when they contain no
# concrete private directory. This never exempts an injected workspace path.
HISTORICAL_ACTOR_FIELDS = {
    "knowledge/liutao/source/fetch_manifest.json": {
        "$.fetched_by", "$.records[*].acquisition_mode", "$.pages[*].acquisition_mode",
    },
    "knowledge/liutao/source/source.json": {
        "$.source_pages[*].acquisition_mode", "$.reference_pages[*].acquisition_mode",
    },
    "knowledge/liweigongwendui/source/fetch_manifest.json": {"$.fetched_by"},
    "knowledge/sanlue/source/fetch_manifest.json": {"$.fetched_by"},
    "knowledge/simafa/source/fetch_manifest.json": {"$.records[9].acquisition", "$.notes[1]"},
    "knowledge/simafa/source/source.json": {"$.reference_pages[3].acquisition_mode"},
    "knowledge/weiliaozi/source/fetch_manifest.json": {"$.kind"},
    "knowledge/zhongyong/source/source.json": {"$.author_stage"},
    "knowledge/sanlue/source/semantic_review_references.json": {"$.references[*].obtained"},
    "knowledge/simafa/source/semantic_review_references.json": {"$.method"},
}
RUNTIME_ROOT_FILES = {"SKILL.md", "VERSION", "LICENSE", "LICENSE-CODE", "THIRD_PARTY_NOTICES.md",
                      "README.md", "README.en.md", "CONTRIBUTING.md"}
# Keep the small documentation set so README/navigation and license links resolve.
# docs/english-trial.json is a public summary, not the archived full tool logs.
RUNTIME_DOCS = {"docs/corpus.md", "docs/examples.zh-CN.md", "docs/examples.en.md", SUMMARY,
                "docs/portable-prompt.zh-CN.md", "docs/portable-prompt.en.md",
                "docs/installation.zh-CN.md", "docs/installation.en.md", "docs/github-release.md",
                "docs/validation.md", "docs/validation-results.json", "docs/english-trial.json",
                "docs/source-attribution.json"}
REQUIRED = (
    "SKILL.md", "VERSION", "agents/openai.yaml", "knowledge/kb.py",
    "knowledge/normalization.py", "knowledge/ranking.py", "knowledge/english_query.py",
    "knowledge/english_keywords.json", "knowledge/catalog.json", "knowledge/知识库总览.md",
    "references/guide.zh-CN.md", "references/lenses.md", "references/人物原典使用说明.md",
    "references/research-method.md", "references/research-examples.zh-CN.md",
    "references/research-examples.en.md",
    "docs/corpus.md", "docs/examples.zh-CN.md", "docs/examples.en.md", SUMMARY,
    "docs/portable-prompt.zh-CN.md", "docs/portable-prompt.en.md",
    "LICENSE", "LICENSE-CODE", "THIRD_PARTY_NOTICES.md",
)


def scan_public_text(relative, content):
    """Find concrete private directories in public JSON/Markdown, without edits.

    Original upstream evidence with such a path must be reviewed explicitly;
    callers must reject findings rather than silently rewrite the source.
    """
    findings, allowed = [], []
    if not relative.endswith((".json", ".md")):
        return {"findings": findings, "allowed": allowed}

    def inspect(value, location, is_key=False):
        matches = []
        for match in PRIVATE_WORKSPACE_PATH.finditer(value):
            path = match.group()
            # Generic shell/template components in documentation are not
            # concrete user workspaces; real literal directory names are.
            parts = path.strip("/").split("/")
            workspace_index = 2 if parts[0] == "private" else 1
            if parts[workspace_index].startswith(("$", "[")):
                continue
            matches.append(path)
        for path in matches:
            findings.append({"file": relative, "location": location,
                             "kind": "private_workspace_path", "path": path})
        fields = HISTORICAL_ACTOR_FIELDS.get(relative, set())
        normalized = re.sub(r"\[\d+\]", "[*]", location)
        if (not is_key and not matches and ACTOR_WORD.search(value)
                and (location in fields or normalized in fields)):
            allowed.append({"file": relative, "location": location,
                            "kind": "historical_source_role", "value": value})

    if relative.endswith(".json"):
        try:
            document = json.loads(content)
        except (ValueError, TypeError):
            findings.append({"file": relative, "location": "$", "kind": "invalid_json"})
            return {"findings": findings, "allowed": allowed}

        def visit(node, location="$"):
            if isinstance(node, dict):
                for key, value in node.items():
                    inspect(key, location + ".<key>", is_key=True)
                    visit(value, location + "." + key)
            elif isinstance(node, list):
                for index, value in enumerate(node):
                    visit(value, location + "[" + str(index) + "]")
            elif isinstance(node, str):
                inspect(node, location)

        visit(document)
    else:
        for number, line in enumerate(content.splitlines(), 1):
            inspect(line, "line " + str(number))
    return {"findings": findings, "allowed": allowed}


def check_public_text(relative, data):
    """Reject findings with a relative diagnostic; return allowed role metadata."""
    if not relative.endswith((".json", ".md")):
        return []
    result = scan_public_text(relative, data.decode("utf-8"))
    if result["findings"]:
        finding = result["findings"][0]
        raise ValueError("Public file needs manual review: " + relative + " at "
                         + finding["location"] + " (" + finding["kind"] + "). "
                         "Do not silently rewrite upstream source evidence.")
    return result["allowed"]


def process_exclusion(relative):
    parts = PurePosixPath(relative).parts
    for pattern, reason in PROCESS_EXCLUSIONS:
        if len(parts) == len(PurePosixPath(pattern).parts) and fnmatchcase(relative, pattern):
            return reason
    return None


def generated_exclusion(relative):
    path = PurePosixPath(relative)
    return (any(part in SKIP_DIRS for part in path.parts)
            or path.name == ".DS_Store" or path.suffix in {".pyc", ".zip"}
            or path.name in {".env", "RELEASE_MANIFEST.json"} or path.name.startswith(".env."))


def runtime_includes(relative):
    path = PurePosixPath(relative)
    if "tests" in path.parts or process_exclusion(relative) or generated_exclusion(relative):
        return False
    return (relative in RUNTIME_ROOT_FILES or relative in RUNTIME_DOCS
            or path.parts[0] in {"knowledge", "references", "agents"})


def inventory(root):
    root = Path(root)
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if generated_exclusion(relative):
            continue
        if path.is_symlink():
            raise ValueError("Symbolic link in package input: " + relative)
        if path.is_file():
            yield path, relative


def redirect_links(relative, content):
    parent = posixpath.dirname(relative)
    replacement = posixpath.relpath(SUMMARY, parent or ".") + "#archived-records"

    def redirect(match):
        target = match.group(2)
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc or target.startswith(("/", "#")):
            return match.group(0)
        linked = posixpath.normpath(posixpath.join(parent, unquote(parsed.path)))
        return "](" + replacement + ")" if process_exclusion(linked) else match.group(0)

    return MARKDOWN_LINK.sub(redirect, content)


def attribution_bytes(data):
    """Disclose archived evidence, preserving its historical source hash."""
    document = json.loads(data)

    def mark(node):
        if isinstance(node, dict):
            relative = node.get("file")
            if isinstance(relative, str) and process_exclusion(relative):
                if "sha256" in node:
                    node["source_sha256"] = node.pop("sha256")
                node["distribution_status"] = "archived_local_only"
                node["public_summary"] = SUMMARY_ANCHOR
            for value in list(node.values()):
                mark(value)
        elif isinstance(node, list):
            for value in node:
                mark(value)

    mark(document)
    document["distribution_note"] = (
        "Historical evidence hashes describe the unchanged local source tree. "
        "archived_local_only records are not included. Actual public-file hashes "
        "and Markdown link/path changes are recorded in RELEASE_MANIFEST.json."
    )
    return (json.dumps(document, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def public_bytes(relative, data):
    if relative == "docs/source-attribution.json":
        return attribution_bytes(data)
    if not relative.endswith(".md"):
        return data
    content = redirect_links(relative, data.decode("utf-8"))
    if relative in PROCESS_PATH_NOTES:
        content = LOCAL_PROCESS_PATH.sub("<local-author-workspace>", content)
    return content.encode("utf-8")
