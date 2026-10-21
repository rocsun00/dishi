# Imperial Preceptor 帝师 · Your AI Strategist

[中文](README.md) · [Examples](docs/examples.en.md) · [Research examples](references/research-examples.en.md) · [Installation](docs/installation.en.md) · [Chat-app prompt](docs/portable-prompt.en.md) · [Corpus and languages](docs/corpus.md)

**In an age of upheaval more than two millennia ago, China's Hundred Schools of Thought asked what to do next. Imperial Preceptor brings that counsel to the choices you face today.**

During the Spring and Autumn and Warring States periods, the Zhou order was breaking apart. Rival states fought for supremacy, old rules no longer held, and a new order had yet to take shape. Advisers traveled from court to court, helping rulers survive and deciding for themselves when to serve and when to leave. In that turbulent age, Confucius, Laozi, Sunzi, Mozi, Mencius, Zhuangzi, Han Fei and others developed ways to read a situation, deal with people, and make difficult choices. Later generations called them the Hundred Schools of Thought.

We live in an age of upheaval too. Technology is reshaping industries, rules are being rewritten, and careers and lives feel less certain. These thinkers did not foresee our circumstances, but the questions they kept asking are still ours. How do you read a shifting situation? What do the people involved really want? When should you advance, and when should you step back? Which rules are worth setting? What kind of person do you want to become?

Imperial Preceptor is an AI strategist. It draws on selected texts from the Hundred Schools and on texts by or about figures from across Chinese history, including Fan Li, Zhuge Liang and Wang Yangming. Imperial Preceptor helps you map the situation, weigh distinct options, and hear the objection you might not want to hear. It checks classical quotations against their sources before citing them, offers no advice that depends on harming others, and leaves the final decision to you.

Created and maintained by **Roc Sun**. **Imperial Preceptor** is the public project name; the repository name, skill identifier, and installation folder remain `dishi` for compatibility. Invoke it with `$dishi` or `/dishi`, depending on the host.

The skill includes an offline Chinese source library for a host that can read local files and run Python. A [portable prompt](docs/portable-prompt.en.md) brings the same advisory method to chat apps. The prompt alone does not include that library or grant access to files on your computer.

## How Imperial Preceptor advises

1. **Map the situation (问局).** Clarify goals, resources, people, limits, and timing. Ask only about gaps that could change the recommendation.
2. **Search broadly and study the texts (广搜研典).** For every substantive consultation, first search the classical sources actually accessible for the problem, across works and traditions, including opposing views. Then select relevant passages for close reading. Do not limit the search to one or two traditions in advance or claim to exhaust the literature.
3. **Examine causes and circumstances (察因辨势).** Read passages in context: what produced the problem, what circumstances a proposal addressed, and what followed. Use verifiable historical cases to identify conditions and costs, then compare them with present facts. Do not invent motives or historical events to fill gaps.
4. **Compare and judge (比较裁决).** Preserve disagreements. Compare premises, causal accounts, scope, and counterexamples, explaining what applies, needs adaptation, or should be rejected. The reading must shape the judgment; do not produce generic advice first and attach classical quotations afterward.
5. **Advise and set a first step (献策定步).** Offer genuinely workable courses and a recommendation with actions, gains, costs, risks, and conditions. Do not force three options. Raise a candid objection, give a concrete first step, and specify signals for continuing, adjusting, or stopping.
6. **Review the result (复盘).** When you return with results, compare them with the original reasoning and explain what new evidence changes.

Scale the research to the depth of the question; a short answer can summarize the process. Search broadly, then select carefully: a long book list is no substitute for judgment. Confucian, Daoist, Mohist, Legalist, and other traditions ask different questions. Figures including Fan Li, Zhuge Liang, and Wang Yangming have distinct documentary contexts. Without readable sources or search tools, the chat prompt must clearly label its help as an unverified overview of ideas and present-day analysis, while still providing useful assistance. It must not pretend to have searched. See the [research method](references/research-method.md) and [paired research examples](references/research-examples.en.md).

## What the instructions ask the assistant to do

- **Trace the reasoning and quotations.** The skill requires a problem-led search across the local library before reading candidate passages and relevant context. Check quotations, work, chapter, and passage ID against sources linked to fixed electronic editions. Distinguish source text, ancient commentary, AI readings, and modern application, and explain how the evidence supports or limits the advice. Leave unchecked quotations out; retrieval scores are not confidence values. Report the actual search scope and gaps without claiming exhaustive coverage.
- **Give candid counsel.** Serve your real interests, question assumptions, and explain risks even when you might prefer agreement.
- **Use strategy without harm.** Recognize risks, defend against manipulation, and negotiate fairly. Do not offer fraud, coercive manipulation, framing, or harm.

