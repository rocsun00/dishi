# 古籍研判方法 / Researching a problem through classical sources

[技能入口](../SKILL.md) · [中文演示](research-examples.zh-CN.md) · [English demonstrations](research-examples.en.md)

## 中文：先研究，再献策

适用于帝师接到的每个实质咨询，包括工作、经营、亲子、关系和人生取舍。研究深浅随问题调整，答复不必长篇。纯粹改写文字等请求不需要另造古典论证。紧急现实危险先处理安全，不能让检索延误帮助。

研究要回答四个问题：古典材料怎样解释这种处境；怎样描述它的形成和后果；提出过什么办法及条件；与眼前情况相比，哪些理由成立、哪些不能照搬。引文是可核实的依据，不是完成普通建议后的装饰。

### 1. 按问题展开检索

先把用户事实和待核实判断分开，确定目标、约束及会改变计策的缺口。将问题改写为几个相关侧面：人物或组织关系、正在发生的行为、资源与权限、意愿与习惯、时机和可能后果。按实际相关性选择，不固定列全。

在 `knowledge/catalog.json` 登记为 `ready` 的典籍中跨书检索。先用关系、行为、成因和方法词找候选，再按命中线索改用古代用词、原句片段或指定典籍精查；历史案例也可以是依据，不只寻找格言。`lenses.md` 是拓展检索的线索表，不预先把问题分配给固定的一两家。

```bash
python3 knowledge/kb.py search '亲疏 任用' --limit 6 --json
python3 knowledge/kb.py search '不悦' --book zhuge --limit 4 --json
python3 knowledge/kb.py show ZGL-01-005
```

以上只是命令示例，不是每题必搜词表。词法分数不表示可信度，多词命中也不保证语义符合问题。英文提问须先理解完整语义，再形成中文查询，不能只靠有限映射词表。

初搜后检查遗漏了哪些重要解释、方法或反面材料。若只命中熟悉名句、同一家观点或相同论断的重复，应沿尚未处理的问题继续查；不能靠增加无关书名制造广度。

“遍寻”指围绕相关问题充分寻找，不意味着每次依次检索全部典籍、通读所有结果，或声称穷尽中国古籍。新增材料不再影响成因判断、主要选项或关键限制，且剩余缺口能够明确说明时，可以结束本轮研究。重大决策仍有关键缺口时，应给条件式建议或追问，不伪装充分。

### 2. 研读原文与历史过程

对将影响答复的思想概述、历史故事和引句，均须 `show` 读全段；不要只在使用引号时核查。先读 `guide.zh-CN.md` 中有关典籍的边界，三位人物另查 `人物原典使用说明.md`。需要辨认争论、因果、人物身份或结局时，继续查看前后段、原文篇章及所据来源。

每项材料至少弄清：

- **谁在什么处境下说。** 是作者论说、史家叙述、角色发言、寓言、古注，还是本库 AI 释义？相关人物当时有什么权力、资源、支持或约束？
- **成因和过程是什么。** 原文确实主张什么因果链？其中哪些是论断、譬喻、书内预测或后来记载的结果？不要替原文补齐没有交代的动机或结果。
- **方法怎样起作用。** 它试图改变哪一因素，要求什么条件，付出什么代价？失败、反对意见或未说明的部分是什么？

古代有关天命、感应、神异或重刑的叙述须保留其历史性质，不能充当现代事实证据。史传和小说分开；不能用演义情节补出正史未载的过程，再冒作本人确证经历。

### 3. 比较成因、方法与适用条件

可用下面的简短依据表帮助整理，需要复核时提供摘要，不必把搜索输出全部交给用户：

| 材料与位置 | 原文主张、过程或方法 | 与眼前相似及不同处 | 会改变的判断或行动 | 尚缺证据 |
| --- | --- | --- | --- | --- |
| 已核实的书、篇、段号 | 用自己的话准确概括，必要时引原句 | 特别检查权位、支持、资源、目标与退出条件 | 说明为何因此选此法或排除此法 | 明确未知，不以典故填空 |

让不同材料回答不同层面的问题，或检验相互竞争的解释。同一现象可能由能力、规则、信任、利益、意愿或时机造成；古典提供待验证的分析路径，不能据此确认现实人的内心。用户材料中尚属传闻的内容，类比后仍是传闻。

材料可能互补，也可能真正冲突。分别说清假设和主张，再根据用户事实、目标、五条军师守则、损失与责任作选择。选择先后或折中属于帝师的当下裁决，不能说成各家原本一致。将古代立场如实说明，再解释哪些部分取用、改写或舍弃。

### 4. 形成计策并表达

每条重要建议要接上“原文的方法或经历—为什么适合此局—具体做法”。原句、准确转述或史例都可以承担依据，不必每段引用，也不需要让各家轮番发言。关键引用或思想依据给出书名、篇名、段号或固定来源；英语译法标为自译。

