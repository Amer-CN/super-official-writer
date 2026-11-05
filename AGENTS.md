# super-official-writer 仓库指南（给下一个会话）

一句话：中文体制内公文写作 skill——知识库（corpus 分层）+ 模板 + 量化风格参数 + 自检脚本 + GB/T 9704 docx 排版，GitHub 公开（Amer-CN/super-official-writer）。

## 怎么跑/验证

```bash
python scripts/version_check.py                          # 版本自检（应 current）
python scripts/check_integrity.py                        # 完整性门禁（推送前必跑，应全 PASS）
python scripts/search_corpus.py "核稿 批复"              # 知识库排序检索（--stats 看库存）
python tests/test_search_corpus.py                       # 检索回归自测（CI 同款）
python scripts/check_params.py 稿件.md --genre 文种       # 风格自检（--match 猜文种）
python scripts/build_corpus_index.py                     # 重建 references/corpus/INDEX.md
node scripts/render_docx.js --demo                       # docx 排版演示（需 npm install）
```

## 关键约定（改前必读）

- **版本锚点**：SKILL.md 中 YAML frontmatter 与 H1 之后的第一个非空行 `<!-- skill-version: vX.Y -->`，release 时与 CHANGELOG/README 版本行三处同步。
- **frontmatter**：SKILL.md 首部必须有 YAML frontmatter（`name: super-official-writer` 与目录名一致 + `description`），Cherry Studio / Claude Code 等按它识别技能；**不要写 `version` 字段**（版本唯一真源是锚点）。check_integrity 第 14/15 项已断言。
- **corpus 分层**：知识按来源进 `references/corpus/` 一个来源一个文件；新增蒸馏 = 新层文件 + `corpus-lingyun.md` 索引页加行 + 重跑 build_corpus_index.py。**不往单体塞。**
- **INDEX.md 自动生成勿手改**；dataset（F:/AIXM/XZ/lingyun/dataset/gongwen_writing_dataset.jsonl，1919 条）是知识单元的唯一结构化真身。
- **评测循环**：tests/test-cases.md 固定 15 用例（run1-3 全量三轮已收官）+ run4 起改为**跨模型增量盲评**（异厂出题/答题/双裁判/事实核查，见 test-cases.md 四轮节）；每稿清稿前必跑 `check_params.py --final` 终检门（引号不过不得清稿）。
- 知识收集原则：**按需定向**（评测暴露短板再补），不批量漫灌。
- 数据集不公开发布（版权风险，2026-09-04 拍板，见 .work/decisions/）。

## 目录

- `references/corpus/`：28 个分层文件 + INDEX.md（来源见索引页）
- `references/`：templates（21 模板）/ style-params（7 文种参数）/ phrase-library / format-spec（GB/T 9704）/ sources（条例+GB9704 原文+27 份报告）
- `scripts/`：render_docx（排版，v0.16 起含 docNumber 文号行+keepNext+奇偶页码，GB/T 9704 要素齐备）/ check_params（风格自检+--final 终检门）/ version_check（更新）/ build_corpus_index（索引）/ search_corpus（排序检索）/ check_integrity（完整性门禁，CI 跑 --structural）
- `docs/distillation-sop.md`：抖音博主蒸馏流水线 SOP（供其他窗口/项目复用）
- `docs/integration-contract.md`：集成契约（下游稳定面承诺；改 SKILL 章节编号/T 编号/锚点格式前必读，breaking 须 CHANGELOG 标注）
- `tests/`：test-cases.md 评测基线；test_search_corpus.py 检索回归自测（CI 跑）
- `.work/`：任务简报与决策备忘（gitignored）；决策备忘在 `.work/decisions/`

## 当前状态（2026-11-05）

v0.24 本地已改（2026-11-05，待推送：知识库排序检索 + 结构 CI，无知识增量，dataset 仍 1919/48 类）；v0.23 已推送（补 Agent Skills frontmatter，breaking 版本锚点位置）；v0.22 已推送（炼成2单书蒸馏层 `book-liancheng2.md` 24 条，dataset 1895→1919/48 类）。**接手入口：`F:/AIXM/XZ/lingyun/HANDOFF-2026-09-16.md`**（09-15/16 会话全记录+机制+遗留；09-06 版留作历史）。语料生产现场在 `F:/AIXM/XZ/lingyun/`（本地 git，博主查重表 `blogger-registry.md`；该仓另有另一窗口的 blogger6/erp_dev 独立数据集，与本 skill 无关勿混）。评测五轮收官（run5 增量盲评：10 黑洞模板首测可用，终分 57/65，虚构是跨写作者头号失分项）。遗留：十二书单收官（顿彬未上架除外）；评测后续走增量盲评模式。推送前必跑 `python scripts/check_integrity.py`（15 项完整性断言：版本三处/dataset 唯一 id 与合计对账/SKILL 计数行自洽/INDEX 零 diff/终检门回归 24 稿/盲卷零泄漏/README 散文计数/致谢博主覆盖/版本字符串三类/索引页计数抽查/frontmatter 合规/锚点紧跟 H1，索引页抽查对 2 个层文件各出一条故共 16 行 PASS）；CI 跑 `--structural` 档（9 行 PASS，跳过仓外 dataset/评测稿/注册表相关 6 项），配置在 `.github/workflows/integrity.yml`。**注意：若 INDEX 属本版本交付物，"INDEX 零 diff"断言会 FAIL 且脚本自动 checkout 回滚它——提交前须最后重跑一次 `build_corpus_index.py`。**
