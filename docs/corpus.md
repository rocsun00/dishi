# 原典与语言说明 / Corpus and language notes

[中文首页](../README.md) · [English README](../README.en.md) · [中文案例](examples.zh-CN.md) · [English examples](examples.en.md)

## 收录与统计 / Coverage and counts

截至本版，目录中有 **27 种 `ready` 典籍或文献集**，包括 **6,640 个原文定位单元及对应释义、2,226 张思想卡、871 组问答**，本地验收记录 **3,645 次逐字引文匹配校验**。统计衡量收录量与引句对应关系，不衡量解释准确率、历史真实性或决策效果；校验次数不等于互不重复的引文数量。

This version contains **27 ready texts or document collections**, with **6,640 source units and corresponding readings, 2,226 idea cards, and 871 question-and-answer examples**. Local validation records **3,645 exact quotation-match checks**. These counts describe coverage and quotation correspondence, not interpretive accuracy, historical truth, or decision outcomes. A check count is not a count of unique quotations.

实际状态以[目录](../knowledge/catalog.json)为准；全库记录见[校验汇总](../knowledge/validation.json)，各书下有 `data/validation.json`。`ready` 是项目检索与验收状态；`staged` 不进入正式检索。“完整”仅指下列明确范围，不补造亡篇，也不代表所有异本或某人的全部著作。

The [catalog](../knowledge/catalog.json) defines the actual status. See the [validation summary](../knowledge/validation.json) and each collection's `data/validation.json` for records. `ready` is a project retrieval and validation status; `staged` collections are excluded from normal search. “Complete” refers only to the stated scope below, not lost chapters, every textual variant, or a person's complete works.

书名链接进入本地原文；英文书名供识别，不表示采用或随附了同名英文出版译本。段落可以是章句、故事、论述组或整篇，其长度并不统一。

Title links open the local Chinese source text. English titles identify the works; they do not imply that a published English translation is included or used. A source unit may be a saying, story, argument group, or complete chapter; units do not have uniform length.

