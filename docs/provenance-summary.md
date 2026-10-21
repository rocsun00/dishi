# 来源与过程记录 / Provenance and workflow records

[中文介绍](../README.md) · [English overview](../README.en.md) · [来源署名 / Source attribution](../THIRD_PARTY_NOTICES.md)

公开知识资料与开发过程记录分开保存。原典正文、固定修订的原始电子快照、API来源证据、提取区间、篇目映射、异文、古注、质量说明和有限对读仍随发布包提供。它们支持回查材料与处理过程，不能证明所有解释正确。

Public knowledge resources are separate from development transcripts. The release retains source passages, fixed-revision electronic snapshots, source API evidence, extraction ranges, chapter maps, variants, old notes, quality documents, and finite comparisons. These support traceability, not a guarantee of interpretation.

<a id="archived-records"></a>
## 本地归档的过程记录 / Locally archived workflow records

完整工具输出、AI代理会话、一次性作者脚本、自检和中间交接不作为用户知识库分发。包括历史验收覆盖JSON、覆盖缺口审计的机器记录，以及作者自检、构建报告、草稿冻结和中途交接记录。源项目保留这些材料；公开包和运行安装排除它们。

Full tool outputs, AI-agent conversations, one-off author scripts, self-checks, and intermediate handoffs are not distributed as knowledge resources. Historical acceptance-coverage JSON, the machine coverage-audit record, author self-checks/build reports, draft freezes, and handoffs remain in the local source project and are excluded from public and runtime packages.

规则由 `scripts/package_rules.py` 定义，发布清单逐项列出实际排除文件的名称、大小、原始摘要及原因。历史文档中指向归档记录的链接会在公开副本指向本节；原链接标签保留用于辨认历史记录，本节不冒充那些记录的全文。

The rules are defined in `scripts/package_rules.py`. The release manifest lists each excluded file's name, size, original hash, and reason. Public copies redirect historical links to this section, preserving their labels to identify the original records. This summary does not replace their full audit content.

## 摘要与复核边界 / Summaries and review scope

现库27种文献的范围与数量以目录和数据校验为准。历史“独立审查”“根代理复核”等措辞指同一AI工作流程中不同代理的交叉检查；不表示外部机构认证、人类专家逐字校勘或统计准确率。公开的质量说明保留当时的具体检查范围。

The catalog and data validation define the 27 included collections. Historical “independent review” or coordinator-review labels refer to cross-checks by different AI agents within one workflow, not external certification, expert line-by-line editing, or a statistical accuracy benchmark. Quality notes retain their historical scope.

来源JSON内少量历史采集角色标签属于采集元数据，保留原字节以维持固定快照与摘要关系。它们与已排除的整段工具会话分开处理。原始证据摘要仍描述本地原始文件；公开副本的实际摘要、链接改向及明确的路径处理见发布manifest。安装目录只包含运行资料，不包含仓库测试或发布脚本。

A few historical acquisition-role labels remain in source metadata to preserve evidence bytes and hash relationships. They are distinct from the excluded full conversations. Historical evidence hashes describe original local files; the release manifest records actual public-file hashes and declared transformations. Installed skills contain runtime resources rather than repository tests or release scripts.

本版的检查和限制见[验证范围](validation.md)。

See [validation scope](validation.md) for current checks and limits.

## v0.2.0 现代编辑修订 / Modern editorial revisions

本轮按复查意见修改 GGZ-Q10 的一个回答字段及其 Markdown、HTML 展示，并把《吕氏春秋》总览的一处现代规范称谓同步为军师守则。原典正文、引句、段号、问题和原始电子来源均未改。与完整原典集基线相比，1,337 文件一致，四个文件有意修改，具体路径及改前改后摘要见[验证记录](validation-results.json)。

This revision changes one modern answer field in GGZ-Q10 and its Markdown/HTML views, plus one modern norm label in the Lüshi Chunqiu overview. Classical passages, quoted words, IDs, questions and original electronic evidence are unchanged. Against the collection baseline, 1,337 files match and four are intentionally revised; see the [validation record](validation-results.json) for paths and before/after hashes.

历史鬼谷子验收覆盖记录中的 `data/examples.json` 摘要仍指修改前的文件，不能作为 v0.2.0 当前文件摘要。该历史记录保持原值；当前发布文件以新 manifest 的实际 SHA-256 为准。改动属于明示的现代编辑修订，不是静默修改原典或重写历史验收结果。

The historical Guiguzi acceptance-coverage hash for `data/examples.json` describes the file before the GGZ-Q10 revision, not its current v0.2.0 bytes. The historical record is preserved. Use the new release manifest for current public-file hashes; this is a declared modern editorial change, not a silent source-text alteration or a rewritten historical check.
