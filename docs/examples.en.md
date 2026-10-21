# Using Dishi: four examples

[中文](examples.zh-CN.md) · [Back to the README](../README.en.md) · [Corpus and language notes](corpus.md)

These four scenarios are **hypothetical demonstrations, not customer success stories**. The sample responses illustrate a way to ask questions and make judgments; they do not promise a particular host model's output or real-world results. The Chinese and English versions cover the same cases. English renderings of the quotations are original translations for this project, not translations supplied by the cited electronic editions.

Each case presents a situation, a reusable prompt, and a judgment, three strategies, recommendation, candid objection, first step, and sources. A / B / C correspond to 上 / 中 / 下: different tradeoffs, not a fixed ranking from good to bad. Each option depends on its stated conditions. Recommendations depend on the facts stipulated in the scenario. The classics offer perspectives, not proof that the advice will work. Quotations retain the Chinese base text's characters. Passage IDs are project references, not universal numbering across editions.

<a id="case-1"></a>
## 1. Team delivery: change the system or replace people?

**Hypothetical demonstration, not a customer success story.**

**Hypothetical situation.** A team of six has missed two deadlines. Its leader thinks the members have “poor execution” and wants to replace people. A review finds that acceptance criteria changed twice during delivery, purchasing needed the leader's approval, and a member's warning about data quality went unanswered. There is not yet enough evidence to establish a lack of ability or deliberate failure to honor commitments.

**A prompt to reuse**

> Use $dishi to help me think through this team problem. We are a team of six and have missed two deadlines. Acceptance criteria changed during delivery, purchasing waited on my approval, and someone raised a data risk. I want to replace people. Separate what we know from what we do not know, check whether I am blaming people for problems in the system, and give a main recommendation, its strongest objection, and a first step we can examine within two weeks. If you quote a classical text, give its passage ID and full context.

**Judgment**

Correct the task and authority problems already established, while checking individual capability. The facts do not yet support replacing people as the solution; skills and access to resources still need investigation. Record your own changes to requirements and approval delays in the same log.

**Three strategies: A / B / C (上 / 中 / 下)**

- **A — Trial one small deliverable.** Agree on acceptance criteria, an owner, resources, decision authority, and response times for decisions outside that authority; try this for two weeks. The gain is evidence separating process blockers from skill gaps. The cost is changing your own management first, and genuine skill gaps may still consume time. This fits a situation with no established serious misconduct and room for a limited trial.
- **B — Protect the critical delivery through temporary reassignment.** If delivery cannot wait, give critical tasks to people with demonstrated capability, support the other members, and set a review date. The gain is lower short-term delivery risk. Costs include pressure on experienced staff and coordination; reassignment may also hide the original bottleneck. Use this when there is real time pressure and evidence of capability, rather than labels based on the leader's impressions.
- **C — Change staffing when the evidence supports it.** After stabilizing criteria, providing resources, and hearing the person's explanation, compare training, a different role, and replacement if an essential skill gap still prevents meeting role requirements. This addresses an established mismatch, at the cost of transition, lost knowledge, and replacement effort; process problems may remain. It fits sufficient evidence. Clear harm or serious misconduct calls for timely action without mechanically waiting two weeks.

**Recommendation**

Start with A on the facts given, recording the support individuals need during the trial. It tests both your management arrangements and their conditions for delivering. Two weeks supplies limited evidence, not proof of improvement across the whole team.

**Candid objection**

You may be the first person who needs to change. If requirements keep changing and approvals keep waiting, a responsibility chart cannot test capability fairly. Conversely, “the system is flawed” must not become a permanent excuse for avoiding real skill gaps.

**First step**

Today, choose one small deliverable with the team and agree on acceptance criteria, ownership, authority, resources, and a blocker log. Delays that track approval bottlenecks or requirement changes support changes in management. Repeated need for help beyond the reasonable demands of a role under stable conditions strengthens the case for changing roles or people.

