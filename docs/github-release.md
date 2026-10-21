# GitHub 发布准备 / GitHub release preparation

[中文介绍](../README.md) · [English overview](../README.en.md)

公开名称 / Public name: **帝师 Imperial Preceptor**

发起与维护 / Created and maintained by: **Roc Sun**

现有仓库 / Existing repository: [rocsun00/dishi](https://github.com/rocsun00/dishi)

仓库名、技能标识、安装目录与 ZIP 前缀继续使用 `dishi`，兼容已有链接和调用方式；英文展示名使用 **Imperial Preceptor**。

The repository name, skill identifier, installation folder, and ZIP prefix remain `dishi` for compatibility with existing links and invocations. The English public name is **Imperial Preceptor**.

推荐简介 / Suggested description:

> Imperial Preceptor: your AI strategist, drawing on China's Hundred Schools of Thought. Bilingual, source-checked counsel and an offline classical corpus. By Roc Sun.

建议主题 / Suggested topics: `agent-skills`, `chinese-classics`, `chinese-philosophy`, `decision-making`, `ai-advisor`, `strategy`, `codex`, `bilingual`.

## 当前版本与历史 / Current revision and history

本轮准备 **v0.2.1**：采用 Roc Sun 署名与 Imperial Preceptor 英文名称，完成验证与产物检查后发布到现有仓库。v0.2.0 曾公开，现已撤下其 GitHub Release、发布资产及同名标签；仓库源码保留。本地历史包与验证记录保留为归档，不把旧包当作本轮成品。

This revision prepares **v0.2.1** with the Roc Sun credit and Imperial Preceptor name for publication in the existing repository after validation and artifact checks. Version v0.2.0 was previously public; its GitHub Release, assets, and tag have since been removed. Repository source remains available. Earlier local packages and validation records remain archived and are not this revision's deliverables.

## v0.2.1 发布说明 / Release notes

> In an age of upheaval more than two millennia ago, China's Hundred Schools of Thought asked what to do next. Imperial Preceptor brings that counsel to the choices you face today.

- 统一英文展示名为 Imperial Preceptor，并采用 Roc Sun 署名；第三方材料保留各自的署名与适用条件。 / Adopts Imperial Preceptor as the public English name and Roc Sun as the project credit; third-party attributions and applicable terms remain intact.
- 技术标识 `dishi`、`$dishi`、`/dishi`、安装路径与 ZIP 前缀保持兼容。 / Keeps the `dishi` identifier, `$dishi` and `/dishi` invocations, installation paths, and ZIP prefix compatible.
- 保留先广搜原典、再研读比较、最后献策的古籍研判机制及五条现代军师守则。 / Retains the research-first classical method and five modern adviser rules.
- 保留双语说明、聊天应用提示词、27 种文献及有限英文辅助检索；提示词不自带原典库或工具权限。 / Retains bilingual documentation, portable prompts, 27 collections, and finite English retrieval support; prompts do not include the corpus or grant tool access.
- 只声明本轮实际完成的检查，不把历史记录、假设示例或单次试答说成真实用户效果验证。 / Reports checks actually completed for this revision without presenting historical records, hypothetical examples, or individual trials as evidence of user outcomes.

## 本地发布包 / Local release package

在源项目根目录运行 `scripts/build_release.py --output`，传入源目录以外、尚不存在的发布文件夹。例如：

Run `scripts/build_release.py --output` from the source project root, passing a fresh release folder outside that checkout. For example:

```bash
python3 scripts/build_release.py --output ../GitHub发布包/v0.2.1/dishi
```

脚本输出清洁目录、同级版本 ZIP 及其 SHA-256；不会调用 GitHub 或上传文件。本地包生成后还须检查 manifest、ZIP 与目录逐字节一致性，并从 ZIP 临时安装、校验原典和相对文件链接。最终摘要与产物检查记录放在交付目录中另存。

The script produces a clean directory, a versioned sibling ZIP, and its SHA-256. It does not contact GitHub or upload anything. Then verify the manifest and byte-for-byte ZIP/directory consistency, temporarily install from the ZIP, and check corpus validity and relative file links. Store final checksums and artifact-check records separately alongside the package.

发布包排除缓存、系统临时文件和完整 AI 过程记录，保留原始电子来源与正文。公开副本将指向归档记录的链接改到[过程摘要](provenance-summary.md#archived-records)，并标记来源索引中的本地归档证据。`RELEASE_MANIFEST.json` 逐项记录文件实际摘要、声明的转换及被排除记录。历史验收不改写为本版测试，原典、现代编辑内容和第三方条件的边界不因改名而改变。

The package excludes caches, system artifacts, and full AI workflow transcripts while retaining original electronic sources and passages. Public copies redirect archived-record links to the [provenance summary](provenance-summary.md#archived-records) and mark locally archived evidence in the source index. `RELEASE_MANIFEST.json` records public hashes, declared transformations, and excluded records. Historical checks are not rewritten as current tests; the name change does not alter the boundaries between source texts, modern editorial content, and third-party terms.

## 上传步骤 / Publishing steps

1. 使用现有的 [rocsun00/dishi](https://github.com/rocsun00/dishi) 仓库，不为改名新建仓库。审阅待提交的清洁发布目录，使 `README.md` 与 `SKILL.md` 位于仓库根目录；不要上传包含个人安装回查的上级工作文件夹。
2. 确认待提交内容与本轮已检查的发布目录一致，检查 Git 提交者身份和差异，再提交并推送。Git 提交身份与许可证署名分别维护；不要把私有邮箱、访问凭证或本地个人路径写入公开文件。
3. 为本轮新建 **v0.2.1** 标签及 Release，附上 `dishi-0.2.1.zip` 与相应 SHA-256。发布说明使用 Imperial Preceptor 名称及 Roc Sun 署名，并如实列明本轮实际完成和未完成的验证。
4. 上传后再次核对远端提交、标签、资产名称和下载文件摘要。v0.2.0 已撤下，不重新上传旧包或重建旧标签。

1. Use the existing [rocsun00/dishi](https://github.com/rocsun00/dishi) repository; a display-name change does not require a new repository. Review the clean release contents with `README.md` and `SKILL.md` at the repository root. Do not upload the parent working folder containing private installation audit reports.
2. Confirm that the staged contents match this revision's checked release directory. Review the Git author identity and diff before committing and pushing. Git commit identity and license credit are maintained separately; keep private email addresses, credentials, and personal local paths out of public files.
3. Create a new **v0.2.1** tag and Release with `dishi-0.2.1.zip` and its SHA-256. Use Imperial Preceptor and the Roc Sun credit in the release notes, stating the validation actually completed and its limits.
4. After upload, check the remote commit, tag, asset names, and downloaded file checksum. Version v0.2.0 has been withdrawn; do not re-upload its package or recreate its tag.

下载或 star 不代表使用效果或购买意愿，发布说明只写实际具备和验证的能力。

Downloads and stars do not establish effectiveness or purchase intent. Describe actual capabilities and checks without promising adoption, outcomes, or revenue.
