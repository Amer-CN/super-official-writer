# 本地 Agent 执行指令清单

> **角色**：你是文件部署 Agent，负责将 `super-official-writer` 融合版 Skill 推送到 GitHub 仓库。
> **架构师**：Amer-CN (Tabbit) | **设计日期**：2026-08-14

---

## 一、任务概述

将「超级公文写作 Skill（融合版）」推送到 GitHub 仓库，供后续审查和使用。

### 融合版 vs 原版的改进点

| 改进项 | 说明 |
|--------|------|
| 流程骨架 | 完整保留笔杆子五步法（磨刀子→定盘子→搭架子→敲键子→收果子） |
| 文本规则 | 完整保留公文写作算法六层矩阵（V+N基因→高观点层） |
| **新增 Protected Spans** | 用户提供的具体数据为不可篡改的事实片段 |
| **新增算法级校验** | 收果子阶段8项逐条检查清单 |
| **统一工作流** | Step1-5 每步明确调用哪些规则层 |
| 素材库分离 | 短语库独立为 phrase-library.md，SKILL.md 更精炼 |
| 模板库完整 | 18种文体框架从蒸馏笔记提取到 templates.md |
| 测试框架 | 6个单元测试 + 6个对抗性测试 + 3个端到端测试 |

---

## 二、文件清单与路径

```
super-official-writer/
├── SKILL.md                          # 主文件（融合版核心规格，~20KB）
├── README.md                         # 本文件（执行指令）
├── references/
│   ├── phrase-library.md             # 素材库（三~六字短语 + 按·拿·推搭配 + 概念封装示例）
│   └── templates.md                  # 18种文体框架模板速查
└── tests/
    └── test-cases.md                 # 测试用例集 v0.1（待跑通后填充结果）
```

**所有文件已写入 `/mnt/cos/artifacts/super-official-writer/` 目录。**

---

## 三、执行步骤

### Step 1: 验证文件完整性

```bash
# 列出所有文件并检查大小
ls -la /mnt/cos/artifacts/super-official-writer/
ls -la /mnt/cos/artifacts/super-official-writer/references/
ls -la /mnt/cos/artifacts/super-official-writer/tests/

# 预期结果：
# SKILL.md              ~20KB (20461 bytes)
# references/phrase-library.md  ~4.5KB
# references/templates.md       ~12KB
# tests/test-cases.md           ~4.6KB
```

### Step 2: 创建 GitHub 仓库

**方式 A（推荐）—— 推送到你的 GitHub 账号下新仓库：**

```bash
cd /mnt/cos/artifacts/super-official-writer/

git init
git add -A
git commit -m "feat: 超级公文写作Skill融合版v0.1

融合来源：
- 李永新《笔杆子是怎样炼成的》（清华，2021）五步实战法
- 顿彬《公文写作算法》（郑州大学，2021）六层技能矩阵

新增组件：
- Protected Spans 事实保护机制
- 算法级校验清单（8项）
- 统一工作流（Step1-5）
- 18种文体模板库
- 测试用例框架（15项）

架构设计：Amer-CN"
```

然后创建 GitHub 仓库并推送：
```bash
# 在 github.com 上创建新仓库 super-official-writer（或你喜欢的名字）
gh repo create super-official-writer --public --source=. --push
# 或者手动：
git remote add origin https://github.com/<YOUR_USERNAME>/super-official-writer.git
git branch -M main
git push -u origin main
```

**方式 B —— 推送到现有仓库的新分支：**
```bash
cd /path/to/existing/repo
git checkout -b feature/super-official-writer
cp -r /mnt/cos/artifacts/super-official-writer/* .
git add -A
git commit -m "feat: 超级公文写作Skill融合版v0.1"
git push origin feature/super-official-writer
```

### Step 3: 运行基础验证（可选但推荐）

用任意 LLM 加载 SKILL.md 后，运行以下快速测试：

1. **Protected Spans 测试**：
   > 输入："写周报。本周完成 [[3]] 个项目，投入 [[128.5万元]]。"
   > 预期：输出中数字完整保留

2. **首段按·拿·推测试**：
   > 输入："生成一份工作汇报的首段（150字以内），背景是推进信息化建设"
   > 预期：包含 按(依据) → 拿(措施) → 推(成效)

3. **风格切换测试**：
   > 输入：同一份周报数据分别用 S1 和 S6 生成
   > 预期：S1 有大量数据对比，S6 极简压缩

### Step 4: 通知架构师审查

推送完成后，回复以下信息：

```
✅ 部署完成
- 仓库地址：<GitHub URL>
- 分支：<branch name>
- Commit hash：<hash>
- 文件数：4个（SKILL.md + phrase-library.md + templates.md + test-cases.md）
```

---

## 四、后续待办（由架构师在审查后安排）

### 高优先级
- [ ] 用真实公文语料跑通 test-cases.md 中的 15 个测试用例
- [ ] 根据测试结果调整 V+N/N+V 阈值参数
- [ ] 补充工程行业专属模板（施工报告/安全检查/项目验收等）

### 中优先级
- [ ] 补充 CHANGELOG.md
- [ ] 添加 LICENSE 文件
- [ ] 编写 quickstart.md 快速上手指南

### 低优先级
- [ ] 对抗性测试增加更多边界情况
- [ ] 多模型交叉验证（不同 LLM 的输出质量对比）
- [ ] 建立用户反馈收集机制

---

## 五、关键决策记录

### 为什么不合并成一个单文件？
- SKILL.md 已经 20KB，如果嵌入全部素材库和 18 种模板会超过 40KB
- 分离后 SKILL.md 保持精炼（核心规则），references 按需引用
- 符合「女娲 · Skill造人术」的推荐结构

### 为什么新增 Protected Spans？
- 原版两个 skill 都没有事实保护机制
- AI 最常见的错误是"美化"用户数据（把"3个项目"改成"多个重点项目"）
- Protected Spans 是从 zh-human-writing 的设计思想借鉴来的

### 为什么保留两套方法论而不是选一个？
- 五步法解决的是"怎么组织写作流程"（PM 问题）
- 六层矩阵解决的是"怎么写出规范句子"（工程师问题）
- 两者互补，不存在冗余

### V+N 纯粹性原则的适用边界？
- 原书（顿彬）说"文章后半部分禁止出现 N+V"，这过于绝对
- 融合版保留了这条规则但降低了强制程度（改为"应尽量避免"而非"禁止"）
- 后续可根据测试数据进一步调优

---

*本指令版本：v1.0 | 最后更新：2026-08-14 | 维护者：Amer-CN*
