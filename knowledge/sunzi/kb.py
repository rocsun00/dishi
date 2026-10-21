#!/usr/bin/env python3
"""Read, search, render, and validate the local Sunzi working corpus."""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
from html import escape
import json
import math
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_corpus(root: Path = ROOT) -> dict:
    passages = read_jsonl(root / "data/passages.jsonl")
    analysis = read_json(root / "data/analysis.json")
    return {
        "source": read_json(root / "source/source.json"),
        "search_text": read_json(root / "data/search_text.json"),
        "search_metadata": read_json(root / "source/search_normalization.json"),
        "passages": passages,
        "by_id": {row["id"]: row for row in passages},
        "chapters": analysis,
        "readings": {row["passage_id"]: row for chapter in analysis for row in chapter["readings"]},
        "concepts": [row for chapter in analysis for row in chapter["concepts"]],
        "examples": read_json(root / "data/examples.json"),
    }


def search(query: str, corpus: dict, limit: int = 5) -> list[dict]:
    """Rank lexical matches; no network, embeddings, or generated answers."""
    query = query.strip()
    if not query:
        return []
    if query.upper() in corpus["by_id"]:
        selected = [corpus["by_id"][query.upper()]]
        return [result_record(selected[0], corpus, 1.0)]
    words = re.findall(r"[a-zA-Z0-9_-]+|[\u3400-\u9fff]+", query.lower())
    grams = set()
    for word in words:
        if re.fullmatch(r"[\u3400-\u9fff]+", word) and len(word) > 2:
            grams.update(word[i : i + 2] for i in range(len(word) - 1))
        else:
            grams.add(word)
    if not grams:
        return []
    documents = {}
    for passage in corpus["passages"]:
        related = [card for card in corpus["concepts"] if passage["id"] in card["passage_ids"]]
        reading = corpus["readings"][passage["id"]]
        documents[passage["id"]] = " ".join(
            [passage["text"], corpus["search_text"][passage["id"]], passage["chapter_title"], reading["explanation"], reading.get("caution", "")]
            + [json.dumps(card, ensure_ascii=False) for card in related]
        ).lower()
    frequencies = Counter({gram: sum(gram in text for text in documents.values()) for gram in grams})
    ranked = []
    total = len(documents)
    for passage in corpus["passages"]:
        text = documents[passage["id"]]
        score = sum(math.log(1 + total / (1 + frequencies[gram])) for gram in grams if gram in text)
        score += 8 * sum(word in text for word in words if len(word) > 1)
        score += 12 * (query.lower() in passage["text"].lower())
        if score > 0:
            ranked.append(result_record(passage, corpus, round(score, 4)))
    ranked.sort(key=lambda row: (-row["score"], row["id"]))
    return ranked[:limit]


def result_record(passage: dict, corpus: dict, score: float) -> dict:
    return {
        "id": passage["id"],
        "chapter": passage["chapter"],
        "chapter_title": passage["chapter_title"],
        "score": score,
        "text": passage["text"],
        "explanation": corpus["readings"][passage["id"]]["explanation"],
        "caution": corpus["readings"][passage["id"]].get("caution", ""),
        "concepts": [row["title"] for row in corpus["concepts"] if passage["id"] in row["passage_ids"]],
        "source_url": passage["source_url"],
    }


def normalize_markup(markup: str) -> str:
    text = re.sub(r"\[\[[^]|]+\|([^]]+)\]\]", r"\1", markup)
    return re.sub(r"\{\{另\|([^|}]+)\|([^}]+)\}\}", r"\1", text)


