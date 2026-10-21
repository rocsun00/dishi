# GitHub 发布准备 / GitHub release preparation

[中文介绍](../README.md) · [English overview](../README.en.md)

推荐仓库名 / Suggested repository name: `dishi`

推荐简介 / Suggested description:

> Your AI strategist, drawing on China's Hundred Schools of Thought for an age of upheaval. Bilingual, source-checked classical quotations, offline corpus.

建议主题 / Suggested topics: `agent-skills`, `chinese-classics`, `chinese-philosophy`, `decision-making`, `ai-advisor`, `strategy`, `codex`, `bilingual`.

本轮整理为 **v0.2.0**，按作者要求生成独立的本地发布目录与 ZIP；不覆盖已有 v0.1.1 产物，不更新已安装技能，也不上传。本页给出发布准备步骤，最终包的摘要和回查记录在交付目录中另存。

This revision is **v0.2.0**, prepared as a separate local folder and ZIP. Existing v0.1.1 artifacts and installed skills remain unchanged; nothing is uploaded. Final artifact checks and checksums are delivered separately alongside the package.

## v0.2.0 发布说明 / Release notes

> In an age of upheaval more than two millennia ago, China's Hundred Schools of Thought asked what to do next. Dishi brings that counsel to the choices you face today.

- AI 军师定位，采用五条现代军师守则及问局、察势、献策、逆言、定步、复盘。 / AI strategist identity with five modern adviser rules and a six-step method.
- 中英文聊天应用通用提示词，明确原典与工具访问边界。 / Bilingual portable prompts with explicit source and tool-access boundaries.
- 新增大客户续约压价案例；案例 2 展示条件改变后的重排和两策情形，数字只是假设阈值。 / A client-renewal case plus case 2 re-ranking examples, including two remaining courses; numerical thresholds are illustrative.
- 保留 27 种文献与有限英文辅助检索；英文问题仍须理解完整条件并核对原文。 / Retains 27 collections and finite English retrieval support, with interpretation and source verification still required.
- 清理两处旧规范表述；原典集 1,337 文件不变、四处现代编辑内容有意修改，历史验收摘要不重写。 / Removes two outdated norm references; 1,337 collection files are unchanged and four modern editorial files intentionally revised, without rewriting historical evidence.
- 未做安装前后效果对比，不声称客户成效或完整英文译本。 / No installed-versus-uninstalled effect comparison, customer outcome claim or complete English edition.

## 本地发布包 / Local release package

在源项目根目录运行 `scripts/build_release.py --output`，传入源目录以外、尚不存在的发布文件夹。脚本输出清洁目录、同级版本ZIP及其SHA-256；不会调用GitHub或上传文件。

Run `scripts/build_release.py --output` from the source project root, passing a fresh release folder outside that checkout. The script produces a clean directory, a versioned sibling ZIP, and its SHA-256. It does not contact GitHub or upload anything.

发布包排除缓存、系统临时文件和完整AI过程记录；原始电子来源与正文保留。公开副本将指向归档记录的链接改到[过程摘要](provenance-summary.md#archived-records)，并标记来源索引中的本地归档证据。`RELEASE_MANIFEST.json` 逐项记录文件实际摘要、声明的转换及被排除记录。原始电子来源保留；本版四处现代编辑修订见验证记录，旧验收不冒充本版测试。

The package excludes caches, system artifacts, and full AI workflow transcripts while retaining original electronic sources and passages. Public copies redirect archived-record links to the [provenance summary](provenance-summary.md#archived-records) and mark locally archived evidence in the source index. `RELEASE_MANIFEST.json` records public hashes, declared transformations, and excluded records. Original electronic source evidence remains preserved; validation notes disclose the four modern editorial revisions. Historical checks are not presented as current tests.

## 上传步骤 / Publishing steps

1. 在GitHub选择账号并新建空仓库，建议名为 `dishi`。上传本发布目录中的全部内容，使 `README.md` 与 `SKILL.md` 位于仓库根目录。不要上传包含个人安装回查的上级工作文件夹。
2. 使用Git时，可在发布目录执行以下本地初始化；随后执行GitHub新仓库页面给出的远端连接和推送命令。选择哪个账号及公开范围应在实际发布时确认。
3. 发布此版本的 Release 时使用 `v0.2.0`，附版本ZIP，并概述双语使用、27种文献的明确范围、有限词法检索及已完成检查。

1. Choose the intended GitHub account and create an empty repository, suggested name `dishi`. Upload this release folder's contents with `README.md` and `SKILL.md` at the repository root. Do not upload the parent working folder containing private installation audit reports.
2. For Git, initialize locally as below, then use the remote and push commands shown by the new repository. Confirm the account and visibility when actually publishing.
3. For this Release, use `v0.2.0`, attach the versioned ZIP, and describe bilingual use, the scoped 27 collections, finite lexical retrieval, and completed checks.

```bash
git init -b main
git add .
git commit -m "Prepare Dishi v0.2.0"
```

Git提交前检查自己的提交者身份设置；上面命令不配置身份、不创建远端、不推送。下载或star不代表使用效果或购买意愿，发布说明只写实际具备和验证的能力。

Check your Git author identity before committing. These commands do not configure an identity, create a remote, or push. Describe actual capabilities and checks rather than promising adoption, stars, outcomes, or revenue.
