# Installation and use

[简体中文](installation.zh-CN.md) · [Project overview](../README.en.md)

Imperial Preceptor gives an AI assistant an adviser's method: read the situation, offer distinct options, and raise candid objections. The user decides. The local skill requires a host that can read files, run Python, and understand Chinese and English. The CLI retrieves and validates evidence; the host model writes the final analysis.

The public name is **Imperial Preceptor** (帝师). The repository, skill identifier, folder, and commands retain `dishi` for compatibility; keep the `$dishi` and `/dishi` invocations and paths shown below.

## Chat apps: use the portable prompt

The web or mobile versions of Doubao, ChatGPT, and Claude can use the [English portable prompt](portable-prompt.en.md) or [中文通用提示词](portable-prompt.zh-CN.md). Copy it into instruction settings supported by the app, or send it as the first message of a new conversation. Settings, uploads, and tool access depend on the app; this project has not tested the complete workflow in each one.

The prompt provides an advisory method without the local corpus or automatic file and Python access. It forbids direct classical quotations when the source cannot be read. Users can supply relevant source material and should verify important citations themselves. If uploads are supported, select source passages, corresponding readings, and edition and limitation notes relevant to the question, and confirm that the assistant can read them. An accepted upload does not guarantee complete retrieval of all collections. For the accompanying offline library, install the local skill below.

## Requirements

- Python 3.9 or newer, standard library only. No `pip install` or additional API key is required for the bundled scripts.
- Download and extract the project ZIP, or clone the repository. Open a terminal in the folder containing `SKILL.md`, `knowledge/`, and `scripts/`. A copy of `SKILL.md` alone is insufficient.
- Installation, retrieval, and validation are offline. The host AI may still require a subscription or send conversation content to its provider. A local corpus does not imply on-device AI inference.

Run installation and test commands from a freshly downloaded source checkout or release folder. An installed skill excludes `scripts/` and tests; update it using the installer in a new download. Retrieval commands can also run from the installed skill folder. On Windows, replace `python3` with `py -3 -X utf8`. Actual release checks ran on macOS; native Windows and Linux host sessions have not been tested.

## Codex

Preview the destination, then install:

```bash
python3 scripts/install.py --target codex --dry-run
python3 scripts/install.py --target codex
```

The default destination is `~/.agents/skills/dishi`, following the current personal-skill location in [OpenAI's documentation](https://learn.chatgpt.com/docs/build-skills). OpenAI recommends plugins for installable distribution; this release is a manually installed standalone skill folder and has not been submitted to a plugin directory.

The installer refuses to overwrite an existing skill. It also detects a legacy `~/.codex/skills/dishi` install to help avoid duplicate discovery. To update, explicitly select the folder you actually use:

```bash
python3 scripts/install.py --destination ~/.agents/skills/dishi --replace
```

For an existing legacy installation:

```bash
python3 scripts/install.py --destination ~/.codex/skills/dishi --replace
```

`--replace` validates the staged runtime resources, copies the previous installation to a backup outside skill discovery, then switches to the new version. Standard personal installations use `~/.local/share/dishi/backups/dishi-…/dishi`; custom destinations use an outer `.dishi-backups/` location rather than the personal home directory. JSON output reports the exact location. Use `--backup-dir` to choose another store outside the skill scan tree. Personal modifications survive in that backup; they are not merged automatically and older backups are not pruned automatically. Runtime installation retains knowledge, source evidence, methods, and linked documentation, excluding tests, release tools, and full workflow logs. Remove a backup manually only after checking it.

Select `dishi` in Codex, or ask:

```text
Use $dishi: our team repeatedly misses delivery dates. Should we change the process or replace people? Answer in English and cite the relevant passages.
```

```text
用 $dishi 分析：稳定工作和创业之间，我应该先验证哪些条件？
```

Codex detects skill changes automatically. If the `dishi` skill does not appear, restart the host and check for duplicate skills with the same name.

## Claude Code (optional)

```bash
python3 scripts/install.py --target claude
```

This uses `~/.claude/skills/dishi`, the personal-skill location in [Claude Code's documentation](https://code.claude.com/docs/en/skills). Invoke `/dishi` followed by your question. Folder installation and the shared Python CLI are locally testable; this release has not been tested in an actual Claude Code conversation.

## Explore without installing

From the project root:

```bash
python3 knowledge/kb.py list
python3 knowledge/kb.py validate
python3 knowledge/kb.py explain-query 'trust and cooperation' --json
python3 knowledge/kb.py search 'trust and cooperation' --limit 3 --json
python3 knowledge/kb.py search '组织 责任' --limit 3 --json
python3 knowledge/kb.py show HF-43-002
```

Expect `valid: true` from validation and 27 `ready` entries from `list`. `show` returns the Chinese passage, explanation, cautions, and fixed source. The [bilingual corpus table](corpus.md) links to the Chinese reading pages; those pages are not a full English translation.

English CLI retrieval uses a finite, inspectable keyword mapping. `explain-query` exposes mapped terms, unknown words, and negation warnings. It does not translate full sentences or interpret their full conditional, comparative, or negative logic. English negation conservatively disables English mappings and requests reformulation. Book hints can boost existing candidates; only `--book` restricts the corpus. The host should preserve the user's meaning, try precise Chinese search terms when needed, and inspect the original context. Matching scores are not confidence values. The CLI returns evidence candidates, not generated English advice.

## Remove or restore

Exit the host and remove the installed `dishi` folder to uninstall. To restore an older version, copy the backup named in the installer output to the original location, preserving any personal changes first. Avoid leaving two discoverable skills named `dishi`.

If you lack write permission, choose a skill directory you own. The installer does not elevate privileges, download software, or change host configuration.