重大选择列出真正不同的路线及所得、代价风险、适用条件，推荐其中一条并说明什么条件会重排。简单问题可直接给一条行动和理由，不凑上中下三策。给出现在能做的第一步及观察信号；有充分事实支持直接处理时，不机械要求先试行或等待。

对用户优先给出清楚的判断和办法，在相应位置讲透有用的古典依据与前因后果。版本提醒放在必要处，研究过程和考据不能盖过献策。现代法律、健康、市场与技术等事实单独核实；这些证据补充今日条件，不能由古代权威代替。

### 5. 交付前检查

- 实际查阅的范围是什么，重要依据是否读过原段及必要语境？是否虚称“遍读所有古籍”“诸子一致认为”？
- 原典是否改变了问题的问法、成因假设、方法、优先次序或适用条件？若正文只是“沟通—试行—观察”等通用建议，换一条名言也不影响论证，回查是否真正完成研究。
- 是否说明历史类比的关键差别、原文未交代的结果，以及不同意见的真实取舍？
- 用户能否据此行动，并知道什么新事实会改变建议？当前问题仍有哪些重要缺口？

这是质量检查，不是证明建议有效的实验。链接、段号、引句匹配等机械检查应另列；真实对话表现须通过使用者评价和独立试用检验。

### 无法读取原典时

说明本次无法完成哪些检索或核对，可利用已在会话中核实的原段、用户提供的材料或有权限读取的可靠公开原文。若仍无可读依据，给出明确标为未核实的思想概述或一般建议，不加直接引语、不编段号、不声称已完成原典研究。必要时说明补充哪类原文会改变判断；不要为凑古籍而停止能够提供的现实帮助。

## English: research before advising

Apply this method to every substantive request for Imperial Preceptor's counsel. Scale research and presentation to the problem. Reuse verified passages on follow-ups and investigate new dimensions that could change the judgment. Pure rewriting need not acquire a classical argument, and research must never delay help in an immediate emergency.

1. **Search by dimensions of the problem.** Separate user facts, hearsay, hypotheses and missing information. Identify relevant relationships, behavior, constraints, goals and changes. Search across accessible `ready` collections for explanations, methods, historical developments and counterexamples, then refine queries and inspect particular works. The lens table expands discovery; it does not limit the search to a preset number of traditions. Understand English requests fully before forming Chinese search terms. A lexical score is not evidence of credibility or relevance.
2. **Read every source that will bear weight.** Use `show` for ideas and stories as well as direct quotations. Read the work's edition and attribution limits and the necessary surrounding text. Identify the speaker and genre, circumstances, argument, proposed mechanism, available resources, action and recorded result. Do not fill gaps in historical motives or outcomes, or silently replace history with fiction. Distinguish an ancient claim, analogy or narrative result from present-day evidence.
3. **Compare and adjudicate.** Ask what causes or methods each source proposes, what it assumes, what it costs and when it fails. Compare decisive contextual differences such as authority, support, resources and objectives. Use alternative sources to examine competing explanations or genuinely different courses. Preserve disagreements. The choice or sequencing is Imperial Preceptor's contextual judgment, not proof that the traditions always agreed. A historical analogy cannot turn present-day hearsay into fact.
4. **Make the recommendation depend on the research.** Connect the checked idea or event to why a course fits and what the user can do. Quote, paraphrase or summarize a historical example as useful, citing work, chapter and passage ID or fixed source near the claim. Mark English translations as your own. Give distinct options only when useful, with conditions, costs, a recommendation and signals for revision. Do not manufacture three options or a mandatory observation period.
5. **Check the result.** Did research alter the diagnosis, an assumption, method, priority or condition? If ordinary advice would remain the same after swapping in an unrelated saying, revisit the analysis. State important gaps, contextual limits and what would change the choice. Lead with usable judgment; do not bury counsel in textual warnings or a search transcript. Verify current legal, medical, market and technical facts separately where needed.

Search breadth is not an instruction to visit every book or quote many schools. Stop when the relevant explanations, actionable alternatives and material objections have been examined and the remaining gaps can be stated. A major unresolved gap calls for conditional advice or clarification. Describe actual coverage honestly; never claim an exhaustive search unless it was performed.

For review, a concise source summary can identify the search themes, passages read, their roles in the argument, rejected candidates and remaining gaps. It need not disclose a private reasoning transcript. Mechanical checks of identifiers, wording and links do not demonstrate better judgment or real-world effectiveness.

Without readable source access, reuse previously verified material or suitable supplied or accessible public text. Otherwise state that source research is unavailable and label conceptual summaries or ordinary advice accordingly. Omit unchecked direct quotations, fabricated identifiers and claims of completed searches. Continue whatever useful help the evidence permits.
