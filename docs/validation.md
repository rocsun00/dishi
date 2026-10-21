# 验证范围 / Validation scope

[中文介绍](../README.md) · [English overview](../README.en.md) · [机器记录 / Machine record](validation-results.json)

## 当前阶段：F1 修复的打包前检查 / Current stage: pre-package checks after F1

本段记录研判机制版的**打包前源码检查**；最终 ZIP、manifest、目录和临时安装验收在包旁的 `交付检查.json` 与 `SHA256SUMS.txt` 中另记。此处不写最终 ZIP 摘要，避免生成包后再改包内记录。版本仍为未发布的 0.2.0；打包安排为完整归档介绍词版发布目录后生成同版本新包，真实已安装的 0.1.1 技能不替换，不上传。

This section records **pre-package source checks** for the research-method revision after F1. Final ZIP, manifest, directory and temporary-installation verification is recorded beside the package in `交付检查.json` and `SHA256SUMS.txt`, outside the archive. No final ZIP hash is embedded here. The unpublished version remains 0.2.0; the complete introduction-revision release is archived before a same-version replacement is built. The real installed 0.1.1 skill is not replaced, and nothing is uploaded.

- **F1 已修复。** 英文可复制提示词从 8,915 压至 **7,291 字符**，五条军师守则逐字保留；中文提示词正文仍为 **2,317 字符**且逐字未变。两文档都补充入口和长度限制说明：完整提示词优先作为首条消息，指令字段仅在可用且容量足够时使用；知识文件提供参考材料，不使其中的提示词自动生效。
- **7,500 是项目维护预算，不是官方通用上限。** 没有声称所有 ChatGPT 或其他应用入口都能保存完整提示词。入口限制参考[官方自定义指令说明](https://help.openai.com/en/articles/8096356-chatgpt-custom-instructions)，指令与知识文件的区别参考[官方 GPT 配置说明](https://help.openai.com/en/articles/8554397-creating-and-editing-gpts)；本轮没有实际登录这些应用粘贴测试。
- Python 3.14.3 和 3.9.6 **各通过 121 项**：85 项知识库、24 项安装发布、12 项参谋契约测试。两版本原典校验均有效。新增测试检查唯一完整提示词块、非空与字符预算；临时副本中恢复原 8,915 字符英文提示词，会触发预期预算断言失败，当前提示词通过。
- 与 F1 修复前源码快照相比，仅两份提示词文档、参谋契约测试及两份验证记录改变；`knowledge/` 下 **1,374 个非缓存文件全部不变**。SKILL、研究方法、研究示例、检索及排序实现不变。独立代码审查与 Python 增量审查通过；本轮未重做对话质量试用，上一阶段试答记录保留其原范围。
- Claude 的用户转交报告认可源码机制与示例，提出 F1；该报告中的两道试答和缺陷探针属于其自述复查结果，不冒称本轮由 Codex 重新执行。O1 上下文 CLI、短答示例、英文映射噪声及此前暂缓事项，本轮未扩展。

F1 is resolved: the English copyable prompt is **7,291 characters**, down from 8,915, with all five adviser rules preserved verbatim. The Chinese prompt body remains **2,317 characters**, byte-identical to its baseline. Both documents explain entry-specific limits and reference-only knowledge uploads. **7,500 is a project maintenance budget, not an official universal field limit.** Both Python versions pass **121 tests each** (85 corpus, 24 distribution, 12 adviser contracts), and corpus validation passes. The new regression rejects the original oversized English prompt and accepts the current prompts. Only the two prompt documents, the adviser test file and the two validation records change relative to the pre-F1 source snapshot; all **1,374 knowledge files** and the research mechanism remain unchanged. Code and Python reviews approve the change. No new advice-quality trial, real chat-app paste test or optional feature work is claimed. The user-supplied Claude review retains its own reported scope.

## 上一阶段源码工作稿检查（历史） / Previous research working-copy checks (historical)

本轮修改源码的工作机制：每个实质咨询先按问题广搜可访问原典，核对思想、史例和引句的语境，比较成因、前后果、方法条件与代价，再形成判断和行动。不预选固定数量的学派，也不以先写通用建议、后附名言完成任务。详见[研判方法](../references/research-method.md)及[中文](../references/research-examples.zh-CN.md)、[英文](../references/research-examples.en.md)演示。技能入口、详细指南、视角说明、双语 README 与聊天提示词及 UI 元数据已同步。

This working source revision researches accessible classical texts before substantive advice, checks contextual ideas, historical examples and quotations, compares causes, developments, conditions and costs, and then forms a judgment and action. It neither preselects a fixed number of traditions nor drafts ordinary advice and adds sayings afterward. The entrypoint, guides, bilingual overview and portable prompts, and UI metadata are aligned; see the method and examples linked above.

**当前只是源码工作稿。** `VERSION` 仍为 0.2.0；现有介绍词版发布目录、ZIP 和已安装的 0.1.1 技能均未替换，没有上传。以下介绍词修订及更早记录属于历史范围，不能拿其中的旧文件摘要、119 项测试或“逐字节一致”描述本轮源码。

**This is a source working revision only.** `VERSION` remains 0.2.0. The introduction-revision release directory and ZIP, and the installed 0.1.1 skill, are unchanged; nothing is uploaded. The introduction and earlier records below are historical. Their old hashes, 119-test counts and byte-identity statements do not describe this working source.

### 本轮检查 / Checks for this working revision

- Python 3.14.3 和 3.9.6 **各通过 120 项**：85 项知识库测试、24 项安装发布测试、11 项参谋契约测试；两版本原典校验有效。新机制文件及双语研究例属于安装必需项，真实临时安装和缺文件拒装、旧版保全均已检查。
- 新示例每种语言 **12 处**来源表原句进入逐字匹配，旧四例每种语言仍为 8 处。段号存在检查和本地 Markdown 文件链接检查现覆盖新示例与 references。链接检查不验证锚点、外链或渲染。
- 完整临时副本中，分别向中文、英文研究例的原句插入错字，各触发 1 次预期断言失败、0 次加载错误；未改副本通过。源码没有被注入缺陷。
- 官方技能验证器通过。PyYAML 6.0.3 仅放在临时维护目录用于校验，不成为帝师运行依赖。
- 对本轮修改前快照核对，`knowledge/` 下 **1,374 个非缓存文件全部不变**，包含原文、释义、索引、检索及排序实现与测试。发布目录和真实技能目录与修改前快照一致。
- 独立代码审查和 Python 增量审查通过；曾发现新例引句未被格式化校验覆盖，已补非零断言、原句标记和实际错字探针关闭该缺口。

Both Python versions pass **120 tests each** (85 corpus, 24 distribution, 11 adviser contracts), and corpus validation passes. New research references are required runtime resources; real temporary installation, rejection of incomplete inputs and preservation of the previous install are checked. Each new language example has **12 checked source quotations**, alongside eight per language in the earlier cases. Identifier and relative-file-link checks cover the new references; anchors, external links and rendering are outside that check. Separate temporary-copy typo probes each produce one expected assertion failure and no loading error, while the unmodified copy passes. The official skill validator passes using temporary maintainer-only PyYAML. All **1,374 non-cache knowledge files**, the existing release and the real installed skill match the pre-revision snapshot. Independent code and Python reviews approve the final change; the initially missing quotation-check coverage is resolved.

### 对话试用与限度 / Conversation trial and limits

两份新研究示例是实际检索后编写的编辑演示：执行20组不同查询，读过33个不同原段，公开相关材料、排除理由与裁决。它们不是宿主实测、当事人调查或成效实验。

另以未用于示例的合伙工作室问题，做了 **1 次独立 AI 试答**：实际执行9次检索、读11段，答复采用4段。复核可见，《韩非子》参与分析单方承诺、追加投入与异议标签，《荀子》影响是否保留互补分工，反面材料又影响授权例外。引句与语境已复核。这是本次输出出现研究行为的证据，**不证明比旧版更好，也不证明现实有效**。试答及依据记录另存本地交付目录，没有修改技能或替用户采取行动。

The two new examples are editorial demonstrations based on 20 distinct executed queries and 33 distinct passages read, not live-host or outcome studies. One independent AI trial used a separate partnership scenario, executed nine searches, read 11 passages and used four in the answer. Review found that the checked sources affected the causal analysis, choice between complementary roles and separation, and exceptions to rigid boundaries. This establishes visible behavior in **one output**, not superiority to the previous version or real-world effectiveness. Its answer and evidence are retained with the local handoff records. No model fine-tuning, live chat-app comparison or Windows/Linux native-host testing is claimed.

## 以下为介绍词修订及更早历史 / Historical introduction revision and earlier records

本页记录 **v0.2.0 介绍词修订的打包前源码检查**。作者已授权把介绍词并入未发布的 v0.2.0；第三轮待发布包完整归档后，生成同版本的新本地发布包。现有 v0.1.1 产物及已安装技能不覆盖，也不上传。最终 manifest、ZIP 摘要和临时安装回查在交付目录另存，避免把 ZIP 自身摘要写入 ZIP 内形成循环。

This page records **pre-package source checks for the v0.2.0 introduction revision**. The author approved merging the copy into the unpublished v0.2.0 release. The complete round 3 pending package is archived before a same-version local replacement is built. Existing v0.1.1 artifacts and installed skills remain unchanged; nothing is uploaded. Final manifest, ZIP and temporary-installation checks are delivered separately alongside the artifact, avoiding self-referential archive hashes.

## 本轮结果 / Current results

Python **3.14.3 和 3.9.6 各通过 119 项测试**：85 项知识库、英文映射与排序，24 项既有安装与发布，以及 10 项参谋版契约测试。两个版本的 `knowledge/kb.py validate` 均有效。本轮没有修改代码或测试，也没有新增测试函数；结果是对既有套件的重新运行，不是建议质量实验。

Python **3.14.3 and 3.9.6 each passed 119 tests**: 85 corpus, English-mapping and ranking tests, 24 existing distribution tests, and 10 adviser contract tests. Corpus validation passed on both versions. No code, tests or test functions changed in this revision. These are fresh runs of the existing suites, not an advice-quality experiment.

本轮只修改中英文 README 的标语及开头、发布准备文档的仓库简介及发布说明首句，以及两份验证记录。README 后续内容逐字节保留。相对作者草案的三类措辞澄清均已披露：历史概述明确横跨春秋战国，英文标语与中文“两千多年前”对齐；能力描述限于已整理、选收的文本；范蠡等人物使用“所著或相关文献”，不暗示范蠡材料是本人著作全集。没有新增古文引句。

Only the bilingual README taglines and openings, the GitHub About and first release-description sentence, and the two validation records changed. Downstream README sections remain byte-identical. Three disclosed clarifications to the author draft identify the Spring and Autumn and Warring States span and align both taglines with “more than two millennia”; limit capability wording to selected source texts; and distinguish texts by or about historical figures rather than implying an authored Fan Li oeuvre. No classical quotation was added.

独立 AI 文案复核已通过，范围仅为两份 README 和发布准备文档的双语含义及最小改动，不是新一轮 Python 代码审查或真实宿主试用。两份验证记录另作打包前一致性检查；最终产物结果在包旁交付。具体文案摘要及报告摘要见机器记录。

Independent AI copy review approved the two README files and release-preparation copy, covering bilingual meaning and exact permitted changes. It is not a new Python review or real-host trial. The two validation records receive a separate pre-package consistency check; final artifact evidence is delivered alongside the package. Reviewed copy hashes and the report hash appear in the machine record.

本地相对链接测试只验证目标文件存在，不验证锚点、外链或完整渲染。四个双语案例每种语言仍有 8 处引文，合计 8 条不同引句；案例、引文、SKILL 和提示词均与第三轮逐字节一致。逐字匹配不证明解释、历史真实性或现代建议有效。PyYAML 仅用于维护验证，运行仍只需 Python 标准库；本轮没有重新声称官方技能验证器或完整 YAML 检查的历史结果为新测。

Local link tests establish file existence, not anchors, external availability or rendering. Four bilingual cases retain eight quotations per language and eight distinct quoted passages. Cases, quotations, SKILL and prompts remain byte-identical to round 3. Exact matching does not prove interpretation, historical truth or modern effectiveness. PyYAML remains a maintainer-only dependency; runtime is standard-library-only. Earlier official skill-validator and full-YAML checks are not represented as fresh results.

## 第二轮原典修订保留 / Preserved round2 editorial revisions

本次介绍词修订未修改 knowledge 下任何内容。与归档的完整原典集基线比较，**1,341 文件中 1,337 个完全一致，恰好四个按任务有意修改**：

This introduction revision changes nothing under knowledge. Against the archived full collection baseline, **1,337 of 1,341 files match exactly; precisely four are intentionally revised**:

- `knowledge/guiguzi/data/examples.json`
- `knowledge/guiguzi/问答示例.md`
- `knowledge/guiguzi/阅览.html`
- `knowledge/lvshichunqiu/知识库总览.md`

GGZ-Q10 只改 `answer` 的一处现代规范表述，问题、段号和引句不变。第二轮实际执行 `build --book guiguzi` 后仅上述三个鬼谷子文件改变，其余 46 个文件字节一致，无须回退或手工修补。吕氏春秋总览只作指定的四字替换。原典正文、释义、思想卡和原始来源证据未改；检索代码、词表、既有排序测试也未改。

Only one modern norm phrase in GGZ-Q10's `answer` changed; its question, passage IDs and quotations are unchanged. The round2 Guiguzi build changed only the three listed Guiguzi files; its other 46 files match byte for byte, requiring no rollback or manual repair. The Lüshi Chunqiu overview has only the requested four-character replacement. Classical passages, readings, concept cards, original electronic evidence, retrieval code, vocabulary and existing ranking tests are unchanged.

鬼谷子历史验收覆盖记录中的 `examples.json` 摘要仍描述改前文件，不能作为当前 v0.2.0 文件摘要；历史记录保持不改。机器记录列有四个文件的改前、改后摘要及历史摘要出现的记录名称。当前公开文件以新 manifest 的实际摘要为准，详见[来源与过程记录](provenance-summary.md)。

Historical acceptance-coverage hashes for Guiguzi's `examples.json` describe its pre-revision bytes, not v0.2.0. Those records remain unmodified. The machine record lists all four before/after hashes and the historical records containing the previous QA hash. The new manifest identifies current public-file hashes; see [provenance notes](provenance-summary.md).

## 案例历史、复核及边界 / Case history, review and limits

案例 2 第二轮插入条件重排小节，第三轮仅修订 R1、R2 两条情形：中英文各仅第 84、86 行改变，逐字符合第三轮任务书且保留半角引号。全职升为首选须事先写好退出条件；储备或照护压力下，中策的换工作部分因收入空档风险暂缓，仍可在现单位协商。数字仍是假设阈值，A/B/C 与上中下对应。小节其他行、其他案例及全部引文均未改。

Round 2 inserted the case 2 re-ranking section. Round 3 revised only R1 and R2, exactly lines 84 and 86 in each language, matching the third-round brief and retaining straight quotes. Full-time work requires written exit conditions; when reserves or care responsibilities constrain choices, the job-change part of option B is deferred because of income-gap risk, while internal negotiation remains possible. Thresholds remain illustrative. All other lines, cases and quotations are unchanged.

27 种 ready 文献、6,640 段原文与对应释义、2,226 张思想卡、871 组问答、3,645 次库内引文匹配的规模未变。AI 交叉复核指同一流程中不同代理的检查，不是人类专家逐字校勘、外部认证或客户成效证明；具体范围见机器记录与交付证据。

The corpus remains at 27 ready collections, 6,640 passages and readings, 2,226 concept cards, 871 QA entries and 3,645 corpus quote matches. AI cross-review means different agents within one workflow, not expert line-by-line editing, external certification or customer outcomes; scope is stated in the machine record and delivery evidence.

机器记录中的第一轮参谋版 117 项测试、第二轮和第三轮结果、此前 0.1.1 的 109 项检查及[英文试用摘要](english-trial.json)均保留明确历史范围，不冒称本版新试用。没有做安装前后效果对比、真实应用对话基准、Windows/Linux 原生宿主测试或法律许可审查。第二轮明确暂缓的 L2、L4 与“三仪”说明未改。

The round 1 adviser 117-test record, round 2 and round 3 results, earlier 0.1.1 109-test checks and [English use summaries](english-trial.json) retain their historical scope. No effect comparison, new real-app conversation benchmark, native Windows/Linux host test or legal clearance is claimed. Deferred L2, L4 and 三仪 issues are unchanged.

## 第三轮缺陷注入与第二轮归档（历史） / Round 3 probes and round 2 archive (historical)

第三轮曾在完整临时源码副本内，分别删去中文退出条件、第三条中策说明、英文 exit conditions、第三条 option B，以及向鬼谷子阅览 HTML 注入旧规范表述；两个 Python 版本各五次均触发预期断言失败，无测试错误。副本已清理，源码探针前后摘要一致。独立 AI 复核另行检查测试与最小差异，均明确为机械检查，不是建议质量实验。

In round 3, five defects were injected into a full temporary source copy: missing Chinese exit conditions, missing third-scenario Chinese option B wording, their two English counterparts, and an obsolete norm inserted into Guiguzi's HTML view. Each produced the intended assertion failure on both Python versions, without test errors. The copy was removed and source hashes were unchanged. Independent AI reviews inspect the tests and minimal changes; these are mechanical checks, not advice-quality experiments.

第二轮待发布目录整体移到本地归档，所有 1,384 个文件摘要一致；第二轮 ZIP 的 SHA-256 为 `639116cc5af4aaabd6da67322e2588959d9a2c0b6b16136269d3a3b1ee662d5d`。新包仍为未发布的 0.2.0，最终清单、ZIP 和临时安装回查在新包旁另存。引号统一 O2 本轮未做，其他暂缓项也未扩展。

The complete round 2 pending directory was moved to the local archive, preserving all 1,384 file hashes. Its ZIP SHA-256 is recorded above. The replacement remains unpublished version 0.2.0; final manifest, ZIP and temporary-install evidence is delivered alongside it. Quote-style normalization O2 and other deferred work remain out of scope.

## 本轮归档 / Current archive

本轮把第三轮待发布目录完整归档，1,384 个文件的摘要全部一致；其中旧 ZIP 的 SHA-256 为 `6045d3b7a8c8fbfe24d5211ea03cb2ca607d143348e52ff60c3e5e906aed54e5`。这不是本轮新包的摘要。新包仍为未发布的 0.2.0，最终清单、ZIP 和临时安装回查在新包旁另存。

This revision archives the complete round 3 pending directory with all 1,384 file hashes preserved. Its old ZIP SHA-256 is recorded above and does not identify the new introduction-revision package. The replacement remains unpublished version 0.2.0; final manifest, ZIP and temporary-installation evidence is delivered separately alongside it.

## 可复核命令 / Reproduce the checks

在源仓库或清洁发布目录运行；已安装运行包不包含开发测试。

Run from the source or clean release directory; installed runtime resources omit development tests.

```bash
python3 -B knowledge/kb.py validate
python3 -B -m unittest discover -s knowledge/tests -v
python3 -B -m unittest discover -s tests -v
```

如有 Python 3.9，使用对应解释器重复以上命令。测试不需要付费模型 API 或网络。

Repeat with a Python 3.9 interpreter when available. Tests need no paid model API or network.
