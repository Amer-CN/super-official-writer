# super-official-writer 仓库指南（给下一个会话）

一句话：中文体制内公文写作 skill——知识库（corpus 分层）+ 模板 + 量化风格参数 + 自检脚本 + GB/T 9704 docx 排版，GitHub 公开（Amer-CN/super-official-writer）。

## 怎么跑/验证

```bash
python scripts/version_check.py                          # 版本自检（应 current）
python scripts/check_params.py 稿件.md --genre 文种       # 风格自检（--match 猜文种）
python scripts/build_corpus_index.py                     # 重建 references/corpus/INDEX.md
node scripts/render_docx.js --demo                       # docx 排版演示（需 npm install）
```

## 关键约定（改前必读）

- **版本锚点**：SKILL.md 第 3 行 `<!-- skill-version: vX.Y -->`，release 时与 CHANGELOG/README 版本行三处同步。
- **corpus 分层**：知识按来源进 `references/corpus/` 一个来源一个文件；新增蒸馏 = 新层文件 + `corpus-lingyun.md` 索引页加行 + 重跑 build_corpus_index.py。**不往单体塞。**
- **INDEX.md 自动生成勿手改**；dataset（F:/AIXM/XZ/lingyun/dataset/gongwen_writing_dataset.jsonl，1895 条）是知识单元的唯一结构化真身。
- **评测循环**：tests/test-cases.md 固定 15 用例（run1-3 全量三轮已收官）+ run4 起改为**跨模型增量盲评**（异厂出题/答题/双裁判/事实核查，见 test-cases.md 四轮节）；每稿清稿前必跑 `check_params.py --final` 终检门（引号不过不得清稿）。
- 知识收集原则：**按需定向**（评测暴露短板再补），不批量漫灌。
- 数据集不公开发布（版权风险，2026-09-04 拍板，见 .work/decisions/）。

## 目录

- `references/corpus/`：27 个分层文件 + INDEX.md（来源见索引页）
- `references/`：templates（21 模板）/ style-params（7 文种参数）/ phrase-library / format-spec（GB/T 9704）/ sources（条例+GB9704 原文+27 份报告）
- `scripts/`：render_docx（排版，v0.16 起含 docNumber 文号行+keepNext+奇偶页码，GB/T 9704 要素齐备）/ check_params（风格自检+--final 终检门）/ version_check（更新）/ build_corpus_index（索引）
- `docs/distillation-sop.md`：抖音博主蒸馏流水线 SOP（供其他窗口/项目复用）
- `docs/integration-contract.md`：集成契约（下游稳定面承诺；改 SKILL 章节编号/T 编号/锚点格式前必读，breaking 须 CHANGELOG 标注）
- `.work/`：任务简报与决策备忘（gitignored）；决策备忘在 `.work/decisions/`

## 当前状态（2026-09-16）

v0.21 已推送（速成法套装四卷蒸馏层 `book-sucheng1.md` 49／`book-sucheng2.md` 54／`book-sucheng3.md` 11／`book-sucheng4.md` 109 条，dataset 1672→1895/48 类）。**接手入口：`F:/AIXM/XZ/lingyun/HANDOFF-2026-09-16.md`**（09-15/16 会话全记录+机制+遗留；09-06 版留作历史）。语料生产现场在 `F:/AIXM/XZ/lingyun/`（本地 git，博主查重表 `blogger-registry.md`；该仓另有另一窗口的 blogger6/erp_dev 独立数据集，与本 skill 无关勿混）。评测五轮收官（run5 增量盲评：10 黑洞模板首测可用，终分 57/65，虚构是跨写作者头号失分项）。遗留：炼成2（模板书，低优先级）待排期；顿彬《公文写作算法》未上架不走通道；评测后续走增量盲评模式。推送前必跑 `python scripts/check_integrity.py`（13 项完整性断言：版本三处/dataset 唯一 id 与合计对账/SKILL 计数行自洽/INDEX 零 diff/终检门回归 24 稿/盲卷零泄漏/README 散文计数/致谢博主覆盖/版本字符串三类/索引页计数抽查，索引页抽查对 2 个层文件各出一条故共 14 行 PASS）。**注意：若 INDEX 属本版本交付物，"INDEX 零 diff"断言会 FAIL 且脚本自动 checkout 回滚它——提交前须最后重跑一次 `build_corpus_index.py`。**