**Sources: original context and limits of application**
| Quotation and reference | Original context and the limits of modern use |
| --- | --- |
| *Han Feizi*, “Defining Standards”: **“循名而責實”**. `book=hanfeizi`, [`HF-43-002`](../knowledge/hanfeizi/原文.md#hf-43-002), [fixed source, oldid=2327670](https://zh.wikisource.org/w/index.php?title=韓非子/定法&oldid=2327670). | The complete passage distinguishes the ruler's administrative techniques from publicly established rules. It explicitly includes the power over life and death, “操殺生之柄.” This is a context of monarchical control over ministers. Here it prompts a question about whether assigned roles match actual performance. Transparent authority, support, and a chance to respond are modern choices made for this case. |
| Zhuge Liang's memorial, commonly called the *First Memorial on Dispatching the Army*, embedded in Chen Shou's *Records of the Three Kingdoms*: **“陟罰臧否，不宜異同。”** `book=zhuge`, [`ZGL-05-003`](../knowledge/zhuge/原文.md#zgl-05-003), [fixed source, oldid=2115776](https://zh.wikisource.org/w/index.php?title=%E4%B8%89%E5%9C%8B%E5%BF%97%2F%E5%8D%B735&oldid=2115776). | The passage opposes favoritism and different standards inside the palace and the administration. Here it asks whether the leader is subject to the same rules. Ancient punishments and rewards are not a modern team policy; the passage cannot justify harsh punishment or absolute obedience. |

**Original English translations for this project**

- “循名而責實”: *Assess actual performance against the assigned role.*
- “陟罰臧否，不宜異同。”: *Advancement, penalties, and judgments of conduct should not follow different standards.*

The two sources emphasize a ruler's assessment and the avoidance of favoritism respectively. This does not turn them into a single modern theory of governance. Staffing choices still require evidence about skills, conduct, available support, and costs.

<a id="case-2"></a>
## 2. A stable job or a venture: how big a step now?

**Hypothetical demonstration, not a customer success story.**

**Hypothetical situation.** Someone with a stable job wants to build a product of their own and values autonomy most. They have no paying customers. Household reserves cover six months of essential spending, and six hours a week are available for a trial. Household expenses and care responsibilities cannot simply stop. Demand has not been established.

**A prompt to reuse**

> Use $dishi to help me compare keeping a stable job with starting a venture. I want autonomy, have no paying customers, have household reserves for six months of essentials, and can spend six hours a week on a trial. I also have care responsibilities. Do not assume entrepreneurship is braver or stability is better. Give a conditional recommendation, its main cost, the strongest objection, and the evidence that would change your judgment.

**Judgment**

Given these conditions, keep the job for now and use a limited trial to learn about demand. Six months of reserves describes a capacity to absorb losses, not a six-month window for success. Also distinguish dissatisfaction with this particular job from a long-term wish to leave employment: that changes the options.

**Three strategies: A / B / C (上 / 中 / 下)**

- **A — Validate demand alongside the job.** Use the available six hours a week for a four-week minimal demonstration and conversations with real prospective users, checking what they would give up or pay. The gain is learning while retaining income. Costs include slower progress and less rest; a small sample can mislead. This fits the stated conditions, after checking work commitments and conflicts of interest and agreeing on the time and resources with affected household members.
- **B — Change the form of employment first.** If autonomy is the central concern, investigate a different role, a different job, or negotiated working arrangements before choosing a venture. This may directly improve autonomy, at the cost of searching or negotiation and with no guarantee of satisfaction. It fits dissatisfaction rooted mainly in the current role. Availability must be investigated; an employer's agreement cannot be assumed.
- **C — Move full time when the conditions justify it.** Compare full-time commitment once there is verified willingness to pay, credible delivery capability, workable household arrangements, and a clear exit route. The gain is concentrated time. The costs are income and reserve exposure, and faster work can accelerate mistakes. It fits those conditions plus an evidenced time window; the current facts do not establish them.

**Recommendation**

Start with A and investigate whether B would meet the main need for autonomy. Set conditions for continuing, changing direction, and stopping before starting. Those conditions follow from your responsibilities and values; a quotation cannot specify a universal spending limit.

**When conditions change, the ranking changes**

This ranking holds only under the assumptions of this case. The figures below are illustrative thresholds, not recommendations; set your own according to your responsibilities and what you can afford to lose.

- **If verifiable paying commitments arrive within four weeks** (for example, three users sign written orders or pay in advance), you can deliver on time, your family agrees to adjusted arrangements, and you have written down exit conditions in advance (for example, the reserve level or the number of months with insufficient income that would send you back to a job search or part-time work), then the former option C, going full-time, becomes the first choice. Validating while employed drops to a fallback for checking whether demand repeats. The main reason against going full-time, unproven demand, has been overturned by new evidence. The exit conditions supply the exit path that option C already required; until they are written down, going full-time is still premature.
- **If the trial shows that the autonomy you want is mainly about escaping your current manager or role**, rather than building this product, then option B, changing the form of your work, becomes the first choice and the venture trial becomes secondary.
- **If household reserves fall below three months, or caregiving responsibilities grow substantially**, going full-time leaves the table for now. The part of option B that involves changing jobs is also deferred, because a job search or probation period could create an income gap you cannot absorb now. Two courses remain: reduce the commitment and keep validating while employed, or pause the venture trial and only negotiate duties or hours with your current employer, without risking income. There is no need to force a third option.

Each re-ranking should name the evidence or condition that changed, not a shift in mood or someone else's encouragement.

**Candid objection**

A part-time trial could miss a real opportunity, or turn into permanent preparation. Examine the time window seriously, but enthusiasm, praise, and being busier cannot replace evidence of demand. If the real aim is leaving this particular job, entrepreneurship may be an expensive answer to a different problem.

**First step**

Write a one-page trial agreement: the demand to investigate, how to use six hours each week, affordable costs, household arrangements, evidence to record, and a review after four weeks. Adjust or stop if users show no clear need or the trial displaces responsibilities that cannot be interrupted. Stronger evidence supports comparing a larger trial with full-time commitment. Four weeks still cannot establish long-term viability.

**Sources: original context and limits of application**
| Quotation and reference | Original context and the limits of modern use |
| --- | --- |
| *The Art of War*, “Planning an Attack”: **“知可以戰與不可以戰者勝”**. `book=sunzi`, [`SZ-03-007`](../knowledge/sunzi/原文.md#sz-03-007), [fixed source, oldid=7906064](https://zh.wikisource.org/w/index.php?title=孫子兵法&oldid=7906064#謀攻第三). | The complete passage lists five conditions for understanding victory, involving military conditions, the use of forces, aligned aims, preparation, and command authority. Here it prompts a question about whether conditions for action exist. A venture is not a war, customers are not enemies, and this sentence supplies no probability of business success. |
| *Laozi*, chapter 44, Chinese main text of the Wang Bi edition: **“知足不辱，知止不殆，可以長久。”** `book=laozi`, [`LZ-44-001`](../knowledge/laozi/原文.md#lz-44-001), [fixed source, oldid=2354026](https://zh.wikisource.org/w/index.php?title=道德經%20%28王弼本%29&oldid=2354026). | The chapter compares reputation, the person, possessions, gain, and loss, warning against excessive attachment and urging a sense of limits. Here it asks which costs the person is unwilling to bear. Contentment does not mean everyone must accept the status quo, and suffering loss does not prove that someone failed to be content. |

**Original English translations for this project**

- “知可以戰與不可以戰者勝”: *Those who know when they can fight and when they cannot are the ones who prevail.*
- “知足不辱，知止不殆，可以長久。”: *Knowing what is enough avoids disgrace; knowing where to stop avoids danger. In this way one can endure.*

Sunzi's concern with victory and the *Laozi*'s limits on reputation and possessions do not prescribe the same goal in life. This case keeps that tension visible. The person chooses according to their priorities among autonomy, responsibilities, and losses; the quotations do not vote on the outcome.

<a id="case-3"></a>
## 3. Cross-cultural cooperation: disagreement and boundaries

**Hypothetical demonstration, not a customer success story.**

**Hypothetical situation.** Two small organizations from different countries are planning an exhibition. One says a date is “worth considering”; the other treats that as agreement and makes an external commitment. Written feedback then feels harsh, and some participants stop speaking. There is no evidence that nationality or a fixed cultural character explains these behaviors.

**A prompt to reuse**

> Use $dishi to help me handle a disagreement in a partnership. They said a date was “worth considering”; we treated it as agreement and promised it to others. Written criticism now feels humiliating, and some people no longer speak. Consider both parties and affected third parties without guessing motives from nationality. How can we confirm commitments, allow disagreement, and define unacceptable behavior?

**Judgment**

Repair the chain of commitments first, then decide the scale of cooperation. Misunderstanding about the date and difficulty speaking up are established; nationality, a fixed cultural character, and deliberate obstruction are not. “Cultural difference” cannot require someone to honor a commitment they never made.

**Three strategies: A / B / C (上 / 中 / 下)**

- **A — Confirm again and continue the full partnership.** Have authorized people on both sides confirm the date, explain the uncertainty to affected people, and distinguish discussion, proposals, and confirmed decisions in language both sides understand. The gain is preserving the project and relationship. Costs include repair time and communication work, with a risk of recurrence. This fits willingness on both sides to correct misunderstanding and share repair costs.
- **B — Reduce the scope and try one part.** Limit joint commitments to a part both sides explicitly accept, give each side responsibility for other work, and set a joint review point. The gain is less dependence and a chance to test cooperation. Costs include reduced project scope, lost coordination benefits, and extra interfaces. This fits continuing value without restored trust; it does not justify unilaterally reducing confirmed commitments.
- **C — Exit in an orderly way.** If clarification and repair are followed by repeated humiliation, pressure to cross declared boundaries, unauthorized commitments, or refusal to address their effects, negotiate an end and meet responsibilities to third parties. The gain is ending repeated violations. Costs include sunk effort, handover, and reputational risk. This fits persistently breached boundaries; threatening exit must not be used to impose conditions never agreed.

**Recommendation**

Try A first. Require formal confirmation for decisions affecting costs, dates, or third parties while keeping routine discussion light. Feedback should identify specific work or behavior, its impact, and the requested change. Include time zones, language proficiency, and who bears extra communication work in the arrangements.

**Candid objection**

Your side turned “worth considering” into an external promise; that may be the responsibility most urgently requiring repair. More forms cannot solve refusal to respect boundaries. Preserving the partnership must not leave every repair cost with the people who have stopped speaking.

**First step**

Jointly review the latest date commitment: who proposed it, who could confirm it, whether there was explicit agreement, and who has relied on it. Record agreed, pending, and rejected items and unacceptable behavior, and identify who will correct external expectations. At the next meeting, observe whether both sides correct misunderstandings, express disagreement, and share repair costs. Repeated violations or refusal to correct them supports a smaller partnership or exit.

**Sources: original context and limits of application**
| Quotation and reference | Original context and the limits of modern use |
| --- | --- |
| *Analects*, “Zilu”: **“君子和而不同，小人同而不和。”** `book=lunyu`, [`LY-13-023`](../knowledge/lunyu/原文.md#ly-13-023), [fixed source, oldid=11118102](https://zh.wikisource.org/w/index.php?title=論語/子路第十三&oldid=11118102#十三之二三). | The recorded saying of Confucius contrasts harmony and sameness through the exemplary and petty person, in a context of ethical cultivation. Here it distinguishes cooperation from agreement. It is not a label for calling either partner “petty,” nor does it mean all conflicts should remain unresolved. |
| *Mozi*, “Inclusive Care, Part II”: **“視人之國若視其國，視人之家若視其家，視人之身若視其身。”** `book=mozi`, [`MZ-15-002`](../knowledge/mozi/原文.md#mz-15-002), [fixed source, oldid=2200469](https://zh.wikisource.org/w/index.php?title=墨子/兼愛中&oldid=2200469). | The complete passage advocates inclusive mutual care and mutual benefit, expecting this to restrain warfare, appropriation, and the strong overpowering the weak. Here it brings costs borne by the other party and third parties into the decision. It is a normative ideal, not proof that goodwill automatically removes power or conflicting interests. |

**Original English translations for this project**

- “君子和而不同，小人同而不和。”: *The exemplary person lives harmoniously with others without needing to agree; the petty person agrees without living harmoniously.*
- “視人之國若視其國，視人之家若視其家，視人之身若視其身。”: *Regard another's state as one's own, another's household as one's own, and another person as oneself.*

Confucian cultivation and relational ethics differ from the Mohist argument for inclusive care. This example uses their respective reminders about disagreement and others' circumstances without claiming the traditions agree on everything. Classical Chinese thought is not an authority that every culture must obey.

<a id="case-4"></a>
## 4. A major client asks for 30% off at renewal

**Hypothetical demonstration, not a customer success story.**

**Hypothetical situation.** A major client asks for a 30% reduction from the existing renewal price. You want to retain the client but worry about losses and delivery. Only the request is established: the client's budget, alternatives, and purchasing motives are unknown, as are your full delivery costs, cash pressure, client concentration, and replacement orders. The analysis provisionally assumes both sides remain willing to talk and neither has accepted new terms. It does not establish that the client is merely testing your minimum price.

**A prompt to reuse**

> Use $dishi to help me prepare a major client's renewal. They want 30% off. I want to keep them, but I have not fully checked costs, cash pressure, replacement orders, or why they want the reduction. Give three distinct routes, your recommendation, a candid objection, and a first step. Do not invent competing offers or scarce capacity, or quietly reduce delivery standards. Check any quotation against a passage ID and explain its original context.

**Judgment**

The immediate question is whether you can sustainably deliver what you promise after that reduction, and whether the client wants lower total spending, a lower unit price, or different payment and service arrangements. These are questions to investigate, not established motives. Without cost and cash information, neither accepting nor rejecting the order is automatically justified.

**Three strategies: A / B / C (上 / 中 / 下)**

- **A — Redesign the package.** If total budget is the constraint, price service scope, delivery frequency, and support levels explicitly, offering a lower total price for an agreed reduction in scope. If a longer commitment or payment arrangement actually reduces your costs, describe the verifiable exchange. The gain is potentially lower spending with sustainable delivery. Costs include redesign and coordination; the client may need the original scope or the proposed exchange may save little. Use this only with informed agreement and matching costs; it does not promise exactly 30% off.
- **B — Keep scope and price, explain verifiable value.** If the full scope is necessary and the existing price sustainable, explain deliverables, established results, and cost boundaries. Invite comparisons on equivalent scope and jointly identify waste that can be removed without lowering quality. The gain is protecting delivery and a defensible price. The cost is potentially losing the order. This fits demonstrated value and an ability to bear that loss; invented competitor criticisms or “last slots” are unacceptable.
- **C — Decline the new terms and reduce or exit in an orderly way.** If the client insists on the original scope at 30% less and you cannot sustain delivery, say what you cannot promise and discuss transition, handover, and existing obligations. The gain is avoiding an undeliverable commitment. Costs include lost income and a cash gap. This requires understanding your capacity to absorb the change; cash pressure calls for examining feasible transition arrangements, not treating the willingness to lose a client as costless bravado.

**Recommendation**

Prepare A first: establish what matters to the client and exchange real scope or terms. Thirty percent is their opening request, not a target you have accepted. Whether original scope and that reduction can coexist depends on actual figures. If the conditions do not fit, consider B or C within your ability to absorb the cash impact. No classical text supplies a universal minimum price.

**Candid objection**

Your vulnerability may be dependence on one client, rather than weak negotiating language. If losing the order immediately threatens basic operations, sounding tougher does not create alternatives. Yet hiding losses or delivery reductions to preserve headline revenue can transfer risks to staff and the client. The client may also have a real budget problem; a request for a discount is not evidence of bad faith.

**First step**

Prepare a one-page renewal calculation: delivery costs at old and new prices, payment timing, capacity required, and affordable losses, marking unknown figures. Then ask: “Is the main constraint total budget, a unit-price target, payment timing, or changed service needs? Which outcomes must remain?” Use confirmed information to prepare two transparent scope-and-price offers. Continue if needs and exchange conditions can be agreed. Adjust or stop if terms require hidden cuts, broken obligations, or commitments you cannot bear.

**Sources: original context and limits of application**

| Quotation and reference | Original context and the limits of modern use |
| --- | --- |
| *Guiguzi*, “Opening and Closing”: **“以求其實，貴得其指。”** `book=guiguzi`, [`GGZ-01-002`](../knowledge/guiguzi/原文.md#ggz-01-002), [fixed source, oldid=2276561](https://zh.wikisource.org/w/index.php?title=%E9%AC%BC%E8%B0%B7%E5%AD%90%2F%E5%8D%B701&oldid=2276561). | The complete passage investigates another's intentions through following desires, counterquestions, and opening and closing, including covert testing and control. Here it prompts checking what a statement actually means. Transparent questions, permission not to answer, and joint confirmation are modern choices in this case. It does not justify leading people, intimidation, or obtaining private information without permission. |
| *The Art of War*, “Planning an Attack”: **“知彼知己，百戰不殆；”** `book=sunzi`, [`SZ-03-008`](../knowledge/sunzi/原文.md#sz-03-008), [fixed source, oldid=7906064](https://zh.wikisource.org/w/index.php?title=孫子兵法&oldid=7906064#謀攻第三). | In a military setting, the passage compares different conditions of knowing the other side and oneself, following five conditions for understanding victory. Here it prompts checking both parties' constraints and your own delivery capability. A client is not an enemy. Avoiding peril does not mean guaranteed victory, zero risk, or a successful agreement, and supplies no discount percentage. |

**Original English translations for this project**

- “以求其實，貴得其指。”: *Seek what is actually the case; what matters is grasping the intended meaning.*
- “知彼知己，百戰不殆；”: *Know the other side and yourself, and you need not be imperiled in a hundred battles.*

The persuasive techniques of *Guiguzi* and Sunzi's military judgments are not a modern business ethic. This case uses them to test information and capability, while separately choosing honest exchange, informed agreement, and deliverable promises. Strategic advice does not grant permission to deceive.

## Verify the quotations

All eight quotations were located through local `search`, read in their full passages through `show`, and checked character for character against the indicated source passage. From the repository root, you can reproduce the reading, for example:

```bash
python3 knowledge/kb.py search "循名" --book hanfeizi --limit 3
python3 knowledge/kb.py show HF-43-002 --book hanfeizi
python3 knowledge/kb.py show ZGL-05-003 --book zhuge
python3 knowledge/kb.py show SZ-03-007 --book sunzi
python3 knowledge/kb.py show LZ-44-001 --book laozi
python3 knowledge/kb.py show LY-13-023 --book lunyu
python3 knowledge/kb.py show MZ-15-002 --book mozi
python3 knowledge/kb.py search "以求其實" --book guiguzi --limit 3
python3 knowledge/kb.py show GGZ-01-002 --book guiguzi
python3 knowledge/kb.py search "知彼知己" --book sunzi --limit 3
python3 knowledge/kb.py show SZ-03-008 --book sunzi
```

Fixed sources identify the revisions used. Exact matching establishes that a quotation occurs in that base text; it does not settle textual criticism, authorship, historical truth, or the effectiveness of a modern application.