def validate(corpus: dict, root: Path = ROOT) -> dict:
    errors = []
    source = corpus["source"]
    passages = corpus["passages"]
    raw_bytes = (root / "source/wikisource.wikitext").read_bytes()
    raw = raw_bytes.decode("utf-8")
    lines = raw.splitlines()
    if hashlib.sha256(raw_bytes).hexdigest() != source["raw_sha256"]:
        errors.append("原始快照摘要不符")
    if set(corpus["search_text"]) != set(corpus["by_id"]):
        errors.append("简体检索层未完整对应原文段落")
    search_bytes = (root / "data/search_text.json").read_bytes()
    if hashlib.sha256(search_bytes).hexdigest() != corpus["search_metadata"]["sha256"]:
        errors.append("简体检索层摘要不符")
    headers = [(i, match.group(1)) for i, line in enumerate(lines, 1) if (match := re.fullmatch(r"== (.+?) ==", line))]
    if len(headers) != 14 or headers[-1][1] != "答話":
        errors.append("源快照章节边界改变，须重新审查")
        return {"valid": False, "chapters": len(corpus["chapters"]), "passages": len(passages), "readings": len(corpus["readings"]), "concepts": len(corpus["concepts"]), "examples": len(corpus["examples"]), "verified_quotes": 0, "errors": errors}
    expected_lines = {i for i in range(headers[0][0] + 1, headers[13][0]) if lines[i - 1].strip() and not lines[i - 1].startswith("==")}
    if expected_lines != {p["source_line"] for p in passages}:
        errors.append("正文段落未完整覆盖源十三篇")
    if len(passages) != source["passage_count"] or len(corpus["chapters"]) != 13:
        errors.append("篇数或段落总数不符")
    if len(corpus["by_id"]) != len(passages):
        errors.append("原文段落编号重复")
    if [p["source_line"] for p in passages] != sorted(expected_lines):
        errors.append("原文段落排列顺序不符")
    for p in passages:
        if not 1 <= p["source_line"] <= len(lines) or not 1 <= p["chapter"] <= 13:
            errors.append(f"原文行号或篇号无效：{p['id']}")
            continue
        if p["source_markup"] != lines[p["source_line"] - 1].strip() or p["text"] != normalize_markup(p["source_markup"]):
            errors.append(f"原文不忠于快照：{p['id']}")
        start, title = headers[p["chapter"] - 1]
        end = headers[p["chapter"]][0]
        if not start < p["source_line"] < end or p["chapter_title"] != title:
            errors.append(f"原文归篇不符：{p['id']}")
        expected_notes = [{"primary": match.group(1), "alternative": match.group(2), "kind": "source_variant_template"} for match in re.finditer(r"\{\{另\|([^|}]+)\|([^}]+)\}\}", p["source_markup"])]
        if p["editorial_notes"] != expected_notes:
            errors.append(f"底本异文不忠于快照：{p['id']}")
    reading_ids = [row["passage_id"] for chapter in corpus["chapters"] for row in chapter["readings"]]
    if Counter(reading_ids) != Counter(corpus["by_id"].keys()):
        errors.append("逐段释义存在遗漏、重复或无效编号")
    if [c["chapter"] for c in corpus["chapters"]] != list(range(1, 14)):
        errors.append("释义篇次缺失、重复或乱序")
    for chapter in corpus["chapters"]:
        expected_order = [p["id"] for p in passages if p["chapter"] == chapter["chapter"]]
        expected = set(expected_order)
        mapped = {pid for row in chapter["argument_map"] for pid in row["passage_ids"]}
        if mapped != expected:
            errors.append(f"论证结构覆盖不符：第{chapter['chapter']}篇")
        if {r["passage_id"] for r in chapter["readings"]} != expected:
            errors.append(f"释义跨章或缺段：第{chapter['chapter']}篇")
        elif [r["passage_id"] for r in chapter["readings"]] != expected_order:
            errors.append(f"释义段落顺序不符：第{chapter['chapter']}篇")
    card_ids = [card["id"] for card in corpus["concepts"]]
    if len(card_ids) != len(set(card_ids)):
        errors.append("思想卡编号重复")
    quote_count = 0
    for card in corpus["concepts"]:
        ids = card["passage_ids"]
        if not ids or any(pid not in corpus["by_id"] for pid in ids):
            errors.append(f"思想卡段落编号无效：{card['id']}")
        elif not card["quote"] or not any(card["quote"] in corpus["by_id"][pid]["text"] for pid in ids):
            errors.append(f"思想卡引句不在对应原文中：{card['id']}")
        else:
            quote_count += 1
    for example in corpus["examples"]:
        if not example["passage_ids"] or any(pid not in corpus["by_id"] for pid in example["passage_ids"]):
            errors.append(f"示例段落编号无效：{example['id']}")
        for quote in example.get("quotes", []):
            if not quote["text"].strip() or quote["passage_id"] not in example["passage_ids"] or quote["passage_id"] not in corpus["by_id"] or quote["text"] not in corpus["by_id"][quote["passage_id"]]["text"]:
                errors.append(f"示例引句不在原文中：{example['id']}")
            else:
                quote_count += 1
    return {"valid": not errors, "chapters": len(corpus["chapters"]), "passages": len(passages), "readings": len(reading_ids), "concepts": len(card_ids), "examples": len(corpus["examples"]), "verified_quotes": quote_count, "errors": errors}


