# 安装与使用

[English](installation.en.md) · [项目介绍](../README.md)

帝师 Imperial Preceptor 为 AI 助手提供军师、谋士、参谋的方法：看清局势，献上可选计策，说出逆耳之言，决定由用户作出。本地技能版需要一个能读取文件、运行 Python 并理解中英文的宿主模型；知识库 CLI 自身负责检索和校验，完整建议由宿主模型生成。

英文展示名为 **Imperial Preceptor**；为兼容已有安装，仓库、技能标识、目录及命令仍使用 `dishi`。下文的 `$dishi`、`/dishi` 和路径无需改名。

## 聊天应用：直接使用提示词

豆包、ChatGPT、Claude 的网页版或 App 可使用[中文通用提示词](portable-prompt.zh-CN.md)或[English portable prompt](portable-prompt.en.md)。将提示词复制到应用支持的指令设置中，或作为新对话的第一条消息发送；具体入口、上传和工具权限由应用决定，本项目未逐一完成这些应用的使用验证。

提示词只提供参谋方法，不含本地原典库，也不会自动获得文件或 Python 权限。无法读取原段时不直接引用古文；用户可提供相关来源并自行复核。支持上传时，应按问题选择原文及对应导读、版本边界，确认助手实际能读取；上传成功不保证完整检索全部文献。需要随附离线库时，继续按下文安装本地技能。

## 准备

- 安装 Python 3.9 或更新版本。脚本只用标准库，无需 `pip install`，不要求额外 API 密钥。
- 下载项目 ZIP 后解压，或克隆仓库。终端进入含 `SKILL.md`、`knowledge/` 和 `scripts/` 的目录。不要只下载 `SKILL.md`。
- 本地检索、安装和校验无需联网。宿主 AI 的订阅、联网及数据处理规则由其服务决定；“本地知识库”不表示对话一定在设备上处理。

安装和测试命令在新下载的源码或发布包根目录运行；已经安装的 Skill 不包含 `scripts/` 和测试目录。更新时从新下载目录运行安装器。本地检索命令也可在已安装 Skill 目录运行。Windows 可把 `python3` 换成 `py -3 -X utf8`；本发布版的实际运行检查在 macOS 进行，未完成 Windows 或 Linux 原生宿主测试。

## 安装到 Codex

先查看计划，再安装：

```bash
python3 scripts/install.py --target codex --dry-run
python3 scripts/install.py --target codex
```

默认安装到 `~/.agents/skills/dishi`，与当前 [OpenAI 官方技能文档](https://learn.chatgpt.com/docs/build-skills) 的个人目录约定一致。官方文档建议以插件分发可安装扩展；本项目当前提供手动安装的独立 Skill 文件夹，尚未提交插件目录。

已有旧版本时，安装脚本会拒绝直接覆盖。若检测到 `~/.codex/skills/dishi` 的旧位置，也会要求明确目录，避免新旧重复加载。要更新已有版本，请指定**实际存在的那一个目录**：

```bash
python3 scripts/install.py --destination ~/.agents/skills/dishi --replace
```

旧位置用户相应使用：

```bash
python3 scripts/install.py --destination ~/.codex/skills/dishi --replace
```

`--replace` 先校验新的运行资料，再把已有安装完整复制到技能扫描目录之外，最后切换新副本。标准个人安装默认备份到 `~/.local/share/dishi/backups/dishi-…/dishi`；自定义安装默认备份到扫描目录外层的 `.dishi-backups/`，不会使用个人家目录。JSON 输出给出实际备份位置。可用 `--backup-dir` 明确指定扫描树以外的备份目录。旧版本里的个人修改保留在备份中，需要自行选择是否合并；脚本不会自动合并或清理旧备份。运行安装包含知识资料、来源、方法和相互链接的说明文档，排除开发测试、发布工具和完整过程日志。备份确认无用后再手动删除。

在 Codex 中选择 `dishi`，或输入：

```text
用 $dishi 分析：团队经常错过交付日期，应该先改流程还是换人？
```

```text
Use $dishi to examine this decision: should I keep my stable job or test a business idea? Answer in English and cite the relevant passages.
```

Codex 支持自动发现技能变更；若未显示，请重启宿主并检查是否有重复的同名技能。上面路径是供命令行使用的 `~` 家目录写法，无需把任何人的真实用户名写进文件。

## Claude Code（可选）

```bash
python3 scripts/install.py --target claude
```

默认目录 `~/.claude/skills/dishi`，与 [Claude Code 官方文档](https://code.claude.com/docs/en/skills) 一致。在 Claude Code 使用 `/dishi` 后附上问题。目录复制和同一 Python CLI 可本地验证；本版未实际启动 Claude Code 对话做端到端验证。

## 不安装也能查阅

在项目根目录执行：

```bash
python3 knowledge/kb.py list
python3 knowledge/kb.py validate
python3 knowledge/kb.py search '组织 责任' --limit 3 --json
python3 knowledge/kb.py explain-query 'trust and cooperation' --json
python3 knowledge/kb.py search 'trust and cooperation' --limit 3 --json
python3 knowledge/kb.py show HF-43-002
```

`validate` 应返回 `valid: true`；`list` 列出 27 个 `ready` 条目。`show` 返回中文原段、释义、注意点与固定来源。也可打开 [知识库总览](../knowledge/知识库总览.md) 或各书 `阅览.html`，本地阅读页以中文为主。

英文查询使用有限人工关键词映射；`explain-query` 会显示映射、未识别词和否定提示。它不翻译整句话，也不理解完整的条件、比较或否定逻辑；检测到英文否定时会保守停用英文映射并提示改写。书名提示可以提升已有候选，但只有 `--book` 才限定范围。宿主模型应保留用户原意，对映射不足的概念尝试准确的中文检索词，再核对全文语境。匹配分不是事实可信度。检索返回原典候选，CLI 不直接生成英文决策建议。

## 卸载和恢复

退出宿主后，删除实际安装的 `dishi` 文件夹即可卸载；不需要改其他设置。恢复旧版时，把安装输出中记录的备份目录复制回原位置，并避免同时保留多个可发现的同名技能。操作前保留需要的个人修改。

遇到权限不足时，选择自己有写权限的技能目录；脚本不会提权、下载软件或改动宿主配置。
