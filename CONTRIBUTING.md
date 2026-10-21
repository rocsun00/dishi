# 参与改进 / Contributing

欢迎提交可核实的文字纠错、英文术语改进、安装问题及使用反馈。请勿把私人对话、客户资料或访问凭证放入公开 issue。

We welcome verifiable text corrections, English retrieval improvements, installation reports, and usage feedback. Keep private conversations, client information, and credentials out of public issues.

项目发起与维护：**Roc Sun**。公开展示名为 **帝师 Imperial Preceptor**，技术标识 `dishi` 保持兼容；贡献者保留其依法享有的权利，第三方材料按各自条件使用。

Created and maintained by **Roc Sun**. The public name is **Imperial Preceptor** (帝师), while `dishi` remains the compatible technical identifier. Contributors retain their applicable rights; third-party material remains subject to its own terms.

## 提交问题 / Report an issue

- 原典：给出书名、完整段号、所据版本或固定来源，以及你认为有问题的文字。不同版本的读法应分层记录，不直接覆盖工作底本。
- 英文：提供原问题、`explain-query` 的映射、预期含义和实际结果。指出是检索缺词、译述错误还是现实推断问题。
- 安装：提供系统、Python 版本、运行命令和已脱敏的错误信息。

- For a textual issue, include the work, full passage ID, edition or fixed source, and exact disputed wording. Record variant readings separately rather than silently replacing the base text.
- For English, include the original question, `explain-query` output, intended meaning, and actual result. Distinguish retrieval gaps, translation errors, and problems in modern reasoning.
- For installation, include the operating system, Python version, command, and a redacted error report.

## 修改与检查 / Changes and checks

维护原典、古注、现代解读与应用的分层；保留上游来源、许可和加工记录。新增英文映射应可审查，不能把关联词检索包装成语义理解。示例需标明假设，不能伪造客户成绩、引文或模型测试数据。

Keep source text, commentary, modern interpretation, and application distinct. Preserve upstream attribution, terms, and processing records. English mappings must remain inspectable; keyword retrieval is not semantic understanding. Label hypothetical examples and do not invent customer outcomes, quotations, or test results.

From the repository root / 从项目根目录：

```bash
python3 -B -m unittest discover -s knowledge/tests -v
python3 -B -m unittest discover -s tests -v
python3 -B knowledge/kb.py validate
```

安装集成测试会在临时目录复制完整知识库、更新并读回，不会写入个人技能目录。改动某部原典时还需按该书来源和质量说明检查上下文；通用校验不证明解释无误。

The installation integration test copies, updates, and reads back the full corpus in a temporary directory; it does not install into your personal skills folder. Textual changes also need contextual review against that work's source and quality notes. Mechanical validation does not prove an interpretation correct.

提交贡献意味着你有权按本项目对应的[内容许可](LICENSE)或[原创代码许可](LICENSE-CODE)提供该贡献；第三方内容须另带其适用条款与署名。

Contribute only material you may provide under the applicable [content](LICENSE) or [original-code](LICENSE-CODE) terms. Include the terms and attribution for third-party material separately.
