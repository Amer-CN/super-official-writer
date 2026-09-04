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
- **INDEX.md 自动生成勿手改**；dataset（F:/AIXM/XZ/lingyun/dataset/，958 条）是知识单元的唯一结构化真身。
- **评测循环**：tests/test-cases.md 是固定用例集（15 用例），新版本可重跑对比；问题清单驱动下一版本定向修复（v0.12 为首轮修复）。
- 知识收集原则：**按需定向**（评测暴露短板再补），不批量漫灌。
- 数据集不公开发布（版权风险，2026-09-04 拍板，见 .work/decisions/）。

## 目录

- `references/corpus/`：13 个分层文件 + INDEX.md（来源见索引页）
- `references/`：templates（21 模板）/ style-params（7 文种参数）/ phrase-library / format-spec（GB/T 9704）/ sources（条例+GB9704 原文+27 份报告）
- `scripts/`：render_docx（排版）/ check_params（风格自检）/ version_check（更新）/ build_corpus_index（索引）
- `.work/`：任务简报与决策备忘（gitignored）；决策备忘在 `.work/decisions/`

## 当前状态（2026-09-04）

v0.12 已推送。语料生产现场在 `F:/AIXM/XZ/lingyun/`（本地 git）。遗留备选：3 条未认领评测 P2、SKILL.md 七·二分类旧计数漂移、tests 尚无自动化断言。
