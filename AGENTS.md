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
- **INDEX.md 自动生成勿手改**；dataset（F:/AIXM/XZ/lingyun/dataset/gongwen_writing_dataset.jsonl，965 条）是知识单元的唯一结构化真身。
- **评测循环**：tests/test-cases.md 固定 15 用例（run1-3 全量三轮已收官）+ run4 起改为**跨模型增量盲评**（异厂出题/答题/双裁判/事实核查，见 test-cases.md 四轮节）；每稿清稿前必跑 `check_params.py --final` 终检门（引号不过不得清稿）。
- 知识收集原则：**按需定向**（评测暴露短板再补），不批量漫灌。
- 数据集不公开发布（版权风险，2026-09-04 拍板，见 .work/decisions/）。

## 目录

- `references/corpus/`：13 个分层文件 + INDEX.md（来源见索引页）
- `references/`：templates（21 模板）/ style-params（7 文种参数）/ phrase-library / format-spec（GB/T 9704）/ sources（条例+GB9704 原文+27 份报告）
- `scripts/`：render_docx（排版，v0.16 起含 docNumber 文号行+keepNext+奇偶页码，GB/T 9704 要素齐备）/ check_params（风格自检+--final 终检门）/ version_check（更新）/ build_corpus_index（索引）
- `docs/distillation-sop.md`：抖音博主蒸馏流水线 SOP（供其他窗口/项目复用）
- `.work/`：任务简报与决策备忘（gitignored）；决策备忘在 `.work/decisions/`

## 当前状态（2026-09-06）

v0.16 已推送（GB/T 9704 docx 渲染要素齐备：标题/文号/字体/页码）。语料生产现场在 `F:/AIXM/XZ/lingyun/`（本地 git，博主查重表 `blogger-registry.md`；该仓另有另一窗口的 blogger6/erp_dev 独立数据集，与本 skill 无关勿混）。评测四轮收官（run4 盲评 executor 0.942＞主窗口 0.833）。遗留：P2-19 观察项（不动）、tests 尚无自动化断言、评测后续走增量盲评模式。