def ref(pid: str) -> str:
    return f"[{pid}](原文.md#{pid.lower()})"


def render(root: Path = ROOT) -> dict:
    corpus = load_corpus(root)
    report = validate(corpus, root)
    if not report["valid"]:
        raise ValueError("；".join(report["errors"]))
    source = corpus["source"]
    original = ["# 孙子兵法十三篇原文", "", f"电子工作底本：[中文维基文库固定修订版 {source['source_revision']}]({source['source_url']})。保留繁体正文；段落编号为本库所加。底本异文在对应段后单列。", ""]
    guide = ["# 孙子兵法逐篇导读", "", "以下为 AI 依据本库固定原文撰写的逐段释义提要，不是古代注家原注或逐字全译。现代应用单列于思想索引；版本与校核范围见《质量说明》。", ""]
    cards_md = ["# 孙子兵法思想索引", "", "每张卡区分军事语境、解释与现代类比；引句可按段落编号回查。", ""]
    toc_html = []
    chapters_html = []
    for chapter in corpus["chapters"]:
        number = chapter["chapter"]
        title = chapter["title_simplified"]
        heading = f"{number:02d} {title}"
        original.extend([f"## {heading}", ""])
        guide.extend([f"## {heading}", "", chapter["overview"], "", "论证结构：", ""])
        for block in chapter["argument_map"]:
            guide.append(f"- {'、'.join(ref(pid) for pid in block['passage_ids'])}：{block['point']}")
        guide.append("")
        toc_html.append(f'<a href="#chapter-{number}"><span>{number:02d}</span>{escape(title)}</a>')
        segments_html = []
        for reading in chapter["readings"]:
            pid = reading["passage_id"]
            p = corpus["by_id"][pid]
            original.extend([f"### {pid}", "", p["text"], ""])
            notes = "；".join(f"正文作“{n['primary']}”，异文作“{n['alternative']}”" for n in p["editorial_notes"])
            if notes:
                original.extend([f"底本异文：{notes}。", ""])
            guide.extend([f"### {pid}", "", f"原文：{ref(pid)}", "", reading["explanation"], ""])
            terms = "；".join(f"{key}：{value}" for key, value in reading["terms"].items())
            if terms:
                guide.extend([f"词义提示：{terms}", ""])
            if reading.get("caution"):
                guide.extend([f"读法与边界：{reading['caution']}", ""])
            details = (f'<p class="terms">词义提示　{escape(terms)}</p>' if terms else "") + (f'<p class="caution">读法与边界　{escape(reading["caution"])}</p>' if reading.get("caution") else "") + (f'<p class="caution">底本异文　{escape(notes)}</p>' if notes else "")
            segments_html.append(f'<article id="{pid.lower()}"><div class="passage-id">{pid} · <a href="{escape(p["source_url"], quote=True)}">核对来源</a></div><div class="parallel"><div><span class="label">原文</span><p lang="zh-Hant" class="original">{escape(p["text"])}</p></div><div><span class="label">AI 释义提要</span><p>{escape(reading["explanation"])}</p>{details}</div></div></article>')
        cards_md.extend([f"## {heading}", ""])
        concept_html = []
        for card in chapter["concepts"]:
            cards_md.extend([f"### {card['id']} {card['title']}", "", f"关键词：{'、'.join(card['tags'])}", "", f"> {card['quote']}", "", f"原文定位：{'、'.join(ref(pid) for pid in card['passage_ids'])}", "", f"军事语境：{card['source_context']}", "", f"思想解释：{card['interpretation']}", "", "成立条件：" + "；".join(card["conditions"]), "", f"常见误读：{card['misreading']}", "", f"现代类比：{card['modern_application']}", "", f"应用边界：{card['boundary']}", ""])
            concept_html.append(f'<details class="concept"><summary>{escape(card["title"])}</summary><blockquote>{escape(card["quote"])}</blockquote><p><b>军事语境</b>　{escape(card["source_context"])}</p><p><b>思想解释</b>　{escape(card["interpretation"])}</p><p><b>成立条件</b>　{escape("；".join(card["conditions"]))}</p><p><b>常见误读</b>　{escape(card["misreading"])}</p><p><b>现代类比</b>　{escape(card["modern_application"])}</p><p><b>应用边界</b>　{escape(card["boundary"])}</p></details>')
        chapters_html.append(f'<section id="chapter-{number}"><header><div class="eyebrow">第 {number} 篇</div><h2>{escape(title)}</h2><p class="overview">{escape(chapter["overview"])}</p></header>{"".join(segments_html)}<div class="concept-group"><h3>本篇思想卡</h3>{"".join(concept_html)}</div></section>')
    examples_md = ["# 帝师问答示例", "", "以下为依据本库原文撰写的人工可审查示例，不是模型训练后的性能成绩。现代问题的回答为类比推演，不等同于原典结论。", ""]
    examples_html = []
    for example in corpus["examples"]:
        examples_md.extend([f"## {example['id']} {example['question']}", "", example["answer"], "", "原文依据：" + "、".join(ref(pid) for pid in example["passage_ids"]), ""])
        example_links = "、".join(f'<a href="#{pid.lower()}">{pid}</a>' for pid in example["passage_ids"])
        examples_html.append(f'<details class="example"><summary>{escape(example["question"])}</summary><p>{escape(example["answer"])}</p><p class="terms">原文定位　{example_links}</p></details>')
    files = {"原文.md": original, "逐篇导读.md": guide, "思想索引.md": cards_md, "问答示例.md": examples_md}
    for name, lines_out in files.items():
        (root / name).write_text("\n".join(lines_out).rstrip() + "\n", encoding="utf-8")
    html = """<!doctype html><html lang="zh-Hans"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>帝师知识库 孙子兵法十三篇</title><style>
:root{color-scheme:light;--ink:#263532;--muted:#5b6864;--paper:#f6f3ec;--line:#d9dfd8;--accent:#235d4c}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:17px/1.85 -apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",sans-serif}a{color:var(--accent);text-underline-offset:4px}a:focus-visible,summary:focus-visible{outline:3px solid #8c4e1d;outline-offset:4px}aside{position:fixed;inset:0 auto 0 0;width:240px;padding:38px 24px;overflow:auto;border-right:1px solid var(--line);background:#eeeee5}aside h1{font-size:22px;margin:0 0 6px}aside p{font-size:13px;color:var(--muted);margin:0 0 24px}nav a{display:block;padding:7px 0;text-decoration:none;font-size:14px}nav span{display:inline-block;width:30px;color:var(--muted);font-variant-numeric:tabular-nums}main{margin-left:240px;max-width:1450px;padding:55px 6vw}.hero{margin-bottom:55px}.eyebrow,.label{font-size:12px;font-weight:650;letter-spacing:.09em;color:var(--accent)}h1,h2,h3{line-height:1.4}h1{font-size:38px;margin:12px 0}h2{font-size:29px;margin:8px 0 20px}h3{font-size:20px}.intro{max-width:800px;color:var(--muted)}.facts{display:flex;flex-wrap:wrap;gap:10px;margin:24px 0}.facts span{border:1px solid var(--line);padding:5px 12px;background:#fffdf8;font-size:14px}.note{padding:18px 22px;border-left:3px solid #b58950;background:#f0e8d9;font-size:14px}.note p{margin:0}section{scroll-margin-top:30px;margin-bottom:70px}.overview{max-width:920px;color:var(--muted)}article{scroll-margin-top:24px;border-top:1px solid var(--line);padding:26px 0}.passage-id{font-size:12px;color:var(--muted);margin-bottom:12px}.parallel{display:grid;grid-template-columns:1fr 1fr;gap:36px}.parallel p{margin-top:9px}.original{font-family:"Songti SC","Noto Serif CJK TC",serif;font-size:19px;line-height:2}.terms,.caution{font-size:13px;color:var(--muted)}.caution{border-left:2px solid #bc9b6d;padding-left:12px}.concept-group{background:#eeeee5;padding:18px 25px;margin-top:10px}details{border-top:1px solid var(--line);padding:12px 0}summary{cursor:pointer;font-weight:600}details p,blockquote{font-size:15px}blockquote{border-left:3px solid #8caa9b;margin:18px 0;padding-left:18px}.bottom{font-size:13px;color:var(--muted);border-top:1px solid var(--line);padding-top:25px}@media(max-width:850px){aside{position:static;width:auto;padding:22px}aside p{margin-bottom:12px}nav{display:flex;gap:4px 20px;flex-wrap:wrap}nav a{font-size:13px;padding:2px 0}main{margin:0;padding:30px 22px}.parallel{grid-template-columns:1fr;gap:12px}h1{font-size:30px}.original{font-size:18px}}@media print{aside{display:none}main{margin:0;padding:0}.concept-group{background:none}details{break-inside:avoid}.parallel{gap:22px}a{color:inherit}}
</style></head><body><aside><h1>帝师知识库</h1><p>首部原典 · 孙子兵法</p><nav>__TOC__<a href="#examples">问答示例</a></nav></aside><main><header class="hero"><div class="eyebrow">公开原典与可核查解读</div><h1>孙子兵法十三篇</h1><p class="intro">完整保留传世十三篇正文，逐段对应 AI 释义，并将现代应用另列。使用浏览器查找可检索当前页；点击思想卡可展开。</p><div class="facts"><span>13 篇原文</span><span>__PASSAGES__ 段对应释义</span><span>__CONCEPTS__ 张思想卡</span><span>__EXAMPLES__ 个问答示例</span></div><div class="note"><p>工作底本：中文维基文库固定修订版 __REVISION__。源条目未明示统一纸本底本；本版完成结构与引句检查、有限原文抽核，尚未经过专业学者逐字校勘。AI 释义不是古代注家原注。<a href="质量说明.md">查看质量说明</a></p></div></header>__CHAPTERS__<section id="examples"><div class="eyebrow">可审查的应用示范</div><h2>问答示例</h2><p class="overview">引文回到本库原文，现实应用说明推论与边界。</p>__EXAMPLE_BLOCKS__</section><footer class="bottom">来源：<a href="__SOURCE__">中文维基文库及其贡献者</a> · 原始快照、版本记录、正文数据与释义数据均保存在本地。知识库可检索使用，本版没有进行模型微调训练。</footer></main></body></html>"""
    for key, value in {"__TOC__": "".join(toc_html), "__PASSAGES__": str(report["passages"]), "__CONCEPTS__": str(report["concepts"]), "__EXAMPLES__": str(report["examples"]), "__REVISION__": str(source["source_revision"]), "__CHAPTERS__": "".join(chapters_html), "__EXAMPLE_BLOCKS__": "".join(examples_html), "__SOURCE__": escape(source["source_url"], quote=True)}.items():
        html = html.replace(key, value)
    (root / "阅览.html").write_text(html, encoding="utf-8")
    (root / "data/validation.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="帝师孙子兵法本地知识库：原文检索与可核查导读，不联网")
    sub = parser.add_subparsers(dest="command", required=True)
    find = sub.add_parser("search", help="关键词检索，返回原文与释义，不自动生成答案")
    find.add_argument("query")
    find.add_argument("--limit", type=int, choices=range(1, 21), default=5)
    find.add_argument("--json", action="store_true")
    show = sub.add_parser("show", help="按段落编号读取完整记录")
    show.add_argument("passage_id")
    sub.add_parser("validate", help="核对正文覆盖、原始快照摘要、释义及引句")
    sub.add_parser("build", help="从已整理的数据生成阅读文件")
    args = parser.parse_args()
    try:
        corpus = load_corpus()
        if args.command in ("validate", "build"):
            report = render() if args.command == "build" else validate(corpus)
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return 0 if report["valid"] else 1
        if args.command == "show":
            pid = args.passage_id.upper()
            if pid not in corpus["by_id"]:
                print(f"未找到原文段落：{args.passage_id}", file=sys.stderr)
                return 2
            print(json.dumps(result_record(corpus["by_id"][pid], corpus, 1.0), ensure_ascii=False, indent=2))
            return 0
        results = search(args.query, corpus, args.limit)
        if args.json:
            print(json.dumps(results, ensure_ascii=False, indent=2))
        elif not results:
            print("没有找到相关关键词；这不等于原典中不存在该思想，可尝试更具体或不同的词语。")
        else:
            for row in results:
                print(f"{row['id']}　{row['chapter_title']}　关键词匹配分 {row['score']}")
                print(f"原文：{row['text']}")
                print(f"AI 释义提要：{row['explanation']}")
                if row["caution"]:
                    print(f"读法与边界：{row['caution']}")
                print(f"来源：{row['source_url']}\n")
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"知识库读取或校验失败：{error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