The five adviser rules are **serve the user's real interests (忠于所托), pursue goals without harm (谋事不害人), ground claims in evidence (言必有据), advise without deciding for the user (策不代断), and know the limits of your knowledge (知所不知)**. These are instructions to the host, not a guarantee that a model will always comply. Users should still check important quotations and judgments.

## Four examples

These are **hypothetical demonstrations, not customer success stories**. The Chinese and English versions cover the same cases.

| Situation | A more useful question |
| --- | --- |
| [Team delivery: change the system or replace people?](docs/examples.en.md#case-1) | Do responsibilities, authority, and results line up? |
| [A stable job or a venture: how big a step now?](docs/examples.en.md#case-2) | How do the wish for autonomy, the available evidence, and unacceptable losses fit together? |
| [Cross-cultural cooperation: disagreement and boundaries](docs/examples.en.md#case-3) | What behaviors and commitments need clarification so respect becomes workable cooperation? |
| [A major client demands a 30% renewal discount](docs/examples.en.md#case-4) | What do costs, alternatives, and limits allow you to offer honestly? |

After installation, you can ask an assistant that supports skills:

> Use $dishi: my team has missed two deadlines. I want to replace people, but acceptance criteria and approval authority are also unclear. Clarify key facts, search accessible classical sources broadly, compare their causes, conditions, costs, and opposing views, then give a recommendation, the strongest objection, and a first step.

> Imperial Preceptor, a major client wants a 30% renewal discount. Help me weigh workable approaches without inventing negotiating leverage.

You can ask in English, Chinese, or another language supported by the host. The exact way to invoke a skill, including whether `$dishi` works directly, depends on the host. English answers are generated by the host from Chinese sources. The local English dictionary is limited; the assistant should preserve your full meaning when preparing Chinese search terms.

## Install and explore locally

Download and extract the repository, then run from its root directory (Python 3.9+):

```bash
python3 scripts/install.py --target codex
```

The installer uses Codex's user skill directory by default and refuses to overwrite an existing destination. See the [English installation guide](docs/installation.en.md) or [Chinese guide](docs/installation.zh-CN.md) for existing installations, other hosts, and manual installation.

You can read and search the corpus without installing the skill. From the repository root:

```bash
python3 knowledge/kb.py list
python3 knowledge/kb.py search "赏罚" --book zhuge --limit 3
python3 knowledge/kb.py show ZGL-05-003 --book zhuge
python3 knowledge/kb.py explain-query "trust and cooperation" --json
```

`explain-query` shows how a limited English vocabulary maps to Chinese search terms. It does not translate arbitrary English questions. The CLI retrieves and displays local material; it does not call a model to generate answers.

## Evidence and limits

The current **27 ready texts or document collections** contain **6,640 source passages with corresponding readings, 2,226 idea cards, and 871 question-and-answer examples**. The local validation baseline records **3,645 exact quotation-match checks**. That is a count of checks on included quotations, not independent historical evidence or a measure of effectiveness. See [corpus and language notes](docs/corpus.md) for coverage, source layers, and verification.

- Source text, interpretation, modern application, and a model's judgment are distinct layers. Historical analogies do not establish present-day laws or guarantee results.
- Both language experiences use the Chinese base texts. The host model generates English explanations and translations on request. Ordinary English questions usually need the host to interpret the full intent and reformulate it in Chinese. The local dictionary supports limited phrases; it does not understand arbitrary English sentences or provide a complete English edition.
- Fixed sources, project passage IDs, and exact-match checks support traceability. Electronic working texts may still contain uncertain characters, variants, and disputed attributions; they are not scholarly critical editions.
- Later works are identified separately from pre-Qin traditions. The three personal collections cover the documents actually included, not complete works. The corpus has not been used for model fine-tuning.
- Questions that depend on current data or professional expertise require additional verification. The assistant's advice is open to scrutiny; the user makes the decision.

## License and sources

Historical references to “independent review” mean cross-checks by different AI agents within the same workflow, not certification by human experts or an external institution.

See [LICENSE](LICENSE) for original project material and [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) for source snapshots, third-party material, and their respective conditions. Check the relevant scope and source notes before reuse or redistribution.

[Validation scope](docs/validation.md) · [Contributing](CONTRIBUTING.md) · [Release preparation](docs/github-release.md)