| CLI `book` | 中文 / English | 实际范围 / Included scope | 原文单元 / Units |
| --- | --- | --- | ---: |
| `sunzi` | [孙子兵法 / The Art of War](../knowledge/sunzi/原文.md) | 十三篇 / 13 chapters | 74 |
| `laozi` | [老子 / Laozi (Daodejing)](../knowledge/laozi/原文.md) | 王弼本正文八十一章 / 81 chapters, main text of the Wang Bi edition | 81 |
| `daxue` | [大学 / Great Learning](../knowledge/daxue/原文.md) | 《礼记》篇本 / the chapter in the Book of Rites | 16 |
| `gongsunlongzi` | [公孙龙子 / Gongsun Longzi](../knowledge/gongsunlongzi/原文.md) | 现存六篇 / 6 surviving chapters | 35 |
| `lunyu` | [论语 / Analects](../knowledge/lunyu/原文.md) | 二十篇 / 20 chapters | 501 |
| `zhuangzi` | [庄子 / Zhuangzi](../knowledge/zhuangzi/原文.md) | 三十三篇，保留内外杂篇 / 33 chapters; Inner, Outer, and Miscellaneous groups retained | 289 |
| `mozi` | [墨子 / Mozi](../knowledge/mozi/原文.md) | 现存五十三篇，保留缺号 / 53 surviving chapters; missing numbers retained | 650 |
| `hanfeizi` | [韩非子 / Han Feizi](../knowledge/hanfeizi/原文.md) | 五十五篇 / 55 chapters | 766 |
| `mengzi` | [孟子 / Mencius](../knowledge/mengzi/原文.md) | 七篇十四卷 / 7 books in 14 parts | 260 |
| `xunzi` | [荀子 / Xunzi](../knowledge/xunzi/原文.md) | 三十二篇 / 32 chapters | 481 |
| `lvshichunqiu` | [吕氏春秋 / Annals of Lü Buwei](../knowledge/lvshichunqiu/原文.md) | 二十六卷一百六十子篇 / 26 juan, 160 sections | 735 |
| `huainanzi` | [淮南子 / Huainanzi](../knowledge/huainanzi/原文.md) | 传世内篇二十一篇，含《要略》 / 21 transmitted Inner chapters, including Yaolüe | 460 |
| `guanzi` | [管子 / Guanzi](../knowledge/guanzi/原文.md) | 八十六目中的七十六存篇 / 76 surviving chapters from 86 listed titles | 661 |
| `shangjunshu` | [商君书 / Book of Lord Shang](../knowledge/shangjunshu/原文.md) | 二十六目中的二十四存篇 / 24 surviving chapters from 26 listed titles | 127 |
| `fanli` | [范蠡相关早期文献集 / Early documents concerning Fan Li](../knowledge/fanli/原文.md) | 《国语·越语下》及《史记》两处完整相关节 / Yueyu II in Guoyu and two complete relevant sections in Shiji | 28 |
| `zhuge` | [诸葛亮核心文献与史传 / Core documents and historical accounts concerning Zhuge Liang](../knowledge/zhuge/原文.md) | 十五整理单元 / 15 editorial units | 75 |
| `wangyangming` | [王阳明核心原典 / Core texts concerning Wang Yangming](../knowledge/wangyangming/原文.md) | 《传习录》三卷、《大学问》 / 3 juan of Instructions for Practical Living and Questions on the Great Learning | 353 |
| `guiguzi` | [鬼谷子 / Guiguzi](../knowledge/guiguzi/原文.md) | 三卷现存正文，二十一工作单元 / surviving text in 3 juan, 21 working units | 52 |
| `zhanguoce` | [战国策 / Strategies of the Warring States](../knowledge/zhanguoce/原文.md) | 士礼居丛书电子工作本三十三卷 / 33 juan, electronic working text of the Shiliju collection edition | 497 |
| `wuzi` | [吴子 / Wuzi](../knowledge/wuzi/原文.md) | 现存六篇 / 6 surviving chapters | 43 |
| `simafa` | [司马法 / Methods of the Sima](../knowledge/simafa/原文.md) | 现存五篇 / 5 surviving chapters | 68 |
| `weiliaozi` | [尉缭子 / Weiliaozi](../knowledge/weiliaozi/原文.md) | 四库电子本五卷二十四篇 / Siku electronic text, 5 juan, 24 chapters | 24 |
| `liutao` | [六韬 / Six Secret Teachings](../knowledge/liutao/原文.md) | 六组六十篇 / 6 groups, 60 chapters | 60 |
| `sanlue` | [三略（兵学扩展） / Three Strategies (military-text extension)](../knowledge/sanlue/原文.md) | 上中下三略 / Upper, Middle, and Lower Strategies | 65 |
| `liweigongwendui` | [李卫公问对（兵学扩展） / Questions and Replies of Li, Duke of Wei (military-text extension)](../knowledge/liweigongwendui/原文.md) | 三卷，源题《唐李问对》 / 3 juan; source title Tang Li Wendui | 50 |
| `zhongyong` | [中庸 / Doctrine of the Mean](../knowledge/zhongyong/原文.md) | 《礼记》篇本，五十项目语义段 / the chapter in the Book of Rites, 50 project-defined semantic passages | 50 |
| `liezi` | [列子 / Liezi](../knowledge/liezi/原文.md) | 传世八篇电子工作本 / electronic working text of the 8 transmitted chapters | 139 |

## 来源层次与时代 / Sources, layers, and periods

各书的 `source/source.json` 记录所据电子页面、固定修订或来源清单；`source/` 保存原始快照和加工记录；`data/passages.jsonl` 保存带段号、来源的正文。原文、古注、后人评论、项目释义、思想卡与问答各有层次。引用重要句子时，应先 `show` 读全段，再查看本书质量说明和对读校记（如有）。项目段号是本库定位工具，不是所有版本共用的古代章次。

Each collection's `source/source.json` records the electronic source, fixed revision, or source list. `source/` preserves snapshots and processing records, and `data/passages.jsonl` stores source passages with IDs and references. Main text, old commentary, later commentary, project readings, idea cards, and examples are distinct layers. Before using an important quotation, read the complete passage with `show`, then consult that collection's quality notes and comparison notes where available. Project passage IDs are retrieval references, not universal ancient numbering.

这不是二十七部同一时代、同一学派、作者均可确证的书。《大学》《中庸》以《礼记》篇本入库；《中庸》的五十段不是朱熹三十三章。《庄子》等传本保留编纂层次与多种声音，《列子》等的归属及成书争议不因入库而消失。《淮南子》是汉代合编著作；诸葛亮与王阳明不归为先秦诸子。《三略》《李卫公问对》作为后世兵学扩展收录，旧题与人物对话不证明逐字实录或亲著。人物文献集也区分本人文书、史家记述、门人记录和有争议的归属。

These are not 27 works from a single period or school with uniformly secure authorship. The *Great Learning* and *Doctrine of the Mean* use their *Book of Rites* chapter forms; the latter's 50 units are not Zhu Xi's 33 chapters. Transmitted works such as the *Zhuangzi* retain different voices and compilation layers; inclusion does not resolve disputes concerning works such as the *Liezi*. The *Huainanzi* is a Han-period compilation. Zhuge Liang and Wang Yangming are not pre-Qin thinkers. The *Three Strategies* and *Questions and Replies of Li, Duke of Wei* are included as later military-text extensions; traditional titles and dialogue frames do not establish verbatim records or personal authorship. Personal collections distinguish documents, historical accounts, disciples' records, and disputed attributions.

全库是电子工作资料与 AI 辅助释读，不是学术校勘定本；保留疑字或校记是为了追溯，不是宣布疑问已解决。逐字校验可以发现引句与本底本不符，却不能证明底本无误，也不能证明释义或现实建议正确。本库没有用于模型微调训练。

The corpus is an electronic working resource with AI-assisted readings, not a scholarly critical edition. Retaining uncertain characters and comparison notes supports traceability; it does not resolve every uncertainty. Exact-match checks can find quotations that do not match the base text, but cannot prove that the base text, interpretation, or modern advice is correct. The corpus has not been used for model fine-tuning.

## 中英文如何共用 / How Chinese and English use the same corpus

**中文底本共同，英语按需译述。** 英文用户可以用宿主助手支持的语言提问。宿主模型读取中文材料后生成英文解释或翻译，应保留中文引文、来源和不确定性。项目目前没有全库英文逐段译本；英语自译也不冒充学术出版翻译。模型的语言能力与本地检索器的词表覆盖是两回事。

**Both language experiences use the Chinese base text; English is generated on demand.** Users may ask in a language supported by the host assistant. The host model reads Chinese material and generates an English explanation or translation, retaining the Chinese quotation, source, and uncertainty. There is no complete passage-by-passage English edition of the corpus. Original project translations are not presented as scholarly published translations. The model's language ability and the local retriever's vocabulary coverage are separate capabilities.

本地 CLI 按字段权重、词频饱和与长度排序，原文权重高于现代解释；支持中文词法检索，并提供有限的人工英文关键词与书名映射；它不翻译任意句子，也不是语义检索或英文全文检索。映射只能提出阅读候选，不能判定相关性、赞同某项观点或识别完整论证。用 `explain-query` 查看实际命中的词、映射词、忽略词、未识别词及警告；如需限定典籍，使用 `--book`，不能仅靠查询里出现书名。书名提示可以提升已有命中的排序；含英文否定时停用英文映射，需要宿主保留原意重新检索。

The local CLI ranks fields with term-frequency saturation and length normalization, giving original text greater weight than modern commentary. It supports Chinese lexical search and a finite, curated mapping of English keywords and book names. It does not translate arbitrary sentences, perform semantic search, or search a complete English corpus. Mappings produce reading candidates; they do not establish relevance, agreement with a claim, or the structure of an argument. Use `explain-query` to inspect recognized input, mapped terms, ignored terms, unrecognized terms, and warnings. Use `--book` to restrict a collection; mentioning a title alone does not impose that restriction. Book hints can boost matching candidates. English negation disables English mappings conservatively, requiring the host to preserve the intent when reformulating.

从仓库根目录运行 / Run from the repository root:

```bash
python3 knowledge/kb.py explain-query "trust and cooperation" --json
python3 knowledge/kb.py search "trust and cooperation" --limit 3 --json
python3 knowledge/kb.py search "合作 信任" --limit 3
python3 knowledge/kb.py show LY-13-023 --book lunyu
python3 knowledge/kb.py validate
```

最后一项重新执行本地检查。CLI 不联网、不自动生成答案；需要英语解释时，由宿主模型在检索之后完成。一个问题没有检索结果，不等于古籍从未讨论过相关问题；有结果也必须回看原文与语境。

The last command reruns local checks. The CLI works offline and does not generate answers. A host model supplies any English explanation after retrieval. No search results do not establish that the sources never address an issue, and a match still requires reading the text in context.

## 使用与再分发 / Use and redistribution

古代思想的现代转用需明示条件和代价。各家真实分歧应保留，历史类比不当作现代规律；军事、君主控制与古代等级关系也不自动成为当代合作规则。需要当下数据或专业意见时，应另行核实。

Modern applications need explicit conditions and costs. Preserve real disagreements among traditions, and do not turn historical analogies into present-day laws. Warfare, monarchical control, and ancient hierarchies do not automatically supply rules for contemporary cooperation. Verify current facts and obtain relevant professional input when a question requires them.

许可范围见 [LICENSE](../LICENSE) 与 [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md)。源文本、电子快照与项目新增内容的来源和许可可能不同，不能因古代作品年代久远而忽略电子来源的再分发条件。

See [LICENSE](../LICENSE) and [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md). Source texts, electronic snapshots, and new project material may have different origins and licensing terms. A work's age does not remove the need to examine the electronic source's redistribution conditions.
